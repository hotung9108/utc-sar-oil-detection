"""Check catalog box coordinates against patch corner interpolation.

This checks metadata consistency, not independent registration to SAR pixels.
Object geographic corners may have been computed from the same patch transform.
"""
import csv
import hashlib
import io
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def main():
    path=ROOT/'data/dartis/catalog.tsv'; raw=path.read_bytes()
    rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig').split('*/',1)[1].lstrip()),delimiter='\t'))
    fields=list(rows[0])
    def key(suffix):
        result=[f for f in fields if f.endswith('('+suffix+')')]
        assert len(result)==1
        return result[0]
    def coordinate(row,prefix,corner):
        return np.array([float(row[key(prefix+'_'+corner+'_lon')]),float(row[key(prefix+'_'+corner+'_lat')])])
    cases=[]
    for row in rows:
        name=row[key('jpg_file')]
        if not name.startswith(('oc-','ow-')): continue
        width,height=int(row[key('patch_width')]),int(row[key('patch_height')])
        ul,ur,br,bl=[coordinate(row,'patch',c) for c in ('ul','ur','br','bl')]
        x0,y0,x1,y1=[float(row[key('obj_patchloc_'+axis)]) for axis in ('xmin','ymin','xmax','ymax')]
        errors={}
        for convention,denominator in [('pixel_edges',(width,height)),('pixel_centers_extents',(width-1,height-1))]:
            distances=[]
            for corner,(x,y) in zip(('ul','ur','br','bl'),[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]):
                u,v=x/denominator[0],y/denominator[1]
                predicted=(1-u)*(1-v)*ul+u*(1-v)*ur+u*v*br+(1-u)*v*bl
                actual=coordinate(row,'obj',corner)
                delta=np.deg2rad(predicted-actual)
                # Local tangent approximation; used only for small residual diagnostics.
                distances.append(float(6371000*np.hypot(delta[0]*np.cos(np.deg2rad(actual[1])),delta[1])))
            errors[convention]=max(distances)
        cases.append({'tag':row[key('tag')],'image':name,'max_corner_residual_m':errors})
    assert len(cases)==3225
    summary={name:{'max_m':float(np.max(values)),'median_m':float(np.median(values)),
                   'p95_m':float(np.percentile(values,95))} for name in ('pixel_edges','pixel_centers_extents')
             for values in [[r['max_corner_residual_m'][name] for r in cases]]}
    result={'catalog_sha256':hashlib.sha256(raw).hexdigest(),'oil_objects':len(cases),
            'summary':summary,'independent_pixel_registration_verified':False,
            'scope':'Internal consistency of supplied geographic corners and box coordinates; not independent ground truth accuracy',
            'limits':['Do not infer an oil pixel mask from a bounding box','No inverse mapping to original SAR DN proven',
                      'Near-zero arithmetic residual is not nanometre geolocation accuracy',
                      'Publisher applies SNAP corrections, assembly, multilooking and scene-level normalization'],
            'per_object':cases}
    (ROOT/'docs/management/dartis_geolocation_audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__': main()
