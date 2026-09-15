"""Evidence-based camera identity. Distance is a gate, never the sole match signal."""
from __future__ import annotations
import re
from camera_data import distance
from geocode_locations import road_key


def angle(a,b): return abs((a-b+180)%360-180)


def location_key(c):
    value=c.get('locationKey')
    return road_key(value) if value else None


def road_names(c):
    return {road_key(s) for s in c.get('roadNames',[]) if s}


def same_approach(a,b):
    x,y=a.get('travelBearing'),b.get('travelBearing')
    return x is not None and y is not None and angle(x,y)<=25


def distinct(a,b):
    x,y=a.get('travelBearing'),b.get('travelBearing')
    # Preserve opposing approaches even at the same agency-published coordinate.
    if x is not None and y is not None and angle(x,y)>100:return 'Opposing monitored approaches'
    # Explicit single monitored-road names are stronger than a proximity match.
    ra,rb=road_names(a),road_names(b)
    if len(ra)==len(rb)==1 and ra.isdisjoint(rb):return 'Different named roads'
    return None


def match(a,b):
    if a['id']==b['id']:return 'Same stable identity'
    if len(a['geometry'])!=1 or len(b['geometry'])!=1 or distinct(a,b):return None
    d=distance(a['geometry'][0],b['geometry'][0])
    if d>75:return None
    # Never erase a red-light function based on a speed-only report.
    if a['kind']!=b['kind']:return None
    shared=set(a.get('sourceIDs',[])) & set(b.get('sourceIDs',[]))
    if any(s.startswith(('osm/node/', 'agency/')) for s in shared):
        return 'Same source device identity'
    if same_approach(a,b):
        if location_key(a) and location_key(a)==location_key(b) and d<=60:return 'Same listed location and monitored approach'
        if road_names(a) & road_names(b) and d<=30:return 'Same named road and monitored approach within 30 m'
    # Equivalent undirected OSM points are redundant warning records, including
    # separately tagged nodes at the identical mapped signal/device coordinate.
    if a['id'].startswith('osm-') and b['id'].startswith('osm-') and d<1 and a.get('travelBearing')==b.get('travelBearing'):
        if a['label']==b['label']:return 'Coincident OSM points with identical warning semantics'
    return None


def automatic_rules(incoming, reference):
    """Only mutually unique cross-source matches can acquire an existing identity."""
    possibilities={}
    for c in incoming:
        if c['id'] in reference:continue
        choices=[(r['id'],why) for r in reference.values() if (why:=match(c,r))]
        if len(choices)==1:possibilities[c['id']]=choices[0]
    counts={target:sum(t==target for t,_ in possibilities.values()) for target,_ in possibilities.values()}
    return {key:{'targetID':target,'preservePosition':True,'evidence':why}
            for key,(target,why) in possibilities.items() if counts[target]==1}


def collapse_equivalent_osm(records, previous):
    records=dict(records); changes=[]; replaced=set()
    old={c['id'] for c in previous.get('cameras',[])}
    keys=sorted(records, key=lambda k:(k not in old,k))
    # Grid bounds the comparisons without requiring a new runtime dependency.
    cells={}
    for key in keys:
        c=records[key]
        if not key.startswith('osm-'):continue
        p=c['geometry'][0];cell=(round(p['latitude']*10000),round(p['longitude']*10000))
        nearby=[k for dx in (-1,0,1) for dy in (-1,0,1) for k in cells.get((cell[0]+dx,cell[1]+dy),[])]
        matches=[(k,why) for k in nearby if (why:=match(c,records[k]))]
        if len(matches)==1:
            target,why=matches[0];kept=records[target]
            kept['sourceIDs']=sorted(set(kept['sourceIDs']+c['sourceIDs']))
            records.pop(key);replaced.add(key)
            changes.append({'id':key,'targetID':target,'reason':why})
        else:cells.setdefault(cell,[]).append(key)
    return records,replaced,changes
