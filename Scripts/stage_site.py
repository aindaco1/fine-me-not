#!/usr/bin/env python3
"""Stage one published database for modern and pre-1.0.6 clients."""
import copy
import hashlib
import shutil

from camera_data import ROOT, encode, read, write


def legacy_snapshot(snapshot):
    """Older validators only accept polylines classified as possibleSpeed."""
    legacy = copy.deepcopy(snapshot)
    changed = False
    for camera in legacy['cameras']:
        if len(camera['geometry']) > 1 and camera['kind'] != 'possibleSpeed':
            assert camera['kind'] == 'speed', 'Unsupported legacy camera conversion'
            camera['kind'] = 'possibleSpeed'
            changed = True
    if changed:
        legacy['version'] += '-legacy'
    return legacy


def stage(root=ROOT):
    output = root / 'work/site'
    output.mkdir(parents=True, exist_ok=True)
    shutil.copytree(root / 'Site', output, dirs_exist_ok=True)
    published = root / 'Data/Published'
    data = output / 'data'
    # Keep all previously published immutable filenames available on both feeds.
    shutil.copytree(published, data, dirs_exist_ok=True)
    shutil.copytree(published, data / 'v2', dirs_exist_ok=True)
    for path in sorted(published.glob('cameras-*.json')):
        snapshot = read(path)
        legacy = legacy_snapshot(snapshot)
        if legacy['version'] != snapshot['version']:
            write(data / f"cameras-{legacy['version']}.json", legacy)
    legacy = legacy_snapshot(read(published / 'cameras.json'))
    filename = f"cameras-{legacy['version']}.json"
    write(data / filename, legacy)
    write(data / 'cameras.json', legacy)
    manifest = read(published / 'manifest.json')
    manifest.update(version=legacy['version'], file=filename,
                    sha256=hashlib.sha256(encode(legacy)).hexdigest())
    write(data / 'manifest.json', manifest)
    summary = read(published / 'speed-limit-coverage.json')
    summary['version'] = legacy['version']
    write(data / 'speed-limit-coverage.json', summary)
    shutil.copyfile(root / 'App/Resources/Assets.xcassets/AppIcon.appiconset/AppIcon.png', output / 'app-icon.png')
    page = output / 'index.html'
    page.write_text(page.read_text().replace('<!-- speed-limit-coverage -->', f"The current list contains {summary['totalCameras']:,} warning locations. Of the speed-camera directions in that list, {summary['eligible']:,} of {summary['speedCameras']:,} have enough limit information to use Quiet below speed limit ({summary['coveragePercent']}%). That includes {summary['albuquerqueCity']['eligible']} of {summary['albuquerqueCity']['speedCameras']} listed Albuquerque city directions. Some values are conservative estimates; this is not a count of verified speed-limit signs."))
    (output / '.nojekyll').touch()
    return output


if __name__ == '__main__':
    print(stage())
