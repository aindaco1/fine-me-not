# Fine Me Not

**Speed cameras ahead. Keep your cash.**

Free, open-source camera warnings for iPhone. One switch, one brief siren. No maps, ads, subscriptions, accounts or trip history.

Fine Me Not targets **iOS 27+** and is available in the owner’s internal TestFlight group; Apple reports build 0.1.0 (2) installed on iPhone 16 Pro Max. It automatically monitors after one-time opt-in, including permitted background operation. It never promises uninterrupted execution in every iPhone state. See the physical acceptance checklist before relying on it.

- [Supported iOS versions and iPhones](docs/SUPPORT.md)
- [Data coverage and reconciliation](docs/DATA.md)
- [Census metro coverage and weekly source checks](docs/METRO-COVERAGE.md)
- [Speed-check behavior and coverage](docs/SPEED-CHECK.md)
- [Build and TestFlight release](docs/RELEASE.md)
- [Tests and physical acceptance](docs/TESTING.md)
- [Research and implementation plan](docs/PLAN.md)
- [Sources, privacy and support](https://finemenot.xyz/)

## Run

Open `FineMeNot.xcodeproj` in Xcode, select your signing team and an iOS 27 iPhone. `project.yml` is maintained with XcodeGen; the generated project is committed. The shared core is a local Swift package with no third-party app dependencies.

```sh
swift test
python3 -m unittest discover -s Tests/Pipeline -v
python3 Scripts/publish_cameras.py
```

The development CI overrides the minimum only for simulator compatibility checks. Distribution remains iOS 27.0. Never mistake a compatibility build or successful archive for an installed TestFlight build or a passed physical road test.

## Background and audio

A retained Core Location service session and background activity session receive automotive location updates. Significant-change monitoring supports permitted relaunch/recovery. Every fix uses one on-device alert engine. Alerts are one original 1.8-second siren, using the system-selected audio route and media volume, with brief audio ducking. No silent-audio keepalive, location uploads, or claimed critical-alert entitlement.

## Weekly database

Upstream source checks run Sunday at 9 p.m. Denver time, with automatic reconciliation and durable review reports in GitHub Actions. The publisher is scheduled for Monday at 12:00 a.m. `America/Denver` (Sunday night), including daylight saving. GitHub and iOS can delay execution/download. Invalid data retains the last good snapshot. The live database combines national OSM data, reviewed Albuquerque metro locations and agency feeds. The installed app downloads updates through Update now and caches them for offline use. Each release also bundles its release-time snapshot. Coverage is incomplete; all published camera records include provenance.

## License

Code, original icon and siren: [MIT](LICENSE). Camera database: [ODbL 1.0](Data/LICENSE.md), © OpenStreetMap contributors, with source-linked municipal facts.

The **Quiet below speed limit** setting is on by default. It only suppresses speed-camera warnings when both the measured speed and applicable limit are reliable; unknown limits and red-light cameras still warn. See [speed check](docs/SPEED-CHECK.md), [geocoding and identity](docs/GEOCODING-AND-IDENTITY.md), and [source maintenance](docs/MAINTENANCE.md).
