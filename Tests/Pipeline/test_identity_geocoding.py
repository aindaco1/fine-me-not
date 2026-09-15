import copy
import datetime as dt
import pathlib
import tempfile
import unittest
from unittest.mock import patch
import sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[2]/'Scripts'))
from camera_identity import match, distinct, automatic_rules, collapse_equivalent_osm
from geocode_locations import intersection_points, address
from text_camera_sources import rows
from test_agency_sources import camera, SOURCE, NOW


class Identity(unittest.TestCase):
    def pair(self):
        a=camera('osm-node-1');a['locationKey']='1200 North Main Street';a['roadNames']=['North Main Street']
        b=camera('agency-test-1',lat=37.7001);b['locationKey']='1200 N. Main St';b['roadNames']=['N Main St']
        return a,b
    def test_matching_location_and_approach_merges_but_radius_alone_does_not(self):
        a,b=self.pair();self.assertTrue(match(a,b));b.pop('locationKey');b.pop('roadNames');self.assertIsNone(match(a,b))
    def test_opposing_parallel_and_different_enforcement_remain_distinct(self):
        a,b=self.pair();b['travelBearing']=270;self.assertTrue(distinct(a,b));self.assertIsNone(match(a,b))
        b['travelBearing']=90;b['roadNames']=['Other Road'];self.assertTrue(distinct(a,b));self.assertIsNone(match(a,b))
        a,b=self.pair();b['kind']='redLight';self.assertIsNone(match(a,b))
    def test_multiple_close_candidates_are_not_guessed(self):
        a,b=self.pair();other=copy.deepcopy(a);other['id']='osm-node-2'
        self.assertFalse(automatic_rules([b],{a['id']:a,other['id']:other}))
        b2=copy.deepcopy(b);b2['id']='agency-test-2'
        self.assertFalse(automatic_rules([b,b2],{a['id']:a}))
    def test_exact_osm_warning_equivalents_keep_old_id_and_provenance(self):
        a=camera('osm-node-a');b=camera('osm-node-b')
        records,replaced,_=collapse_equivalent_osm({a['id']:a,b['id']:b},{'cameras':[b]})
        self.assertEqual(list(records),[b['id']]);self.assertEqual(replaced,{a['id']})
        self.assertEqual(len(records[b['id']]['sourceIDs']),2)
    def test_different_numbered_intersections_need_more_than_same_road(self):
        a,b=self.pair();b['geometry'][0]['latitude']+=.0004;b['locationKey']='1500 N Main St'
        self.assertIsNone(match(a,b))

class Geocoding(unittest.TestCase):
    def way(self,key,name,nodes,coords):
        return {'id':key,'type':'way','tags':{'highway':'primary','name':name},'nodes':nodes,'geometry':[{'lat':a,'lon':b} for a,b in coords]}
    def test_intersection_requires_connected_named_roads(self):
        ways=[self.way(1,'Main Street',[1,2],[(35,-106),(35.001,-106)]),self.way(2,'First Avenue',[2,3],[(35.001,-106),(35.001,-105.999)])]
        self.assertEqual(intersection_points(ways,['Main Street','First Avenue']),[{'latitude':35.001,'longitude':-106}])
        ways[1]['nodes']=[4,3] # Grade-separated crossing with identical coordinates.
        with self.assertRaises(ValueError):intersection_points(ways,['Main Street','First Avenue'])
    def test_census_match_cached_and_wrong_state_rejected(self):
        match={'coordinates':{'x':-75.16,'y':39.95},'matchedAddress':'100 N BROAD ST, PHILADELPHIA, PA',
               'addressComponents':{'state':'PA','preDirection':'N','streetName':'BROAD','suffixType':'ST'}}
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            with patch('source_watch.json_request',return_value={'result':{'addressMatches':[match]}}) as fetch:
                result=address(root,'100 N Broad Street','Philadelphia','PA',NOW)
                self.assertEqual(result['positionPrecision'],'census-address-estimate')
                self.assertEqual(result,address(root,'100 N Broad Street','Philadelphia','PA',NOW+dt.timedelta(days=7)))
                self.assertEqual(fetch.call_count,1)
                with self.assertRaises(ValueError):address(root,'100 N Broad Street','Philadelphia','NJ',NOW)
                with self.assertRaises(ValueError):address(root,'School name','Philadelphia','PA',NOW)
    def test_source_parser_preserves_future_dates_and_does_not_geocode_schools(self):
        groups=['100 N Broad Street','F Street','School: Main St (First to Second)','6000 Baltimore Ave (Live Enforcement Begins 10-30-26)']
        html=''.join('Speed Camera Locations:<ul><li>'+s+'</li></ul>' for s in groups).encode()
        result=rows({'id':'philadelphia-addresses'},html)
        self.assertEqual(result[3]['live'],'2026-10-30');self.assertTrue(result[2]['unsupported'])
        with self.assertRaises(ValueError):rows({'id':'philadelphia-addresses'},b'<p>temporarily unavailable</p>')

if __name__=='__main__':unittest.main()

class Retention(unittest.TestCase):
    def test_geocoder_outage_keeps_original_success_date(self):
        from geocode_locations import cached
        from camera_data import read
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp);query={'provider':'test','location':'public agency location'}
            first=cached(root,query,NOW,lambda:{'geometry':[]})
            path=next((root/'Data/Geocoding').glob('*.json'));original=path.read_bytes()
            def fail():raise TimeoutError('offline')
            self.assertEqual(first,cached(root,query,NOW+dt.timedelta(days=200),fail))
            self.assertEqual(path.read_bytes(),original)
    def test_failed_lookup_is_shared_by_multiple_approaches(self):
        from geocode_locations import cached
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            with patch('builtins.input',side_effect=TimeoutError('offline')) as lookup:
                for _ in range(3):
                    with self.assertRaises((TimeoutError,ValueError)):cached(root,{'test':'junction'},NOW,lookup)
                self.assertEqual(lookup.call_count,1)
    def test_agency_combiner_leaves_limit_approval_to_shared_resolver(self):
        from camera_data import write
        from agency_cameras import combine
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            write(root/'Data/source-registry.json',{'sources':[SOURCE]})
            c=camera();c['speedLimitCandidate']={'value':25,'unit':'mph','sourceID':c['sourceIDs'][0],'conditional':False}
            write(root/'Data/External/sf.json',{'cameras':[c],'checkedAt':'2026-09-01T00:00:00Z'})
            result,_,_,_=combine(root,{}, {},NOW)
            self.assertNotIn('speedLimit',result[c['id']])
            self.assertEqual(result[c['id']]['speedLimitCandidate'],c['speedLimitCandidate'])
