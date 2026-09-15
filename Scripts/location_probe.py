#!/usr/bin/env python3
"""Manual diagnostic only; a control-app result is never an app acceptance result."""
import json
import pathlib
import plistlib
import shutil
import subprocess
import sys
import time
import simulator_smoke as smoke

version = sys.argv[1]
distance_filter = sys.argv[2] if len(sys.argv) > 2 else '10'
smoke.OUTPUT.mkdir(parents=True, exist_ok=True)
app = smoke.OUTPUT / 'LocationProbe.app'
app.mkdir(exist_ok=True)
bundle = 'xyz.dustwave.fine-me-not.location-probe'
info = {'CFBundleIdentifier': bundle, 'CFBundleExecutable': 'LocationProbe',
        'CFBundleName': 'LocationProbe', 'CFBundlePackageType': 'APPL',
        'CFBundleShortVersionString': '1.0', 'CFBundleVersion': '1',
        'MinimumOSVersion': '17.0', 'LSRequiresIPhoneOS': True,
        'UIDeviceFamily': [1], 'UILaunchScreen': {}, 'UIBackgroundModes': ['location'],
        'NSLocationWhenInUseUsageDescription': 'Synthetic simulator GPS diagnostic.',
        'NSLocationAlwaysAndWhenInUseUsageDescription': 'Synthetic simulator GPS diagnostic.'}
(app / 'Info.plist').write_bytes(plistlib.dumps(info))
sdk = subprocess.check_output(['xcrun', '--sdk', 'iphonesimulator', '--show-sdk-path'], text=True).strip()
subprocess.run(['xcrun', 'swiftc', '-swift-version', '5', '-parse-as-library',
                '-sdk', sdk, '-target', 'arm64-apple-ios17.0-simulator',
                'Tests/RuntimeFixtures/LocationProbe.swift', '-o', str(app / 'LocationProbe')], check=True)
runtime = next(r for r in json.loads(smoke.sim('list', 'runtimes', '-j'))['runtimes']
               if r['version'] == version and r['isAvailable'] and r['name'].startswith('iOS'))
device = smoke.sim('create', f'Location control {version}', 'com.apple.CoreSimulator.SimDeviceType.iPhone-SE-3rd-generation', runtime['identifier'])
try:
    smoke.sim('boot', device)
    smoke.sim('bootstatus', device, '-b', timeout=600)
    smoke.sim('install', device, str(app.resolve()))
    smoke.sim('privacy', device, 'grant', 'location-always', bundle)
    smoke.sim('location', device, 'set', f'{smoke.LATITUDE},{smoke.START_LONGITUDE}')
    smoke.sim('launch', device, bundle, '-distanceFilter', distance_filter)
    container = pathlib.Path(smoke.sim('get_app_container', device, bundle, 'data'))
    time.sleep(10)
    smoke.replay_route(device, 'control-route.json')
    time.sleep(10)
    fixes = container / 'Documents/fixes.json'
    if fixes.exists():
        shutil.copyfile(fixes, smoke.OUTPUT / 'control-fixes.json')
        rows = json.loads(fixes.read_text())
    else:
        rows = []
    result = {'runtime': runtime['name'], 'controlAppOnly': True, 'distanceFilter': float(distance_filter), 'fixCount': len(rows),
              'distinctLongitudes': len({r['longitude'] for r in rows})}
    (smoke.OUTPUT / 'control-result.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result))
    assert result['distinctLongitudes'] > 2, 'Control app also failed to receive moving GPS fixes'
except Exception as error:
    (smoke.OUTPUT / 'control-error.json').write_text(json.dumps({'error': str(error)}))
    raise
finally:
    try:
        subprocess.run(['xcrun', 'simctl', 'shutdown', device], timeout=30, check=False)
    except subprocess.TimeoutExpired:
        print('Control simulator shutdown timed out; runner cleanup will reclaim it.')
