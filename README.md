# Fine Me Not

**Speed cameras ahead. Keep your cash.**

Free, open-source alerts for fixed speed cameras, red-light cameras, and published mobile-camera sites. One settings screen, one brief siren, no ads or subscriptions.

## Status

Initial implementation in progress. Target: iOS 27 and iPhone; the first physical test device is iPhone 16 Pro Max. TestFlight availability and device acceptance are tracked in `docs/RELEASE.md`. Do not interpret a successful compile as verified background or audio reliability.

## Design

Location matching happens on the phone. The app does not collect routes, require an account, or show maps. A shared weekly database refresh is scheduled for Monday 00:00 America/Denver; each phone installs updates when iOS permits execution.

See [the implementation plan](docs/PLAN.md) for behavior, reconciliation rules, and known iOS limitations.

## Licensing

Application and pipeline code: MIT. OSM-derived database: ODbL, with attribution to OpenStreetMap contributors. Other source notices stay attached to their records. Fine Me Not will remain free to use.
