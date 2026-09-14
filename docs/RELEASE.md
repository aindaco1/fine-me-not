# TestFlight release

- App: Fine Me Not
- Bundle: `xyz.dustwave.fine-me-not`
- Owner/team: Volver Health LLC (`PWT3Q52LZ2`), explicitly selected by the project owner
- Version: 0.1.0 (1)
- Distribution minimum: iOS 27.0
- Source: https://github.com/aindaco1/fine-me-not
- Support / privacy: https://aindaco1.github.io/fine-me-not/
- Category: Utilities (minimal camera proximity warnings)
- Price: Free; no purchases, subscriptions, ads or accounts

## Build

Use Xcode 27 preferably. `project.yml` is the project configuration source; regenerate with XcodeGen after changes. The checked-in Xcode project permits building without XcodeGen.

```sh
swift test
python3 -m unittest discover -s Tests/Pipeline -v
xcodebuild -project FineMeNot.xcodeproj -scheme FineMeNot \
  -configuration Release -destination 'generic/platform=iOS' \
  -archivePath work/FineMeNot.xcarchive -allowProvisioningUpdates archive
python3 Scripts/check_bundle.py work/FineMeNot.xcarchive/Products/Applications/FineMeNot.app --release
```

Do not use the simulator deployment override for a TestFlight archive. Increment the build number for each uploaded binary. Xcode's saved account may create/refresh team signing assets; credentials and provisioning files are never committed.

## App Store Connect

Create or select the app record for the exact bundle ID under Volver Health LLC. Upload a signed App Store Connect distribution with symbols. Confirm Apple has processed the build, export compliance is resolved, and the build is assigned to an internal test group that contains the owner's Apple account. A successful archive or upload alone is not TestFlight delivery. External public beta testing requires Apple's beta review; the first test is internal on the owner's phone.

Only standard HTTPS is used. `ITSAppUsesNonExemptEncryption=false`. No account is needed to review the app. Privacy answers should describe no developer collection of location or other app data, with the public hosting provider connection-log caveat in the privacy policy. Confirm answers against the final binary before submission.

## Suggested beta description

Fine Me Not gives you one brief siren as you approach a mapped speed or red-light camera. Free, open source, no ads or subscriptions. Turn warnings on once, allow Always and Precise Location, and test the warning on your car audio while parked. The app uses your selected audio route and media volume, including in Silent mode. Albuquerque metro coverage and background reliability are being tested; coverage is incomplete and warnings are not guaranteed.

## What to test

Check the siren on iPhone speaker, Bluetooth and CarPlay in Silent mode. Test screen-locked driving, another navigation app open, overnight stationary recovery, direction filtering, no repeat while stopped near a camera, offline warnings, and database updates. Follow [TESTING.md](TESTING.md). Note the public site name, app build and phone/audio state in feedback; do not include personal routes in public GitHub issues.

## Review notes

The app's only background purpose is user-enabled camera proximity warnings. Core Location computes proximity on device; it does not upload locations. The audio background mode is used only for the short audible warning. There is no silent audio loop. Open the app, enable Camera warnings, grant location permissions, and tap Test warning to exercise the sound. No CarPlay UI or critical-alert entitlement is requested. Mobile deployment areas say Possible speed camera because presence is not live-confirmed.

## Gates

1. Source tests and full bundle checks pass.
2. Signed archive passes export and App Store validation.
3. Apple finishes processing; build is available to the owner in TestFlight.
4. Owner confirms installation on iPhone 16 Pro Max / iOS 27.
5. Physical audio/background tests pass before claims of supported behavior or a public App Store release.
