"""Cache free estimates for agency-listed locations, never represent them as surveyed devices.

Census handles numbered US addresses. OSM handles named intersections using shared
road nodes (not school centroids or nearest-name guesses). No driver locations leave the phone.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import json
import re
from camera_data import read, write, encode, stamp, distance

CENSUS_URL = 'https://geocoding.geo.census.gov/geocoder/locations/address'
OVERPASS_URL = 'https://overpass.private.coffee/api/interpreter'
ROAD_WORDS = {'north':'n','south':'s','east':'e','west':'w','northeast':'ne','northwest':'nw',
              'southeast':'se','southwest':'sw','street':'st','avenue':'ave','boulevard':'blvd',
              'road':'rd','drive':'dr','lane':'ln','parkway':'pkwy','highway':'hwy','place':'pl',
              'court':'ct','terrace':'ter','saint':'st'}


def road_key(value):
    words = re.findall(r'[a-z0-9]+', value.lower())
    return ' '.join(ROAD_WORDS.get(w, w) for w in words)


def cached(root, query, now, fetch):
    key = hashlib.sha256(encode(query)).hexdigest()
    path = root/f'Data/Geocoding/{key}.json'
    old = read(path)
    if old:
        at = dt.datetime.fromisoformat(old['checkedAt'].replace('Z','+00:00'))
        ttl = 1 if old.get('error') else 180
        if dt.timedelta(0) <= now-at < dt.timedelta(days=ttl):
            if old.get('error'): raise ValueError(old['error'])
            return old['result']
    try: result = fetch()
    except Exception as error:
        # A failed road lookup is shared by every approach at that intersection.
        # Keep a previous successful estimate during an upstream outage.
        if old and old.get('result'): return old['result']
        write(path, {'query':query, 'checkedAt':stamp(now), 'error':str(error)})
        raise
    write(path, {'query':query, 'checkedAt':stamp(now), 'result':result})
    return result


def address(root, street, city, state, now):
    from source_watch import json_request
    if not re.match(r'^\d+\s+\S', street): raise ValueError('Numbered street address required')
    query = {'provider':'census-address-v1','street':street,'city':city,'state':state}
    def fetch():
        data = json_request(CENSUS_URL, street=street, city=city, state=state,
                            benchmark='Public_AR_Current', format='json')
        matches = data.get('result',{}).get('addressMatches',[])
        if len(matches) != 1: raise ValueError(f'Expected one Census address match, got {len(matches)}')
        m=matches[0]; parts=m['addressComponents']
        actual=' '.join(parts.get(k,'') or '' for k in ['preQualifier','preDirection','preType','streetName','suffixType','suffixDirection','suffixQualifier'])
        expected=re.sub(r'^\d+\s+', '', street)
        if parts['state'] != state or road_key(actual) != road_key(expected):
            raise ValueError('Census changed the requested street/state; needs review')
        return {'geometry':[{'latitude':m['coordinates']['y'],'longitude':m['coordinates']['x']}],
                'positionPrecision':'census-address-estimate','matchedAddress':m['matchedAddress'],
                'roadNames':[expected], 'providerURL':CENSUS_URL,
                'evidence':'Census TIGER address-range interpolation; approximate listed block, not a camera survey.'}
    return cached(root,query,now,fetch)


def road_matches(actual, requested):
    a,b=road_key(actual),road_key(requested)
    if a==b:return True
    # Agencies often omit a compass prefix. It may be omitted only from the
    # query, and multiple disconnected matches still fail the geometry check.
    compass={'n','s','e','w','ne','nw','se','sw'}
    return a.split(' ')[0] in compass and b.split(' ')[0] not in compass and a.split(' ',1)[1]==b


def intersection_points(elements, roads):
    groups=[]
    for name in roads:
        ways=[e for e in elements if e.get('type')=='way' and road_matches(e.get('tags',{}).get('name',''), name)
              and e.get('tags',{}).get('highway') not in ('footway','cycleway','path','steps','pedestrian')]
        groups.append({node:point for way in ways for node,point in zip(way['nodes'],way['geometry'])})
    shared=set(groups[0]) & set(groups[1])
    points=[{'latitude':groups[0][n]['lat'],'longitude':groups[0][n]['lon']} for n in sorted(shared)]
    if not points: raise ValueError('No connected intersection of both named roads; needs review')
    if any(distance(a,b)>180 for a in points for b in points): raise ValueError('Multiple distant intersections; needs review')
    # A divided junction may have several shared nodes. Its center is an estimate.
    return [{'latitude':sum(p['latitude'] for p in points)/len(points),
             'longitude':sum(p['longitude'] for p in points)/len(points)}]


def intersection(root, roads, bbox, now):
    from source_watch import json_request
    if len(roads)!=2 or len(bbox)!=4: raise ValueError('Two roads and a bounded search area required')
    query={'provider':'osm-intersection-v1','roads':sorted(roads),'bbox':bbox}
    def fetch():
        # Named roads only, in the agency jurisdiction. No world-scale geocoding.
        pattern='('+'|'.join('.*'.join(re.findall(r'[A-Za-z0-9]+',r)) for r in roads)+')$'
        q='[out:json][timeout:25];way('+','.join(map(str,bbox))+')[highway][name~'+json.dumps(pattern)+'];out geom;'
        data=json_request(OVERPASS_URL,data=q)
        if data.get('remark'): raise ValueError('Incomplete road geometry response')
        elements=data.get('elements',[])
        return {'geometry':intersection_points(elements,roads), 'positionPrecision':'osm-intersection-estimate',
                'roadNames':roads, 'providerURL':OVERPASS_URL,
                'roadWayIDs':[e['id'] for e in elements],
                'evidence':'Center of connected OSM road intersection nodes; approximate enforcement intersection, not a camera survey.'}
    return cached(root,query,now,fetch)
