#!/usr/bin/env python3
"""Replay a public camera fixture on a NEW simulator; never use a personal device.

This checks real Core Location / audio integration while another app is in front.
Permissions are pre-granted test fixtures, not a test of Apple's prompt UI. It
does not establish locked-screen, physical audibility, Bluetooth or CarPlay results.
"""
import json
import math
import pathlib
import plistlib
import subprocess
import sys
import time

BUNDLE = 'xyz.dustwave.fine-me-not'
OUTPUT = pathlib.Path('build/compatibility')
LATITUDE, START_LONGITUDE, END_LONGITUDE = 35.05822, -106.6045, -106.5900


def sim(*args):
    print('simctl ' + ' '.join(args), flush=True)
    return subprocess.check_output(['xcrun', 'simctl', *args], text=True, timeout=180).strip()


def replay_route(device, evidence_name):
    # On the hosted iOS 18.0 runtime, `location start` generated moving daemon
    # fixes without delivering them to clients, even in the foreground. Timed
    # `set` updates exercise the same real Core Location delegate and matcher.
    # Use elapsed time so slow simctl calls cannot make the car move too fast.
    meters = math.radians(END_LONGITUDE - START_LONGITUDE) * 6_371_000 * math.cos(math.radians(LATITUDE))
    duration = meters / 25
    started = time.monotonic()
    positions = []
    while True:
        elapsed = time.monotonic() - started
        fraction = min(elapsed / duration, 1)
        longitude = START_LONGITUDE + (END_LONGITUDE - START_LONGITUDE) * fraction
        sim('location', device, 'set', f'{LATITUDE:.5f},{longitude:.7f}')
        positions.append({'elapsedSeconds': round(elapsed, 3), 'latitude': LATITUDE, 'longitude': longitude})
        if fraction == 1:
            break
        time.sleep(2)
    (OUTPUT / evidence_name).write_text(json.dumps(positions, indent=2) + '\n')


def diagnose_failure(device, journal):
    """Keep the failing evidence, then probe foreground delivery; never retry to pass."""
    if not journal or not journal.exists():
        return
    (OUTPUT / 'journal.json').write_bytes(journal.read_bytes())
    command = ['xcrun', 'simctl', 'spawn', device, 'log', 'show', '--last', '5m', '--info',
               '--style', 'compact', '--predicate', 'process == "locationd" OR process == "FineMeNot"']
    with (OUTPUT / 'location-service.log').open('w') as log:
        try:
            subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=30, check=False)
        except subprocess.TimeoutExpired:
            log.write('\nLocation-service log capture timed out.\n')
    try:
        print('Diagnostic foreground probe after failure (does not change test outcome)', flush=True)
        sim('launch', device, BUNDLE)
        replay_route(device, 'foreground-probe-route.json')
        time.sleep(10)
        (OUTPUT / 'foreground-probe-journal.json').write_bytes(journal.read_bytes())
    except (OSError, subprocess.SubprocessError) as error:
        (OUTPUT / 'probe-error.txt').write_text(str(error))


def main():
    version, app_path = sys.argv[1:]
    app = pathlib.Path(app_path).resolve()
    info = plistlib.loads((app / 'Info.plist').read_bytes())
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for name in ('result.json', 'journal.json', 'location-service.log', 'foreground-probe-journal.json',
                 'probe-error.txt', 'cleanup-warning.txt', 'route.json', 'foreground-probe-route.json'):
        (OUTPUT / name).unlink(missing_ok=True)
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
        replay_route(device, 'route.json')
        wait_for(lambda rows: any(r['event']['code'] == 'audio' and r['event']['values'].get('audio') == 'completed' and r['event']['values'].get('appState') == 'background' for r in rows))
        # The route has finished; remain stationary and check for repeated sirens.
        time.sleep(10)
        audio = [r for r in events() if r['event']['code'] == 'audio']
        starts = sum(r['count'] for r in audio if r['event']['values'].get('audio') == 'started')
        completions = sum(r['count'] for r in audio if r['event']['values'].get('audio') == 'completed')
        assert starts == completions == 1, audio
        assert all(r['event']['values'].get('audio') in ('started', 'completed') for r in audio), audio
        summary = {'runtime': runtime['name'], 'runtimeBuild': runtime['buildversion'],
                   'device': 'iPhone SE (3rd generation)', 'appVersion': info['CFBundleShortVersionString'],
                   'appBuild': info['CFBundleVersion'], 'minimumOS': info['MinimumOSVersion'],
                   'permissionSetup': 'simctl pre-granted Always', 'foregroundApp': 'Safari',
                   'locationDriver': 'timed simctl positions at 25 m/s; speed inferred from displacement',
                   'backgroundSirenStarts': starts, 'backgroundSirenCompletions': completions,
                   'physicalDeviceTest': False}
        (OUTPUT / 'result.json').write_text(json.dumps(summary, indent=2) + '\n')
        print(json.dumps(summary, indent=2))
    except Exception:
        diagnose_failure(device, journal)
        raise
    finally:
        if journal and journal.exists() and not (OUTPUT / 'journal.json').exists():
            (OUTPUT / 'journal.json').write_bytes(journal.read_bytes())
        # Hosted runners may have no display surface; screenshots can hang even
        # after a successful playback test. The journal and result are evidence.
        try:
            subprocess.run(['xcrun', 'simctl', 'shutdown', device], timeout=30, check=False)
        except subprocess.TimeoutExpired:
            (OUTPUT / 'cleanup-warning.txt').write_text('Simulator shutdown timed out; hosted runner cleanup will reclaim it.\n')


if __name__ == '__main__':
    main()
