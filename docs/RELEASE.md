# TestFlight release

- App: Fine Me Not
- Bundle: `xyz.dustwave.fine-me-not`
- Owner/team: Volver Health LLC (`PWT3Q52LZ2`), explicitly selected by the project owner
- Version: 0.1.0 (7)
- Distribution minimum: iOS 27.0
- Source: https://github.com/aindaco1/fine-me-not
- Support / privacy: https://finemenot.xyz/
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

## Icon update — build 3

Build 0.1.0 (3), source `9d975fd`, replaces the ticket with a speed camera and pale-blue prohibition overlay. The 1024 × 1024 opaque icon was checked on the simulator Home Screen, and the signed archive passed the bundle check. Apple confirmed the upload at 23:21 UTC on September 14, 2026. Apple finished processing and the First Drive group now shows build 0.1.0 (3) as Testing. The icon update notes were saved in TestFlight. [CI](https://github.com/aindaco1/fine-me-not/actions/runs/34908349722) passed. Installation of build 3 on the physical phone has not been checked.

## Missed-warning fixes — build 4

Build **0.1.0 (4)**, source `fd99484`, is **Testing** in the First Drive internal group. Apple accepted the upload at 00:29 UTC on September 15, 2026 (September 14 Mountain time), after a network timeout on the first export attempt. Processing completed, the build-specific test instructions were saved, and the existing group with one tester was assigned. No tester roles or access changed. Physical installation of build 4 has not been verified.

This build requests continuous standard background location with automatic pauses disabled, infers movement when reported speed is unavailable, chooses the newest valid saved/bundled database, and adds local diagnostics. It bundles `2026-09-14-971a10f8454e-571f726e` with 1,758 warning records, including approximate Coors/St. Joseph NB/SB warning areas. The city confirms the site and directions, but exact device positions remain unverified.

[CI for the app source](https://github.com/aindaco1/fine-me-not/actions/runs/34913290315) passed all 14 Swift and 10 publisher tests and the simulator bundle checks. The signed archive passed validation with minimum iOS 27.0. Both Coors directions produced one warning and recorded siren completion during locked-screen simulator replays. Real iOS 27 Low Power Mode, long idle recovery, car-audio audibility and battery use still require physical acceptance. See [DEBUGGING.md](DEBUGGING.md) for findings and the next phone test.

## Complete city-list representation — build 5

Build **0.1.0 (5)**, source `632c77b`, is **Testing** in the First Drive internal group. Apple accepted the upload at 01:09:47 UTC on September 15, 2026 (September 14 Mountain time). Processing completed, the build-specific What to Test notes were saved, and the existing group with one tester was assigned. No tester roles changed. Installation of build 5 on the physical phone remains unverified.

The build bundles `2026-09-14-6466b7b09db1-78026b1a` with **1,777 warning records**. The 19 additions bring current Albuquerque city-list representation to **40 of 40 directional approaches: 19 mapped points and 21 approximate areas**. Carlisle uses Delamar Avenue as confirmed by the city certificate. Approximate boundaries follow reviewed OSM road geometry; they are warning buffers, not surveyed equipment positions or enforcement boundaries. See [ALBUQUERQUE.md](ALBUQUERQUE.md) for every city entry. No location/audio runtime code changed for this build.

[Source CI](https://github.com/aindaco1/fine-me-not/actions/runs/34915680253) passed all 15 Swift and 12 publisher tests and the simulator bundle checks. The signed archive passed the full release bundle check with minimum iOS 27.0. [Database publication](https://github.com/aindaco1/fine-me-not/actions/runs/34915680188) succeeded; the live immutable snapshot matched its SHA-256 manifest and all 40 city references. An installed build 4 simulator downloaded it using Update now, then produced exactly one southbound Carlisle warning with playback completed while locked. These checks establish data delivery and simulated behavior. Real iOS 27 car-audio audibility, Low Power Mode, overnight recovery and battery acceptance remain pending.

## Speed check and automated maintenance — build 6

Build **0.1.0 (6)**, source `af60017`, is **Testing** in the First Drive internal group with the existing one tester. Apple accepted the upload at **03:56:29 UTC on September 15, 2026** (September 14 Mountain time). Processing completed, build-specific What to Test notes were saved, and group availability was verified at approximately 04:04 UTC. No tester roles changed. Physical installation and driving acceptance of build 6 remain unverified.

The build adds the default-on Quiet below speed limit setting and diagnostics. It bundles `2026-09-14-263679a7aa6b-9935f9b5` with **2,681 records** and 31 approved SFMTA speed limits. Unknown, stale or conditional limits continue to warn, including Albuquerque where approved camera limits are not yet available. Red-light and combined warnings remain on. A quiet encounter remains armed in case speed subsequently rises.

The signed archive passed codesign verification and the release bundle check (minimum iOS 27.0). [Source CI](https://github.com/aindaco1/fine-me-not/actions/runs/34926802914) passed 20 Swift tests, 39 pipeline tests and the simulator compatibility build. Simulator UI checks verified the upgrade default on, persisted off after relaunch, the Test warning button, and the bundled count. The archive uses Xcode 26.6 / SDK 26.5 with the requested distribution minimum 27.0; simulator deployment overrides are never used for the distribution archive.

The [GitHub source-check run](https://github.com/aindaco1/fine-me-not/actions/runs/34926817137) and subsequent [staged publication](https://github.com/aindaco1/fine-me-not/actions/runs/34927188598) both completed successfully. The latter publishes **2,695 records** in `2026-09-14-352059fee0b5-23bbacd6`, adding 14 Chicago approaches once refreshed source road metadata made their distinct identities clear. Its live SHA-256 matches the manifest. Four watched pages returned HTTP 403, and an OSM alias query returned HTTP 429; previous evidence was retained and failures remain recorded. A green workflow means the resilient pipeline completed, not that every source responded successfully. The Codex maintenance heartbeat was deleted; recurring work now runs entirely in GitHub Actions.

The installed build 6 simulator fetched that newer snapshot using Update now and visibly displayed **2,695 warning locations**, with Quiet below speed limit still enabled. This verifies the download/validation/display path independently of the offline bundle. It does not establish physical background delivery timing or car-audio behavior.

## Custom domain and source research — build 7

Build **0.1.0 (7)**, app source `61938f2`, is **Testing** in the First Drive internal group with the existing one tester. Apple accepted the upload at **04:31:51 UTC on September 15, 2026** (September 14 Mountain time). Processing completed, the build-specific notes were saved, and group availability was verified at approximately 04:43 UTC. No tester roles changed. The physical phone was last reported on build 6; installation and field acceptance of build 7 have not been verified.

This build centralizes website/database URLs in `AppLinks` and moves them directly to `https://finemenot.xyz/`. It bundles **2,695 warning records** in `2026-09-14-352059fee0b5-23bbacd6`, with the existing 31 approved SFMTA limits. No new research speed-limit candidates were approved for suppression. The owner requested no compatibility work for older test builds.

The signed archive passed codesign verification and the release bundle check with minimum iOS 27.0. The simulator compatibility build installed and launched with 2,695 records and the default-on speed check. [App source CI](https://github.com/aindaco1/fine-me-not/actions/runs/34928273608) passed, as did the [research/source-monitor CI](https://github.com/aindaco1/fine-me-not/actions/runs/34929151098) and [site publication](https://github.com/aindaco1/fine-me-not/actions/runs/34929151034). Local pipeline verification passed 39 tests. The archive still uses Xcode 26.6 / SDK 26.5; simulator deployment overrides were not used for distribution.

**Domain activation remains pending at this verification point.** Cloudflare has the apex and www DNS-only CNAMEs and answers the expected GitHub Pages IPs directly. The registrar record is active, but the `.xyz` parent nameservers still return NXDOMAIN. GitHub's origin serves the correct page and manifest when addressed directly; this does not prove public DNS or TLS. GitHub reports that the domain certificate does not yet exist, so HTTPS enforcement cannot yet be enabled. The app's downloads require HTTPS and retain their bundled/last-good data on failure. TestFlight notes disclose this activation period.

The [manual, read-only HTTPS verification run](https://github.com/aindaco1/fine-me-not/actions/runs/34929772047) waits for public delivery for up to 65 minutes. It does not change administrator settings or add a recurring schedule. Once DNS and the certificate are available, enable HTTPS enforcement in Pages, confirm `Scripts/check_site.py` passes, and exercise Update now and the website link in build 7. The [website runbook](WEBSITE.md) records the routing contract.

The [research report](DATA-RESEARCH.md) documents new camera sources and speed-limit APIs. Nine page monitors were added to the existing Sunday GitHub source checks; seven succeeded locally and two returned 403. New camera readers, road matching and approval of additional speed limits remain identified implementation work, not shipped data coverage.
