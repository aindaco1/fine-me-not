# More cameras and better speed limits

Research checked September 14, 2026, America/Denver. Scope: free, open-source Fine Me Not; Albuquerque metro first, followed by the Census top 20 metropolitan areas. “Speed limit” means the posted legal limit applicable to the monitored approach, not a camera’s ticket threshold.

## Findings and priorities

There are useful additional sources. The best expansion remains a combination of agency location lists, agency road networks and OpenStreetMap, rather than one complete national camera file. This investigation identified new local camera inventories, proved three public road-data APIs, and measured an Albuquerque speed-limit candidate pool. None of that establishes complete metro coverage or warrants automatically silencing additional warnings.

The recommended order is:

1. **Albuquerque: NMDOT road segments plus current sign evidence.** The public SpeedLimit layer returned 995 segments in the Albuquerque-area query. Every one of the 20 city-camera approaches represented as points in the current master has a segment within 75 metres. This is promising proximity, not a verified camera-to-road assignment. The other city approaches are approximate areas and were not part of that point test.[^1]
2. **Use evidence already collected.** The source caches contain candidate limits for 268 DC records, 32 Arlington records and one Tacoma record. OSM has 515 entities with numeric/raw maxspeed values linked to source IDs in the accepted master. These need interpretation and approval; they are not 515 additional cameras or approved limits.
3. **Add Phoenix- and Washington-area inventories.** Scottsdale, Mesa, Fairfax County and Prince George’s County provide useful location lists. They need deterministic extraction, geocoding where appropriate, and reconciliation against existing OSM/agency identities.[^2][^3][^4][^5]
4. **Use Seattle and NYC street networks for limit candidates.** Both APIs returned real geometries and posted-speed fields without an account. They can enrich existing cameras after matching the correct road and direction.[^6][^7]
5. **Evaluate Overture for national road matching.** It provides an openly licensed transportation network and a speed-limit schema. Test actual field population around our cameras before committing to a national enrichment job.[^8]

The app’s approved suppression coverage remains **31 SFMTA camera limits** in the 2,695-record snapshot examined. No new research candidate was promoted to a suppression-approved limit in this change.

## Additional camera sources

“New” below means additional to the source registry at the start of this investigation. A listing may overlap cameras already present through OSM; the counts below are source rows, intersections or systems as specified, never claimed net additions.

| Source | What it adds | Coordinate quality / recurring access | Recommendation |
|---|---|---|---|
| **Scottsdale Police — new** | 11 directional entries at 10 distinct intersections, including two approaches at Frank Lloyd Wright/Greenway-Hayden Loop. | Current HTML table; street names and directions, no pole coordinates in the table. | High priority. Reuse intersection geocoding and preserve approach identity. Confirm each device’s functions before assigning combined enforcement.[^2] |
| **Mesa Police — new** | Eleven listed intersection systems, plus a separate school-zone deployment program. | HTML and linked seasonal schedule documents. Intersection centroids are estimates. | High priority for Phoenix metro. Separate permanent intersection records from dated school deployments.[^3] |
| **Fairfax County — new** | Twenty current/active school locations, operating windows, and separately identified planned installations. | Current HTML tables; school/road descriptions rather than surveyed camera positions. | Import active locations after road-specific geocoding. Keep proposed sites out of the live inventory until activation is established.[^4] |
| **Prince George’s County red-light locations — new** | Twenty directional location rows. | Official intersection table; no complete API verified in this pass. Local automated retrieval returned HTTP 403. | Valuable Washington-metro lead. Register the source and resolve repeatable access before building its reader.[^5] |
| **Snellville Police — new** | School camera roads, schedules, posted limits and separate enforcement thresholds. | Official HTML; applies to Snellville, not every Gwinnett jurisdiction. | Particularly useful for future conditional-limit support. Do not collapse its several speed values into one maximum.[^9] |
| **Wheat Ridge Police — new** | Four speed-camera location descriptions; two additional red-light intersections mentioned in the 2026 expansion text. | Mixture of intersections, park references and a street segment. The page mixes expansion language with a current-location FAQ. | Use the four-location list as evidence candidates; confirm activation for the two red-light additions. Mobile corridors are not fixed device positions.[^10] |
| **CDOT locations and program FAQ — new** | Directional highway milepoints and point-to-point average-speed enforcement. | Official location page plus applicability FAQ; milepoints require the correct route/calibration, not address geocoding. | Monitor nationally. Some corridors are outside Denver’s MSA. Model average-speed zones before treating endpoint cameras like ordinary instantaneous-speed devices.[^11][^12] |
| **NYC DOT quarterly enforcement reports — new lead** | Quarterly aggregate unreadable-plate reports with enforcement locations and dates; Q2 2026 is linked. | Official recurring XLSX series. The workbook download returned HTTP 403 locally; its schema and row counts were not validated. | Useful recent operational corroboration after extraction succeeds. Absence from this event-based report does not prove that a camera is absent or retired.[^13] |
| **Miami-Dade — existing monitor, deeper evidence** | Current school/road list plus an annual implementation report. | HTML and PDF. School address and enforced road can differ. | Find installation exhibits or a current device register. The report records 70 systems across 27 school zones by July 2025; the 206-zone figure is an authorization/expansion universe, not 206 verified current devices.[^14][^15] |
| **Minneapolis — existing monitor** | Pilot location analysis, program timeline and annual reporting. | Official pages/PDF; automated access remains unreliable. Candidate studies include sites not selected for installation. | Reconcile selected/active locations with the current master. Do not ingest every study candidate.[^16] |

