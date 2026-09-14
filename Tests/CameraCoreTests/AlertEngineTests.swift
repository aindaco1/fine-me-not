import Foundation
import Testing
@testable import CameraCore

private let start = Date(timeIntervalSince1970: 1_789_430_400)
private func camera(_ id: String = "abq-1", bearing: Double? = 0, kind: CameraKind = .speed,
                    geometry: [Coordinate] = [Coordinate(35.003, -106)]) -> Camera {
    Camera(id: id, label: "Test road", kind: kind, geometry: geometry, travelBearing: bearing,
           sourceIDs: ["test"], evidence: "Fixture")
}
private func fix(_ latitude: Double, lon: Double = -106, seconds: Double = 0, course: Double? = 0,
                 speed: Double = 20, accuracy: Double = 5) -> LocationFix {
    LocationFix(coordinate: Coordinate(latitude, lon), timestamp: start.addingTimeInterval(seconds),
                accuracy: accuracy, speed: speed, course: course)
}

@Test func warnsOnceAndRearmsAfterLeaving() {
    let index = CameraIndex(cameras: [camera()]); var engine = AlertEngine()
    #expect(engine.evaluate(fix(35.0005), index: index, now: start).count == 1)
    #expect(engine.evaluate(fix(35.001, seconds: 5), index: index, now: start.addingTimeInterval(5)).isEmpty)
    #expect(engine.evaluate(fix(35.003, seconds: 70, speed: 0), index: index, now: start.addingTimeInterval(70)).isEmpty)
    #expect(engine.evaluate(fix(35.02, seconds: 130), index: index, now: start.addingTimeInterval(130)).isEmpty)
    #expect(engine.evaluate(fix(35.0005, seconds: 200), index: index, now: start.addingTimeInterval(200)).count == 1)
}

@Test func rejectsOppositeDirectionAndCameraBehind() {
    var engine = AlertEngine()
    let index = CameraIndex(cameras: [camera(), camera("opposite", bearing: 180)])
    #expect(engine.evaluate(fix(35.0005), index: index, now: start).map(\.camera.id) == ["abq-1"])
    var behind = AlertEngine()
    #expect(behind.evaluate(fix(35.005), index: CameraIndex(cameras: [camera(bearing: nil)]), now: start).isEmpty)
}

@Test func rejectsBadAndOldFixes() {
    var engine = AlertEngine(); let index = CameraIndex(cameras: [camera()])
    #expect(engine.evaluate(fix(35.001, accuracy: 100), index: index, now: start).isEmpty)
    #expect(engine.evaluate(fix(35.001), index: index, now: start.addingTimeInterval(30)).isEmpty)
    #expect(engine.evaluate(fix(35.001, speed: 0), index: index, now: start).isEmpty)
}

@Test func restartAndDatabaseCorrectionPreserveCooldown() throws {
    var engine = AlertEngine(); let index = CameraIndex(cameras: [camera()])
    #expect(engine.evaluate(fix(35.001), index: index, now: start).count == 1)
    let restored = try JSONDecoder().decode([String: Encounter].self, from: JSONEncoder().encode(engine.encounters))
    var relaunched = AlertEngine(encounters: restored)
    let corrected = CameraIndex(cameras: [camera(geometry: [Coordinate(35.0031, -106)])])
    #expect(relaunched.evaluate(fix(35.001, seconds: 5), index: corrected, now: start.addingTimeInterval(5)).isEmpty)
}

@Test func longMobileCorridorIsIndexedAtItsMiddle() {
    let mobile = camera(bearing: nil, kind: .possibleSpeed, geometry: [Coordinate(35, -106), Coordinate(35.1, -106)])
    let index = CameraIndex(cameras: [mobile]); var engine = AlertEngine()
    #expect(index.nearby(Coordinate(35.05, -106)).count == 1)
    #expect(engine.evaluate(fix(35.05), index: index, now: start).first?.camera.kind == .possibleSpeed)
    #expect(engine.evaluate(fix(35.055, seconds: 90), index: index, now: start.addingTimeInterval(90)).isEmpty)
}

@Test func expiredMobileSiteDoesNotWarn() {
    let c = Camera(id: "expired", label: "Site", kind: .possibleSpeed, geometry: [Coordinate(35.003, -106)], validUntil: start)
    var engine = AlertEngine()
    #expect(engine.evaluate(fix(35.001), index: CameraIndex(cameras: [c]), now: start).isEmpty)
}

@Test func unknownCourseNeedsApproachEvidence() {
    var engine = AlertEngine(); let index = CameraIndex(cameras: [camera(bearing: nil)])
    #expect(engine.evaluate(fix(35.0005, course: nil), index: index, now: start).isEmpty)
    #expect(engine.evaluate(fix(35.001, seconds: 5, course: nil), index: index, now: start.addingTimeInterval(5)).count == 1)
}

@Test func denverMidnightFollowsDaylightSaving() {
    let parse = ISO8601DateFormatter()
    for (date, expected) in [("2026-03-08T18:00:00Z", "2026-03-09T06:00:00Z"),
                             ("2026-11-01T18:00:00Z", "2026-11-02T07:00:00Z")] {
        #expect(UpdateSchedule.nextRefresh(after: parse.date(from: date)!) == parse.date(from: expected)!)
    }
    let monday = parse.date(from: "2026-09-14T06:00:00Z")!
    #expect(UpdateSchedule.currentWeekStart(at: monday) == monday)
    #expect(!UpdateSchedule.isDue(generatedAt: monday, now: monday))
    #expect(UpdateSchedule.isDue(generatedAt: monday.addingTimeInterval(-1), now: monday))
}
