#!/usr/bin/env python3
"""Reuse an available runtime or download its official Apple architecture variant."""
import json
import subprocess
import sys

version = sys.argv[1]
runtimes = json.loads(subprocess.check_output(['xcrun', 'simctl', 'list', 'runtimes', '-j'], text=True))['runtimes']
if any(r['name'].startswith('iOS') and r['version'] == version and r['isAvailable'] for r in runtimes):
    print(f'Using installed iOS {version}')
else:
    # Apple distributes newer runtimes by architecture; older versions use a
    # universal image. Do not remove a working runtime just to download it again.
    variant = 'arm64' if int(version.split('.')[0]) >= 26 else 'universal'
    subprocess.run(['xcodebuild', '-downloadPlatform', 'iOS', '-buildVersion', version,
                    '-architectureVariant', variant], check=True)
