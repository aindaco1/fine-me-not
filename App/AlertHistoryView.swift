import SwiftUI
import UserNotifications

struct AlertHistoryView: View {
    @Bindable var history: AlertHistory
    @Environment(\.dismiss) private var dismiss
    @State private var confirmingClear = false

    var body: some View {
        NavigationStack(path: $history.path) {
            page(title: "Alert log") {
                if history.entries.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        Image(systemName: "bell").font(.title).foregroundStyle(AppStyle.accent)
                        Text("No alerts yet").font(.system(.headline, design: .monospaced))
                        Text("Camera notifications will appear here. Quiet approaches aren’t logged.")
                            .font(.body).foregroundStyle(AppStyle.accent)
                    }.padding(.vertical, 20)
                } else {
                    LazyVStack(alignment: .leading, spacing: 0) {
                        ForEach(history.entries) { entry in
                            separator
                            NavigationLink(value: entry.id) {
                                HStack(alignment: .top, spacing: 16) {
                                    VStack(alignment: .leading, spacing: 8) {
                                        Text(entry.title).font(.system(.headline, design: .monospaced))
                                        ForEach(Array(entry.cameras.enumerated()), id: \.offset) { _, camera in
                                            Text(camera.label).font(.body)
                                        }
                                        Text(entry.date.formatted(date: .abbreviated, time: .shortened))
                                            .font(.footnote).foregroundStyle(AppStyle.accent)
                                    }
                                    Spacer(minLength: 0)
                                    Image(systemName: "chevron.right").foregroundStyle(AppStyle.accent)
                                }.padding(.vertical, 20).contentShape(Rectangle())
                            }.buttonStyle(.plain)
                        }
                        separator
                    }
                }
                Text("The latest 500 camera notifications stay on this iPhone. No uploads or backups.")
                    .font(.footnote).foregroundStyle(AppStyle.accent)
                if let error = history.storageError { Text(error).font(.footnote) }
            }
            .navigationDestination(for: UUID.self) { id in
                page(title: "Camera alert") {
                    if let entry = history.entries.first(where: { $0.id == id }) {
                        Text(entry.date.formatted(date: .complete, time: .standard))
                            .font(.system(.body, design: .monospaced)).foregroundStyle(AppStyle.accent)
                        ForEach(Array(entry.cameras.enumerated()), id: \.offset) { _, camera in
                            VStack(alignment: .leading, spacing: 16) {
                                separator
                                Text(camera.kind.title.uppercased())
                                    .font(.system(.caption, design: .monospaced).weight(.semibold))
                                    .tracking(1).foregroundStyle(AppStyle.accent)
                                Text(camera.label).font(.system(.title2, design: .monospaced).weight(.semibold))
                                if camera.kind == .speed || camera.kind == .possibleSpeed {
                                    if let limit = camera.speedLimit, limit.metersPerSecond(at: entry.date) != nil {
                                        Text("Speed-check limit: \(limit.value.formatted()) \(limit.unit)")
                                            .font(.system(.headline, design: .monospaced))
                                        Text("Warnings can still sound near the limit or when GPS speed is uncertain.")
                                            .font(.footnote).foregroundStyle(AppStyle.accent)
                                    } else {
                                        Text("No usable speed-check limit saved with this alert.")
                                            .font(.footnote).foregroundStyle(AppStyle.accent)
                                    }
                                }
                            }
                        }
                    } else {
                        Text("Alert no longer saved").font(.system(.headline, design: .monospaced))
                    }
                }.accessibilityIdentifier("alert-log-detail")
            }
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    if !history.entries.isEmpty {
                        Button("Clear", role: .destructive) { confirmingClear = true }
                            .font(.system(.body, design: .monospaced))
                    }
                }
            }
            .confirmationDialog("Clear the alert log?", isPresented: $confirmingClear, titleVisibility: .visible) {
                Button("Clear alert log", role: .destructive) {
                    history.clear()
                    UNUserNotificationCenter.current().removeAllDeliveredNotifications()
                }
            }
        }.tint(AppStyle.accent)
    }

    private var separator: some View {
        Rectangle().fill(AppStyle.accent.opacity(0.4)).frame(height: 1)
    }

    private func page<Content: View>(title: String, @ViewBuilder content: () -> Content) -> some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24, content: content)
                .frame(maxWidth: 560, alignment: .leading)
                .padding(24).frame(maxWidth: .infinity, alignment: .center)
        }
        .foregroundStyle(.white)
        .background(AppStyle.blue.ignoresSafeArea())
        .navigationTitle(title)
        .navigationBarTitleDisplayMode(.inline)
        .toolbarBackground(AppStyle.blue, for: .navigationBar)
        .toolbarBackground(.visible, for: .navigationBar)
        .toolbar {
            ToolbarItem(placement: .principal) {
                Text(title).font(.system(.headline, design: .monospaced)).foregroundStyle(.white)
            }
            ToolbarItem(placement: .confirmationAction) {
                Button("Done") { dismiss() }.font(.system(.body, design: .monospaced))
            }
        }
    }
}
