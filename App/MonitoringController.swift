import Foundation
import Observation
import CoreLocation
import UIKit
import CameraCore

@MainActor @Observable
final class MonitoringController: NSObject, CLLocationManagerDelegate {
    private(set) var enabled: Bool
    private(set) var authorization = CLAuthorizationStatus.notDetermined
    private(set) var precise = true
    private(set) var lastFixAt: Date?
    private(set) var stationary = false
    private(set) var failure: String?
    private(set) var warningCount = 0
    private let manager = CLLocationManager()
    private let defaults: UserDefaults
    private let store: CameraStore
    private let presenter: AlertPresenter
    private var serviceSession: CLServiceSession?
    private var activitySession: CLBackgroundActivitySession?
    private var updates: Task<Void, Never>?
    private var retry: Task<Void, Never>?
    private var sessionID = UUID()
    private var engine: AlertEngine

    init(store: CameraStore, presenter: AlertPresenter, defaults: UserDefaults = .standard) {
        self.store = store; self.presenter = presenter; self.defaults = defaults
        enabled = defaults.bool(forKey: "warnings.enabled")
        let saved = defaults.data(forKey: "warnings.encounters")
            .flatMap { try? JSONDecoder().decode([String: Encounter].self, from: $0) } ?? [:]
        engine = AlertEngine(encounters: saved)
        super.init()
        manager.delegate = self
        manager.activityType = .automotiveNavigation
        refreshAuthorization()
    }

    func setEnabled(_ value: Bool) {
        enabled = value; defaults.set(value, forKey: "warnings.enabled")
        if value {
            start()
            Task { await presenter.requestNotifications() }
        } else { stop() }
    }

    func start() {
        guard enabled, updates == nil else { return }
        retry?.cancel(); retry = nil; failure = nil
        let sessionID = UUID()
        self.sessionID = sessionID
        refreshAuthorization()
        guard authorization != .denied && authorization != .restricted else { return }
        // Sessions belong to the feature's lifetime, including permitted
        // background relaunches, never to the settings view.
        serviceSession = CLServiceSession(authorization: .always)
        activitySession = CLBackgroundActivitySession()
        if CLLocationManager.significantLocationChangeMonitoringAvailable() {
            manager.startMonitoringSignificantLocationChanges()
        }
        updates = Task { [weak self] in
            do {
                for try await update in CLLocationUpdate.liveUpdates(.automotiveNavigation) {
                    guard !Task.isCancelled, let self, self.enabled else { break }
                    self.stationary = update.stationary
                    self.refreshAuthorization()
                    if update.authorizationDenied || update.authorizationDeniedGlobally {
                        self.failure = "Location access is off."
                    } else if update.accuracyLimited {
                        self.failure = "Turn on Precise Location for timely warnings."
                    } else if let location = update.location {
                        self.consume(location)
                    }
                }
            } catch {
                if !Task.isCancelled { self?.failure = "Location paused. Retrying automatically." }
            }
            guard let self, self.sessionID == sessionID else { return }
            self.updates = nil
            if self.enabled && !Task.isCancelled { self.scheduleRetry() }
        }
    }

    private func scheduleRetry() {
        retry?.cancel()
        retry = Task { [weak self] in
            try? await Task.sleep(for: .seconds(10))
            guard !Task.isCancelled else { return }
            self?.start()
        }
    }

    private func stop() {
        sessionID = UUID()
        retry?.cancel(); retry = nil
        updates?.cancel(); updates = nil
        manager.stopMonitoringSignificantLocationChanges()
        serviceSession?.invalidate(); serviceSession = nil
        activitySession?.invalidate(); activitySession = nil
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
        if stationary { return "Ready · waiting for movement" }
        guard let lastFixAt, now.timeIntervalSince(lastFixAt) <= 30 else { return "Waiting for location" }
        return "Monitoring"
    }

    private func consume(_ location: CLLocation) {
        let now = Date.now
        let fix = LocationFix(coordinate: Coordinate(location.coordinate.latitude, location.coordinate.longitude),
                              timestamp: location.timestamp, accuracy: location.horizontalAccuracy,
                              speed: location.speed,
                              course: location.courseAccuracy >= 0 && location.courseAccuracy <= 45 ? location.course : nil)
        guard fix.isUsable(at: now), precise else { return }
        failure = nil; lastFixAt = location.timestamp
        let previousEncounters = engine.encounters
        let warnings = engine.evaluate(fix, index: store.index, now: now)
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
            if self.enabled && self.updates == nil { self.start() }
        }
    }

    nonisolated func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        // Significant-change is a recovery source. It uses the same matcher;
        // coarse fixes fail the common accuracy/freshness gate.
        Task { @MainActor [weak self] in
            guard let self, self.enabled else { return }
            self.start()
            if let location = locations.last { self.consume(location) }
        }
    }
}
