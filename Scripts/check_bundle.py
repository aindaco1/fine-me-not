#!/usr/bin/env python3
"""Validate the delivered bundle, including resources a compile cannot check."""
import json, pathlib, plistlib, sys, wave
app = pathlib.Path(sys.argv[1])
for name in ['Info.plist','FineMeNot','Assets.car','siren.wav','cameras.json','PrivacyInfo.xcprivacy']:
    assert (app/name).is_file(), f'Missing app resource: {name}'
info=plistlib.loads((app/'Info.plist').read_bytes())
assert info['CFBundleIdentifier']=='xyz.dustwave.fine-me-not'
assert set(info['UIBackgroundModes'])=={'audio','location','fetch'}
assert info['NSLocationRequireExplicitServiceSession'] is True
assert info['CFBundleIcons']['CFBundlePrimaryIcon']['CFBundleIconName']=='AppIcon'
if '--release' in sys.argv:
    assert info['MinimumOSVersion']=='27.0'
    assert info['CFBundleShortVersionString']=='0.1.0'
    assert int(info['CFBundleVersion']) >= 1
with wave.open(str(app/'siren.wav')) as sound:
    assert 1 <= sound.getnframes()/sound.getframerate() <= 2
snapshot=json.loads((app/'cameras.json').read_text())
assert len(snapshot['cameras']) > 1000
assert len({c['id'] for c in snapshot['cameras']})==len(snapshot['cameras'])
assert any(c['id'].startswith('abq-') for c in snapshot['cameras'])
print(f"Bundle verified: {len(snapshot['cameras'])} records; siren, icons, privacy, background modes; minimum iOS {info['MinimumOSVersion']}")