These sources complement the existing Chicago, DC, Arlington, Seattle, Tacoma, SFMTA, Phoenix, Philadelphia and Hillsborough readers. Montgomery County and Maryland SafeZones also remain useful previously identified leads; their age, reuse conditions or deployment semantics have not been resolved merely by finding another copy of their data.

A public agency page is a strong source of location facts, but it is not automatically a blanket license to redistribute its prose, maps or imagery. The new page monitors store fingerprints and source metadata. Before adopting a downloadable dataset, record its specific terms and attribution. Applying ODbL to our combined database does not override upstream restrictions.

## Speed-limit sources that actually merit implementation

### NMDOT: the best Albuquerque lead

The accessible endpoint is the **SpeedLimit layer 33** in NMDOT’s EGIS viewer service. It supports a geographic bounding-box query, WGS84 output and polyline geometries. The response includes `RouteID`, `FromMeasure`, `ToMeasure`, `FromDate`, `ToDate`, `SpeedLimit`, `last_edited_date`, `LocError` and object/event identifiers.[^1]

The successful query covered longitude −107 to −106.3 and latitude 34.7 to 35.6, requested records with no `ToDate`, and returned 995 segments without a transfer-limit warning. The response’s edit timestamps span 2021–2024. Those dates are evidence of old edits, not proof that the limits are wrong; a successful 2026 download also does not prove that every limit was checked in 2026.

I compared each point-based city approach with all line segments using a local planar distance calculation. All 20 had a segment within 75 metres. This diagnostic intentionally did not approve any match. It excludes approximate corridors and does not account for grade separation, travel direction, lane assignment or road-name equivalence.

| Camera approach | Nearby numeric limit value | Approximate distance | Why review remains necessary |
|---|---:|---:|---|
| Coors between Montaño and Paseo, northbound | 45 | 9.5 m | Route NM45P; establish applicable carriageway and current signs. |
| Eubank north of Central, northbound | 40 | 3.9 m | Route FL4063P; source edit is July 2023. |
| Unser north of Dellyne, northbound | 45 | 3.3 m | Route FL4082P; requires current applicability evidence. |
| Paseo near Barstow, westbound | 55 and 30 | 30.2 and 30.6 m | Two different routes are almost equally close. Nearest-road matching can choose the wrong limit. |
| Broadway north of Iron, southbound | 35 and 30 | 21.2 and 70.0 m | Nearby cross-street data must not override the monitored road. |

The numeric values above are **raw source values**. The retrieved field definition did not explicitly establish units; confirm the publisher’s unit convention before converting to mph. Also resolve the layer’s redistribution terms. Neither issue can be solved by assuming that all US numeric fields mean mph.

