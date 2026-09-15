"""A durable review queue produced by GitHub Actions, with no Codex dependency."""
from camera_data import ROOT, read, write, stamp, UTC
import datetime as dt


def generate(root=ROOT):
    now=dt.datetime.now(UTC)
    watches=read(root/'Data/Review/source-watch.json',{})
    identity=read(root/'Data/Review/agency-reconciliation.json',{})
    moved=read(root/'Data/Review/metro-source-changes.json',{})
    items=[]
    for c in watches.get('checks',[]):
        if c.get('reviewRequired'):
            items.append({'source':c['id'],'url':c['url'],'reason':c.get('error','Source page changed'),
                          'added':c.get('added',[]),'removed':c.get('removed',[]),'lastGoodAt':c.get('lastGoodAt')})
    items += identity.get('review',[]) + moved.get('review',[])
    report={'generatedAt':stamp(now),'reviewCount':len(items),'items':items}
    write(root/'Data/Review/maintenance.json',report)
    lines=['# Weekly camera maintenance','',f"Generated {stamp(now)}",'',
           f"{len(watches.get('checks',[]))} registered sources checked; {len(identity.get('automaticMatches',[]))} evidence-based identity matches; {len(items)} unresolved findings.",'',
           'New unambiguous agency records and validated coordinate estimates are staged automatically. Ambiguous identities, source removals, changed page layouts, and failed checks retain previous coverage and remain in this queue until reviewed.','',
           '| Source or record | Finding |','|---|---|']
    for item in items:
        key=item.get('id',item.get('sourceRecord',item.get('source','Source')))
        reason=item.get('reason','Review required')
        lines.append(f"| {str(key).replace('|','/')} | {str(reason).replace('|','/')} |")
    lines += ['', 'Full added/removed facts, nearby candidates, and evidence are in maintenance.json and the source-specific reports.', '']
    (root/'Data/Review/maintenance.md').write_text('\n'.join(lines))
    print(f'{len(items)} unresolved maintenance findings.')
    return report

if __name__=='__main__':generate()
