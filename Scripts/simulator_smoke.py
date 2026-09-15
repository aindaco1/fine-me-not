#!/usr/bin/env python3
"""Replay a public camera fixture on a NEW simulator; never use a personal device.

This checks real Core Location / audio integration while another app is in front.
Permissions are pre-granted test fixtures, not a test of Apple's prompt UI. It
does not establish locked-screen, physical audibility, Bluetooth or CarPlay results.
"""
import json
import pathlib
import plistlib
import subprocess
import sys
import time

BUNDLE = 'xyz.dustwave.fine-me-not'
OUTPUT = pathlib.Path('build/compatibility')


def sim(*args):
    return subprocess.check_output(['xcrun', 'simctl', *args], text=True, timeout=180).strip()


def main():
    version, app_path = sys.argv[1:]
    app = pathlib.Path(app_path).resolve()
    info = plistlib.loads((app / 'Info.plist').read_bytes())
    OUTPUT.mkdir(parents=True, exist_ok=True)
    runtimes = json.loads(sim('list', 'runtimes', '-j'))['runtimes']
    runtime = next(r for r in runtimes if r['version'] == version and r['isAvailable'] and r['name'].startswith('iOS'))
    device = sim('create', f'Fine Me Not compatibility {version}',
                 'com.apple.CoreSimulator.SimDeviceType.iPhone-SE-3rd-generation', runtime['identifier'])
    journal = None
    try:
        sim('boot', device)
        sim('bootstatus', device, '-b')
        sim('install', device, str(app))
        sim('privacy', device, 'grant', 'location-always', BUNDLE)
        sim('location', device, 'set', '35.05822,-106.6045')
        sim('launch', device, BUNDLE, '-warnings.enabled', 'YES')
        container = pathlib.Path(sim('get_app_container', device, BUNDLE, 'data'))
        journal = container / 'Library/Application Support/FineMeNot/Support/journal.json'

        def events():
            if not journal.exists():
                return []
            return json.loads(journal.read_text())['events']

        def wait_for(predicate, timeout=90):
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                if predicate(events()):
                    return
                time.sleep(1)
            raise AssertionError('Simulator did not reach expected state; see journal artifact')

        wait_for(lambda rows: any(r['event']['values'].get('location') == 'always' for r in rows))
        sim('launch', device, 'com.apple.mobilesafari')
        wait_for(lambda rows: any(r['event']['code'] == 'lifecycle' and r['event']['values'].get('appState') == 'background' for r in rows))
        sim('location', device, 'start', '--speed=25', '--distance=20',
            '35.05822,-106.6045', '35.05822,-106.5900')
        wait_for(lambda rows: any(r['event']['code'] == 'audio' and r['event']['values'].get('audio') == 'completed' and r['event']['values'].get('appState') == 'background' for r in rows))
        # Finish the approach and prove it does not generate a repeated siren.
        time.sleep(45)
        audio = [r for r in events() if r['event']['code'] == 'audio']
        starts = sum(r['count'] for r in audio if r['event']['values'].get('audio') == 'started')
        completions = sum(r['count'] for r in audio if r['event']['values'].get('audio') == 'completed')
        assert starts == completions == 1, audio
        assert all(r['event']['values'].get('audio') in ('started', 'completed') for r in audio), audio
        summary = {'runtime': runtime['name'], 'runtimeBuild': runtime['buildversion'],
                   'device': 'iPhone SE (3rd generation)', 'appVersion': info['CFBundleShortVersionString'],
                   'appBuild': info['CFBundleVersion'], 'minimumOS': info['MinimumOSVersion'],
                   'permissionSetup': 'simctl pre-granted Always', 'foregroundApp': 'Safari',
                   'backgroundSirenStarts': starts, 'backgroundSirenCompletions': completions,
                   'physicalDeviceTest': False}
        (OUTPUT / 'result.json').write_text(json.dumps(summary, indent=2) + '\n')
        print(json.dumps(summary, indent=2))
    finally:
        if journal and journal.exists():
            (OUTPUT / 'journal.json').write_bytes(journal.read_bytes())
        subprocess.run(['xcrun', 'simctl', 'io', device, 'screenshot', str(OUTPUT / 'screen.png')], timeout=30, check=False)
        subprocess.run(['xcrun', 'simctl', 'shutdown', device], timeout=30, check=False)


if __name__ == '__main__':
    main()
