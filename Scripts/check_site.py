#!/usr/bin/env python3
"""Verify the canonical HTTPS website and the exact database the app downloads."""
import hashlib
import json
import re
import sys
import urllib.parse
import urllib.request

from camera_data import ROOT


def check():
    source = (ROOT / 'Site/index.html').read_text()
    base = re.search(r'<link rel="canonical" href="([^"]+)">', source)[1]
    origin = urllib.parse.urlsplit(base)
    assert origin.scheme == 'https', 'Canonical URL must use HTTPS'

    def download(path):
        request = urllib.request.Request(urllib.parse.urljoin(base, path),
            headers={'User-Agent': 'FineMeNot-site-check/1.0'})
        with urllib.request.urlopen(request, timeout=15) as response:
            final = urllib.parse.urlsplit(response.url)
            assert final.scheme == 'https' and final.netloc == origin.netloc, 'Unexpected redirect'
            raw = response.read(20_000_001)
            assert len(raw) <= 20_000_000, 'Response too large'
            return raw

    page = download('').decode('utf-8')
    assert f'<link rel="canonical" href="{base}">' in page, 'Wrong canonical website'
    for anchor in ('features', 'setup', 'compatibility', 'sources', 'privacy', 'support', 'legal'):
        assert f'id="{anchor}"' in page, f'Missing {anchor} section'
    assert 'Built and maintained by <strong>Alonso Indacochea</strong>' in page, 'Wrong maintainer credit'
    assert 'Volver Health LLC' not in page, 'Obsolete website maintainer credit'
    icon = download('app-icon.png')
    expected_icon = ROOT / 'App/Resources/Assets.xcassets/AppIcon.appiconset/AppIcon.png'
    assert icon == expected_icon.read_bytes(), 'Website icon differs from the app icon'
    manifest = json.loads(download('data/manifest.json'))
    filename = manifest['file']
    assert re.fullmatch(r'cameras-[A-Za-z0-9-]+\.json', filename), 'Invalid snapshot path'
    raw = download('data/' + filename)
    assert hashlib.sha256(raw).hexdigest() == manifest['sha256'], 'Snapshot digest mismatch'
    database = json.loads(raw)
    assert database['version'] == manifest['version'], 'Snapshot version mismatch'
    assert len(database['cameras']) == manifest['recordCount'], 'Snapshot count mismatch'
    assert json.loads(download('data/cameras.json')) == database, 'Public database differs from manifest'
    summary = json.loads(download('data/speed-limit-coverage.json'))
    speed = [c for c in database['cameras'] if c['kind'] in ('speed', 'possibleSpeed')]
    approved = [c for c in database['cameras'] if c.get('speedLimit')]
    assert all(c['kind'] in ('speed', 'possibleSpeed') for c in approved), 'Red-light suppression found'
    assert summary['version'] == manifest['version'], 'Coverage report version mismatch'
    assert summary['totalCameras'] == len(database['cameras']), 'Coverage total mismatch'
    assert summary['speedCameras'] == len(speed) and summary['eligible'] == len(approved), 'Suppression count mismatch'
    assert f"{len(approved):,} of {len(speed):,}" in page, 'Website coverage differs from database'
    print(f"Verified {base} with {manifest['recordCount']} cameras and {len(approved)}/{len(speed)} suppression limits; version {manifest['version']}")


if __name__ == '__main__':
    try:
        check()
    except (AssertionError, OSError, ValueError, KeyError) as error:
        print(f'Website verification pending or failed: {error}', file=sys.stderr)
        sys.exit(1)
