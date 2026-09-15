"""Reconcile agency coordinates without proximity-based identity guesses."""
from __future__ import annotations
import copy
import datetime as dt
from camera_data import read, write, distance, stamp
from source_watch import inside_geometry
from camera_identity import automatic_rules, distinct, collapse_equivalent_osm


def combine(root, records, previous, now):
    records = dict(records); old = {c['id']: c for c in previous.get('cameras', [])}
    rules = read(root/'Data/Overrides/agency-aliases.json', {'decisions': {}})['decisions']
    registry = read(root/'Data/source-registry.json', {'sources': []})['sources']
    # Preserve already accepted agency records for overlap checks, even during an outage.
    records, replaced, automatic = collapse_equivalent_osm(records, previous)
    reference = {k:v for k,v in {**old, **records}.items() if k not in replaced}
    sources = []; review = []; accepted = []
    # Reuse aliases accepted in a previous snapshot even after the OSM tag changes.
    established = {c['agencyID']: {'targetID':c['id'], 'preservePosition':True,
                   'evidence':c['evidence']} for c in old.values() if c.get('agencyID') and c['agencyID'] != c['id']}
    for source in registry:
        if source.get('monitorOnly'): continue
        cached = read(root/f"Data/External/{source['id']}.json")
        if not cached:
            review.append({'source': source['id'], 'reason': 'No successful agency fetch'}); continue
        sources.append({'id': source['id'], 'name': source['name'], 'url': source.get('page', source['url']),
                        'license': source['license'], 'checkedAt': cached['checkedAt'],
                        'status': 'Agency-listed locations; coordinate precision is recorded per camera. Overlaps and missing records require review.'})
        for excluded in cached.get('excluded', []):
            if 'needs review' in excluded['reason']:
                review.append({'source': source['id'], **excluded})
        fresh_ids = {c['id'] for c in cached['cameras']}
        inferred = automatic_rules(cached['cameras'], reference)
        source_rules = {**inferred, **established, **rules}
        automatic += [{'id':key, **rule} for key,rule in inferred.items() if key not in rules and key not in established]
        for original in cached['cameras']:
            c = copy.deepcopy(original); key = c['id']; rule = source_rules.get(key, {})
            candidate = c.get('speedLimitCandidate', {})
            # SFMTA's live operational table publishes unconditional limits.
            # Conditional school-zone limits and unsurveyed estimates stay unknown.
            if source.get('speedLimitPolicy') == 'unconditional-posted' and candidate and not candidate.get('conditional'):
                checked = dt.datetime.fromisoformat(cached['checkedAt'].replace('Z', '+00:00'))
                c['speedLimit'] = {k: candidate[k] for k in ('value', 'unit', 'sourceID', 'conditional')}
                c['speedLimit'].update(verifiedAt=stamp(checked), validUntil=stamp(checked + dt.timedelta(days=30)))
            if rule and not rule.get('evidence'): raise ValueError('Agency decision requires evidence')
            if rule.get('exclude'):
                replaced.update([key, rule.get('targetID', key), *rule.get('replaces', [])]); continue
            target = rule.get('targetID', key)
            # A reviewed alias keeps the existing app identity and its encounter cooldown.
            aliases = set(rule.get('replaces', []))
            if target != key: aliases.add(key)
            prior = old.get(target)
            if prior and distance(prior.get('agencyGeometry', prior['geometry'])[0], c['geometry'][0]) > 100:
                review.append({'id': key, 'reason': 'Moved more than 100 m; retain accepted position', 'targetID': target})
                continue
            overlaps = []
            for other in reference.values():
                if other['id'] in aliases | {target}: continue
                # Distinct approaches published in the same agency feed retain separate identities.
                if other.get('agencyID', other['id']) in fresh_ids: continue
                d = distance(c['geometry'][0], other['geometry'][0])
                if d < 150 and not distinct(c, other): overlaps.append({'id': other['id'], 'meters': round(d, 1)})
            unresolved = [o for o in overlaps if o['id'] not in rule.get('distinctFrom', [])]
            if unresolved and not prior:
                review.append({'id': key, 'label': c['label'], 'nearby': unresolved,
                               'reason': 'Nearby accepted record; identity/approach review required'})
                continue
            if target != key:
                c['id'] = target; c['siteID'] = prior.get('siteID', target) if prior else target
                c['sourceIDs'] = sorted(set(c['sourceIDs'] + (prior or reference.get(target, {})).get('sourceIDs', [])))
            if rule.get('preservePosition'):
                c['agencyGeometry'] = c['geometry']
                c['geometry'] = (prior or reference[target])['geometry']
                c['positionPrecision'] = (prior or reference[target]).get('positionPrecision', 'reviewed-osm-device' if target.startswith('osm-') else 'mapped-point')
                c['evidence'] = rule['evidence']
            c['agencyID'] = key
            records[target] = c; reference[target] = c; accepted.append(target)
            replaced.update(aliases)
    for key in replaced: records.pop(key, None)
    # An OSM addition near an accepted agency record is also queued, in either fetch order.
    agency = [c for c in reference.values() if c.get('agencyID') or c['id'].startswith('agency-')]
    for key, c in list(records.items()):
        if not key.startswith('osm-') or key in old: continue
        near = [a['id'] for a in agency if a['id'] != key and distance(c['geometry'][0], a['geometry'][0]) < 150]
        if near:
            records.pop(key); review.append({'id': key, 'nearby': near, 'reason': 'New OSM record overlaps accepted agency data; review identity'})
    report = {'checkedAt': stamp(now), 'acceptedAgencyRecords': len(accepted), 'automaticMatches': automatic, 'review': review}
    write(root/'Data/Review/agency-reconciliation.json', report)
    return records, sources, review, replaced


def coverage_report(root, records, now):
    metros = read(root/'Data/Regions/metros.json')
    if not metros: return
    boundaries = read(root/'Data/Regions/metros.geojson')['features']
    regions = {f['properties']['GEOID']: f['geometry'] for f in boundaries}
    rows = []
    for m in metros['regions']:
        selected = [c for c in records if inside_geometry(c['geometry'][0], regions[m['id']])]
        rows.append({**m, 'warningRecords': len(selected),
                     'agencyPoints': sum(bool(c.get('agencyID')) for c in selected),
                     'possibleAreas': sum(len(c['geometry']) > 1 for c in selected)})
    write(root/'Data/Review/metro-coverage.json', {'generatedAt': stamp(now), 'metros': rows})


def audit_metro_points(root, documents, overrides, now):
    nodes = {f"osm/node/{e['id']}": e for d in documents for e in d['elements'] if e['type'] == 'node'}
    changes = []
    for camera in overrides.get('cameras', []):
        for sid in camera['sourceIDs']:
            if not sid.startswith('osm/node/') or len(camera['geometry']) != 1: continue
            node = nodes.get(sid)
            if not node:
                changes.append({'id': camera['id'], 'sourceID': sid, 'reason': 'Mapped source absent; retain reviewed position pending retirement review'})
            elif distance(camera['geometry'][0], {'latitude': node['lat'], 'longitude': node['lon']}) > 20:
                changes.append({'id': camera['id'], 'sourceID': sid, 'reason': 'Mapped source moved over 20 m; review retained override', 'newPosition': {'latitude': node['lat'], 'longitude': node['lon']}})
    write(root/'Data/Review/metro-source-changes.json', {'checkedAt': stamp(now), 'review': changes})
