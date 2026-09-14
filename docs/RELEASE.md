# TestFlight release

- App: Fine Me Not
- Bundle: `xyz.dustwave.fine-me-not`
- Owner/team: Volver Health LLC (`PWT3Q52LZ2`), explicitly selected by the project owner
- Version: 0.1.0 (2)
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

Create or select the app record for the exact bundle ID under Volver Health LLC. Upload a signed App Store Connect distribution with symbols. Confirm Apple has processed the build, export compliance is resolved, and the build is assigned to a test group containing the owner-requested tester. Use internal testing if that tester is already an eligible App Store Connect user; otherwise use external testing and complete Apple’s beta review. Do not grant an App Store Connect role solely to bypass beta review. A successful archive or upload alone is not TestFlight delivery.

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
4. TestFlight reports installation on iPhone 16 Pro Max / iOS 27; owner verifies the app opens and permissions work.
5. Physical audio/background tests pass before claims of supported behavior or a public App Store release.

## Release evidence — September 14, 2026

Xcode confirmed **0.1.0 (2) uploaded successfully** to App Store Connect under Volver Health LLC at 22:56 UTC. Apple reported that the uploaded package was processing. Source/build commit: `7cabd13`; bundled snapshot: `2026-09-14-0f9b8c9a0cd0-43142730`, 1,756 warning records. Build 2 adds offline OpenStreetMap attribution. The previous build, 0.1.0 (1), also uploaded successfully.

[Build 2 CI](https://github.com/aindaco1/fine-me-not/actions/runs/34906072688) passed. At approximately 23:06 UTC, App Store Connect showed build **0.1.0 (2)** as **Testing** in the **First Drive** internal group, with the owner-requested tester assigned. The tester was already an eligible team member; no App Store Connect role was added. TestFlight then reported **Installed 0.1.0 (2)** on **iPhone 16 Pro Max / iOS 27.0**. The tester’s email is omitted from this public repository.

The build’s What to Test instructions were saved in TestFlight, covering permissions, audio routes, screen-locked and overnight behavior, direction/repeat filtering, offline operation and database downloads. The group uses manual build assignment; future uploads must be added after validation. This is an internal beta, not a public App Store release.

The archive and exported distribution signed successfully using Xcode’s saved team account. The final archive passed the complete bundle check with MinimumOSVersion 27.0, version 0.1.0, the siren, database, icon, privacy manifest and expected background modes. Processing, tester assignment and the reported device installation were subsequently verified in App Store Connect. Physical background reliability, audio audibility and battery acceptance remain pending; installation alone does not establish those behaviors.
