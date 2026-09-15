#!/usr/bin/env python3
import pathlib, shutil, json
from publish_cameras import ROOT
output=ROOT/'work/site'
output.mkdir(parents=True,exist_ok=True)
shutil.copytree(ROOT/'Site',output,dirs_exist_ok=True)
shutil.copytree(ROOT/'Data/Published',output/'data',dirs_exist_ok=True)
summary=json.loads((ROOT/'Data/Published/speed-limit-coverage.json').read_text())
page=output/'index.html'
page.write_text(page.read_text().replace('<!-- speed-limit-coverage -->',f"Current database: {summary['eligible']:,} of {summary['speedCameras']:,} speed-camera approaches have a limit or conservative bound ({summary['coveragePercent']}%). Albuquerque city: {summary['albuquerqueCity']['eligible']} of {summary['albuquerqueCity']['speedCameras']} approaches."))
(output/'.nojekyll').touch()
print(output)
