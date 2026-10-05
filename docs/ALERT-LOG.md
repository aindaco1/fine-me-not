# On-device alert log

Build 1.0.6 (16) added **Alert log** in Settings, but its notification-tap
callback crashed during UIKit state restoration. Build 17 switches to explicit
completion callbacks that finish on the main actor, including invalid payloads.
A notification tap opens its specific entry, including after a terminated launch.
Entries show the notification time and each camera's name and type. Grouped warnings remain
one entry per notification, preserving every camera in that warning.

The app records an immediate camera notification after iOS accepts it while
visual notifications are enabled. Focus and system presentation rules can still
delay or hide the banner; acceptance is not proof the driver saw it. Denied
notifications, posting failures, Quiet-suppressed approaches and Test warning
do not create entries. Notification callbacks deduplicate by the request UUID.
The payload includes the entry snapshot so a tapped notification can recover
its details after a relaunch or later database change.

The latest 500 entries are stored in `Application Support/AlertHistory/alerts.json`,
atomically written with protection until first unlock and excluded from device
and iCloud backups. No GPS track, speed measurement, account, sync, analytics
or upload is added. The alert log is separate from the location-free support
report contract and is never added to reports. **Clear** deletes saved entries
and removes the app's delivered notifications from Notification Center.

Coors field verification is documented in [the dated source record](COORS-FIELD-VERIFICATION.md).

Build 17 uses the main screen's shared blue background, pale-blue accents,
monospaced headings and separators on both log screens. Done is available from
the detail screen as well. New entries retain the camera's speed-limit snapshot
and display its value only if eligible at the time of the alert. This is the
limit in that notification's database, not a current live sign reading. Build 16
entries and notification payloads remain readable without the optional limit.
The app does not backfill old entries from a later database.
