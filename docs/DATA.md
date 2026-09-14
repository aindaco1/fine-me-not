# Camera data and weekly publication

The live database is a **partial, community-sourced beta**. The U.S. has no single complete open national camera feed. Warning records are not a count of physical devices. Do not interpret an empty area as camera-free.

## Inputs and licenses

- OpenStreetMap: nationwide `highway=speed_camera`, speed/red-light enforcement devices and relations, plus known red-light aliases. [ODbL 1.0](https://www.openstreetmap.org/copyright). Raw source downloads and normalization code are available in this repository. A node explicitly shared by relations keeps one stable device identity. Combined speed/red-light devices produce one warning.
- [Albuquerque current list](https://www.cabq.gov/automated-speed-enforcement): source-linked facts about current sites and monitored travel direction. A reviewed subset is matched to OSM coordinates. The full 40-approach research inventory remains in `Data/Review`.
- [Bernalillo County](https://www.bernco.gov/public-works/automated-photo-speed-enforcement/): installed sites, mobile sites and pending sites are inventoried separately. Pending installations are excluded. The original NB/SB description on Dennis Chavez conflicts with road alignment and remains a review item.
- [Rio Rancho](https://rrnm.gov/1584/STOP-Safe-Traffic-Operations-Program): mobile deployments, including three published NM 528 corridors. Published deployment areas do not imply equipment is present now.

The app code, original icon and original siren use MIT. The combined distributed camera database uses ODbL 1.0, with attribution and source facts preserved. Municipal web lists did not state a separate open-data license; this repository transcribes limited public location facts with provenance, not page text, graphics or a proprietary camera dataset. No SCDB, PhotoEnforced or Waze data is included.

## Current metro acceptance boundary

The broad review box is 34.85–35.40 N and 106.85–106.40 W; it is a review region, not a municipal boundary. Raw metro records are quarantined unless explicitly reconciled. `Data/Overrides/metro.json` is the accepted identity/geometry register. Each accepted record includes its evidence, upstream references and mapped geometry. Desk reconciliation is not a survey or road test.

The city has 19 accepted fixed-camera approaches in the first snapshot. Remaining city approaches, county sites and Rio Rancho corridors are tracked separately as geometry work proceeds. `Data/Review/publisher-report.json` provides the exact current counts and unresolved candidates. Do not describe the beta as complete Albuquerque metro coverage. Generic OSM records outside the metro are not individually corroborated against government sources.

## Reconciliation

1. Keep stable IDs for a site/approach, independent of source list order and geometry corrections. Save explicit source aliases in `replaces` when accepting a correction.
2. Give official sources authority for program type, current status and monitored travel direction. Use matched OSM device coordinates or the actual road polyline for a documented mobile corridor. Never turn a geocoded intersection or midpoint into an asserted device position.
3. OSM camera-facing `direction` is **not** the monitored vehicle bearing. National vehicle bearings are inferred only from an unambiguous enforcement relation's explicit from/to nodes. Unknown direction remains unknown.
4. Shared explicit device identity can merge evidence. Being within 100m only generates a review candidate; it never merges opposing directions, nearby parallel roads or unrelated cameras.
5. Explicit tombstones prevent stale upstream aliases from resurrecting removed records. Expired mobile records are omitted even if upstream still lists them. One missing fetch does not mean removal. Successful complete absences accumulate for review; the prior accepted value remains until a reviewed removal.
6. Failed, malformed, rollback or >25% source-count-drop responses retain the last good input. The phone verifies a SHA-256 manifest and schema before atomically replacing its offline database; it keeps a backup and bundled fallback.
7. “Possible speed camera” means an identified deployment place with uncertain current equipment presence. Unresolved location geometry is excluded instead of hidden behind that label.

The engine filters accuracy, freshness, movement, approaching direction and repeat encounters. It uses a spatial index and one geometry matcher for points and corridors. It does not perform full road/lane map matching; parallel-road false positives remain a physical-test concern.

## Publishing

`Scripts/publish_cameras.py` is the single publisher. It uses Python's standard library. `--fetch` refreshes upstream OSM inputs; without it the build is reproducible from checked-in sources and overrides. Files are normalized, validated, versioned and SHA-256 checked. Manifest filenames are immutable; `cameras.json` is the latest bundle/download alias.

The GitHub workflow starts at **Monday 00:00 America/Denver** with DST handled by the scheduler. GitHub [documents possible queue delays/dropped scheduled jobs](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule); exact-on-the-clock completion is not guaranteed. Source fetches also take time. The app registers a best-effort background refresh, checks again on activation and while receiving location fixes, and permits manual refresh. iOS will not promise a midnight download while suspended or offline.

The workflow saves reproducible inputs/results, then deploys the static website and database to GitHub Pages. It can be rerun manually. Public-repository schedules can be disabled after 60 days without activity; successful weekly publication normally creates repository activity. Check Actions failures and source freshness before asserting recurring delivery health.

## Correcting a location

Review the public source and geometry, update `Data/Overrides/metro.json`, add a tombstone for a removed identity or stale alias, run tests and publish. Keep exact evidence and direction instead of a confidence score. Use GitHub review for changes; there is no separate admin interface.
