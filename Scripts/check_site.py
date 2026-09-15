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
    for anchor in ('sources', 'privacy', 'support'):
        assert f'id="{anchor}"' in page, f'Missing {anchor} section'
    manifest = json.loads(download('data/manifest.json'))
    filename = manifest['file']
    assert re.fullmatch(r'cameras-[A-Za-z0-9-]+\.json', filename), 'Invalid snapshot path'
    raw = download('data/' + filename)
    assert hashlib.sha256(raw).hexdigest() == manifest['sha256'], 'Snapshot digest mismatch'
    database = json.loads(raw)
    assert database['version'] == manifest['version'], 'Snapshot version mismatch'
    assert len(database['cameras']) == manifest['recordCount'], 'Snapshot count mismatch'
    assert json.loads(download('data/cameras.json')) == database, 'Public database differs from manifest'
    print(f"Verified {base} with {manifest['recordCount']} cameras; version {manifest['version']}")


if __name__ == '__main__':
    try:
        check()
    except (AssertionError, OSError, ValueError, KeyError) as error:
        print(f'Website verification pending or failed: {error}', file=sys.stderr)
        sys.exit(1)
