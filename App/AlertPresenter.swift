import Foundation
import Observation
import AVFAudio
import UserNotifications
import CameraCore

@MainActor @Observable
final class AlertPresenter: NSObject, AVAudioPlayerDelegate {
    private(set) var isPlaying = false
    private(set) var audioError: String?
    private(set) var route = "Current audio output"
    private(set) var volume: Float = 0
    private(set) var lastWarning: String?
    private var player: AVAudioPlayer?
    private var notificationObservers: [NSObjectProtocol] = []
    private let audio = AVAudioSession.sharedInstance()

    override init() {
        super.init()
        for name in [AVAudioSession.routeChangeNotification, AVAudioSession.interruptionNotification,
                     AVAudioSession.mediaServicesWereResetNotification] {
            notificationObservers.append(NotificationCenter.default.addObserver(forName: name, object: nil, queue: .main) { [weak self] notification in
                let name = notification.name
                let interrupted = (notification.userInfo?[AVAudioSessionInterruptionTypeKey] as? UInt)
                    == AVAudioSession.InterruptionType.began.rawValue
                Task { @MainActor [weak self] in
                    guard let self else { return }
                    if interrupted || name == AVAudioSession.mediaServicesWereResetNotification {
                        if self.isPlaying { self.audioError = "Warning audio was interrupted." }
                        self.finish()
                    }
                    self.refreshRoute()
                }
            })
        }
        refreshRoute()
    }

    func refreshRoute() {
        route = audio.currentRoute.outputs.map(\.portName).joined(separator: ", ")
        if route.isEmpty { route = "System-selected output" }
        volume = audio.outputVolume
    }

    func requestNotifications() async {
        _ = try? await UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound])
    }

    func present(_ warnings: [CameraWarning]) {
        guard let first = warnings.first else { return }
        let title = warnings.count == 1 ? first.camera.kind.title : "Cameras nearby"
        let body = warnings.map { "\($0.camera.kind.title): \($0.camera.label)" }.joined(separator: "\n")
        lastWarning = "\(title) · \(first.camera.label)"
        let didStart = playSiren()
        let content = UNMutableNotificationContent()
        content.title = title; content.body = body
        content.interruptionLevel = .timeSensitive
        // Direct audio is the Silent-mode path. A soundless notification avoids
        // sounding twice; ordinary sound is only a degraded fallback.
        content.sound = didStart ? nil : .default
        let request = UNNotificationRequest(identifier: UUID().uuidString, content: content, trigger: nil)
        UNUserNotificationCenter.current().add(request)
    }

    @discardableResult
    func playSiren() -> Bool {
        guard !isPlaying else { return true }
        audioError = nil
        do {
            try audio.setCategory(.playback, mode: .default, options: [.duckOthers])
            try audio.setActive(true)
            guard let url = Bundle.main.url(forResource: "siren", withExtension: "wav") else {
                throw CocoaError(.fileNoSuchFile)
            }
            let player = try AVAudioPlayer(contentsOf: url)
            player.delegate = self; player.numberOfLoops = 0; player.volume = 1
            self.player = player
            guard player.play() else { throw CocoaError(.fileReadUnknown) }
            isPlaying = true; refreshRoute()
            return true
        } catch {
            audioError = "Couldn't play the siren. \(error.localizedDescription)"
            finish(); return false
        }
    }

    private func finish() {
        player?.stop(); player = nil; isPlaying = false
        try? audio.setActive(false, options: .notifyOthersOnDeactivation)
    }

    nonisolated func audioPlayerDidFinishPlaying(_ player: AVAudioPlayer, successfully flag: Bool) {
        let identifier = ObjectIdentifier(player)
        Task { @MainActor [weak self] in
            guard let self, let current = self.player, ObjectIdentifier(current) == identifier else { return }
            if !flag { self.audioError = "Warning audio did not finish." }
            self.finish()
        }
    }
    nonisolated func audioPlayerDecodeErrorDidOccur(_ player: AVAudioPlayer, error: Error?) {
        let identifier = ObjectIdentifier(player)
        Task { @MainActor [weak self] in
            guard let self, let current = self.player, ObjectIdentifier(current) == identifier else { return }
            self.audioError = "Couldn't decode the warning sound."; self.finish()
        }
    }
}
