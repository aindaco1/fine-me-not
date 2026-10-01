import SwiftUI
import UserNotifications

struct AlertHistoryView: View {
    @Bindable var history: AlertHistory
    @Environment(\.dismiss) private var dismiss
    @State private var confirmingClear = false

    var body: some View {
        NavigationStack(path: $history.path) {
            List {
                if history.entries.isEmpty {
                    ContentUnavailableView("No alerts yet", systemImage: "bell",
                        description: Text("Camera notifications will appear here. Quiet approaches aren’t logged."))
                } else {
                    ForEach(history.entries) { entry in
                        NavigationLink(value: entry.id) {
                            VStack(alignment: .leading, spacing: 6) {
                                Text(entry.title).font(.headline)
                                ForEach(Array(entry.cameras.enumerated()), id: \.offset) { _, camera in
                                    Text(camera.label).font(.subheadline)
                                }
                                Text(entry.date.formatted(date: .abbreviated, time: .shortened))
                                    .font(.caption).foregroundStyle(.secondary)
                            }.padding(.vertical, 4)
                        }
                    }
                }
                Section {
                    Text("The latest 500 camera notifications stay on this iPhone. No uploads or backups.")
                        .font(.footnote).foregroundStyle(.secondary)
                    if let error = history.storageError { Text(error).foregroundStyle(.red) }
                }
            }
            .navigationTitle("Alert log")
            .navigationDestination(for: UUID.self) { id in
                if let entry = history.entries.first(where: { $0.id == id }) {
                    List {
                        Section {
                            Text(entry.date.formatted(date: .complete, time: .standard))
                        }
                        ForEach(Array(entry.cameras.enumerated()), id: \.offset) { _, camera in
                            Section(camera.kind.title) { Text(camera.label) }
                        }
                    }
                    .navigationTitle("Camera alert")
                    .navigationBarTitleDisplayMode(.inline)
                    .accessibilityIdentifier("alert-log-detail")
                } else {
                    ContentUnavailableView("Alert no longer saved", systemImage: "bell.slash")
                }
            }
            .toolbar {
                ToolbarItem(placement: .confirmationAction) { Button("Done") { dismiss() } }
                ToolbarItem(placement: .topBarLeading) {
                    if !history.entries.isEmpty {
                        Button("Clear", role: .destructive) { confirmingClear = true }
                    }
                }
            }
            .confirmationDialog("Clear the alert log?", isPresented: $confirmingClear, titleVisibility: .visible) {
                Button("Clear alert log", role: .destructive) {
                    history.clear()
                    UNUserNotificationCenter.current().removeAllDeliveredNotifications()
                }
            }
        }
    }
}
