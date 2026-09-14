import SwiftUI
import BackgroundTasks
import UserNotifications
import CameraCore

@MainActor
final class AppServices {
    static let shared = AppServices()
    static let refreshID = "xyz.dustwave.fine-me-not.database-refresh"
    let store: CameraStore
    let presenter: AlertPresenter
    let monitoring: MonitoringController
    private init() {
        store = CameraStore()
        presenter = AlertPresenter()
        monitoring = MonitoringController(store: store, presenter: presenter)
    }

    func scheduleRefresh() {
        let request = BGAppRefreshTaskRequest(identifier: Self.refreshID)
        request.earliestBeginDate = store.isDue ? Date.now.addingTimeInterval(900) : UpdateSchedule.nextRefresh(after: .now)
        try? BGTaskScheduler.shared.submit(request)
    }

    func handleRefresh(_ task: BGTask) {
        let operation = Task { @MainActor in
            let success = await store.refresh(force: true)
            task.setTaskCompleted(success: success)
            scheduleRefresh()
        }
        task.expirationHandler = { operation.cancel() }
    }
}

@MainActor
final class AppDelegate: NSObject, UIApplicationDelegate, UNUserNotificationCenterDelegate {
    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]? = nil) -> Bool {
        let services = AppServices.shared
        UNUserNotificationCenter.current().delegate = self
        BGTaskScheduler.shared.register(forTaskWithIdentifier: AppServices.refreshID, using: .main) { task in
            MainActor.assumeIsolated { AppServices.shared.handleRefresh(task) }
        }
        services.monitoring.start()
        services.scheduleRefresh()
        return true
    }

    nonisolated func userNotificationCenter(_ center: UNUserNotificationCenter,
                                            willPresent notification: UNNotification) async -> UNNotificationPresentationOptions {
        [.banner, .sound]
    }
}

@main
struct FineMeNotApp: App {
    @UIApplicationDelegateAdaptor(AppDelegate.self) private var delegate
    @Environment(\.scenePhase) private var scenePhase
    private let services = AppServices.shared
    var body: some Scene {
        WindowGroup {
            SettingsView(services: services)
                .preferredColorScheme(.dark)
                .task { await services.store.refresh() }
                .onChange(of: scenePhase) { _, phase in
                    if phase == .active {
                        services.monitoring.refreshAuthorization()
                        services.monitoring.start()
                        services.presenter.refreshRoute()
                        Task { await services.store.refresh() }
                    } else if phase == .background { services.scheduleRefresh() }
                }
        }
    }
}
