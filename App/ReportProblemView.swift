import SwiftUI
import SupportCore

struct ReportProblemView: View {
    let services: AppServices
    @Environment(\.dismiss) private var dismiss
    @State private var category: ReportCategory = .other
    @State private var notes = ""
    @State private var includeDetails = true
    @State private var evidenceIndex = -1
    @State private var crashIndex: Int = -1
    @State private var crashes: [CrashEvidence] = []
    @State private var events: [SupportEvent] = []
    @State private var drafts: [SupportReport] = []
    @State private var frozen: SupportReport?
    @State private var sending = false
    @State private var receipt: ReportReceipt?
    @State private var error: String?
    private let journal = SupportDiagnostics.shared.journal

    var body: some View {
        NavigationStack {
            Form {
                if let receipt {
                    Section("Report sent. Thank you.") {
                        Text("Your report is on GitHub. Similar reports may share the same issue.")
                        Link("View report #\(receipt.issueNumber)", destination: receipt.url)
                    }
                } else if let report = frozen {
                    Section("Review before sending") {
                        Text("This report and anything you write will be posted publicly on GitHub. The automatic details leave out your location, camera names and trip history. Please leave out personal information. Send it when you’re parked.")
                        Text(report.category.title).font(.headline)
                        if !report.notes.isEmpty { Text(report.notes).textSelection(.enabled) }
                        DisclosureGroup("Full report") {
                            Text(report.preview).font(.system(.caption, design: .monospaced)).textSelection(.enabled)
                                .accessibilityIdentifier("report-preview")
                        }
                    }
                    Section {
                        Button(sending ? "Sending…" : "Send report") { send(report) }.disabled(sending)
                            .accessibilityIdentifier("send-report")
                        Button("Copy report") { UIPasteboard.general.string = report.preview }
                        Button("Edit as a new report") {
                            category = report.category; notes = report.notes; evidenceIndex = -1; crashIndex = -1; frozen = nil; error = nil
                        }.disabled(sending)
                        Button("Discard draft", role: .destructive) {
                            Task { await journal.discard(report.id); frozen = nil; await load() }
                        }.disabled(sending)
                    } footer: { Text("A failed send keeps this draft for seven days. Retry sends the same report, so it won’t be counted twice.") }
                } else {
                    Section {
                        Text("Found something weird? Tell me about it.")
                        Picker("What happened?", selection: $category) {
                            ForEach(ReportCategory.allCases) { Text($0.title).tag($0) }
                        }
                        TextField("Anything else? (optional)", text: $notes, axis: .vertical).lineLimit(4...10)
                            .accessibilityIdentifier("report-notes")
                        Text("\(notes.unicodeScalars.count) / 2,000 characters").font(.caption)
                        Toggle("Include technical details", isOn: $includeDetails)
                        Text("Permissions, recent warning decisions, audio status and camera-update results. No location, camera names or driving speeds.").font(.footnote)
                    }
                    if includeDetails && !events.isEmpty {
                        Section("Related technical event (optional)") {
                            Picker("Which event matches the problem?", selection: $evidenceIndex) {
                                Text("Not sure").tag(-1)
                                ForEach(Array(events.enumerated()), id: \.offset) { index, event in
                                    Text("\(event.code.capitalized): \(event.values["audio"] ?? event.values["databaseResult"] ?? event.values["match"] ?? event.code) · \(event.values["eventAge"] ?? "today")").tag(index)
                                }
                            }
                            Text("Leave this on Not sure if you don’t know. It helps group reports of the same failure.").font(.footnote)
                        }
                    }
                    if includeDetails && !crashes.isEmpty {
                        Section("Apple crash or hang details") {
                            Picker("Attach a saved diagnostic", selection: $crashIndex) {
                                Text("None").tag(-1)
                                ForEach(Array(crashes.enumerated()), id: \.offset) { index, crash in
                                    Text("\(crash.kind.capitalized) · version \(crash.version) (\(crash.build)) · \(String(crash.periodEnd.prefix(10)))").tag(index)
                                }
                            }
                            Text("These may be from an older app version. Apple doesn’t provide a diagnostic for every problem.").font(.footnote)
                        }
                    }
                    Section {
                        Button("Review report") { prepare() }.accessibilityIdentifier("review-report")
                    } footer: { Text("Nothing is uploaded until you review the report and tap Send report. No GitHub account needed.") }
                    if !drafts.isEmpty {
                        Section("Saved drafts") {
                            ForEach(drafts) { report in
                                Button("\(report.category.title) · \(String(report.createdAt.prefix(10)))") { frozen = report; error = nil }
                            }
                        }
                    }
                    Section {
                        Button("Delete local report history", role: .destructive) {
                            Task { await journal.clear(); await load() }
                        }
                    } footer: { Text("Deletes saved technical events, crash details and drafts from this phone. It does not delete reports already sent to GitHub.") }
                }
                if let error { Section { Text(error).foregroundStyle(.red).accessibilityIdentifier("report-error") } }
            }
            .navigationTitle("Report a problem")
            .toolbar { ToolbarItem(placement: .cancellationAction) { Button(receipt == nil ? "Close" : "Done") { dismiss() }.disabled(sending) } }
            .interactiveDismissDisabled(sending)
            .task { await load() }
        }
    }
    private func load() async {
        let content = await journal.contents(); events = content.events; crashes = content.crashes; drafts = content.drafts
    }
    private func prepare() {
        let crash = includeDetails && crashes.indices.contains(crashIndex) ? crashes[crashIndex] : nil
        let report = SupportReport(category: category, notes: notes,
            metadata: includeDetails ? services.supportMetadata : [:],
            state: includeDetails ? services.supportState : [:], events: includeDetails ? events : [], evidenceIndex: includeDetails && events.indices.contains(evidenceIndex) ? evidenceIndex : nil, crash: crash)
        do {
            _ = try report.encoded(); error = nil; frozen = report
            Task { try? await journal.saveDraft(report) }
        } catch { self.error = error.localizedDescription }
    }
    private func send(_ report: SupportReport) {
        guard !sending else { return }; sending = true; error = nil
        Task {
            defer { sending = false }
            do { try await journal.saveDraft(report); receipt = try await ReportClient.send(report); await journal.discard(report.id) }
            catch { self.error = error.localizedDescription }
        }
    }
}
