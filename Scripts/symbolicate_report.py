#!/usr/bin/env python3
"""Symbolicate reviewed app-relative frames using a matching archived dSYM."""
import argparse, json, pathlib, re, subprocess
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('report', type=pathlib.Path)
p.add_argument('dsym', type=pathlib.Path)
a = p.parse_args()
report = json.loads(a.report.read_text())
crash = report.get('crash') or {}
frames = crash.get('frames', [])
if not frames:
    raise SystemExit('No app frames were included in this report.')
dwarf = a.dsym / 'Contents/Resources/DWARF/FineMeNot'
identity = subprocess.check_output(['xcrun', 'dwarfdump', '--uuid', str(dwarf)], text=True)
uuids = {s.lower() for s in re.findall(r'UUID: ([0-9A-Fa-f-]+)', identity)}
if any(f['uuid'].lower() not in uuids for f in frames):
    raise SystemExit('dSYM UUID does not match this report. Use the original build archive.')
offsets = [hex(int(f['offset'])) for f in frames]
subprocess.run(['xcrun', 'atos', '-o', str(dwarf), '-arch', 'arm64', '-l', '0', *offsets], check=True)
