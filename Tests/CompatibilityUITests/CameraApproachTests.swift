import XCTest
import CoreLocation

final class CameraApproachTests: XCTestCase {
    private struct Route: Decodable {
        let latitude, startLongitude, endLongitude, speedMetersPerSecond, courseDegrees: Double
    }

    @MainActor
    private func launchApp() -> XCUIApplication {
        continueAfterFailure = false
        let app = XCUIApplication()
        app.launchArguments = ["-warnings.enabled", "YES"]
        app.launch()
        XCTAssertTrue(app.switches["Camera warnings"].waitForExistence(timeout: 60))
        return app
    }

    @MainActor
    func testForegroundSirenAndSettings() {
        let app = launchApp()
        let quiet = app.switches["speed-check-toggle"]
        XCTAssertEqual(quiet.value as? String, "1")
        quiet.tap()
        app.terminate()
        app.launch()
        XCTAssertTrue(quiet.waitForExistence(timeout: 60))
        XCTAssertEqual(quiet.value as? String, "0")
        quiet.tap()
        let warning = app.buttons["test-warning"]
        if !warning.isHittable { app.swipeUp() }
        warning.tap()
        Thread.sleep(forTimeInterval: 3)
        XCTAssertEqual(app.state, .runningForeground)
        // The outer runner independently requires foreground audio completion.
    }

    @MainActor
    func testBackgroundCameraApproach() throws {
        continueAfterFailure = false
        let device = XCUIDevice.shared
        let url = try XCTUnwrap(Bundle(for: CameraApproachTests.self).url(forResource: "camera-approach", withExtension: "json"))
        let route = try JSONDecoder().decode(Route.self, from: Data(contentsOf: url))
        let latitude = route.latitude
        let startLongitude = route.startLongitude
        let endLongitude = route.endLongitude
        func setLocation(_ longitude: Double) {
            device.location = XCUILocation(location: CLLocation(
                coordinate: CLLocationCoordinate2D(latitude: latitude, longitude: longitude),
                altitude: 0, horizontalAccuracy: 5, verticalAccuracy: 5,
                course: route.courseDegrees, courseAccuracy: 1, speed: route.speedMetersPerSecond, speedAccuracy: 0.5,
                timestamp: Date()))
        }
        defer { device.location = nil }
        setLocation(startLongitude)
        let app = launchApp()
        device.press(.home)
        XCTAssertTrue(app.wait(for: .runningBackground, timeout: 15))
        let duration = (endLongitude - startLongitude) * .pi / 180 * 6_371_000 * cos(latitude * .pi / 180) / route.speedMetersPerSecond
        let started = ProcessInfo.processInfo.systemUptime
        while true {
            let fraction = min((ProcessInfo.processInfo.systemUptime - started) / duration, 1)
            setLocation(startLongitude + (endLongitude - startLongitude) * fraction)
            if fraction == 1 { break }
            Thread.sleep(forTimeInterval: 2)
        }
        Thread.sleep(forTimeInterval: 10)
        // The outer runner asserts exactly one completed background siren from
        // the app's persisted journal, independently of this route driver.
    }
}
