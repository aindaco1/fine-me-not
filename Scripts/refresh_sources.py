#!/usr/bin/env python3
"""Stage weekly source checks before the Monday Denver publication."""
import argparse
import datetime as dt
from camera_data import ROOT, UTC, read, write, stamp
from publish_cameras import fetch_sources, osm_records, QUERIES
from agency_cameras import audit_metro_points, combine
from source_watch import refresh
from maintenance_report import generate


def run(root=ROOT, now=None, if_stale=False):
    now = now or dt.datetime.now(UTC)
    prior = read(root/'Data/Review/prepublication-check.json', {})
    checked = dt.datetime.fromisoformat(prior['completedAt'].replace('Z', '+00:00')) if prior.get('completedAt') else None
    if if_stale and checked and dt.timedelta(0) <= now-checked <= dt.timedelta(hours=12):
        print('Using source checks staged within the last 12 hours.'); return prior
    osm = fetch_sources(root)
    report = refresh(root, dt.datetime.now(UTC))
    documents = [read(root/f'Data/Sources/osm-us-{name}.json') for name in QUERIES]
    audit_metro_points(root, documents, read(root/'Data/Overrides/metro.json', {}), dt.datetime.now(UTC))
    combine(root, osm_records(documents)[0], read(root/'Data/Published/cameras.json', {}), dt.datetime.now(UTC))
    generate(root)
    result = {'completedAt': stamp(dt.datetime.now(UTC)), 'osmFetches': osm,
              'agencyAndPageChecksAt': report['checkedAt'], 'reviewRequired': report['reviewRequired']}
    write(root/'Data/Review/prepublication-check.json', result)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--if-stale', action='store_true')
    run(if_stale=parser.parse_args().if_stale)
