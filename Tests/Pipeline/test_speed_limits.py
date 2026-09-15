import copy
import datetime as dt
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[2]/'Scripts'))
import speed_limits as s
from camera_data import write, UTC
NOW=dt.datetime(2026,9,15,tzinfo=UTC)
AT='2026-09-14T00:00:00Z'

def camera(**extra):
    return {'id':'osm-node-1','label':'Main Street','kind':'speed','geometry':[{'latitude':35.,'longitude':-106.}],
            'sourceIDs':['osm/node/1'],'travelBearing':0,**extra}

def road(**extra):
    return {'id':'osm/way/1','source':'osm','sourceURL':'https://example.org/road/1','names':['Main Street'],
            'geometry':[{'latitude':34.999,'longitude':-106.},{'latitude':35.001,'longitude':-106.}],
            'nodes':[],'tags':{},'limit':{'value':30,'unit':'mph'},'checkedAt':AT,**extra}

class Parsing(unittest.TestCase):
    def test_units_and_thresholds(self):
        self.assertEqual(s.numeric('50'),{'value':50.,'unit':'km/h'})
        self.assertEqual(s.numeric('35 mph')['unit'],'mph')
        for bad in ('school','signals','none','35 + 10 mph','30 knots','100 mph','nan'):self.assertIsNone(s.numeric(bad))
    def test_conditional_minimum_never_maximum(self):
        v,e=s.tag_limit({'maxspeed':'35 mph','maxspeed:conditional':'20 mph @ (Mo-Fr 07:00-16:00); 15 mph @ (flashing)'})
        self.assertIsNone(e);self.assertEqual(v['value'],15);self.assertEqual(v['basis'],'conservative-lower-bound')
    def test_unknown_conditions_and_variable_fail_closed(self):
        for tags in ({'maxspeed':'35 mph','maxspeed:conditional':'signals @ (school)'},
                     {'maxspeed':'35 mph','maxspeed:variable':'yes'}, {'maxspeed:forward':'35 mph'},
                     {'maxspeed':'35 mph','maxspeed:conditional':'20 mph @ (school); none @ (night)'}):
            self.assertIsNone(s.tag_limit(tags)[0])
    def test_opposing_and_lane_limits_take_lower(self):
        v,_=s.tag_limit({'maxspeed:forward':'40 mph','maxspeed:backward':'30 mph'})
        self.assertEqual(v['value'],30)
        self.assertEqual(s.tag_limit({'maxspeed':'40 mph','maxspeed:lanes':'40 mph|25 mph'})[0]['value'],25)
    def test_overture_scopes(self):
        base={'max_speed':{'value':35,'unit':'mph'}}
        reduced={'max_speed':{'value':20,'unit':'mph'},'when':{'heading':'forward'}}
        self.assertEqual(s.overture_limit([base,reduced])[0]['value'],20)
        self.assertIsNone(s.overture_limit([reduced])[0])
        self.assertIsNone(s.overture_limit([{**base,'between':[.2,.8]}])[0])
        self.assertIsNone(s.overture_limit([{**base,'is_max_speed_variable':True}])[0])
    def test_road_ordinals_and_address(self):
        self.assertTrue(s.same_road('1200 N Fourth Street','4th St NW'))
        self.assertEqual(s.camera_names(camera(label='E/B, Thunderbird Rd: 35th Ave to I-17')), {'thunderbird rd'})

