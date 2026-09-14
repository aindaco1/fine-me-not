import Foundation

public enum Geometry {
    public static func distance(_ a: Coordinate, _ b: Coordinate) -> Double {
        let lat1 = a.latitude * .pi / 180, lat2 = b.latitude * .pi / 180
        let dLat = lat2 - lat1, dLon = (b.longitude - a.longitude) * .pi / 180
        let h = pow(sin(dLat / 2), 2) + cos(lat1) * cos(lat2) * pow(sin(dLon / 2), 2)
        return 6_371_000 * 2 * asin(sqrt(min(1, max(0, h))))
    }

    public static func bearing(from a: Coordinate, to b: Coordinate) -> Double {
        let aLat = a.latitude * .pi / 180, bLat = b.latitude * .pi / 180
        let dLon = (b.longitude - a.longitude) * .pi / 180
        let y = sin(dLon) * cos(bLat)
        let x = cos(aLat) * sin(bLat) - sin(aLat) * cos(bLat) * cos(dLon)
        return (atan2(y, x) * 180 / .pi + 360).truncatingRemainder(dividingBy: 360)
    }

    public static func angleDifference(_ a: Double, _ b: Double) -> Double {
        let delta = abs(a - b).truncatingRemainder(dividingBy: 360)
        return min(delta, 360 - delta)
    }

    public static func nearest(to point: Coordinate, on geometry: [Coordinate]) -> Coordinate {
        guard geometry.count > 1 else { return geometry[0] }
        let scale = max(0.01, cos(point.latitude * .pi / 180))
        var nearest = geometry[0], best = Double.infinity
        for (a, b) in zip(geometry, geometry.dropFirst()) {
            let ax = (a.longitude - point.longitude) * scale, ay = a.latitude - point.latitude
            let bx = (b.longitude - point.longitude) * scale, by = b.latitude - point.latitude
            let dx = bx - ax, dy = by - ay
            let length2 = dx * dx + dy * dy
            let t = length2 == 0 ? 0 : min(1, max(0, -(ax * dx + ay * dy) / length2))
            let candidate = Coordinate(a.latitude + t * (b.latitude - a.latitude), a.longitude + t * (b.longitude - a.longitude))
            let d = distance(point, candidate)
            if d < best { nearest = candidate; best = d }
        }
        return nearest
    }
}

/// A small offline grid. It indexes full corridor bounds, not just endpoints.
public struct CameraIndex: Sendable {
    public let cameras: [Camera]
    private let indicesByID: [String: Int]
    private var buckets: [Cell: [Int]] = [:]
    private struct Cell: Hashable, Sendable { let lat: Int; let lon: Int }
    private static let cellSize = 0.05

    public init(cameras: [Camera]) {
        self.cameras = cameras
        self.indicesByID = Dictionary(cameras.enumerated().map { ($0.element.id, $0.offset) }, uniquingKeysWith: { first, _ in first })
        for (index, camera) in cameras.enumerated() where !camera.geometry.isEmpty {
            let lats = camera.geometry.map(\.latitude), lons = camera.geometry.map(\.longitude)
            for lat in Self.cell(lats.min()!)...Self.cell(lats.max()!) {
                for lon in Self.cell(lons.min()!)...Self.cell(lons.max()!) {
                    buckets[Cell(lat: lat, lon: lon), default: []].append(index)
                }
            }
        }
    }
    private static func cell(_ value: Double) -> Int { Int(floor(value / cellSize)) }

    public func camera(id: String) -> Camera? { indicesByID[id].map { cameras[$0] } }

    public func nearby(_ coordinate: Coordinate, radius: Double = 1000) -> [Camera] {
        let latDelta = radius / 110_000
        let lonDelta = latDelta / max(0.01, cos(coordinate.latitude * .pi / 180))
        var indices = Set<Int>()
        for lat in Self.cell(coordinate.latitude - latDelta)...Self.cell(coordinate.latitude + latDelta) {
            for lon in Self.cell(coordinate.longitude - lonDelta)...Self.cell(coordinate.longitude + lonDelta) {
                indices.formUnion(buckets[Cell(lat: lat, lon: lon)] ?? [])
            }
        }
        return indices.sorted().map { cameras[$0] }
    }
}
