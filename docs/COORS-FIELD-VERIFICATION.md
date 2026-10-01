# Coors field verification — October 1, 2026

The project owner reported successful Albuquerque testing of the private build,
including approaching road zones and Quiet below speed limit, with no observed
issues. They confirmed the northbound and southbound speed cameras on Coors
north of I-40 and a posted **45 mph** limit at both approaches. They reported
that the existing warning locations are correct and requested no geometry change.

This update applies to the existing Coors north of St. Joseph records, city
references ABQ-37 and ABQ-38:

- `abq-coors-st-joseph-possible-nb`, travel bearing 0 degrees.
- `abq-coors-st-joseph-possible-sb`, travel bearing 180 degrees.

Both are classified as speed cameras. Their stable IDs, reviewed road polylines,
road zones and alert extents are retained. The legacy `possible` substring in
the IDs is an identity key, not the current classification. Device coordinates
were not surveyed; the labels continue to identify an approximate area.

Each record carries a dated, approach-specific `speedLimitObservation` and
`presenceVerifiedAt`. The speed-limit resolver accepts field observations through
the same evidence, conflict and 30-day expiry rules as other limits. Republishing
does not renew a field observation. Unknown speed, excessive GPS uncertainty,
expired limits and speeds inside the existing uncertainty margin still warn.

This is the owner's field report, not an independent survey or a measured battery
test. It does not establish physical acceptance for other cities or devices.
