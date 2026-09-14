import Foundation

public struct LocationFix: Sendable {
    public let coordinate: Coordinate
    public let timestamp: Date
    public let accuracy: Double
    public let speed: Double
    public let course: Double?
    public init(coordinate: Coordinate, timestamp: Date, accuracy: Double, speed: Double, course: Double?) {
        self.coordinate = coordinate; self.timestamp = timestamp; self.accuracy = accuracy
        self.speed = speed; self.course = course
    }
    public func isUsable(at now: Date) -> Bool {
        coordinate.isValid && accuracy.isFinite && (0...75).contains(accuracy)
        && now.timeIntervalSince(timestamp) >= -5 && now.timeIntervalSince(timestamp) <= 15
    }
}

public struct CameraWarning: Sendable {
    public let camera: Camera
    public let distance: Double
}

public struct Encounter: Codable, Sendable, Equatable {
    public var lastAlert: Date
    public var armed: Bool
}

public struct AlertEngine: Sendable {
    public private(set) var encounters: [String: Encounter]
    private var previous: LocationFix?
    private var lastMovingAt: Date?
    private var courseAnchor: LocationFix?
    private var derivedCourse: (bearing: Double, at: Date)?
    public init(encounters: [String: Encounter] = [:]) { self.encounters = encounters }

    public mutating func evaluate(_ fix: LocationFix, index: CameraIndex, now: Date) -> [CameraWarning] {
        guard fix.isUsable(at: now) else { return [] }
        if let previous, fix.timestamp <= previous.timestamp { return [] }
        defer { previous = fix }
        if fix.speed.isFinite && fix.speed >= 2.5 { lastMovingAt = now }
        let moving = lastMovingAt.map { now.timeIntervalSince($0) < 120 } ?? false
        // Rearm even when a site is no longer in the spatial query.
        for (id, encounter) in encounters where !encounter.armed {
            guard let camera = index.camera(id: id) else { continue }
            let d = Geometry.distance(fix.coordinate, Geometry.nearest(to: fix.coordinate, on: camera.geometry))
            if d > 850 && now.timeIntervalSince(encounter.lastAlert) >= 60 { encounters[id]?.armed = true }
        }
        guard moving else { return [] }
        let speed = fix.speed.isFinite ? max(0, fix.speed) : 0
        let lead = min(600, max(150, speed * 15))
        let course = travelCourse(for: fix)
        var warnings: [CameraWarning] = []
        for camera in index.nearby(fix.coordinate) {
            if let end = camera.validUntil, now >= end { continue }
            if let encounter = encounters[camera.id], !encounter.armed { continue }
            let nearest = Geometry.nearest(to: fix.coordinate, on: camera.geometry)
            let distance = Geometry.distance(fix.coordinate, nearest)
            guard distance <= lead else { continue }
            if let expected = camera.travelBearing, let course,
               Geometry.angleDifference(expected, course) > 65 { continue }
            // A good course rejects cameras behind the driver. Near a point or
            // inside a corridor, bearing-to-point is unstable and is not used.
            if distance > max(50, fix.accuracy), let course,
               Geometry.angleDifference(course, Geometry.bearing(from: fix.coordinate, to: nearest)) > 75 { continue }
            if course == nil && distance > 100 {
                guard let previous, fix.timestamp.timeIntervalSince(previous.timestamp) < 30 else { continue }
                let oldDistance = Geometry.distance(previous.coordinate, Geometry.nearest(to: previous.coordinate, on: camera.geometry))
                guard oldDistance - distance > 4 else { continue }
            }
            warnings.append(CameraWarning(camera: camera, distance: distance))
            encounters[camera.id] = Encounter(lastAlert: now, armed: false)
        }
        // Retain a stopped encounter for up to a month so waiting at a light or
        // restarting the process does not repeat a warning.
        encounters = encounters.filter { now.timeIntervalSince($0.value.lastAlert) < 30 * 86400 }
        return warnings.sorted { $0.distance < $1.distance }
    }

    private mutating func travelCourse(for fix: LocationFix) -> Double? {
        if let course = fix.course, course.isFinite, (0..<360).contains(course) {
            courseAnchor = fix; derivedCourse = nil
            return course
        }
        // Some location sources supply usable positions without course accuracy.
        // Accumulate enough displacement to exceed GPS uncertainty before inferring travel.
        if let anchor = courseAnchor, fix.timestamp.timeIntervalSince(anchor.timestamp) <= 15 {
            let distance = Geometry.distance(anchor.coordinate, fix.coordinate)
            if distance >= max(20, anchor.accuracy + fix.accuracy) * 1.5 {
                derivedCourse = (Geometry.bearing(from: anchor.coordinate, to: fix.coordinate), fix.timestamp)
                courseAnchor = fix
            }
        } else { courseAnchor = fix; derivedCourse = nil }
        guard let derivedCourse, fix.timestamp.timeIntervalSince(derivedCourse.at) <= 5 else { return nil }
        return derivedCourse.bearing
    }
}