class Matching(unittest.TestCase):
    def match(self,roads,c=None):return s.road_candidates(c or camera(),s.RoadIndex(roads),NOW)
    def test_named_aligned_road(self):
        values,_=self.match([road()]);self.assertEqual(values[0]['value'],30)
    def test_cross_street_is_not_the_monitored_road(self):
        self.assertFalse(self.match([road(names=['Other Street'])])[0])
    def test_direction_and_grade_separation(self):
        self.assertFalse(self.match([road(tags={'oneway':'-1'})])[0])
        self.assertFalse(self.match([road(tags={'bridge':'yes'})])[0])
        self.assertTrue(self.match([road(tags={'bridge':'yes'},nodes=[1])])[0])
    def test_parallel_unnamed_roads_are_ambiguous(self):
        other=road(id='osm/way/2',names=['Frontage Road'],geometry=[{'latitude':34.999,'longitude':-106.0001},{'latitude':35.001,'longitude':-106.0001}])
        self.assertFalse(self.match([road(),other],camera(label='Mapped camera'))[0])
    def test_same_named_carriageways_use_lower_bound_not_a_lane_guess(self):
        other=road(id='osm/way/2',limit={'value':25,'unit':'mph'},geometry=[{'latitude':34.999,'longitude':-106.00033},{'latitude':35.001,'longitude':-106.00033}])
        values,_=self.match([road(),other],camera(label='Mapped camera'))
        self.assertEqual(min(x['value'] for x in values),25)
        self.assertTrue(all(x['basis']=='conservative-lower-bound' for x in values))
        other['limit']=None;other['unavailableReason']='No road limit'
        self.assertFalse(self.match([road(),other],camera(label='Mapped camera'))[0])
    def test_unknown_segment_and_corridor_gaps_do_not_get_filled(self):
        unknown=road(id='osm/way/2',limit=None,unavailableReason='No road limit')
        self.assertFalse(self.match([road(),unknown])[0])
        c=camera(geometry=[{'latitude':35.,'longitude':-106.},{'latitude':35.005,'longitude':-106.}])
        self.assertFalse(self.match([road()],c)[0])
    def test_missing_attribute_on_same_other_provider_is_not_conflict(self):
        r=road(id='nyc/1',source='nyc-roads',limit=None,unavailableReason='No road limit')
        self.assertTrue(self.match([road(),r])[0])
        r['unavailableReason']='Unknown conditional limit value/unit'
        self.assertFalse(self.match([road(),r])[0])
    def test_expired_map_release(self):
        self.assertFalse(self.match([road(expiresAt='2026-09-01T00:00:00Z')])[0])

