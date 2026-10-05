import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / 'Scripts'))
from camera_data import write, read
from fetch_speed_limits import active_osm_shards


class RoadSourceRetentionTests(unittest.TestCase):
    def test_partial_replacement_keeps_previous_set_without_renewing_its_dates(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            old = root / 'Data/SpeedLimits/osm-roads-old.json'
            write(old, {'checkedAt': '2026-09-15T00:00:00Z', 'elements': []})
            write(root / 'Data/SpeedLimits/osm-roads-new-a.json',
                  {'checkedAt': '2026-09-28T00:00:00Z', 'elements': []})
            previous = {'activeOSMShards': ['osm-roads-old']}
            requested = ['osm-roads-new-a', 'osm-roads-new-b']
            self.assertEqual(active_osm_shards(root, requested, previous), ['osm-roads-old'])
            self.assertEqual(read(old)['checkedAt'], '2026-09-15T00:00:00Z')
            write(root / 'Data/SpeedLimits/osm-roads-new-b.json',
                  {'checkedAt': '2026-09-28T00:00:00Z', 'elements': []})
            self.assertEqual(active_osm_shards(root, requested, previous), requested)

    def test_first_fetch_does_not_activate_unrelated_historical_caches(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            write(root / 'Data/SpeedLimits/osm-roads-unrelated.json',
                  {'checkedAt': '2026-09-28T00:00:00Z', 'elements': []})
            self.assertEqual(active_osm_shards(root, ['osm-roads-requested'], {}), ['osm-roads-requested'])


if __name__ == '__main__':
    unittest.main()
