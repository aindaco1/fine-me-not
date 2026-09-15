import Foundation
import Observation
import CoreLocation
import CameraCore

@MainActor @Observable
final class MonitoringController: NSObject, CLLocationManagerDelegate {
    private(set) var enabled: Bool
    private(set) var quietBelowSpeedLimit: Bool
    private(set) var authorization = CLAuthorizationStatus.notDetermined
    private(set) var precise = true
    private(set) var lastFixAt: Date?
    private(set) var lastReceivedAt: Date?
    private(set) var lastAccuracy: Double?
    private(set) var lastReportedSpeed: Double?
    private(set) var lastSpeedAccuracy: Double?
    private(set) var fixStatus = "No location received"
    private(set) var stationary = false
    private(set) var failure: String?
    private(set) var warningCount = 0
    private(set) var isTracking = false
    private let manager = CLLocationManager()
    private let defaults: UserDefaults
    private let store: CameraStore
    private let presenter: AlertPresenter
    private var serviceSession: CLServiceSession?
    private var retry: Task<Void, Never>?
    private var engine: AlertEngine
    var matchDiagnostic: MatchDiagnostic { engine.diagnostic }

    init(store: CameraStore, presenter: AlertPresenter, defaults: UserDefaults = .standard) {
        self.store = store; self.presenter = presenter; self.defaults = defaults
        enabled = defaults.bool(forKey: "warnings.enabled")
        quietBelowSpeedLimit = SpeedCheck.isEnabled(in: defaults)
        let saved = defaults.data(forKey: "warnings.encounters")
            .flatMap { try? JSONDecoder().decode([String: Encounter].self, from: $0) } ?? [:]
        engine = AlertEngine(encounters: saved)
        super.init()
        manager.delegate = self
        manager.activityType = .automotiveNavigation
        manager.desiredAccuracy = kCLLocationAccuracyBestForNavigation
        manager.distanceFilter = 10
        manager.allowsBackgroundLocationUpdates = true
        manager.pausesLocationUpdatesAutomatically = false
        manager.showsBackgroundLocationIndicator = true
        refreshAuthorization()
    }

    func setEnabled(_ value: Bool) {
        enabled = value; defaults.set(value, forKey: "warnings.enabled")
        if value {
            start()
            Task { await presenter.requestNotifications() }
        } else { stop() }
    }

    func setQuietBelowSpeedLimit(_ value: Bool) {
        quietBelowSpeedLimit = value
        defaults.set(value, forKey: SpeedCheck.preferenceKey)
    }

    func start() {
        guard enabled, !isTracking else { return }
        retry?.cancel(); retry = nil; failure = nil
        refreshAuthorization()
        guard authorization != .denied && authorization != .restricted else { return }
        // One continuous location stream owns matching. Explicitly disable
        // automatic pauses; reliability takes priority over idle battery use.
        // Recreate the service session on a permitted background relaunch too.
        serviceSession = CLServiceSession(authorization: .always)
        isTracking = true
        manager.startUpdatingLocation()
        if CLLocationManager.significantLocationChangeMonitoringAvailable() {
            manager.startMonitoringSignificantLocationChanges()
        }
    }

    private func scheduleRetry() {
        guard retry == nil else { return }
        retry = Task { [weak self] in
            try? await Task.sleep(for: .seconds(10))
            guard !Task.isCancelled, let self else { return }
            self.retry = nil
            self.manager.stopUpdatingLocation()
            self.isTracking = false
            self.serviceSession?.invalidate(); self.serviceSession = nil
            self.start()
        }
    }

    private func stop() {
        retry?.cancel(); retry = nil
        manager.stopUpdatingLocation()
        manager.stopMonitoringSignificantLocationChanges()
        isTracking = false
        serviceSession?.invalidate(); serviceSession = nil
        failure = nil; lastFixAt = nil; stationary = false
    }

    func refreshAuthorization() {
        authorization = manager.authorizationStatus
        precise = manager.accuracyAuthorization == .fullAccuracy
    }

    func status(at now: Date) -> String {
        guard enabled else { return "Off" }
        if authorization == .denied || authorization == .restricted { return "Location access needed" }
        if !precise { return "Precise Location needed" }
        if authorization != .authorizedAlways { return "Allow Always location access" }
        if store.snapshot == nil { return "Camera database needed" }
        if let failure { return failure }
        guard let lastFixAt, now.timeIntervalSince(lastFixAt) <= 30 else { return "Waiting for location" }
        if stationary { return "Ready · waiting for movement" }
        return "Monitoring"
    }

    private func consume(_ location: CLLocation) {
        let now = Date.now
        lastReceivedAt = location.timestamp
        lastAccuracy = location.horizontalAccuracy
        lastReportedSpeed = location.speed
        lastSpeedAccuracy = location.speedAccuracy
        let fix = LocationFix(coordinate: Coordinate(location.coordinate.latitude, location.coordinate.longitude),
                              timestamp: location.timestamp, accuracy: location.horizontalAccuracy,
                              speed: location.speed,
                              course: location.courseAccuracy >= 0 && location.courseAccuracy <= 45 ? location.course : nil,
                              speedAccuracy: location.speedAccuracy)
        guard precise else { fixStatus = "Rejected: Precise Location is off"; return }
        guard fix.isUsable(at: now) else {
            fixStatus = "Rejected: location must be within 75 m accuracy and 15 seconds old"
            return
        }
        failure = nil; lastFixAt = location.timestamp; fixStatus = "Accepted"
        retry?.cancel(); retry = nil
        let previousEncounters = engine.encounters
        let warnings = engine.evaluate(fix, index: store.index, now: now, quietBelowSpeedLimit: quietBelowSpeedLimit)
        stationary = (engine.diagnostic.speed ?? 0) < 2.5
        if !warnings.isEmpty {
            presenter.present(warnings)
            warningCount += warnings.count
        }
        if previousEncounters != engine.encounters,
           let data = try? JSONEncoder().encode(engine.encounters) { defaults.set(data, forKey: "warnings.encounters") }
        if store.isDue { Task { await store.refresh() } }
    }

    nonisolated func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        Task { @MainActor [weak self] in
            guard let self else { return }
            self.refreshAuthorization()
            if self.authorization == .denied || self.authorization == .restricted { self.stop() }
            else { self.start() }
        }
    }

    nonisolated func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        // Standard and significant-change recovery fixes share one matcher.
        Task { @MainActor [weak self] in
            guard let self, self.enabled else { return }
            self.start()
            if let location = locations.last { self.consume(location) }
        }
    }

    nonisolated func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        let code = (error as? CLError)?.code
        Task { @MainActor [weak self] in
            guard let self, self.enabled else { return }
            if code == .locationUnknown {
                self.failure = "Location temporarily unavailable"
            } else if code == .denied {
                self.refreshAuthorization(); self.stop()
            } else {
                self.failure = "Location failed. Retrying automatically."
                self.scheduleRetry()
            }
        }
    }

    nonisolated func locationManagerDidPauseLocationUpdates(_ manager: CLLocationManager) {
        Task { @MainActor [weak self] in
            guard let self, self.enabled else { return }
            self.manager.startUpdatingLocation()
        }
    }
}
