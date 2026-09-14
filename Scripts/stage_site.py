#!/usr/bin/env python3
import pathlib, shutil
from publish_cameras import ROOT
output=ROOT/'work/site'
output.mkdir(parents=True,exist_ok=True)
shutil.copytree(ROOT/'Site',output,dirs_exist_ok=True)
shutil.copytree(ROOT/'Data/Published',output/'data',dirs_exist_ok=True)
(output/'.nojekyll').touch()
print(output)