Implementation should join route identifiers to the agency’s road-name/route layers, retain all plausible competing matches, and review the full warning geometry. For Coors/St. Joseph, the app currently uses approximate north/south road areas: establish the speed along those areas rather than borrowing a limit from a different Coors camera. A current sign inventory or dated installation/traffic order can establish applicability more directly than an old traffic study. The earlier Albuquerque city SpeedLimits endpoints returned empty layer lists; NMDOT is a separate, successful source.

### Limits already present in our inputs

This audit examined the checked-in source caches and accepted master, rather than estimating coverage from dataset marketing:

| Input | Candidate evidence found | Current decision |
|---|---:|---|
| DC camera feed | 268 records with candidate values | Review device type, mobility, current status and conditional applicability. No blanket promotion. |
| Arlington | 32 candidate records, marked conditional | Do not use a school-zone value as an unconditional all-day limit. |
| Tacoma | One candidate value among 14 records | Review that specific device’s road, type and semantics. |
| SFMTA | 33 source records with limits; 31 accepted master limits | Already approved through the camera-ID join and current operational table. |
| OSM speed/enforcement inputs | 565 of 3,502 unique OSM entities contain `maxspeed`; 515 are linked to source IDs in the accepted master | Candidate pool only. At least 34 of those 515 have explicit conditional speed tags. |

These are entity/record counts, not unique physical poles or net additions. Multiple OSM entities can contribute to one warning record. Red-light or combined records must retain their existing always-warn behavior.

OSM supports units, directional limits and conditional values. A bare numeric `maxspeed` means km/h by convention; values such as `35 mph` explicitly mean mph. Do not reinterpret bare numbers as mph based on country. `maxspeed:advisory`, design speeds, survey percentiles and enforcement tolerances are different concepts.[^17]

For limits associated with a camera, prefer its explicit enforcement/road relationship over a nearest-way search. Road-level OSM tags can fill gaps, but OSM and an OSM-derived mirror are one evidence lineage, not two independent confirmations.

### Seattle Streets

The official Seattle Streets service returned line geometry, `ONSTREET`, `SPEEDLIMIT`, `ONEWAY` and `ONEWAYDIR` in an unauthenticated sample query. Three sampled 1st Avenue segments returned a numeric value of 25. The layer’s latest edit metadata was September 14, 2026; that is a dataset timestamp, not a sign inspection date. Seattle describes its open data as free to use and share, while the layer warns that accuracy is not guaranteed.[^6][^18]

Use this to generate road-aligned candidates for the Seattle camera inventory. Confirm units and direction codes in the source contract. An ordinary street limit cannot by itself establish a lower flashing school-zone limit or when it applies.

### NYC Street Centerline

The working Socrata data resource is **`inkn-q76z`**, not the map-view ID `3mf9-qshr`. Querying the map as a dataset returned empty objects. Following its metadata to the underlying resource returned real `physicalid`, `full_street_name`, `posted_speed`, `trafdir`, `modified_date` and `the_geom` values. The catalog describes a weekly update cadence.[^7]

The sample included Avenue N, Hone Avenue and 48 Street with numeric 25 values and record modification dates from 2017, 2020 and 2024. Preserve those dates and actual roadbed geometry. Do not infer a camera from a street segment, assume the city default applies everywhere, or confuse this feed with the historical NYC dataset named “speed cameras.”

### Overture Maps

Overture transportation offers road segments, stable identifiers, names and a `speed_limits` representation that supports direction and other scoped rules. Its transportation data is ODbL, with source attribution. This is a good fit for a free, offline-capable application and can reduce repeated ad hoc Overpass queries.[^8][^19]

The current release observed was 2026-08-19.0. No GeoParquet coverage sample was extracted in this pass, so the presence of a schema field must not be reported as complete US speed-limit coverage. Test a bounded Albuquerque extract first. Track release/version and underlying source lineage; monthly map releases can be checked weekly without inventing weekly source freshness. Preserve conditional and segment-range rules rather than flattening them into a single maximum.

### Mapillary and road-authority sign evidence

Mapillary exposes map-feature/sign detections and imagery that can help a reviewer establish what a sign said at capture time. Its imagery is CC BY-SA; computed feature/API access has its own terms and authentication requirements. No API account was created or feature download validated in this pass.[^20][^21]

