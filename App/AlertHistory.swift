import Foundation
import Observation
import CameraCore

/// A snapshot of a posted notification, independent of later database updates.
struct AlertLogEntry: Codable, Identifiable, Hashable, Sendable {
    struct CameraItem: Codable, Hashable, Sendable {
        let id: String
        let label: String
        let kind: CameraKind
        let speedLimit: SpeedLimit?
    }
    let id: UUID
    let date: Date
    let cameras: [CameraItem]
    var title: String { cameras.count == 1 ? cameras[0].kind.title : "Cameras nearby" }
    static let payloadKey = "alertLogEntry"

    init(warnings: [CameraWarning], date: Date = .now) {
        id = UUID()
        self.date = date
        cameras = warnings.map { CameraItem(id: $0.camera.id, label: $0.camera.label,
            kind: $0.camera.kind, speedLimit: $0.camera.speedLimit) }
    }

    var payload: String? {
        (try? JSONEncoder().encode(self)).flatMap { String(data: $0, encoding: .utf8) }
    }

    static func decode(_ payload: String?) -> Self? {
        guard let payload, let data = payload.data(using: .utf8),
              let entry = try? JSONDecoder().decode(Self.self, from: data),
              !entry.cameras.isEmpty else { return nil }
        return entry
    }
}

@MainActor @Observable
final class AlertHistory {
    static let capacity = 500
    private(set) var entries: [AlertLogEntry] = []
    private(set) var storageError: String?
    var isPresented = false
    var path: [UUID] = []
    private let directory: URL
    private var file: URL { directory.appending(path: "alerts.json") }

    init(supportDirectory: URL = .applicationSupportDirectory) {
        directory = supportDirectory.appending(path: "AlertHistory", directoryHint: .isDirectory)
        do {
            try prepareDirectory()
            if FileManager.default.fileExists(atPath: file.path) {
                entries = Array(try JSONDecoder().decode([AlertLogEntry].self, from: Data(contentsOf: file))
                    .sorted { $0.date > $1.date }.prefix(Self.capacity))
            }
        } catch { storageError = "Couldn’t load the alert log." }
    }

    func record(_ entry: AlertLogEntry) {
        guard !entries.contains(where: { $0.id == entry.id }) else { return }
        entries.append(entry)
        entries.sort { $0.date > $1.date }
        entries = Array(entries.prefix(Self.capacity))
        save()
    }

    func open(_ entry: AlertLogEntry) {
        record(entry)
        // Keep a tapped older notification accessible even after the log's cap.
        if !entries.contains(where: { $0.id == entry.id }) {
            entries = Array(entries.prefix(Self.capacity - 1)) + [entry]
            save()
        }
        path = [entry.id]
        isPresented = true
    }

    func show() { path = []; isPresented = true }

    func clear() {
        entries = []
        path = []
        save()
    }

    private func prepareDirectory() throws {
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true,
            attributes: [.protectionKey: FileProtectionType.completeUntilFirstUserAuthentication])
        var url = directory
        var values = URLResourceValues()
        values.isExcludedFromBackup = true
        try url.setResourceValues(values)
    }

    private func save() {
        do {
            try prepareDirectory()
            try JSONEncoder().encode(entries).write(to: file,
                options: [.atomic, .completeFileProtectionUntilFirstUserAuthentication])
            storageError = nil
        } catch { storageError = "Couldn’t save the alert log on this iPhone." }
    }
}
