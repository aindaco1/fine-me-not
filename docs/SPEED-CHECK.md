# Quiet below speed limit

Implemented for build 6, **on by default**, including upgrades with no saved choice. The setting is saved on the phone. Turning it off restores the normal speed-camera warning behavior. Test warning always plays.

The shared location matcher suppresses only speed and possible-speed warnings when all these conditions hold:

- The camera has a source-confirmed, unconditional posted limit with recognized units and unexpired evidence.
- The measured speed is valid, the GPS fix is at most 3 seconds old, and speed uncertainty is 0–2 m/s.
- Measured speed + max(uncertainty, 1 m/s) is strictly below the limit.

At or near the limit, unknown/negative speed, unavailable accuracy, stale fixes, conditional school/work-zone limits, and expired evidence keep warnings enabled. Displacement-derived speed can establish movement but cannot suppress a warning. Red-light and combined cameras always warn. Quiet approaches remain armed: accelerating before the camera can still trigger one siren. Normal encounter cooldowns are unchanged.

## Available limit data

The first approved source is the [SFMTA operational camera table](https://www.sfmta.com/projects/speed-safety-cameras), joined to its agency coordinates by camera ID. It supplies 31 accepted camera limits in this snapshot. These limits expire 30 days after the successful source fetch. A failed refresh retains the original evidence date; it cannot renew the limit.

**Albuquerque limits are not yet approved for suppression.** Its city camera list establishes locations and approaches, but not a complete current set of posted limits. The city’s public SpeedLimits ArcGIS endpoints returned empty layer lists during this release’s research. OSM numeric maxspeed tags and historical traffic studies are candidates, not automatic approval. Albuquerque sirens therefore remain enabled when driving below an unverified limit.

DC’s feed has a SPEED_LIMIT field. Conditional applicability and device mobility need review before promoting it. Arlington and Tacoma school-zone values cannot be treated as all-day limits. An approximate corridor needs a verified limit applicable throughout it; a nearby school address or adjacent street is insufficient.

## Implementation and acceptance

`SpeedCheck` owns the preference default and suppression rule. `MonitoringController` passes the existing CLLocation speedAccuracy and preference to `AlertEngine`; no second matcher, polling loop, background mode, network request, or paid service was added. The camera schema adds optional SpeedLimit metadata, preserving old snapshots. Diagnostics show the setting, measured uncertainty, limit/source/expiry, and whether an alert was quieted.

Tests cover default/migrated preferences, mph and km/h, exact/near/above limits, invalid measurements, expired and conditional limits, red-light/combined cameras, acceleration after suppression, and the off setting. The upgraded simulator showed the default on and retained an off choice after relaunch. Physical iOS 27 driving and car-audio acceptance remain separate checks; GPS uncertainty is not a guaranteed statistical bound.

Apple references: [CLLocation.speed](https://developer.apple.com/documentation/corelocation/cllocation/speed), [speedAccuracy](https://developer.apple.com/documentation/corelocation/cllocation/speedaccuracy). No public MapKit interface is assumed to supply arbitrary road speed limits.
