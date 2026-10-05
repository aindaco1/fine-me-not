import hashlib
import pathlib
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / 'Scripts'))
from camera_data import ROOT, read
from stage_site import stage


class DistributionFeedTests(unittest.TestCase):
    def test_both_feeds_preserve_camera_coverage_and_immutable_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            for path in ('Site', 'Data/Published', 'App/Resources/Assets.xcassets/AppIcon.appiconset'):
                shutil.copytree(ROOT / path, root / path)
            output = stage(root)
            modern = read(output / 'data/v2/cameras.json')
            legacy = read(output / 'data/cameras.json')
            self.assertEqual(modern, read(ROOT / 'Data/Published/cameras.json'))
            self.assertEqual(len(modern['cameras']), len(legacy['cameras']))
            for current, older in zip(modern['cameras'], legacy['cameras']):
                expected = dict(current)
                if len(current['geometry']) > 1 and current['kind'] == 'speed':
                    expected['kind'] = 'possibleSpeed'
                self.assertEqual(older, expected)
                self.assertTrue(len(older['geometry']) == 1 or older['kind'] == 'possibleSpeed')
            for channel in ('data', 'data/v2'):
                folder = output / channel
                manifest = read(folder / 'manifest.json')
                raw = (folder / manifest['file']).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), manifest['sha256'])
                self.assertEqual(read(folder / manifest['file']), read(folder / 'cameras.json'))
                self.assertEqual(read(folder / 'speed-limit-coverage.json')['version'], manifest['version'])
                self.assertEqual(manifest['recordCount'], len(modern['cameras']))
            immutable = {p.name: p.read_bytes() for p in (output / 'data').glob('cameras-*.json')}
            stage(root)
            for name, raw in immutable.items():
                self.assertEqual((output / 'data' / name).read_bytes(), raw)
            for p in (ROOT / 'Data/Published').glob('cameras-*.json'):
                self.assertEqual((output / 'data' / p.name).read_bytes(), p.read_bytes())


if __name__ == '__main__':
    unittest.main()
