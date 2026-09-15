# Test and acceptance record

## Automated checks

Run `swift test`, `python3 -m unittest discover -s Tests/Pipeline -v`, and `Scripts/check_bundle.py` against the built `.app` (add `--release` for an archive). CI exercises the shared warning engine, publisher, complete simulator bundle and embedded resources.

Core cases: approaching vs receding, opposite direction, stale/inaccurate fixes, one alert until leaving/rearming, process restart/corrected coordinates with stable IDs, long mobile corridors, expiry, unknown course, missing speed with real movement vs GPS jitter, published Coors areas in both directions, and Denver DST transitions.

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

## TestFlight installation

On September 14, 2026 at approximately 23:06 UTC, App Store Connect showed build 0.1.0 (2) Testing in the First Drive internal group and the requested tester’s device as **Installed 0.1.0 (2), iPhone 16 Pro Max, iOS 27.0**. The first-drive instructions were saved in TestFlight. This confirms Apple’s installation record; the behavior checks below remain pending.

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

## Missed-warning investigation — build 4

The report was a missed siren on Coors north of I-40, probably with the screen locked. No physical-device logs were available. The city-listed Coors/St. Joseph approaches were absent from the previous accepted database; the exact device passed is not confirmed. Reviewed approximate areas are now included, with the uncertainty stated in their labels and source evidence.

A regression reproduced total warning suppression when speed stayed unavailable even though accurate positions showed movement. Movement and bearing now use a shared displacement fallback before the movement gate. Jitter, stale anchors and implausible jumps do not count as driving. Fourteen Swift tests and ten publisher tests pass.

Continuous standard background location replaces the original async provider; automatic pausing is disabled. This is a reliability change whose real-device effect must be measured, not proof that the previous provider caused this incident. Audio still uses a brief `.playback` / `.duckOthers` session. The app retains only the latest audio attempt with timestamp, camera label, app/power state, route, volume and completion/error. Diagnostics also expose GPS quality, effective movement, match rejection and notification settings.

An upgrade test initially kept an old downloaded 1,756-record snapshot even with the new bundle installed. Startup now selects the newest valid snapshot across the download, backup and bundle. Retesting the upgrade preserved settings and selected the new 1,758-record snapshot without a manual download. The public manifest and immutable file checksum were verified after successful Pages deployment in run `34912766050`.

Build 4 locked-screen simulator route: northbound Coors generated the expected NB warning at 00:22:16 UTC on September 15 (September 14 Mountain time), with persisted audio status `Playback completed`, app state `background / locked`, speaker output and 60% media volume. No SB encounter was created during that northbound run. The simulator had Low Power Mode off. This proves simulated matching and audio completion; it is not a physical audibility test.

The southbound locked-screen replay generated only its SB warning at 00:23:28 UTC, with audio completion persisted. The diagnostics panel showed build 4, the corrected database, Always/Precise state, current GPS/match details and the prior background siren after relaunch. Resetting the simulator app's location authorization produced the normal location prompt again.

Apple completed build 4 processing and First Drive showed **0.1.0 (4), Testing**. [App source CI](https://github.com/aindaco1/fine-me-not/actions/runs/34913290315) passed. Build 4 installation and the physical acceptance matrix remain pending.

## City coverage expansion — build 5

All 40 city-listed approaches are represented by stable production IDs (19 mapped camera points, 21 approximate warning areas). Fifteen Swift and twelve publisher tests pass. The new checks compare every city inventory row against the actual published snapshot and verify its monitored direction; validate every added area segment against referenced OSM road edges; and replay all 21 city areas to require one matching-direction warning and no opposite-direction warning for that record. Geometry was also inspected in three road/junction review sheets.

The database contains 1,777 records in version `2026-09-14-6466b7b09db1-78026b1a`. Carlisle’s source typo was resolved using the official certificate’s Delamar Avenue description, and the Eubank certificate and Juan Tabo documents clarify the side of the cross street. This validates representation and simulated behavior; the physical camera positions and the phone acceptance matrix remain unverified. No location/audio runtime code changes were made for build 5.

[Build 5 source CI](https://github.com/aindaco1/fine-me-not/actions/runs/34915680253) passed for `632c77b`. [Database/website publication](https://github.com/aindaco1/fine-me-not/actions/runs/34915680188) succeeded. The public immutable snapshot matched its SHA-256 manifest and contained exactly one record for each ABQ-01 through ABQ-40 reference. The installed build 4 simulator downloaded it through **Update now**, changing from 1,758 to 1,777 locations. This confirms that existing build 4 installations can receive the coverage expansion without waiting for a new binary. The build 5 signed archive passed the bundle check with minimum iOS 27.0 and 1,777 cameras.

After that live download, a southbound Carlisle replay produced exactly the new `abq-carlisle-hilton-delamar-possible-sb` encounter at 01:05:02 UTC on September 15 (September 14 Mountain time). The app recorded **Playback completed**, **background / locked**, speaker output, and 60% media volume. This demonstrates the new data’s full simulated matching/audio path in build 4; physical audibility and actual hardware coordinates remain unverified.

Apple completed build 5 processing and the First Drive group showed **0.1.0 (5), Testing**, with its test instructions saved. Physical installation and the device acceptance matrix remain pending.
