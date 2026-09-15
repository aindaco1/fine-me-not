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
headers = subprocess.check_output(['xcrun', 'otool', '-arch', 'arm64', '-l', str(dwarf)], text=True)
segment = re.search(r'segname __TEXT\s+vmaddr (0x[0-9a-fA-F]+)', headers)
if not segment:
    raise SystemExit('No arm64 text segment in this dSYM.')
base = int(segment.group(1), 16)
if any(not isinstance(f['offset'], int) or not 0 <= f['offset'] <= 0xFFFFFFFF for f in frames):
    raise SystemExit('Invalid relative frame offset.')
addresses = [hex(base + f['offset']) for f in frames]
result = subprocess.check_output(['xcrun', 'atos', '-o', str(dwarf), '-arch', 'arm64', *addresses], text=True)
print(result, end='')
if all(re.fullmatch(r'0x[0-9a-fA-F]+', line.strip()) for line in result.splitlines()):
    raise SystemExit('No frames resolved. Check the dSYM and report offsets.')
