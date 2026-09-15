"""Small source-specific readers for agency location lists without coordinates."""
import datetime as dt
import re
from camera_data import read
from geocode_locations import address, intersection


def rows(source, raw):
    from source_watch import parse_page
    html=raw.decode('utf-8', errors='replace'); result=[]
    if source['id']=='philadelphia-addresses':
        lists=re.findall(r'Speed Camera Locations:.*?<ul\b[^>]*>(.*?)</ul>',html,re.S|re.I)
        if len(lists)!=4: raise ValueError('Philadelphia location-list structure changed')
        for group in lists:
            for part in re.findall(r'<li\b[^>]*>(.*?)</li>',group,re.S|re.I):
                text=parse_page(part).text
                if not re.match(r'^\d+\s',text):
                    result.append({'label':text, 'unsupported':True});continue
                date=re.search(r'Live Enforcement Begins (\d{2}-\d{2}-\d{2})',text)
                street=re.sub(r'\s*\(.*?\)\s*','',text).strip()
                result.append({'label':text,'street':street,'live':dt.datetime.strptime(date[1],'%m-%d-%y').date().isoformat() if date else None})
    elif source['id']=='hillsborough-intersections':
        text=parse_page(raw).text
        section=text.split('following intersections within unincorporated Hillsborough County:')[1].split('How do they work?')[0]
        for line in section.splitlines():
            match=re.fullmatch(r'(.+?) & (.+?) \(([NSEW]B(?:, [NSEW]B)*)\)',line.strip())
            if match:
                for heading in match[3].split(', '):result.append({'label':f'{match[1]} & {match[2]} · {heading}', 'roads':[match[1],match[2]],'heading':heading})
        if len(result)<6:raise ValueError('Hillsborough intersection-list structure changed')
    else: raise ValueError('Unknown text location source')
    return result


def normalize(source, entries, root, now):
    from source_watch import make_camera, direction
    cameras=[]; excluded=[]
    for entry in entries:
        try:
            if entry.get('unsupported'): raise ValueError('Intersection/segment description needs review')
            if entry.get('live') and entry['live']>now.date().isoformat():
                excluded.append({'sourceRecord':entry['label'],'reason':'Published future enforcement date; not active yet'});continue
            if 'street' in entry:
                location=address(root,entry['street'],source['city'],source['state'],now)
                identifier=entry['street']; kind='possibleSpeed'
            else:
                location=intersection(root,entry['roads'],source['geocodeBounds'],now)
                identifier=entry['label']; kind='redLight'
            p=location['geometry'][0]
            c=make_camera(source,identifier,entry['label']+' · approximate location',kind,p['latitude'],p['longitude'],direction(entry.get('heading')))
            c.update({k:location[k] for k in ['geometry','positionPrecision','roadNames']})
            c['geocodingSource']=location['providerURL']
            c['evidence']=f"Agency-listed enforcement location: {source['url']}. {location['evidence']}"
            c['sourceIDs'].append('census' if 'street' in entry else 'osm')
            c['locationAccuracyMeters']=150
            cameras.append(c)
        except Exception as error:
            excluded.append({'sourceRecord':entry['label'],'reason':f'Location needs review: {error}'})
    return cameras,excluded
