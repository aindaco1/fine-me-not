# Supported iOS versions and iPhones

The current Fine Me Not distribution builds require **iOS 27.0 or later** on a compatible iPhone. There is no Apple Intelligence requirement.

## Compatibility vs. verification

| Environment | Status |
| --- | --- |
| iOS 27 on the compatible iPhones below | Eligible by OS and hardware; not every model has been individually tested. See [TESTING.md](TESTING.md) for field-test evidence. |
| iOS 28 and future releases | Not yet verified; no forward-compatibility promise |
| iOS 26 and earlier | Not supported by the distribution build |
| Simulator compatibility build | Uses an explicit iOS 18 minimum solely for development checks; this does not expand release support |
| iPad, Mac, Apple Watch, Android | No supported app |
| CarPlay | Audio through the system-selected car route; no dashboard app or CarPlay interface |

## Eligible models

Apple's [iOS 27 compatibility list](https://www.apple.com/os/ios/), checked September 15, 2026, includes:

| Family | Models |
| --- | --- |
| Duo | iPhone Duo |
| 18 | iPhone 18 Pro, 18 Pro Max |
| 17 / Air | iPhone 17, 17 Pro, 17 Pro Max, 17e, iPhone Air |
| 16 | iPhone 16, 16 Plus, 16 Pro, 16 Pro Max, 16e |
| 15 | iPhone 15, 15 Plus, 15 Pro, 15 Pro Max |
| 14 | iPhone 14, 14 Plus, 14 Pro, 14 Pro Max |
| 13 | iPhone 13, 13 mini, 13 Pro, 13 Pro Max |
| 12 | iPhone 12, 12 mini, 12 Pro, 12 Pro Max |
| 11 | iPhone 11, 11 Pro, 11 Pro Max |
| SE | iPhone SE, 2nd and 3rd generations |

“Eligible” means the model can run the requested operating system and uses the required location/audio APIs. It does not mean background alerting has been verified on every model. Record actual device, OS build, app build, route and outcomes in [TESTING.md](TESTING.md).

## Required settings and behavior

Enable Camera warnings once. Grant **Always** location access and **Precise Location**. Allow notifications for a visual warning when possible. Turn media volume up and use Test warning while parked on the actual car audio connection. Background App Refresh and network access help database downloads; an already saved database works offline.

Silent mode is bypassed by brief active playback using Apple's playback audio category. Fine Me Not cannot override zero media volume, a disconnected or muted car input, a phone call, or all audio interruptions. Bluetooth and wired/wireless CarPlay must be tested with the vehicle. Critical-alert privileges are not assumed or requested.

Monitoring is automatic after opt-in. A retained location service session, continuous standard location updates and significant-change recovery use the same matcher. iOS controls background execution and relaunch timing. Reopen after a device restart or force-quit; the app must not promise uninterrupted operation under every system condition. The Settings status reports missing permissions and stale location fixes instead of asserting that warnings are active.

## Toolchains

Xcode 26.6 with iOS 26.5 SDK currently compiles and signs the app with a 27.0 deployment minimum, with a warning that this minimum is outside that SDK's known range. This is **not** an iOS 27 runtime test. Xcode 27 / SDK 27 is the preferred release toolchain once available locally; see [Apple's system requirements](https://developer.apple.com/xcode/system-requirements).

Apple's [current upload requirement](https://developer.apple.com/news/upcoming-requirements/) is Xcode 26 or later with the iOS 26 SDK or later. App Store validation, successful processing, TestFlight availability, and physical testing are separate release gates.

## Build 4 background behavior

Camera warnings now request continuous navigation-quality background location with automatic pausing disabled. Low Power Mode does not switch off monitoring in app code. This increases idle and driving battery use; real-device Low Power Mode and overnight reliability are still unverified. A heartbeat timer cannot guarantee execution after iOS suspends or terminates an app. Force-quitting, denied permissions, loss of GPS and unavailable audio output can still prevent a warning.

After updating, open Fine Me Not once, confirm Always and Precise Location, and use Test warning while parked on the audio connection used in the car. The Diagnostics disclosure shows whether GPS is arriving, why the nearest mapped camera was accepted or rejected, and the most recent siren playback result. Copy diagnostics for a missed warning; review camera names before sharing because they can reveal a place you visited. The app does not automatically transmit this report.

## City coverage update

The 1.0 bundle contains **2,695 warning locations**, including all **40 reviewed Albuquerque city-listed approaches** and reviewed locations across the metro. Some are approximate warning areas. See [current coverage](https://finemenot.xyz/#sources) for published totals and speed-limit coverage. Use **Update now** to get the latest list. This represents the reviewed source lists, not a survey or every camera in every municipality.

## iOS 26 feasibility — September 15, 2026

The 27.0 minimum came from the original project scope, not a known API requirement.
`CLServiceSession`, the newest location API used here, is available from iOS 18;
the installed Apple SDK confirms this in `CLServiceSession.h`. The shared Swift
packages also declare iOS 18 as their minimum.

The unchanged app compiled successfully with a development-only deployment minimum
of 26.0 using Xcode 26.6 / SDK 26.5, then installed and launched on an iOS 26.5
simulator. The settings screen displayed the bundled 2,695 locations and the
default-on speed check. No iOS 27-only API requirement or compile failure was found.
This establishes build and launch compatibility, not physical background/audio
acceptance across all iOS 26 releases.

To add iOS 26 distribution support, lower the minimum in `project.yml`, regenerate
the Xcode project, upload a new numbered build, and update the public requirements
and App Store listing together. The current 1.0.0 (8) and 1.0.1 (9) distribution
binaries still require iOS 27. iOS 26 supports iPhone 11 and later and iPhone SE
(2nd generation and later); see [Apple's iOS 26 compatibility list](https://support.apple.com/en-nz/guide/iphone/iphe3fa5df43/ios).
