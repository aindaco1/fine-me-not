import Foundation
import MetricKit
import SupportCore
import UIKit

@MainActor
final class SupportDiagnostics: NSObject, MXMetricManagerSubscriber {
    static let shared = SupportDiagnostics()
    let journal = DiagnosticJournal(directory: URL.applicationSupportDirectory.appending(path: "FineMeNot/Support"))
    private var lastEvent: [String: SupportEvent] = [:]
    private var subscribed = false
    func start() {
        guard !subscribed else { return }; subscribed = true
        MXMetricManager.shared.add(self)
        didReceive(MXMetricManager.shared.pastDiagnosticPayloads)
    }
    func record(_ code: String, _ values: [String: String]) {
        let event = SupportEvent(code, values)
        guard lastEvent[code] != event else { return }
        lastEvent[code] = event
        Task { await journal.append(event) }
    }
    nonisolated func didReceive(_ payloads: [MXDiagnosticPayload]) {
        var filtered: [CrashEvidence] = []
        for payload in payloads.suffix(5) {
            let end = ISO8601DateFormatter().string(from: payload.timeStampEnd)
            for crash in (payload.crashDiagnostics ?? []).prefix(5) {
                filtered.append(.init(kind: "crash", version: crash.applicationVersion, build: crash.metaData.applicationBuildVersion, periodEnd: end,
                    signal: crash.signal?.intValue ?? 0, exception: crash.exceptionType?.intValue ?? 0,
                    frames: CrashFilter.frames(from: crash.callStackTree.jsonRepresentation())))
            }
            for hang in (payload.hangDiagnostics ?? []).prefix(5) {
                filtered.append(.init(kind: "hang", version: hang.applicationVersion, build: hang.metaData.applicationBuildVersion, periodEnd: end,
                    signal: 0, exception: 0, frames: CrashFilter.frames(from: hang.callStackTree.jsonRepresentation())))
            }
        }
        let evidence = filtered
        Task { @MainActor in for item in evidence { await journal.addCrash(item) } }
    }
    static var appState: String {
        switch UIApplication.shared.applicationState {
        case .active: "foreground"
        case .background: "background"
        default: "inactive"
        }
    }
    static var model: String? {
        var info = utsname(); uname(&info)
        let name = withUnsafeBytes(of: &info.machine) { bytes in String(decoding: bytes.prefix { $0 != 0 }, as: UTF8.self) }
        return ReportContract.matches(name, "^iPhone[0-9]{1,3},[0-9]{1,3}$") ? name : nil
    }
}
