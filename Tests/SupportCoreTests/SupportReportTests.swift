import Foundation
import Testing
@testable import SupportCore

@Test func safeContractRejectsLocationSpeedUnknownKeysAndOversizedText() throws {
    let report = SupportReport(category: .other, notes: "A clear explanation.\nSecond line.")
    let data = try report.encoded()
    #expect(try JSONDecoder().decode(SupportReport.self, from: data) == report)
    for key in ["latitude", "cameraID", "portName", "speed", "url", "trip"] {
        let bad = SupportReport(category: .other, notes: "", state: [key: "secret"])
        #expect(throws: (any Error).self) { try bad.encoded() }
    }
    #expect(throws: (any Error).self) { try SupportReport(category: .other, notes: "").encoded() }
    #expect(throws: (any Error).self) { try SupportReport(category: .other, notes: String(repeating: "a", count: 2001)).encoded() }
    _ = try SupportReport(category: .other, notes: String(repeating: "🦉", count: 2000)).encoded()
    var object = try #require(JSONSerialization.jsonObject(with: data) as? [String: Any]); object["unexpected"] = "secret"
    #expect(throws: (any Error).self) { try ReportContract.validate(JSONSerialization.data(withJSONObject: object)) }
}

@Test func reviewedDraftIsImmutableAndExpiresWithoutSending() async throws {
    let folder = FileManager.default.temporaryDirectory.appending(path: UUID().uuidString)
    defer { try? FileManager.default.removeItem(at: folder) }
    let journal = DiagnosticJournal(directory: folder)
    let report = SupportReport(category: .other, notes: "Saved only")
    try await journal.saveDraft(report)
    let loaded = await DiagnosticJournal(directory: folder).contents()
    #expect(loaded.drafts == [report])
    let edited = SupportReport(category: .other, notes: "Edited", id: report.id)
    await #expect(throws: (any Error).self) { try await journal.saveDraft(edited) }
    #expect(await journal.contents(now: .now.addingTimeInterval(8 * 86400)).drafts.isEmpty)
}

@Test func journalFiltersCoalescesBoundsAndExpiresEvents() async {
    let folder = FileManager.default.temporaryDirectory.appending(path: UUID().uuidString)
    defer { try? FileManager.default.removeItem(at: folder) }
    let journal = DiagnosticJournal(directory: folder)
    let now = Date.now
    await journal.append(SupportEvent("audio", ["route": "My Private Car"]), now: now)
    for _ in 0..<30 { await journal.append(SupportEvent("audio", ["audio": "started"]), now: now) }
    let events = await journal.contents(now: now).events
    #expect(events.count == 1)
    #expect(events.first?.values["count"] == "many")
    #expect(await journal.contents(now: now.addingTimeInterval(86401)).events.isEmpty)
}

@Test func crashProjectionKeepsOnlyAppUUIDAndRelativeOffset() throws {
    let tree: [String: Any] = ["callStacks": [["threadAttributed": true, "callStackRootFrames": [
        ["binaryName": "PrivateFramework", "address": 123, "binaryUUID": UUID().uuidString, "offsetIntoBinaryTextSegment": 17],
        ["binaryName": "FineMeNot", "binaryUUID": "9AE8E190-43EA-4F01-A99F-0E542A777193", "offsetIntoBinaryTextSegment": 512, "address": 987654, "path": "/private/user" ]
    ]]]]
    let frames = CrashFilter.frames(from: try JSONSerialization.data(withJSONObject: tree))
    #expect(frames == [.init(uuid: "9ae8e190-43ea-4f01-a99f-0e542a777193", offset: 512)])
    let crash = CrashEvidence(kind: "crash", version: "1.0.0", build: "8", periodEnd: "2026-09-15T08:00:00Z", signal: 6, exception: 1, frames: frames)
    let data = try SupportReport(category: .crash, notes: "", crash: crash).encoded()
    let text = String(decoding: data, as: UTF8.self)
    #expect(!text.contains("private") && !text.contains("987654") && text.contains("1.0.0"))
}

@Test func swiftAndRelayShareGoldenFixture() throws {
    let root = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent()
    let fixture = try Data(contentsOf: root.appending(path: "Sources/SupportCore/Resources/report-fixture.json"))
    try ReportContract.validate(fixture)
    let decoded = try JSONDecoder().decode(SupportReport.self, from: fixture)
    #expect(decoded.events.first?.values["route"] == "bluetooth")
    #expect(decoded.notes.contains("\n"))
}
