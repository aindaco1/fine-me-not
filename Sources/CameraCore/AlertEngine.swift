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

public struct Encounter: Codable, Sendable {
    public var lastAlert: Date
    public var armed: Bool
}

public struct AlertEngine: Sendable {
    public private(set) var encounters: [String: Encounter]
    private var previous: LocationFix?
    private var lastMovingAt: Date?
    public init(encounters: [String: Encounter] = [:]) { self.encounters = encounters }

    public mutating func evaluate(_ fix: LocationFix, index: CameraIndex, now: Date) -> [CameraWarning] {
        guard fix.isUsable(at: now) else { return [] }
        if let previous, fix.timestamp <= previous.timestamp { return [] }
        defer { previous = fix }
        if fix.speed.isFinite && fix.speed >= 2.5 { lastMovingAt = now }
        let moving = lastMovingAt.map { now.timeIntervalSince($0) < 120 } ?? false
        // Rearm even when a site is no longer in the spatial query.
        let byID = Dictionary(uniqueKeysWithValues: index.cameras.map { ($0.id, $0) })
        for (id, encounter) in encounters where !encounter.armed {
            guard let camera = byID[id] else { continue }
            let d = Geometry.distance(fix.coordinate, Geometry.nearest(to: fix.coordinate, on: camera.geometry))
            if d > 850 && now.timeIntervalSince(encounter.lastAlert) >= 60 { encounters[id]?.armed = true }
        }
        guard moving else { return [] }
        let lead = min(600, max(150, max(0, fix.speed) * 15))
        let course = fix.course.flatMap { $0.isFinite && (0..<360).contains($0) ? $0 : nil }
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
}
