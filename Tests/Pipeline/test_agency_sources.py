import copy
import datetime as dt
import json
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]/'Scripts'))
import source_watch as w
import agency_cameras as a
from camera_data import read, write

NOW = dt.datetime(2026, 9, 14, tzinfo=dt.timezone.utc)
SOURCE = {'id': 'sf', 'name': 'Agency', 'adapter': 'sf', 'url': 'https://agency.test/feed', 'page': 'https://agency.test/page', 'metro': '41860', 'minimumRows': 1, 'license': 'Public facts'}


def camera(key='agency-sf-1', bearing=90, lat=37.7, lon=-122.4):
    return {'id': key, 'siteID': key, 'label': 'Test road', 'kind': 'speed', 'geometry': [{'latitude': lat, 'longitude': lon}], 'sourceIDs': ['test/'+key], 'evidence': 'Agency test source', 'travelBearing': bearing}


class SourceChecks(unittest.TestCase):
    def test_city_semantic_monitor_ignores_order_and_site_chrome(self):
        source = {'adapter':'abq-list', 'requiredText':'Camera locations'}
        items = [f'Road {i} (northbound)' for i in range(20)]
        def page(items, chrome=''):
            return ('<nav>'+chrome+'</nav><h2>Camera locations</h2><ol>'+''.join('<li>'+i+'</li>' for i in items)+'</ol>').encode()
        first = w.watch_value(source, page(items))
        self.assertEqual(first, w.watch_value(source, page(list(reversed(items)), 'new banner')))
        self.assertNotEqual(first['contentHash'], w.watch_value(source, page(items+['New road (southbound)']))['contentHash'])
        with self.assertRaises(ValueError): w.watch_value(source, page(items[:2]))

    def test_changed_page_stays_pending_and_failed_fetch_keeps_last_good(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp); source = {'id':'test', 'name':'City', 'adapter':'page', 'url':'https://city.test/', 'requiredText':'camera', 'monitorOnly':True}
            with patch.object(w, 'request', return_value=b'<p>camera '+b'a'*150+b'</p>'): w.fetch_one(source, root, NOW)
            with patch.object(w, 'request', return_value=b'<p>camera '+b'b'*150+b'</p>'):
                self.assertTrue(w.fetch_one(source, root, NOW)['reviewRequired'])
                self.assertTrue(w.fetch_one(source, root, NOW+dt.timedelta(days=1))['reviewRequired'])
            path=root/'Data/Watch/test.json'; prior=path.read_bytes()
            with patch.object(w, 'request', side_effect=TimeoutError('timeout')):
                result=w.fetch_one(source, root, NOW+dt.timedelta(days=2))
            self.assertEqual(result['status'],'failed'); self.assertEqual(path.read_bytes(),prior)

    def test_arcgis_partial_page_fails(self):
        with patch.object(w, 'json_request', side_effect=[{'objectIds':[1,2]}, {'features':[{}], 'exceededTransferLimit':True}]):
            with self.assertRaises(ValueError): w.arcgis_rows('https://agency.test/feed')

    def test_large_active_drop_cannot_replace_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp); path=root/'Data/External/sf.json'
            write(path, {'rowCount':4, 'cameras':[camera(str(i)) for i in range(4)], 'checkedAt':'2026-09-13T00:00:00Z'})
            prior=path.read_bytes()
            with patch.object(w,'arcgis_rows',return_value=[{}]*4), patch.object(w,'request',return_value=b''), patch.object(w,'parse_page') as page:
                page.return_value.rows=[[str(i),'Road','25','Issuing Violations'] for i in range(4)]
                with patch.object(w,'normalize',return_value=([camera()],[])): result=w.fetch_one(SOURCE,root,NOW)
            self.assertEqual(result['status'],'failed');self.assertEqual(path.read_bytes(),prior)

    def test_direction_and_unknown_limits_remain_unknown(self):
        self.assertEqual(w.direction('N/B road'),0);self.assertEqual(w.direction('Southbound'),180)
        self.assertIsNone(w.direction('NB / SB'));self.assertIsNone(w.direction('forward'))
        c=w.make_camera(SOURCE,'1','School','speed',37.7,-122.4,limit='30 MPH / 20 MPH during school hours',conditional=True)
        self.assertNotIn('speedLimitCandidate',c)
        c=w.make_camera(SOURCE,'1','School','speed',37.7,-122.4,limit=20,conditional=True)
        self.assertTrue(c['speedLimitCandidate']['conditional']);self.assertFalse(c['speedLimitCandidate']['suppressionApproved'])

    def test_census_boundary_holes_and_other_metros(self):
        g={'type':'Polygon','coordinates':[[[0,0],[4,0],[4,4],[0,4],[0,0]],[[1,1],[2,1],[2,2],[1,2],[1,1]]]}
        self.assertTrue(w.inside_geometry({'latitude':3,'longitude':3},g))
        self.assertFalse(w.inside_geometry({'latitude':1.5,'longitude':1.5},g))
        self.assertFalse(w.inside_geometry({'latitude':5,'longitude':3},g))

    def test_kml_blank_placeholders_not_invented_as_points(self):
        raw=b'<kml xmlns="http://www.opengis.net/kml/2.2"><Document><Placemark><name>Camera</name></Placemark><Placemark><description>W/B road</description><Point><coordinates>-112,33,0</coordinates></Point></Placemark></Document></kml>'
        rows=w.kml_rows(raw);self.assertEqual(len(rows),1);self.assertEqual(rows[0]['longitude'],-112)


