#!/usr/bin/env python3
"""Resume bounded regional extracts from Overture's public monthly release.

Each successful region is committed independently. A slow region cannot discard
other regions' successful work. No driver coordinates or credentials are used.
"""
import collections
import datetime as dt
import hashlib
import json
import math
import re
import threading
import time
import xml.etree.ElementTree as ET
from camera_data import ROOT, UTC, read, write, stamp, encode
from fetch_speed_limits import get, samples

URL='https://docs.overturemaps.org/guides/transportation/roads/'


def refresh(root=ROOT, timeout=75, budget=900):
    now=dt.datetime.now(UTC);started=time.monotonic();folder=root/'Data/SpeedLimits/Overture'
    index_path=root/'Data/SpeedLimits/overture-roads.json';old=read(index_path,{})
    report={'checkedAt':stamp(now),'source':'overture','regions':[]}
    try:
        import duckdb
        data=ET.fromstring(get('https://overturemaps-us-west-2.s3.us-west-2.amazonaws.com/',
            {'list-type':'2','prefix':'release/','delimiter':'/'}))
        ns={'s':'http://s3.amazonaws.com/doc/2006-03-01/'}
        if data.findtext('s:IsTruncated',namespaces=ns)!='false':raise ValueError('Truncated release listing')
        releases=[x.text.split('/')[1] for x in data.findall('s:CommonPrefixes/s:Prefix',ns)]
        release=max(x for x in releases if re.fullmatch(r'\d{4}-\d{2}-\d{2}\.\d+',x) and x[:10]<=now.date().isoformat())
        cameras=read(root/'Data/Published/cameras.json')['cameras'];groups=collections.defaultdict(set)
        for c in cameras:
            if c['kind'] not in ('speed','possibleSpeed'):continue
            for p in samples(c['geometry']):
                lat,lon=round(p['latitude'],6),round(p['longitude'],6)
                groups[(math.floor(lat*2),math.floor(lon*2))].add((lat,lon))
        # Albuquerque first, then denser regions. Cache reuse makes progress resume.
        groups=sorted(groups.items(),key=lambda x:(not(x[0][0] in (69,70,71) and x[0][1] in (-214,-213)), -len(x[1]),x[0]))
        con=duckdb.connect();con.execute("INSTALL httpfs; LOAD httpfs; INSTALL spatial; LOAD spatial; SET s3_region='us-west-2'; SET threads=2; SET memory_limit='512MB'; SET max_temp_directory_size='512MB'; SET temp_directory='work/overture-temp'; SET http_timeout=25;")
        paths=[];total=0
        try:
            for tile,points in groups:
                ps=sorted(points);key=hashlib.sha256(encode(ps)).hexdigest()[:16];path=folder/(key+'.json');prior=read(path,{})
                status={'id':key,'tile':tile,'queryPoints':len(ps)}
                if prior.get('release')==release:
                    status.update(status='cached',records=prior['recordCount'])
                elif time.monotonic()-started>=budget:
                    status.update(status='deferred',error='Regional acquisition budget reached')
                else:
                    timer=threading.Timer(timeout,con.interrupt);timer.daemon=True;timer.start()
                    try:
                        west=min(lon for lat,lon in ps)-.002;east=max(lon for lat,lon in ps)+.002
                        south=min(lat for lat,lon in ps)-.002;north=max(lat for lat,lon in ps)+.002
                        multipoint='MULTIPOINT ('+','.join(f'{lon} {lat}' for lat,lon in ps)+')'
                        query=f"""SELECT id,names.primary,class,ST_AsGeoJSON(geometry),
                            to_json(speed_limits),to_json(sources),to_json(road_flags),to_json(level_rules)
                            FROM read_parquet('s3://overturemaps-us-west-2/release/{release}/theme=transportation/type=segment/*',hive_partitioning=1)
                            WHERE subtype='road' AND bbox.xmin<{east} AND bbox.xmax>{west}
                            AND bbox.ymin<{north} AND bbox.ymax>{south}
                            AND class IN ('motorway','trunk','primary','secondary','tertiary','unclassified','residential','motorway_link','trunk_link','primary_link','secondary_link','tertiary_link')
                            AND ST_DWithin(geometry,ST_GeomFromText('{multipoint}'),.002)
                            LIMIT 100001"""
                        rows=con.execute(query).fetchall()
                        if len(rows)>100000:raise ValueError('Region exceeded road bound')
                        records=[dict(zip(('id','name','class','geometry','limits','sources','roadFlags','levelRules'),
                            [*r[:3],*[json.loads(v) if v else None for v in r[3:]]])) for r in rows]
                        # Keep full segments near the requested camera/corridor, not an entire city network.
                        def near(road):
                            xs,ys=zip(*[(p[0],p[1]) for p in road['geometry']['coordinates']])
                            return any(min(xs)<lon+.002 and max(xs)>lon-.002 and min(ys)<lat+.002 and max(ys)>lat-.002 for lat,lon in ps)
                        records=[r for r in records if r['geometry']['type']=='LineString' and near(r)]
                        if prior and len(records)<.75*prior['recordCount']:raise ValueError('Region lost more than 25%; retained for review')
                        prior={'release':release,'checkedAt':stamp(now),'sourceURL':URL,'recordCount':len(records),'roads':sorted(records,key=lambda r:r['id'])}
                        write(path,prior,compact=True);status.update(status='downloaded',records=len(records))
                    except Exception as error:status.update(status='retained' if prior else 'unavailable',error=str(error))
                    finally:timer.cancel()
                if prior:
                    paths.append(path.relative_to(root/'Data/SpeedLimits').as_posix());total+=prior['recordCount']
                report['regions'].append(status)
                print(key,status['status'],status.get('records',''),flush=True)
        finally:con.close()
        # The index never advances the per-region evidence dates.
        if paths:write(index_path,{'targetRelease':release,'checkedAt':max(read(root/'Data/SpeedLimits'/path)['checkedAt'] for path in paths),
            'sourceURL':URL,'recordCount':total,'tiles':paths})
        failed=[x for x in report['regions'] if x['status'] in ('deferred','unavailable','retained')]
        report.update(status='partial' if failed else 'complete',release=release,records=total,
            completeRegions=len(groups)-len(failed),totalRegions=len(groups))
        if failed:report['error']=f'{len(failed)} regions unavailable, retained or deferred; see regional results'
    except Exception as error:report.update(status='retained' if old else 'unavailable',error=str(error),lastGoodAt=old.get('checkedAt'))
    write(root/'Data/Review/overture-fetch.json',report)
    print({k:v for k,v in report.items() if k!='regions'},flush=True)
    return report


if __name__=='__main__':refresh()
