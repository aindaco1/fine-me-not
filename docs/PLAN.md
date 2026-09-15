# Fine Me Not — camera alerts for iOS

Research checked September 14, 2026. This is a plan; no app or scheduled service has been created.

## Recommendation

Build Fine Me Not, a free, open-source native iOS 27 app with one settings screen, automatic background monitoring, and offline warnings for fixed speed cameras, red-light cameras, published mobile-camera sites, and reviewed approximate fixed-site areas labeled “Possible speed camera.” Prioritize the whole Albuquerque metro for data review and field testing. Start by proving background location **and audible sirens** on your phone and car. Use OpenStreetMap as the nationwide starting dataset, supplemented by current official city and county inventories.

Two requirements need a practical boundary: iOS cannot promise uninterrupted, timely location delivery under every device condition, and it cannot promise that every phone downloads an update at exactly midnight. The intended behavior is automatic monitoring after one-time setup, recovery when the system permits, and a weekly server refresh followed by installation on the phone at its next execution opportunity. These limitations are material to your “all the time” requirement, not optional implementation details.

## Confirmed scope

- Research and plan first; implementation comes later.
- iOS 27, initially your phone, eventually a public App Store release.
- Automatic monitoring; prioritize warning reliability over battery savings. No per-drive Start button.
- Fixed speed and red-light cameras, including combined devices where supported by evidence.
- Published mobile-camera sites, deployment corridors and reviewed approximate fixed-site areas are included as “Possible speed camera.” The label qualifies uncertain equipment presence or exact device position; it requires defensible road geometry. Use the same brief siren; the qualification appears in the warning text.
- Free to use and open source. OSM attribution and ODbL database sharing are accepted requirements.
- Albuquerque metro is the first coverage priority, including Rio Rancho and unincorporated Bernalillo County. Other metro jurisdictions must be audited before claiming complete metro coverage.
- One aggressive, brief 1–2 second siren burst per approach; no speech or repeating alarm. Create an original bundled sound.
- Audible with Silent mode on, using the iPhone speaker or the selected Bluetooth/CarPlay output. Support means audible playback; a separate CarPlay screen is outside this settings-only design.
- Weekly database refresh begins Monday at 12:00 a.m. in `America/Denver`, including daylight saving time.
- One settings screen. No maps, navigation, accounts, ads, subscriptions, upsells, trip history, or crowd-reporting system.
- OwlSwitch-inspired appearance, implemented with native SwiftUI controls.

Mobile-site warnings are approved. Rio Rancho and Bernalillo County mobile records remain research input until their site/road-segment geometry is verified. The exact iPhone model, car/head unit, and representative test routes are implementation inputs still to collect.

## Data sources: what is actually available

| Source | Access and reuse | What I verified | Recommendation |
|---|---|---|---|
| **OpenStreetMap** | No account required for the research download; ODbL data license, with attribution and database share-alike requirements. | Downloaded a US extract: **1,383 nodes tagged `highway=speed_camera`**, **153 speed-enforcement relations**, and **234 red-light-enforcement relations**, plus standalone tags and relation members. | Best open nationwide starting point, with substantial coverage gaps. |
| **Chicago DOT** | Public JSON/CSV APIs. Dataset metadata says “See Terms of Use.” | Downloaded **209 speed-camera records** and **300 red-light-camera records**. Both official datasets include coordinates and monitored approaches. | Strong supplement and coverage benchmark. Verify the full city terms and required notices before redistributing in the app. |
| **DC / DDOT** | Public ArcGIS JSON/GeoJSON; government catalog lists **CC BY 4.0**. | Downloaded **327 records**: 222 speed, 61 red-light, and 44 other enforcement records. Mobility and operational status need filtering. | Useful supplement; import only records whose fixed-camera eligibility is established. |
| **SCDB / Photo Enforced** | Commercial datasets. SCDB’s consumer download license limits use to private purposes and prohibits third-party redistribution without consent; Photo Enforced sells database access. | Checked the providers’ own terms/product pages. | These do not satisfy an openly redistributable dataset requirement. |

