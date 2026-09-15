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
    command = ['xcodebuild', '-downloadPlatform', 'iOS', '-buildVersion', version]
    # Legacy downloads have no architecture-variant field in Apple's catalog;
    # passing "universal" explicitly makes Xcode fail to find those images.
    if int(version.split('.')[0]) >= 26:
        command += ['-architectureVariant', 'arm64']
    subprocess.run(command, check=True)