class Enrichment(unittest.TestCase):
    def run_enrich(self,c,tags,root,now=NOW,roads=None):
        docs=[{'osm3s':{'timestamp_osm_base':AT},'elements':[{'type':'node','id':1,'tags':tags}]}]
        with patch.object(s,'load_roads',return_value=roads or []):return s.enrich(root,[c],docs,now)[0][0]
    def test_obsolete_road_shards_cannot_reintroduce_a_removed_limit(self):
        with tempfile.TemporaryDirectory() as t:
            root=pathlib.Path(t)
            write(root/'Data/SpeedLimits/osm-roads-old.json',{'checkedAt':AT,'elements':[{'type':'way','id':1,'tags':{'highway':'primary','maxspeed':'40 mph'},'geometry':[{'lat':35.,'lon':-106.},{'lat':35.01,'lon':-106.}]}]})
            write(root/'Data/SpeedLimits/osm-roads-current.json',{'checkedAt':AT,'elements':[]})
            write(root/'Data/Review/speed-limit-fetch.json',{'activeOSMShards':['osm-roads-current']})
            self.assertFalse(s.load_roads(root,NOW))
    def test_source_dates_and_expiry_do_not_renew_on_publish(self):
        with tempfile.TemporaryDirectory() as t:
            root=pathlib.Path(t);c=self.run_enrich(camera(),{'maxspeed':'30 mph'},root)
            self.assertEqual(c['speedLimit']['verifiedAt'],AT);self.assertEqual(c['speedLimit']['validUntil'],'2026-10-14T00:00:00Z')
            self.assertNotIn('speedLimit',self.run_enrich(c,{'maxspeed':'30 mph'},root,NOW+dt.timedelta(days=35)))
    def test_removed_or_unparsed_camera_value_revokes_previous_limit(self):
        with tempfile.TemporaryDirectory() as t:
            root=pathlib.Path(t);c=self.run_enrich(camera(),{'maxspeed':'30 mph'},root)
            self.assertNotIn('speedLimit',self.run_enrich(copy.deepcopy(c),{},root))
            self.assertNotIn('speedLimit',self.run_enrich(c,{'maxspeed':'signals'},root,roads=[road()]))
    def test_red_and_combined_never_receive_suppression(self):
        with tempfile.TemporaryDirectory() as t:
            for kind in ('redLight','speedAndRedLight'):
                self.assertNotIn('speedLimit',self.run_enrich(camera(kind=kind,speedLimit={'value':30}),{'maxspeed':'30 mph'},pathlib.Path(t)))
    def test_conflicts_take_lower_and_do_not_change_camera_identity(self):
        with tempfile.TemporaryDirectory() as t:
            c=self.run_enrich(camera(),{'maxspeed':'25 mph'},pathlib.Path(t),roads=[road()])
            self.assertEqual(c['speedLimit']['value'],25);self.assertEqual(c['speedLimit']['basis'],'conservative-lower-bound')
            self.assertEqual(c['sourceIDs'],['osm/node/1']);self.assertIn('osm/way/1',c['speedLimitEvidenceIDs'])
    def test_agency_removed_record_cannot_reapprove_retained_candidate(self):
        with tempfile.TemporaryDirectory() as t:
            root=pathlib.Path(t);write(root/'Data/source-registry.json',{'sources':[{'id':'dc','url':'https://example.org'}]})
            write(root/'Data/External/dc.json',{'checkedAt':AT,'cameras':[]})
            c=camera(agencyID='agency-dc-1',speedLimitCandidate={'value':35,'unit':'mph','sourceID':'dc/1','conditional':False})
            self.assertNotIn('speedLimit',self.run_enrich(c,{},root))
    def test_replaced_or_moved_agency_limit_does_not_renew_retained_value(self):
        with tempfile.TemporaryDirectory() as t:
            root=pathlib.Path(t);write(root/'Data/source-registry.json',{'sources':[{'id':'dc','url':'https://example.org'}]})
            old={'value':35,'unit':'mph','sourceID':'dc/1','conditional':False}
            c=camera(agencyID='agency-dc-1',speedLimitCandidate=old)
            latest=camera(id='agency-dc-1',speedLimitCandidate={**old,'value':25})
            write(root/'Data/External/dc.json',{'checkedAt':AT,'cameras':[latest]})
            self.assertEqual(self.run_enrich(c,{},root)['speedLimit']['value'],25)
            latest.pop('speedLimitCandidate');write(root/'Data/External/dc.json',{'checkedAt':AT,'cameras':[latest]})
            self.assertNotIn('speedLimit',self.run_enrich(c,{},root))
            latest['speedLimitCandidate']=old;latest['geometry'][0]['latitude']+=1
            write(root/'Data/External/dc.json',{'checkedAt':AT,'cameras':[latest]})
            self.assertNotIn('speedLimit',self.run_enrich(c,{},root))
    def test_longest_agency_prefix_and_exact_philadelphia_address(self):
        with tempfile.TemporaryDirectory() as t:
            root=pathlib.Path(t);write(root/'Data/source-registry.json',{'sources':[{'id':'philadelphia','url':'https://example.org'},{'id':'philadelphia-addresses','url':'https://example.org'}]})
            write(root/'Data/External/philadelphia-addresses.json',{'checkedAt':AT,'cameras':[camera(id='agency-philadelphia-addresses-100-n-broad-street')]})
            write(root/'Data/SpeedLimits/philadelphia-report-limits.json',{'checkedAt':AT,'limits':[{'label':'100 N. Broad Street','value':25,'unit':'mph'},{'label':'3600 S. Broad Street','value':35,'unit':'mph'}]})
            c=camera(agencyID='agency-philadelphia-addresses-100-n-broad-street',label='100 N. Broad Street · approximate location')
            self.assertEqual(self.run_enrich(c,{},root)['speedLimit']['value'],25)
            c=camera(agencyID='agency-philadelphia-addresses-110-n-broad-street',label='110 N. Broad Street · approximate location')
            self.assertNotIn('speedLimit',self.run_enrich(c,{},root))
    def test_school_feed_cannot_use_higher_street_limit_without_policy(self):
        with tempfile.TemporaryDirectory() as t:
            root=pathlib.Path(t);write(root/'Data/source-registry.json',{'sources':[{'id':'chicago-speed','url':'https://example.org'}]})
            c=camera(agencyID='agency-chicago-speed-1')
            write(root/'Data/External/chicago-speed.json',{'checkedAt':AT,'cameras':[camera(id='agency-chicago-speed-1')]})
            self.assertNotIn('speedLimit',self.run_enrich(c,{},root,roads=[road()]))
            write(root/'Data/SpeedLimits/chicago-school-park-policy.json',{'value':20,'checkedAt':AT})
            out=self.run_enrich(c,{},root,roads=[road()]);self.assertEqual(out['speedLimit']['value'],20)
            self.assertFalse(out['speedLimit']['conditional']);self.assertEqual(out['speedLimit']['semantics'],'conservative-suppression-bound')

if __name__=='__main__':unittest.main()
