# Test and acceptance record

## Automated checks

Run `swift test`, `python3 -m unittest discover -s Tests/Pipeline -v`, and `Scripts/check_bundle.py` against the built `.app` (add `--release` for an archive). CI exercises the shared warning engine, publisher, complete simulator bundle and embedded resources.

Core cases: approaching vs receding, opposite direction, stale/inaccurate fixes, one alert until leaving/rearming, process restart/corrected coordinates with stable IDs, long mobile corridors, expiry, unknown course, and Denver DST transitions.

Publisher cases: duplicate relation/device identity, preserved full-node tags despite skeleton responses, combined red-light/speed devices, opposing approaches, camera-facing direction, partial/mass-drop responses, missing-source retention, tombstones, expiry, metro review quarantine, immutable files and checksum.

## Simulator checks

Development compatibility build: iPhone 16 Pro Max simulator on iOS 18, built with Xcode 26.6 / iOS 26.5 SDK using an explicit development-only minimum override. This checks implementation and layout; it does not establish iOS 27 compatibility or physical background reliability.

- App starts with a real offline database and all resources.
- Settings screen readable with the intended midnight-blue design. Build 2 was rebuilt, installed and opened; its offline OpenStreetMap attribution is visible in the footer.
- Test warning starts the 1.8-second siren and returns to ready state.
- Notification and location permission prompts passed; While Using correctly reports that Always access is needed. App-specific Settings link opens the correct settings.
- Always permission granted in the simulator: simulated Gibson Boulevard driving generated a lock-screen camera notification and persisted the encounter while the app was backgrounded. This proves the simulated delivery path, not real-device scheduling, audibility, or CarPlay.
- The simulator did not provide usable course accuracy; this exposed opposite-direction ambiguity. The engine now derives travel direction from sufficient accurate displacement, covered by a regression test.
- Database public HTTPS/manifest/checksum verified. Manual Update now downloaded and installed the live snapshot `2026-09-14-0f9b8c9a0cd0-43142730` with 1,756 records, replacing the bundled copy.
- Final directional simulation while locked: eastbound Gibson encounter refreshed at 22:44:45 UTC; westbound stayed armed with its older 22:41:04 UTC timestamp. The correction warns only for the inferred travel direction.
- Fresh-source workflow run `34905568952` downloaded the speed and enforcement inputs; an alias-source HTTP 504 retained the last good aliases. The combined dataset stayed at 1,756 records and deployment succeeded. This exercised the real failure-retention path, not just fixtures.

## Physical TestFlight acceptance — pending

Use a passenger or a controlled stationary setup for observation; do not interact with the phone while driving. Record app build, iOS build, hardware, start/end time, connection, state and outcome. No route history needs to be uploaded.

| Scenario | Acceptance | Result |
| --- | --- | --- |
| Speaker, Silent mode on | One audible brief siren; no duplicate notification sound | Pending |
| Bluetooth with music/podcast playing | Siren heard; playback ducks then resumes | Pending |
| Wired CarPlay | Siren heard with screen locked and navigation active | Pending |
| Wireless CarPlay | Same, including disconnect/reconnect | Pending |
| Zero volume / inactive car audio input | Status and test explain the limitation | Pending |
| Screen locked for 30+ minutes | Warning before the known approach | Pending |
| Another navigation app foreground | Same | Pending |
| Overnight stationary, next drive | Monitoring resumes automatically | Pending |
| Restart then first unlock and reopen | Monitoring restores saved preference | Pending |
| Force-quit then reopen | Preference restores; no always-on guarantee while terminated | Pending |
| Permission revoked / Precise off | Honest degraded status; no false monitoring claim | Pending |
| Poor GPS / tunnel / old fix | No stale-location warning; recovers on usable fix | Pending |
| Wrong direction / adjacent road | No wrong-direction alert; document unresolved parallel-road false positives | Pending |
| Stoplight / stopped beside camera | Only one siren | Pending |
| Leave >850m and return after 60s | New approach warns again | Pending |
| Database update near a camera | Stable identity prevents a second siren | Pending |
| No network / failed update | Bundled or last good database continues working | Pending |
| Monday midnight across DST | Server scheduled in Denver; phone catches up later if suspended | Pending |
| Low Power Mode / Background Refresh off | Measure actual delivery and battery behavior | Pending |
| Phone call or Siri interruption | No crash or stale siren replay after interruption | Pending |
| 1-hour drive and 8-hour stationary | Record battery consumption before release claims | Pending |

## Coverage acceptance

Reconcile every listed metro approach, preserve documented mobile corridors, exclude pending installations and retired cameras. Drive-test representative city, county and Rio Rancho sites in both directions. The first bundle is incomplete; a lack of an alert is not evidence that a road is camera-free.
