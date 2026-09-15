#!/usr/bin/env python3
import pathlib, shutil, json
from publish_cameras import ROOT
output=ROOT/'work/site'
output.mkdir(parents=True,exist_ok=True)
shutil.copytree(ROOT/'Site',output,dirs_exist_ok=True)
shutil.copytree(ROOT/'Data/Published',output/'data',dirs_exist_ok=True)
shutil.copyfile(ROOT/'App/Resources/Assets.xcassets/AppIcon.appiconset/AppIcon.png',output/'app-icon.png')
summary=json.loads((ROOT/'Data/Published/speed-limit-coverage.json').read_text())
page=output/'index.html'
page.write_text(page.read_text().replace('<!-- speed-limit-coverage -->',f"The current list contains {summary['totalCameras']:,} warning locations. Of the speed-camera directions in that list, {summary['eligible']:,} of {summary['speedCameras']:,} have enough limit information to use Quiet below speed limit ({summary['coveragePercent']}%). That includes {summary['albuquerqueCity']['eligible']} of {summary['albuquerqueCity']['speedCameras']} listed Albuquerque city directions. Some values are conservative estimates; this is not a count of verified speed-limit signs."))
(output/'.nojekyll').touch()
print(output)
