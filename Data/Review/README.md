# Fine Me Not — Albuquerque metro camera research

Checked September 14, 2026. These files support the implementation plan. They are **not an installable or verified camera-alert database**.

## Files and counts

- `official-location-register.csv` and `.json`: 70 research records from three official inventories. Albuquerque contributes 40 listed approaches. Bernalillo County contributes 18 installed directional records at 12 road locations, 3 mobile-site directional records, and 6 pending directional records. Rio Rancho contributes 3 published mobile deployment corridors.
- `osm-metro-candidates.csv`: 67 OSM nodes with coordinates and original tags. The broad research box is latitude 34.4–35.65, longitude -107.25–-105.85. This is not an administrative boundary or a complete coverage claim.
- `summary.json`: machine-readable counts and scope.

Counts describe source records, not unique physical cameras. Opposing directions can share a device/site, and multiple OSM records can describe one installation.

## Official sources

- [Albuquerque current locations](https://www.cabq.gov/automated-speed-enforcement)
- [Albuquerque FAQ](https://www.cabq.gov/automated-speed-enforcement/automated-speed-enforcement-frequently-asked-questions): fixed speed cameras; no current city red-light cameras.
- [Albuquerque supporting documents](https://www.cabq.gov/automated-speed-enforcement/ase-documents)
- [Bernalillo County locations](https://www.bernco.gov/public-works/automated-photo-speed-enforcement/): read successfully in a normal browser after the automated fetch returned 403.
- [Rio Rancho STOP](https://rrnm.gov/1584/STOP-Safe-Traffic-Operations-Program): rotating mobile units, not a live coordinate feed.

The Albuquerque CSV was parsed from the current numbered list. County location/direction facts were transcribed from the rendered official page and split by travel direction. Rio Rancho rows reflect the three published NM 528 corridors. Source-list order is used only for research IDs; those IDs must not become stable production IDs.

## Interpretation

Every row in the original research transcription is marked `release_ready=false`; this historical flag does not describe the current published snapshot.

Official rows deliberately leave latitude/longitude empty. None of the reviewed lists supplied validated, precise device coordinates. A geocoded street or intersection is not automatically a camera location. `date_as_listed` preserves the source date; it is not a date we independently verified in the field. For the newest Albuquerque entries the source supplies dates without explicitly repeating the word “live,” so their status is `listed_current`.

County `presumed_fixed` is an inference from its separation of installed sites and a mobile subsection; verify hardware. The Dennis Chavez source directions are NB/SB and need review against the road alignment. They were not silently rewritten. Pending sites require approval and must not enter the active alert snapshot. The Paseo/Rio Grande listing establishes installation, not its precise citation-start date.

The Louisiana/Marquette [test-certificate filename](https://www.cabq.gov/automated-speed-enforcement/documents/louisiana-near-marquette-nb-1372-test-s4f359-08-28-26.pdf) contains 1372, but page 1 identifies location code 1371 and describes Louisiana between Central and Lomas. Do not infer an official device ID from that filename.

OSM coordinates are candidates for reconciliation. Preserve original tags: camera-facing direction can differ from monitored vehicle direction. Nodes may be stale, mobile, wrongly positioned, or duplicate. The 67 nodes have not been matched one-to-one to official rows. The companion national OSM archive contains the original queries and downloads.

Published mobile sites and deployment corridors are approved for “Possible speed camera” warnings. They remain unreconciled research records: scope approval does not establish usable geometry or equipment presence. Represent corridors as road segments rather than fictitious point cameras. Other municipalities and unincorporated areas in the metro remain to be audited; an absent record does not establish an absence of cameras.

## Reuse

OSM candidate data: © OpenStreetMap contributors, available under the [Open Database License](https://www.openstreetmap.org/copyright). Preserve attribution and applicable database share-alike requirements. The application code license is separate.

Official rows are a factual research transcription with source links. No explicit open-data license for these particular municipal web lists was established in this pass. Preserve provenance and verify applicable redistribution terms before publishing a merged database. A community ArcGIS CSV was inspected as a lead, but its license metadata was blank and its last modification was in August 2025; its coordinates are not included here.

## Before use in alerts

Follow the reconciliation rules in the [implementation plan](../../docs/PLAN.md): verify fixed device/monitored-lane coordinates or mobile-site/corridor geometry and approach directions; verify current status and eligibility; resolve duplicate evidence without merging distinct approaches; assign stable IDs; preserve field evidence and review dates. Exclude unresolved records from the release snapshot. Keep last good data when a source fails or changes unexpectedly, honoring explicit removals and deployment end dates. The current acceptance policy also permits explicitly approximate fixed-site warning areas after road-geometry review; it never permits inventing device coordinates. See the current [data policy](../../docs/DATA.md).

## Implementation follow-up

These original research files remain unchanged as evidence of the initial audit. Accepted desk reconciliations now live in `../Overrides/metro.json`; current published counts and outstanding review candidates live in `publisher-report.json`. Acceptance is not field verification.

## City coverage completion

All 40 city-listed approaches now have accepted production records (19 camera points, 21 approximate areas). `albuquerque-road-areas.json` retains the road/junction evidence for the 19 additions in build 5; `coors-st-joseph-road-geometry.json` retains the earlier Coors review. The original inventory is deliberately unchanged. Each accepted city record’s `reviewReference` links to its `ABQ-xx` research row. See [the current per-approach coverage table](../../docs/ALBUQUERQUE.md). These are desk reviews; physical hardware coordinates and road-test acceptance remain separate.
