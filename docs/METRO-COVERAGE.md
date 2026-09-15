# Metro coverage and source review

Research and initial expansion: September 14, 2026. The master grew from **1,777 to 2,653 warning records: 876 additions, no removals**. This is an expansion with an explicit backlog, not complete precise coverage of all 20 metros. A warning record can represent a monitored approach or a possible deployment area; it is not a count of physical cameras.

The scope is Albuquerque plus the 20 largest **metropolitan statistical areas** in the Census Bureau's [July 1, 2025 population estimates](https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/metro/totals/cbsa-est2025-alldata.csv). County membership and population are in `Data/Regions/metros.json`; [Census TIGER boundaries](https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_ACS2026/MapServer/93) validate source coordinates. This excludes separate metros such as San Jose and Lakeland from the San Francisco and Tampa counts. Revisit the ranking when Census releases a new vintage.

## Added and improved

- **Albuquerque metro:** 26 additions: 14 community-mapped Rio Rancho possible deployment points, three county approaches at mapped points, and nine county road areas. Eubank/Sierra Vista changed from a 750 m approximate area to the mapped device point while retaining its app identity. The city remains 40/40 listed approaches, now 20 mapped points and 20 approximate areas.
- **Elsewhere:** 850 new agency records: Chicago 548, DC 168, Arlington 19, Seattle 61, Tacoma 14, San Francisco 31 and Phoenix 9. These cover five of the top-20 MSAs; other MSAs retain community coverage while more precise sources are researched.
- **32 Seattle identity reconciliations** preserve existing mapped coordinates and app IDs while adding city evidence. Thirty change from combined speed/red-light to red-light-only. These are corrections, not additions.
- **200 nearby candidates remain pending** after the initial pass. Being within 150 m of an accepted record does not establish that two records are the same camera. Unknown road/approach identity stays in review; no proximity merge is applied.

The reproducible current counts are in `Data/Review/metro-coverage.json`. Agency counts include records reconciled to an existing OSM identity. OSM-only records are not all agency-verified and can contain obsolete entries. A zero below means no accepted warning record, not an assurance that there are no cameras.

| Census rank | Metro | Warning records | With agency point evidence | Approximate road areas |
|---:|---|---:|---:|---:|
| — | Albuquerque, NM | 72 | 0 | 32 |
| 1 | New York-Newark-Jersey City, NY-NJ | 99 | 0 | 0 |
| 2 | Los Angeles-Long Beach-Anaheim, CA | 35 | 0 | 0 |
| 3 | Chicago-Naperville-Elgin, IL-IN | 625 | 548 | 0 |
| 4 | Dallas-Fort Worth-Arlington, TX | 86 | 0 | 0 |
| 5 | Houston-Pasadena-The Woodlands, TX | 1 | 0 | 0 |
| 6 | Atlanta-Sandy Springs-Roswell, GA | 31 | 0 | 0 |
| 7 | Washington-Arlington-Alexandria, DC-VA-MD-WV | 509 | 187 | 0 |
| 8 | Miami-Fort Lauderdale-West Palm Beach, FL | 24 | 0 | 0 |
| 9 | Philadelphia-Camden-Wilmington, PA-NJ-DE-MD | 9 | 0 | 0 |
| 10 | Phoenix-Mesa-Chandler, AZ | 33 | 9 | 0 |
| 11 | Boston-Cambridge-Newton, MA-NH | 0 | 0 | 0 |
| 12 | Riverside-San Bernardino-Ontario, CA | 4 | 0 | 0 |
| 13 | San Francisco-Oakland-Fremont, CA | 80 | 31 | 0 |
| 14 | Detroit-Warren-Dearborn, MI | 0 | 0 | 0 |
| 15 | Seattle-Tacoma-Bellevue, WA | 194 | 107 | 0 |
| 16 | Minneapolis-St. Paul-Bloomington, MN-WI | 16 | 0 | 0 |
| 17 | Tampa-St. Petersburg-Clearwater, FL | 28 | 0 | 0 |
| 18 | San Diego-Chula Vista-Carlsbad, CA | 15 | 0 | 0 |
| 19 | Denver-Aurora-Centennial, CO | 22 | 0 | 0 |
| 20 | Orlando-Kissimmee-Sanford, FL | 97 | 0 | 0 |

## Source decisions and gaps

