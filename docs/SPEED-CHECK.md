# Optional speed check: feasibility and implementation contract

The feature is feasible with the existing on-device location and matching pipeline. It needs reliable speed-limit data as well as the phone's measured speed. It does not require a map, account, paid API, new background mode, or additional location polling. This is a follow-up specification; the current app does not yet expose the toggle.

## Settings

**Quiet below speed limit** — off by default.

Supporting text: “Skip speed-camera sirens when your speed is reliably below the known limit. Red-light warnings stay on. Unknown speed or limit? You’ll still get a warning.”

The owner confirmed that red-light warnings must remain on. Combined speed/red-light cameras also keep their warning. Approximate or mobile speed areas qualify only when the applicable limit is verified throughout that area; a limit taken from a nearby road or a school address does not qualify.

## Data feasibility

The 1,777-record baseline has 525 records linked to any OSM `maxspeed` value, of which 520 have one syntactically numeric value. This is a candidate count, not 520 approved suppression locations: values can be stale, conditional, assigned to the wrong approach, or associated with red-light cameras. Five records carry differing source values. Unsuffixed numeric OSM values mean km/h; values ending in `mph` need conversion. Do not assume US numbers always mean mph. Preserve source, units, direction, applicability, verification date and any conditional restriction. The current app model drops speed-limit data entirely.

DC's official camera feed supplies a `SPEED_LIMIT`; SFMTA's current camera-location table supplies posted limits and operational status. Those are promising additional sources. A reviewed limit should represent the posted limit at the monitored approach, not the camera's ticketing threshold. Where school hours, flashing beacons, work zones, weather, vehicle class or different carriageways affect the limit and cannot be resolved offline, keep the warning enabled.

Apple exposes measured speed and its uncertainty through [CLLocation.speed](https://developer.apple.com/documentation/corelocation/cllocation/speed) and [speedAccuracy](https://developer.apple.com/documentation/corelocation/cllocation/speedaccuracy). Invalid/negative values and stale fixes cannot establish that the driver is below the limit. The app's displacement fallback is useful for detecting movement, but should not suppress a warning. The reviewed public [MKRoute interface](https://developer.apple.com/documentation/mapkit/mkroute) does not provide a documented posted-speed-limit lookup for arbitrary current roads; do not depend on the Apple Maps app's private display data.

## Small implementation

1. Add optional, backward-compatible speed-limit metadata to the camera model. Validate units, range, provenance, date and applicability in the publisher and phone. Old snapshots remain usable and simply cannot suppress warnings.
2. Carry `CLLocation.speedAccuracy` into the existing `LocationFix`. Store one `@AppStorage` preference and pass it to the shared alert engine, covering foreground, locked-screen and recovery callbacks alike.
3. After the existing geometry/direction checks, suppress only eligible speed-only records when a fresh measured speed plus an uncertainty margin is strictly below the verified limit. Initial conservative parameters: fix no older than 3 seconds, speed uncertainty no greater than 2 m/s, and measured speed + max(reported uncertainty, 1 m/s) below the limit. These values are a testable product choice, not a statistical guarantee about GPS accuracy.
4. A suppressed approach must remain armed. Re-evaluate on every usable location fix so acceleration above the limit can still trigger one warning before passing the camera. Do not write a cooldown encounter until a real warning is issued. Changing the toggle must not reset unrelated encounters.
5. Add a “Below verified speed limit” diagnostic with measured speed, applicable limit and source. Do not silence the Test warning button. Suppress before starting the brief siren; do not add a separate timer or audio loop.

## Acceptance

Test below, exactly at and above the limit; acceleration after initial suppression; unknown/negative/NaN speed and accuracy; stale fixes; mph/km/h conversion; expired, conflicting and conditional limits; wrong direction; red-light and combined cameras; toggle persistence; and a suppressed approach followed by a valid warning without a restart. Use the existing matcher tests rather than a second matching implementation. Then compare the setting on/off on the iPhone 16 Pro Max in locked-screen and Low Power Mode tests. The setting must never imply that a road is safe to speed on or that GPS is a certified speedometer.

Sources: [OSM maxspeed](https://wiki.openstreetmap.org/wiki/Key:maxspeed), [conditional limits](https://wiki.openstreetmap.org/wiki/Key:maxspeed:conditional), [DC camera data](https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Public_Safety_WebMercator/MapServer/43), [SFMTA active camera table](https://www.sfmta.com/projects/speed-safety-cameras). Researched September 14, 2026.
