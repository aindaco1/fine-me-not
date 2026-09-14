import copy, datetime as dt, hashlib, importlib.util, json, pathlib, tempfile, unittest
spec = importlib.util.spec_from_file_location('publisher', pathlib.Path(__file__).resolve().parents[2] / 'Scripts/publish_cameras.py')
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
NOW = dt.datetime(2026, 9, 14, 7, tzinfo=dt.timezone.utc)

def node(n=1, **tags):
    return {'type':'node','id':n,'lat':40.0,'lon':-105.0,'tags':tags or {'highway':'speed_camera'}}
def document(elements):
    return {'elements':elements,'osm3s':{'timestamp_osm_base':'2026-09-14T01:00:00Z'}}
def camera():
    return next(iter(p.osm_records([document([node()])])[0].values()))

class PublisherTests(unittest.TestCase):
    def test_device_identity_survives_relation_addition_and_skeleton(self):
        relation = {'type':'relation','id':5,'tags':{'enforcement':'maxspeed'},'members':[{'type':'node','ref':1,'role':'device'}]}
        records, _ = p.osm_records([document([node()]),document([{'type':'node','id':1,'lat':40.,'lon':-105.},relation])])
        self.assertEqual(list(records), ['osm-node-1']); self.assertEqual(len(records['osm-node-1']['sourceIDs']), 2)
    def test_lens_direction_is_never_used_as_vehicle_direction(self):
        records, _ = p.osm_records([document([node(highway='speed_camera',direction='270')])])
        self.assertNotIn('travelBearing', records['osm-node-1'])
    def test_combined_device_does_not_become_two_alerts(self):
        records, _ = p.osm_records([document([node(highway='speed_camera',enforcement='traffic_signals')])])
        self.assertEqual(len(records), 1); self.assertEqual(records['osm-node-1']['kind'], 'speedAndRedLight')
    def test_close_opposite_approaches_are_not_merged(self):
        a=camera(); b={**a,'id':'other','travelBearing':180}
        records, _, issues = p.reconcile({a['id']:a,b['id']:b},{},{},{},NOW)
        self.assertEqual(len(records),2); self.assertTrue(issues)
    def test_failed_and_mass_drop_fetch_are_rejected(self):
        with self.assertRaises(ValueError): p.valid_source({'remark':'timeout','elements':[node()]})
        with self.assertRaises(ValueError): p.valid_source(document([node()]),document([node(i) for i in range(100)]))
    def test_absence_requires_review_and_tombstone_prevents_resurrection(self):
        a=camera(); old={'cameras':[a]}
        records,state,_=p.reconcile({}, {}, old, {}, NOW)
        self.assertEqual(records,[a]); self.assertEqual(state['missing'][a['id']],1)
        _,state,_=p.reconcile({}, {}, old, state, NOW,complete=False)
        self.assertEqual(state['missing'][a['id']],1)
        records,_,_=p.reconcile({a['id']:a},{'tombstones':{a['id']:'Official removal'}},old,state,NOW)
        self.assertEqual(records,[])
    def test_expired_mobile_is_removed_even_when_source_returns_it(self):
        a={**camera(),'kind':'possibleSpeed','validUntil':'2026-09-13T00:00:00Z'}
        records,_,_=p.reconcile({a['id']:a},{},{},{},NOW); self.assertEqual(records,[])
    def test_metro_requires_reviewed_geometry(self):
        a=camera()
        records,_,_=p.reconcile({a['id']:a},{'reviewBounds':[39,-106,41,-104]},{},{},NOW)
        self.assertEqual(records,[])
    def test_denver_week_boundary_handles_dst(self):
        self.assertEqual(p.week(dt.datetime.fromisoformat('2026-03-09T05:59:00+00:00')),'2026-03-02')
        self.assertEqual(p.week(dt.datetime.fromisoformat('2026-03-09T06:00:00+00:00')),'2026-03-09')
        self.assertEqual(p.week(dt.datetime.fromisoformat('2026-11-02T07:00:00+00:00')),'2026-11-02')
    def test_publication_is_immutable_and_checksum_matches(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            for name in p.QUERIES: p.write(root/f'Data/Sources/osm-us-{name}.json',document([node()]))
            first=p.publish(root,NOW); second=p.publish(root,NOW+dt.timedelta(hours=1))
            self.assertEqual(first,second)
            manifest=p.read(root/'Data/Published/manifest.json')
            raw=(root/'Data/Published'/manifest['file']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),manifest['sha256'])
            failed=p.publish(root,NOW+dt.timedelta(days=7),[{'source':'speed','status':'retained'}])
            self.assertEqual(first,failed)
            self.assertEqual(manifest,p.read(root/'Data/Published/manifest.json'))

if __name__ == '__main__': unittest.main()