This is corroborating evidence: check capture date, sign orientation, applicable road, school/work-zone plates and whether the sign is still present. Prefer a current agency sign inventory or effective speed order where available. CDOT explains that its signed speed-study documents establish changed limits on the roads it controls; that does not extend authority to every local road.[^22]

### Why a commercial “speed limit API” is not the default

Google Roads advertises speed limits but documents restricted access and cases where returned values may be estimated, incomplete or the maximum variable limit. Its storage and attribution requirements do not fit simply publishing a free downloadable open camera database. Keep it out of the core pipeline unless a specific compatible agreement is established.[^23][^24]

A geocoder is also not a speed-limit service. It can locate an address without knowing the monitored carriageway or current legal speed. There is no verified free API in this investigation that solves every camera, road, condition and jurisdiction correctly in one call.

## Reconciliation and a conservative publication contract

The existing stable camera identities, aliases, reviewed overrides, source caches and one publisher should remain the only publication path. Extend them rather than building a parallel camera database.

For each camera, store candidate limit evidence with its raw value/unit, normalized value, source entity, road/approach, geometry or linear reference, direction, condition, effective dates, source date, fetch time, attribution and match rationale. Keep fetched-at and verified-at distinct. Changing a page fingerprint or successfully re-downloading old data cannot renew sign verification.

A candidate can become eligible to suppress only when the monitored road and direction are unambiguous, the value is a posted limit with explicit units, applicability is supported, and evidence has not expired. Conflicting credible values must hold the candidate for review. Do not take the highest value, a majority vote among mirrors, or the nearest point. Preserve the current warning behavior whenever confidence is insufficient.

For text-only camera locations, prefer agency coordinates, then a validated road intersection, then an address estimate on the named enforcement road, and finally a clearly labeled corridor. A school’s mailing address or building centroid is not a camera position. A camera’s small distance from another record is insufficient to merge it: require compatible road, approach, enforcement type and identity evidence. Opposing directions and nearby distinct intersections can legitimately need separate records.

Average-speed zones need additional treatment: instantaneous speed below the limit near an endpoint does not establish compliant average speed through the zone. Until the app models that distinction, these sources should remain monitor/research inputs rather than silently inheriting the ordinary point-camera suppression rule.

## Weekly maintenance and implementation sequence

Nine additional page monitors were registered in the existing GitHub workflow: Scottsdale, Mesa, Fairfax, Prince George’s red-light locations, Snellville, Wheat Ridge, CDOT locations, CDOT applicability and NYC DOT data feeds. These run with the existing **Sunday 21:00 America/Denver** source checks, before **Monday 00:00 America/Denver** publication. GitHub scheduling can be delayed. No Codex recurring job was added.

Page changes produce review findings; they do not manufacture cameras or approve limits. HTTP failures remain visible and retain any last successful evidence. Prince George’s and NYC DOT returned HTTP 403 during local probes. The source registry and generated maintenance report record actual outcomes; a successfully completed workflow is not a claim that every upstream source responded.

The next implementation work should be three small, reviewable increments:

1. Add a bounded NMDOT candidate reader and route-name matching, plus reviewed Albuquerque sign/limit evidence. Validate correct-road and ambiguous-road examples before enabling suppression on any new camera.
2. Add Scottsdale/Mesa and Fairfax/Prince George’s text readers using the existing geocoding and reconciliation code. Produce explicit accepted/duplicate/ambiguous/inactive counts, with directional source IDs and visible precision labels.
3. Add Seattle/NYC road candidates, then test an Overture regional extract. Build conditional school/average-speed support separately; unknown conditions must continue warning.

Useful acceptance metrics are net distinct approaches added, proportion with agency or reviewed coordinates, unresolved duplicates, proportion of speed cameras with approved current limits, conflicts by source, source success/freshness, and reasons suppression is unavailable. A total camera count alone is a poor measure of reliability.

## Sources