Sources: [OSM speed-camera schema](https://wiki.openstreetmap.org/wiki/Tag:highway%3Dspeed_camera), [OSM enforcement schema](https://wiki.openstreetmap.org/wiki/Relation:enforcement), [OSM license](https://www.openstreetmap.org/copyright), [Chicago speed API](https://data.cityofchicago.org/resource/4i42-qv3h.json), [Chicago red-light API](https://data.cityofchicago.org/resource/thvf-6diy.json), [DC dataset and license](https://catalog.data.gov/dataset/automated-safety-cameras), [DC source layer](https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Public_Safety_WebMercator/MapServer/43), [SCDB terms](https://www.scdb.info/en/terms_of_use/), [Photo Enforced database offering](https://www.photoenforced.com/subscribe.html).

### Coverage findings

I did not find and verify a complete, freely redistributable national inventory of fixed speed and red-light cameras. Nationwide geographic scope is different from complete coverage.

For a simple Chicago spot check, I compared each official coordinate with the nearest candidate in the downloaded OSM data using great-circle distance. Only **21 of 209** official speed-camera records had a tagged OSM speed-camera point within 100 metres; **26** matched within 250 metres. For red-light records, **10 of 300** had a candidate within either distance. The red-light candidate set included enforcement-relation device nodes and recognized standalone tags, including the older `red_light_camera` spelling.

This is a proximity comparison, not a validated recall measurement: it does not establish direction, operational status, identical physical devices, or coverage of every possible OSM tagging scheme. Speed comparison used the 1,383 directly tagged nodes, not every possible device inferred from speed-enforcement relations. Even with those qualifications, the observed mismatch is too large to support an OSM-only reliability claim. Evidence comes from the downloaded [Chicago speed](https://data.cityofchicago.org/resource/4i42-qv3h.json) and [red-light](https://data.cityofchicago.org/resource/thvf-6diy.json) records and the included OSM queries.

DC also illustrates why ingestion needs validation: among its 283 speed/red-light records, only **53 explicitly say `Fixed`**; 23 say `Portable` and 207 have blank mobility. All 53 explicitly fixed records were live or warning-stage. Blank does not mean fixed. The source also contains test/configuration devices. Preserve these distinctions instead of importing all points as active fixed cameras. [DC source layer](https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Public_Safety_WebMercator/MapServer/43)

The accompanying `osm-us-camera-research.zip` contains the actual raw downloads, queries, a speed-tagged CSV, and attribution. It is research input, not a release-ready camera database. Counts overlap; do not add nodes and relations together as a physical-camera total.

### Albuquerque metro supplement

The accompanying `albuquerque-metro-research/` folder contains a factual official-location register in CSV/JSON, an OSM candidate-coordinate CSV, and a README explaining uncertainty. All records remain marked `release_ready=false`; a street segment alone is not a precise device coordinate.

| Jurisdiction | Verified public source | Import decision |
|---|---|---|
| Albuquerque | The current city list has **40 directional entries**, including Central/Texas WB and Louisiana/Marquette NB dated September 4, 2026. The city FAQ identifies fixed speed cameras and says it has **no red-light cameras**. | Use the city list to establish current sites and monitored travel directions, then reconcile precise positions with OSM and on-site evidence. Do not import the old red-light network as active. |
| Bernalillo County | The current page lists **12 installed road locations**, expanded in our register into **18 directional records**, plus **3 mobile-site directional records** and **6 pending directional records** across three pending road areas. | Review the installed locations first. Fixed hardware is inferred from the separate mobile section and still needs confirmation. Keep pending sites out of active alerts. |
| Rio Rancho | The official STOP page describes **10 rotating local-road units** and **3 mobile units on NM 528**, with three deployment corridors published. It does not provide a complete live-position feed. | Include verified published sites/corridors as “Possible speed camera.” A weekly file cannot establish current presence. The count of local-road units does not establish their locations. |

Primary sources: [Albuquerque locations](https://www.cabq.gov/automated-speed-enforcement), [Albuquerque FAQ](https://www.cabq.gov/automated-speed-enforcement/automated-speed-enforcement-frequently-asked-questions), [Bernalillo County locations](https://www.bernco.gov/public-works/automated-photo-speed-enforcement/), [Rio Rancho STOP](https://rrnm.gov/1584/STOP-Safe-Traffic-Operations-Program).

The county page was readable in a normal browser after automated fetching returned 403. It lists Paseo del Norte near the Rio Grande overpass as installed; that listing alone does not establish a citation-start date. The county also labels Dennis Chavez approaches NB/SB despite the road's east/west alignment, so those directions require review instead of automatic correction.

The OSM research bounding box contains **67 candidate nodes**, including potentially stale, duplicated, or mobile records. This is a deliberately broad search area, not a validated metro boundary or a count of operating devices. No one-to-one reconciliation with the official register has been completed.

City test certificates are useful corroboration but the three sampled documents did not supply GPS coordinates. One illustrates why source IDs need care: the Louisiana/Marquette PDF filename contains `1372`, while its first page says location code `1371` and Louisiana between Central and Lomas. Preserve that discrepancy. [City certificate index](https://www.cabq.gov/automated-speed-enforcement/ase-documents), [Louisiana certificate, page 1](https://www.cabq.gov/automated-speed-enforcement/documents/louisiana-near-marquette-nb-1372-test-s4f359-08-28-26.pdf).

Before the private trial, reconcile every alert site on the agreed routes; before claiming metro coverage, reconcile the full current inventories and audit the remaining metro jurisdictions. Establish fixed device/monitored-lane coordinates or reviewed approximate road-area geometry, source-backed direction, status, and duplicate groups. Do not substitute an intersection's geocoded center for the camera. Maintain unresolved records in the same schema with an explicit review state, outside the alert snapshot.

### Reconciliation rules

Reconciliation turns overlapping source records into one consistent alert database. The following are proposed product rules, not additional claims about source accuracy. Run them in the weekly publisher so the phone receives a small, resolved snapshot. Use the same rules for national and metro data.

| Rule | Result |
|---|---|
| **Stable identity** | Give each site and monitored approach a persistent internal ID. Map source IDs to those IDs. Never use coordinates, source-list positions, or file order as identity. Coordinate corrections must preserve alert cooldowns across database updates. |
| **Authority is per field** | Prefer current official evidence for camera purpose, mobility, operational status, and monitored traffic direction. Accept precise OSM geometry only after matching it to the right site. An official street description cannot override a verified device coordinate with a guessed intersection center. Save each chosen field's source, evidence date, and review reason. A new fetch date is not a new observation date. |
| **Proximity suggests a match** | Start with a 100 m candidate-search radius for point records, plus compatible road, type, and travel direction. This is a review aid to tune, never an automatic merge threshold. Named segments and uncertain coordinates use road/segment evidence instead. Automatically reuse previously reviewed source mappings; send new or conflicting matches to review. |
| **Preserve approach distinctions** | Keep opposite directions, parallel roads, bridges, and separate intersections distinct. Preserve both speed and red-light functions when evidence establishes a combined site. Camera-facing direction and monitored travel direction are separate facts. Merge duplicate evidence, not distinct approaches. |
| **Uncertain presence is different from uncertain location** | “Possible speed camera” is valid for a documented mobile deployment site/corridor or a fixed-camera location with reviewed approximate road geometry and explicit uncertainty labeling. It does not make an unknown coordinate, unidentified CCTV camera, or contradictory record eligible. Pending/test sites stay out; warning-stage installations may be included when their existence and eligibility are established. |
| **Mobile corridors stay corridors** | Store a verified road segment between published endpoints, not a fictitious camera at its midpoint. Warn once when approaching/entering that segment, or once if the first usable fix is already inside it. Exit hysteresis and the same encounter cooldown prevent repeat sirens while remaining in the corridor. Direction can remain explicitly unknown when the source does not specify it. |
| **Removal needs evidence** | An explicit current decommissioning/removal ends alerts and leaves a retained removal record so stale OSM data cannot restore the site. A newer verified reinstatement can supersede that record. One missing row or failed fetch is not proof of removal. Two consecutive successful, structurally complete imports missing a previously listed site trigger review; this proposed threshold does not auto-delete it. |
| **Protect the last good result** | Reject malformed imports, impossible geometry, and unexpected mass changes. Retain accepted records for the affected source and mark its freshness accurately. An explicit mobile deployment end date expires eligibility even if subsequent fetching fails. Newly ambiguous records stay out; conflicting updates to existing records retain the prior reviewed value pending review unless clear closure/end-date evidence requires exclusion. |

Keep this small: source adapters produce one shared record schema with stable IDs, type/mobility/status, point or road-segment geometry, monitored directions, source references, and field evidence. A single reconciliation function applies a small version-controlled corrections file and emits the resolved snapshot plus a review report. Corrections record what they supersede and are rechecked when relevant source evidence changes. No confidence score, fuzzy automatic merge system, review dashboard, or extra app setting is needed for v1.

The phone uses one alert engine for both geometry types. A site/encounter key prevents duplicate sirens when several source records describe the same approach. Overlapping mobile corridors and fixed sites require an explicit reviewed grouping before sharing a cooldown; geographic overlap alone must not silence a distinct upcoming camera. Mobile “possible presence” is allowed, while unresolved geometry remains excluded.

Before shipping the data pipeline, verify these cases with small fixtures: duplicate OSM/official records yield one alert; opposing approaches remain distinct; nearby parallel-road records do not merge; explicit removal is not resurrected by stale data; a failed fetch preserves accepted records; a corridor gives one burst per encounter; and an unchanged input or a harmless coordinate correction preserves IDs and cooldown behavior. These checks test observable outcomes rather than mirroring the reconciliation implementation.

## Background behavior on iOS 27

Use SwiftUI, Core Location, AVFAudio, UserNotifications, URLSession, and a small local camera store. There is no need for a cross-platform framework or map SDK.

Build 4 uses one app-lifetime `CLLocationManager` with `allowsBackgroundLocationUpdates = true`, `pausesLocationUpdatesAutomatically = false`, automotive activity, navigation accuracy, and a 10 m distance filter. It retains a `CLServiceSession` requiring Always authorization and restores monitoring immediately on a permitted background relaunch. Significant-change monitoring is only a recovery trigger; every fix reaches the same matcher. This replaces the original async `CLLocationUpdate.liveUpdates` provider so automatic pauses are explicitly under app control. It uses more battery, including while stationary. There is no parallel location stream, silent-audio loop, or heartbeat timer intended to evade suspension. Start the feature and permissions flow in the foreground; monitoring belongs to the feature lifetime rather than the settings view. Physical locked-screen, Low Power Mode and overnight tests remain required. [Apple background updates](https://developer.apple.com/documentation/corelocation/cllocationmanager/allowsbackgroundlocationupdates), [Apple automatic pauses](https://developer.apple.com/documentation/corelocation/cllocationmanager/pauseslocationupdatesautomatically).

Keep processing small: obtain nearby candidates from the local spatial index, evaluate them, and return. Let Core Location report stationary periods and session problems. Do not depend on motion detection, a timer, or a database refresh task to wake the app in time for a camera. Add a regional/significant-change recovery mechanism only if the first device tests establish a need; route every callback through the same monitoring controller.

| Device state | Intended behavior and practical limit |
|---|---|
| Screen locked, another app open | Continue monitoring and delivering local warnings with the required permissions and an active location session. This is the primary acceptance case. |
| Suspended or terminated by the system | Restore the existing location feature promptly when Core Location relaunches the process. A session restoration bug can break continuity. |
| Force-quit | Some location mechanisms can relaunch the app, according to current Apple engineer guidance. That does **not** establish timely continuous warnings after every force-quit. Test separately and never advertise guaranteed survival. |
| Reboot | Region monitoring requires an unlock after reboot. Test monitoring restoration after the first unlock; immediate pre-unlock operation is not a supported promise. |
| Location disabled, permission reduced, poor GPS | Monitoring is impaired or unavailable. Show an actionable status when the app runs; never show a stale “Monitoring” state as current evidence. |
| Offline | Continue warnings from the installed database. Network access is only needed for updates. |

Geofences alone are unsuitable for the primary warning engine. Apple limits monitoring to 20 conditions, and its engineer guidance describes boundary settling and relaunch throttling that can delay detection. These properties are particularly relevant to a car quickly passing a camera. [Apple region-monitoring documentation](https://developer.apple.com/documentation/corelocation/monitoring-the-user-s-proximity-to-geographic-regions), [Apple engineer explanation](https://developer.apple.com/forums/thread/818908)

### Audible warnings with Silent mode on

The primary siren must use **direct app audio playback**, triggered while Core Location gives the app execution time. Use one `AlertPresenter` with an `AVAudioSession` category of `.playback`, mode `.default`, and `.duckOthers`. Enable the legitimate audio background capability as well as location. Apple's playback category supports audio with Silent mode on and the screen locked. Ducking mixes with other apps and temporarily lowers their audio. [Apple playback behavior](https://developer.apple.com/documentation/avfaudio/avaudiosession/category-swift.struct/playback), [Apple ducking behavior](https://developer.apple.com/documentation/avfaudio/avaudiosession/categoryoptions-swift.struct/duckothers).

Configure the session once, activate immediately before the siren, play the same bundled 1–2 second asset, then deactivate promptly. Handle activation errors, interruptions, route changes, and media-service resets in that one presenter. A mixable session matters because iOS can reject background activation of a nonmixable session. Do not keep silent audio playing to keep the app alive. Audio does not replace the location wake mechanism. [Apple activation guidance](https://developer.apple.com/library/archive/documentation/Audio/Conceptual/AudioSessionProgrammingGuide/ConfiguringanAudioSession/ConfiguringanAudioSession.html), [Apple audio errors](https://developer.apple.com/documentation/coreaudiotypes/avaudiosession/errorcode/cannotstartplaying).

Deliver one optional Time Sensitive visual notification with the camera type/location. Avoid a duplicate notification siren when direct playback succeeds. An ordinary notification-sound fallback may be attempted if playback fails, but it does **not** satisfy Silent-mode acceptance. Time Sensitive cannot override Silent mode; Critical Alerts require special approval and are not a dependency of this plan. [Apple notification behavior](https://developer.apple.com/design/human-interface-guidelines/managing-notifications).

Use the system's selected output route and verify all three required cases: phone speaker, Bluetooth car audio, and CarPlay audio. A standalone CarPlay interface is unnecessary for this plan; successful route playback still needs physical-car proof. CarPlay UI templates/entitlements are a separate feature. [Apple audio routing](https://developer.apple.com/documentation/avfaudio/responding-to-audio-route-changes), [CarPlay framework](https://developer.apple.com/documentation/carplay).

Silent mode and output volume are different. The app cannot force system media volume to maximum: `outputVolume` is read-only. A muted head unit, an unselected Bluetooth media source, calls, or Siri can prevent audibility even when the siren was requested correctly. The Test warning control must exercise the actual route so the user can set a useful volume while parked. Record the route and playback outcome in development diagnostics; a successful player callback alone is not evidence that the driver heard it. [Apple volume contract](https://developer.apple.com/documentation/avfaudio/avaudiosession/outputvolume).

## Minimal interface and warning rules

One screen contains:

1. **Camera warnings** — one persistent on/off switch.
2. **Status** — Monitoring, Waiting for location, Off, or a specific permission problem. “Monitoring” requires recent usable evidence while moving.
3. **Test warning** — plays the actual siren through the current route, with a small route/volume status if useful.
4. **Camera database** — installed data date, last successful check, Update now, and a small Sources & licenses link.

Fixed speed, red-light, and published mobile-site warnings are enabled. Avoid distance sliders, sensitivity modes, a speedometer, sound pickers, or separate drive controls in the first build. Use one siren asset and the user's existing media-volume controls.

OwlSwitch’s local source uses a blue `#0A0094` surface, white primary text, pale-blue `#AECFFF` accent, uppercase monospaced labels, and straightforward label/value rows. Carry that visual vocabulary into SwiftUI with readable type, accessible touch targets, Dynamic Type, and VoiceOver. Use system monospaced text initially. The reference was inspected in `main.qml`, `views/Settings.qml`, and shared row/header components; it was source review, not a rendered iOS mockup. This is visual inspiration rather than reuse of its Qt application architecture.

Proposed warning defaults, to tune with recorded routes:

- Warn once on approach, regardless of whether the user is currently speeding.
- Start with a speed-scaled lead distance around 15 seconds of travel, bounded to roughly 150–600 metres. These are trial values, not validated guarantees.
- Check recent position, horizontal accuracy, movement toward the camera, and reliable approach information. Do not interpret a camera’s lens-facing direction as the vehicle’s monitored direction.
- When direction is missing, use a more general “Camera nearby” warning. Nearby parallel roads and grade-separated roads remain a known limitation without road-matching data.
- If the first usable fix is already beside a camera, give one nearby warning. Do not add a routine second “passed” sound or imply that passing a coordinate makes it safe to accelerate.
- Use distance hysteresis and a short cooldown to prevent repeat alerts at red lights. Allow a later return journey to alert again. Deduplicate co-located or overlapping source records without merging opposing approaches accidentally.
- Do not infer operating hours or a speed limit when absent. Exclude removed, pending, test, and unresolved records. Eligible mobile sites/corridors and reviewed approximate fixed-site areas use “Possible speed camera” and the same siren; do not represent an approximate area as a precise device point or a live presence claim.

## Weekly update design

One scheduled server job starts the refresh at **Monday 00:00 `America/Denver`**. This corresponds to 06:00 UTC in daylight time and 07:00 UTC in standard time. Use the named time zone and an idempotent local-week identifier, not a permanently fixed UTC offset.

Fetch sources, validate records and coverage changes, build a compact versioned snapshot, and publish a manifest only after the snapshot is complete. Publication follows processing; if literal midnight publication is required, prepare the snapshot beforehand and switch the manifest then.

The phone bundles an initial snapshot. Every update entry point calls the same updater: app launch, manual Update now, permitted background refresh, and a due check during an existing location session. Use a cached manifest/ETag and one in-flight request. Validate schema, size, record count, coordinates, and checksum before atomically replacing the installed snapshot. Keep the previous good database on any failure, and distinguish data generation time from the last check time.

`BGAppRefreshTask` provides an opportunity to update after the scheduled time; Apple explicitly says `earliestBeginDate` does not guarantee execution at that time. Phones that are offline or not permitted to run must catch up later. A seven-day repeating timer also drifts relative to local midnight across daylight-saving changes. [Apple scheduling contract](https://developer.apple.com/documentation/backgroundtasks/bgtaskrequest/earliestbegindate)

For personal research, a cached weekly Overpass extraction is useful, with failure retention. For public distribution, source OSM through bulk extracts or an appropriately provisioned service; do not make public Overpass the app’s live backend. Geofabrik offers free US/state extracts. This is one shared ingestion job, not a request per phone. [Overpass usage guidance](https://dev.overpass-api.de/overpass-doc/en/preface/commons.html), [Geofabrik US downloads](https://download.geofabrik.de/north-america/us.html)

Retain source IDs, source dates, license, original camera type, fixed/portable/unknown classification, operational status, coordinate-review state, and direction provenance. Keep independently sourced data identifiable and resolve license compatibility before merging for publication. Publish the OSM-derived database under ODbL with the required attribution. Publish the application source and ingestion code under an explicit open-source code license, separately from data notices; the exact code license can be selected before repository publication. The app should calculate location matches locally and upload no route history.

Add Albuquerque, county, and Rio Rancho source adapters to this same ingestion job, feeding the same normalized schema as OSM. Apply the reconciliation rules above, including reviewed corrections and source-failure handling, before publishing. A weekly successful fetch is not a fresh field survey. No app telemetry or user account is needed for the static manifest/database host.

## Small implementation plan

**First bet: a two-day engineering spike plus several days of normal driving.** This is a proposed spending limit, not a delivery estimate. Success means proving the background and alert behavior before spending time on polish or national data integration.

1. **Prove location and audio together.** Native iOS 27 app, permission setup, one monitoring switch, known test-camera fixture, one siren presenter, and bounded local diagnostic timings. Install and test without the Xcode debugger attached. Confirm no per-drive foreground launch is required. Start sirens after long locked/quiet periods and verify audible output on speaker, Bluetooth, and CarPlay with Silent mode on. Stop and reassess if this core case cannot be made reliable.
2. **Add real data and the matcher.** One `CameraStore`, one pure `AlertEngine`, and one `MonitoringController`, reusing the existing `AlertPresenter`. Use the same matcher for foreground fixes, background fixes, recovery, and route replay. Reconcile metro test-route fixed cameras and mobile sites/corridors; keep unresolved geometry out of the installed snapshot.
3. **Add the weekly publisher and updater.** One snapshot schema and validator. Test failed downloads, stale manifests, interrupted replacement, missing upstream records, and DST/week-boundary calculations.
4. **Finish the settings screen and private field trial.** Measure missed/late warnings, duplicate alerts, false nearby-road alerts, automatic restart behavior, idle drain, and drain while driving. Keep detailed location traces limited to explicit development sessions.

Required device cases: locked-screen drives of at least 45–60 minutes; an overnight idle period followed by a drive without opening the app; another navigation/music app in front; cellular loss; speaker/Bluetooth/wired and wireless CarPlay where available; music playing and stopped; Driving Focus; Silent mode; route connection/disconnection; phone calls and Siri; Low Power Mode; force-quit; reboot and first unlock; permission changes; app update; and multiple cameras close together. Simulator route replay verifies geometry and deduplication, but cannot prove real iOS background delivery or car audibility.

For each field pass, record the exact iPhone/iOS build, car/audio route, permissions, first usable fix, expected camera, alert lead time, and heard/not-heard outcome. Separate a missing database camera from a location-session failure and from failed or inaudible playback. Require no unexplained missed or late alerts on the agreed test routes before proceeding; this is a test gate, not proof of nationwide reliability.

Before a public release, expand coverage validation beyond the personal routes, finish source-license requirements, and demonstrate that location background mode directly serves the core warning feature. Apple allows background services for their intended purposes; App Store acceptance still requires review. [App Review Guidelines, 2.5.4](https://developer.apple.com/app-store/review/guidelines/#software-requirements)

The scope scores **8/10** against the 37signals shaping checklist: the product is small and the first bet is bounded, but background acceptance, sound behavior, and sufficient data coverage are not yet solved. Resolve those with the field spike and source checks; do not add features to compensate for unresolved reliability.