class Reconciliation(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup);self.root=pathlib.Path(self.tmp.name)
        write(self.root/'Data/source-registry.json',{'sources':[SOURCE]})

    def cache(self, cameras):
        write(self.root/'Data/External/sf.json',{'cameras':cameras,'checkedAt':'2026-09-14T00:00:00Z'})

    def test_nearby_existing_queues_without_merging(self):
        old=camera('osm-node-1'); self.cache([camera()])
        records,_,review,_=a.combine(self.root,{old['id']:old},{'cameras':[old]},NOW)
        self.assertEqual(list(records),[old['id']]);self.assertEqual(len(review),1)

    def test_distinct_agency_approaches_remain_distinct(self):
        self.cache([camera(),camera('agency-sf-2',180)])
        records,_,review,_=a.combine(self.root,{}, {},NOW)
        self.assertEqual(len(records),2);self.assertFalse(review)

    def test_reviewed_alias_preserves_identity_and_mapped_position(self):
        old=camera('osm-node-1'); incoming=camera(lat=37.7001);incoming['kind']='redLight';self.cache([incoming])
        write(self.root/'Data/Overrides/agency-aliases.json',{'decisions':{incoming['id']:{'targetID':old['id'],'preservePosition':True,'evidence':'Same named street and monitored approach'}}})
        records,_,review,replaced=a.combine(self.root,{old['id']:old},{'cameras':[old]},NOW)
        self.assertEqual(len(records),1);self.assertFalse(review);self.assertIn(incoming['id'],replaced)
        self.assertEqual(records[old['id']]['geometry'],old['geometry']);self.assertEqual(records[old['id']]['kind'],'redLight')

    def test_major_relocation_keeps_previous_position_for_review(self):
        old=camera();self.cache([camera(lat=37.71)])
        records,_,review,_=a.combine(self.root,{}, {'cameras':[old]},NOW)
        self.assertNotIn(old['id'],records);self.assertIn('Moved',review[0]['reason'])
        # The existing publisher retention seam retains the old camera.
        import publish_cameras as p
        result,_,_=p.reconcile(records,{}, {'cameras':[old]}, {},NOW)
        self.assertEqual(result,[old])

    def test_changed_source_id_near_missing_old_is_reviewed(self):
        old=camera();self.cache([camera('agency-sf-new')])
        _,_,review,_=a.combine(self.root,{}, {'cameras':[old]},NOW)
        self.assertEqual(len(review),1)

    def test_future_osm_overlap_also_queues(self):
        old=camera();old['agencyID']=old['id'];self.cache([old]);osm=camera('osm-node-new')
        records,_,review,_=a.combine(self.root,{osm['id']:osm},{'cameras':[old]},NOW)
        self.assertNotIn(osm['id'],records);self.assertTrue(review)

    def test_county_areas_and_metro_points_have_geometry_evidence(self):
        root=pathlib.Path(__file__).resolve().parents[2]
        accepted={c['id']:c for c in read(root/'Data/Overrides/metro.json')['cameras']}
        evidence=read(root/'Data/Review/metro-point-reconciliation.json')
        for item in evidence['points']:
            c=accepted[item['acceptedID']];n=item['node']
            self.assertEqual(c['geometry'],[{'latitude':n['lat'],'longitude':n['lon']}])
            if c['id'].startswith('rr-'):self.assertEqual(c['kind'],'possibleSpeed')
        areas=read(root/'Data/Review/county-road-areas.json');nodes={e['id']:e for e in areas['elements'] if e['type']=='node'}
        ways={e['id']:e for e in areas['elements'] if e['type']=='way'}
        for item in areas['areas']:
            c=accepted[item['id']];self.assertEqual(c['geometry'],item['geometry'])
            edges={(a,b) for wid in item['wayIDs'] for a,b in zip(ways[wid]['nodes'],ways[wid]['nodes'][1:])}
            xy={(n['lat'],n['lon']):i for i,n in nodes.items()}
            route=[xy[(p['latitude'],p['longitude'])] for p in c['geometry']]
            for pair in zip(route,route[1:]):self.assertTrue(pair in edges or pair[::-1] in edges)

class StagedRefresh(unittest.TestCase):
    def test_fresh_staged_pass_is_reused_but_old_or_future_pass_is_not(self):
        import refresh_sources as r
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            write(root/'Data/Review/prepublication-check.json', {'completedAt':'2026-09-13T23:00:00Z'})
            with patch.object(r,'fetch_sources',side_effect=RuntimeError('new pass needed')) as fetch:
                r.run(root,NOW,if_stale=True);fetch.assert_not_called()
                with self.assertRaises(RuntimeError):r.run(root,NOW+dt.timedelta(days=1),if_stale=True)
                with self.assertRaises(RuntimeError):r.run(root,NOW-dt.timedelta(days=1),if_stale=True)

    def test_sunday_source_pass_precedes_monday_release_in_both_offsets(self):
        from zoneinfo import ZoneInfo
        denver=ZoneInfo('America/Denver')
        for day in (dt.datetime(2026,3,8,21,tzinfo=denver),dt.datetime(2026,11,1,21,tzinfo=denver)):
            release=day+dt.timedelta(hours=3)
            self.assertEqual(day.weekday(),6);self.assertEqual(release.weekday(),0)
            self.assertEqual(release.astimezone(dt.timezone.utc)-day.astimezone(dt.timezone.utc),dt.timedelta(hours=3))


if __name__ == '__main__': unittest.main()