| Metro | Current supplemental evidence and next step |
|---|---|
| Albuquerque | [City list](https://www.cabq.gov/automated-speed-enforcement), [county program](https://www.bernco.gov/public-works/automated-photo-speed-enforcement/), [Rio Rancho program](https://rrnm.gov/1584/STOP-Safe-Traffic-Operations-Program). See the county backlog below. Valencia and Torrance are part of this MSA; no additional precise agency feed was found for them. |
| New York | [NYC DOT program](https://www.nyc.gov/html/dot/html/motorist/vision-zero-safe-driving.shtml). Automated HTTP requests return 403. No sufficiently current, complete public coordinate inventory was obtained; expand research to Nassau, Yonkers and other participating municipalities. |
| Los Angeles | [LADOT rollout](https://ladot.lacity.gov/speed-safety-system), [Long Beach rollout](https://longbeach.gov/pw/projects/automated-speed-enforcement-system/), [Culver City active red-light approaches](https://www.culvercitypd.gov/Bureau-Information/Patrol-Bureau/Photo-Enforcement). Proposed speed-camera locations are not automatically counted as operational. Reconcile active red-light approaches against mapped devices. |
| Chicago | [Speed-camera feed](https://data.cityofchicago.org/d/4i42-qv3h) and [red-light feed](https://data.cityofchicago.org/d/thvf-6diy). Current activation dates and separate monitored approaches are retained. Nearby existing records still need explicit matching. Suburban jurisdictions remain a gap. |
| Dallas–Fort Worth / Houston | [TxDOT's current reports and contract exceptions](https://www.txdot.gov/safety/traffic-signs-signals/red-light-cameras/annual-reports.html). Do not republish old installation lists as new active cameras. Existing OSM records require a jurisdiction-by-jurisdiction retirement audit; legal status alone is not used for a bulk deletion. |
| Atlanta | [Gwinnett school-zone program](https://www.gwinnettcounty.com/government/departments/police/school-zone-safety). School names and addresses are not exact camera positions. Obtain deployment geometry and current activation evidence for Gwinnett and Atlanta Public Schools. |
| Washington | [DC agency GIS](https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Public_Safety_WebMercator/MapServer/43) and [Arlington GIS](https://arlgis.arlingtonva.us/arcgis/rest/services/Open_Data/od_DES_Signal_PhotoSpeed_Cameras_pnt/FeatureServer/0). Only active speed/red-light types are ingested. DC portable/unknown-mobility speed devices remain possible deployments. Montgomery, Prince George's, Fairfax and other municipalities need additional precise reconciliation. |
| Miami | [Miami-Dade school program](https://www.miamidade.gov/global/transportation/public-works/redspeed-initiative.page), [Boynton Beach photo enforcement](https://bbpd.org/programs/photo_enforcement.php). Lists establish programs, not precise device coordinates. Do not import a commercial app's proprietary field survey. |
| Philadelphia | [PPA speed program](https://philapark.org/speed-cameras/) and [red-light program](https://philapark.org/red-light-cameras/). Public lists/reports need point-level reconciliation. The older PPA CSV has no device coordinates and is not geocoded into asserted cameras. |
| Phoenix | [City program and linked map](https://www.phoenix.gov/administration/departments/streets/safety-improvements/road-safety-action-plan/photo-safety.html). Nine published point locations are included as possible portable deployments. The page describes 17 units, including eight school-zone units rotating weekly; a nine-point map is not complete live tracking of all units. Research Scottsdale, Mesa and Chandler separately. |
| Boston | [Massachusetts traffic-law resource](https://www.mass.gov/info-details/massachusetts-law-about-traffic-violations). No verified new operating fixed speed/red-light coordinates obtained. Distinguish proposals and school-bus stop-arm cameras from this app's scope. |
| Riverside | No usable current agency coordinate feed obtained. General traffic-signal/CCTV datasets were rejected as enforcement sources. Watch the [IIHS program register](https://www.iihs.org/research-areas/red-light-running/red-light-camera-communities) for participating municipalities and review possible obsolete OSM entries. |
| San Francisco | [SFMTA current operational table](https://www.sfmta.com/projects/speed-safety-cameras) joined by site ID to the map linked from that page. The GIS service name still says “Proposed”; the current operational table is required before acceptance. Oakland and remaining MSA jurisdictions remain a gap. |
| Detroit | [Michigan agency FAQ](https://www.michigan.gov/msp/divisions/ohsp/traffic-safety-related-faqs) is blocked to the automated client. No verified new fixed coordinates obtained. Separately review changing work-zone programs; do not assume an older FAQ describes every 2026 program. |
| Seattle | [Seattle active GIS](https://catalog.data.gov/dataset/automatic-traffic-safety-cameras-atsc-active) and [Tacoma agency GIS](https://www.arcgis.com/home/item.html?id=ed8eb6a8c87643faa3ea1c6864301c05). Red-light and school speed types only. Tacoma points without a stable operational identifier remain excluded. Bellevue and other suburbs need their own sources. |
| Minneapolis | [Official pilot report index](https://lims.minneapolismn.gov/RCA/26163). The candidate-site GIS layer is not an active-camera inventory. Join actual activated sites to defensible device geometry; do not import all potential sites. |
| Tampa | [Tampa red-light program](https://www.tampa.gov/police/info/stop-on-red-tampa), [Hillsborough locations](https://hcfl.gov/government/codes-and-ordinances/red-for-a-reason/red-light-cameras). Published intersection/school lists need precise mapped-device reconciliation. |
| San Diego | [Solana Beach's official location document](https://www.cityofsolanabeach.ca.gov/sites/default/files/Solana%20Beach/Community%20Development/Code%20Compliance/SB%20RedLight%2C%20Pkg%202025%202%20sided%20ENG-SPN%20-%20O.pdf). Reconcile current Solana Beach and Del Mar approaches; do not revive older San Diego city cameras from historical lists. |
| Denver | [Current Denver program](https://www.denvergov.org/Government/Agencies-Departments-Offices/Agencies-Departments-Offices-Directory/Police-Department/Traffic-Enforcement-and-Safety/Photo-Radar-Enforcement) lists four red-light approaches and rotating vans. Its crash/citation analysis GIS is not a camera feed. Obtain current device geometry for Denver and other MSA municipalities. |
| Orlando | [City program](https://www.orlando.gov/Parking-Transportation/Red-Light-Camera-Violations) and [linked location map](https://gis.orlando.gov/PDF_Docs/TransportationMaps/RedLightCameras.pdf). A 2026 procurement/expansion proposal does not prove activation. Reconcile active Orlando, Orange, Osceola and Seminole locations with actual device points. |

## Remaining Albuquerque review

Accepted county research references: BC-01/02, BC-04, BC-07, BC-09/10, BC-11/12, BC-15/16 and BC-25/26, plus the previously accepted Golf Course NB/SB and Bridge WB points. The source register is a dated transcription; production IDs are in `Data/Overrides/metro.json`.

- BC-03, Isleta/Arenal–Montrose NB: the road curves and splits. The initial direction-constrained road walk did not resolve a reliable full warning area; keep it pending.
- BC-13/14, Dennis Chavez: official NB/SB wording conflicts with the road's east–west alignment. Do not silently manufacture a corrected direction.
- BC-17/18, Paseo near the Rio Grande: listed installation but precise hardware position and citation-start status remain unresolved.
- BC-19–24: pending approval in the source register; excluded from active warnings.
- BC-27, Shelly/Speedway: mobile site still needs a defensible road-area/point review.
- Rio Rancho's 14 mapped local-road deployment points are not an official current-location list or 14 simultaneous units. Their mapped coordinates were checked against named OSM roads; the city documents ten rotating local-road units. Keep equipment presence uncertain.
- Exact hardware points remain unverified for 20 Albuquerque city warning areas and the nine added county areas. Field testing is still needed.

## Weekly maintenance

1. **Sunday 21:00 America/Denver:** GitHub runs `Scripts/refresh_sources.py`, fetching national OSM, eight agency coordinate sources, and 26 page/document monitors. It stages source data and review reports without deploying a database. Last good sources survive errors, incomplete pagination and implausible count drops.
2. **During that GitHub Actions run:** normalize feeds, geocode supported textual locations, reconcile identities, and save source changes/ambiguities in `Data/Review/maintenance.md` and a 30-day workflow artifact. No Codex recurring job is required; the former heartbeat was deleted. Unknown source formats still need a maintainer’s review.
3. **Monday 00:00 America/Denver:** the existing publisher uses the staged inputs. If no source pass finished within 12 hours, it performs a catch-up query before publishing. GitHub queues and device downloads can be delayed. An urgent reviewed correction can still be published separately.

The Albuquerque monitor compares the camera-location list independently of ordering and site banners. Added/removed/changed entries remain pending until explicitly reviewed and acknowledged with `python3 Scripts/source_watch.py --acknowledge abq-city`. Other pages compare visible content and linked map/document URLs; PDFs compare file hashes. A changed document behind an unchanged page link needs its own document monitor when that document becomes an accepted source.

`Data/Review/source-watch.json` records source checks/failures, `agency-reconciliation.json` records overlaps/relocations, and `metro-source-changes.json` flags moved or missing OSM points behind accepted metro overrides. No data is silently declared fresh after a failed request. Bernalillo County, NYC DOT, the Michigan FAQ and the Minneapolis report index returned HTTP 403 on the final local pass (Minneapolis had a successful earlier snapshot) to the automated client and remain visible review failures.

Registry additions require a primary program source, current operational semantics, a stable identity, source-appropriate coordinate precision, and a repeatable fetch. Never treat traffic CCTV, ALPR/Flock cameras, school addresses, proposed locations, or a commercial camera map as an interchangeable feed. Review actual decommissioning evidence before adding a tombstone.

## Build 6 update

The release snapshot contains **2,681 warning records**: 29 additions and one redundant OSM warning removed since the 2,653-record expansion. Additions comprise 19 Philadelphia camera-block estimates, six Hillsborough red-light approaches, and four Chicago red-light approaches confirmed distinct by monitored direction. Nine of ten listed Hillsborough approaches have geocoded positions; three overlap unresolved existing records and are withheld, while Sligh/Habana remains unresolved after a road-query timeout. All 40 city-listed Albuquerque approaches remain represented.

Thirty-eight sources are checked: ten normalized camera feeds/lists and 28 page/document monitors. See [maintenance](MAINTENANCE.md) and [coordinate/identity rules](GEOCODING-AND-IDENTITY.md). Coverage remains incomplete.