[^1]: NMDOT, [SpeedLimit layer 33](https://gis.dot.nm.gov/epermit/rest/services/EGIS/EgisViewer/MapServer/33) and [EGIS service](https://gis.dot.nm.gov/epermit/rest/services/EGIS/EgisViewer/MapServer). Public JSON query and local proximity analysis, September 14, 2026.
[^2]: Scottsdale Police, [Photo Enforcement](https://www.scottsdaleaz.gov/police/police-units/photo-enforcement). Table and page reviewed; page reports April 9, 2026 update.
[^3]: Mesa Police, [Photo Safety Program](https://www.mesaaz.gov/Public-Safety/Mesa-Police/About-Mesa-Police/Photo-Safety-Program).
[^4]: Fairfax County, [Speed Cameras](https://www.fairfaxcounty.gov/topics/speed-cameras).
[^5]: Prince George’s County Police, [Red Light Camera Locations](https://www.princegeorgescountymd.gov/departments-offices/police/online-services/red-light-enforcement/red-light-camera-locations). Indexed official page reviewed; direct automation returned 403.
[^6]: Seattle DOT, [Seattle Streets](https://www.arcgis.com/home/item.html?id=f91318f1cc43489fb0e7aca2fde22899), [queryable feature layer](https://services.arcgis.com/ZOyb2t4B0UYuYNYH/arcgis/rest/services/Seattle_Streets_1/FeatureServer/0).
[^7]: NYC OTI, [Centerline dataset](https://data.cityofnewyork.us/City-Government/Centerline/inkn-q76z), [Socrata API](https://data.cityofnewyork.us/resource/inkn-q76z.json). Underlying dataset identified through the [map view’s metadata](https://data.cityofnewyork.us/api/views/3mf9-qshr.json).
[^8]: Overture Maps, [Transportation guide](https://docs.overturemaps.org/guides/transportation/) and [road properties](https://docs.overturemaps.org/guides/transportation/roads/).
[^9]: Snellville Police, [School Zone Speed Cameras](https://www.snellville.gov/police-department/school-zone-speed-cameras).
[^10]: Wheat Ridge Police, [Crash and Traffic Team / Automated Speed Cams](https://www.wheatridge.gov/222/Crash-and-Traffic-Team).
[^11]: CDOT, [Camera Locations](https://www.codot.gov/programs/speedenforcement/cameralocations).
[^12]: CDOT, [Speed Enforcement FAQ](https://www.codot.gov/programs/speedenforcement/faq), including average-speed measurement.
[^13]: NYC DOT, [Data Feeds, Dashboards & Open Data](https://www.nyc.gov/html/dot/html/about/datafeeds.shtml), Automated Enforcement section, and [Q2 2026 workbook](https://www.nyc.gov/html/dot/downloads/excel/quarterly-unreadable-license-plate-report-q2-2026.xlsx). Workbook content not validated.
[^14]: Miami-Dade County, [School Zone Speed Detection Systems](https://www.miamidade.gov/global/transportation/public-works/redspeed-initiative.page).
[^15]: Miami-Dade County, [December 18, 2025 annual report](https://documents.miamidade.gov/mayor/memos/2025-12-18-Annual%20Report%20Regarding%20School%20Zone%20Speed%20Detection%20Systems.pdf), reporting through July 31, 2025.
[^16]: Minneapolis, [Traffic Safety Camera timeline](https://www.minneapolismn.gov/government/programs-initiatives/visionzero/actions-taken/traffic-safety-camera/timeline/) and [location analysis](https://www.minneapolismn.gov/media/-www-content-assets/documents/Minneapolis-Traffic-Safety-Camera-Location-Analysis.pdf).
[^17]: OpenStreetMap, [maxspeed tagging specification](https://wiki.openstreetmap.org/wiki/Key:maxspeed).
[^18]: Seattle, [Privacy, Data, and Security](https://www.seattle.gov/digital/privacy-data-and-security), open-data reuse statement.
[^19]: Overture Maps, [Attribution and Licensing](https://docs.overturemaps.org/attribution/).
[^20]: Mapillary, [Map features](https://help.mapillary.com/hc/en-us/articles/115002332165-Map-features).
[^21]: Mapillary, [CC-BY-SA imagery license](https://help.mapillary.com/hc/en-us/articles/115001770409-CC-BY-SA-license-for-open-data).
[^22]: CDOT, [Speed Management Program](https://www.codot.gov/safety/traffic-safety/operations/speed-management-program).
[^23]: Google, [Roads API speed limits](https://developers.google.com/maps/documentation/roads/speed-limits).
[^24]: Google, [Roads API policies and attribution](https://developers.google.com/maps/documentation/roads/policies).
