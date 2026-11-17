"""Post-test size diagnostics only: no model selection, fitting or threshold changes."""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.optimize import linear_sum_assignment

from cantarell_experiment_data import ROOT, sha
sys.path.insert(0,str(ROOT/'src'))
from sar_oil.reference import label


def object_size_recall(prediction, truth):
    p, g = label(prediction), label(truth)
    npred, ngt = int(p.max()), int(g.max())
    pa, ga = np.bincount(p.ravel(),minlength=npred+1)[1:], np.bincount(g.ravel(),minlength=ngt+1)[1:]
    joint = np.bincount((p*(ngt+1)+g).ravel(),minlength=(npred+1)*(ngt+1)).reshape(npred+1,ngt+1)[1:,1:]
    iou = joint/np.maximum(pa[:,None]+ga[None,:]-joint,1)
    valid = iou>=.5
    pi, gi = linear_sum_assignment(-(valid*(min(npred,ngt)+1)+iou*valid))
    matched = np.zeros(ngt,bool)
    matched[gi[valid[pi,gi]]] = True
    groups = {'below_32':ga<32,'32_to_63':(ga>=32)&(ga<64),'at_least_64':ga>=64}
    return {name:{'gt':int(mask.sum()),'matched':int((mask&matched).sum())} for name,mask in groups.items()}


def main():
    base = ROOT/'results/cantarell'
    source = base/'evaluation.json'
    data = json.loads(source.read_text())
    if not data['complete']:
        raise ValueError('Complete test evaluation required')
    results = {}
    for role,group in data['roles'].items():
        totals = {k:{'gt':0,'matched':0} for k in ('below_32','32_to_63','at_least_64')}
        rows = []
        for row in group['per_image']:
            folder = base/'test_outputs'/role/row['sample']
            for name in ('mask.png','truth.png'):
                if sha(folder/name)!=row['artifact_sha256'][name]:
                    raise ValueError('Test raster changed')
            with Image.open(folder/'mask.png') as im:
                pred = np.asarray(im)>0
            with Image.open(folder/'truth.png') as im:
                truth = np.asarray(im)>0
            sizes = object_size_recall(pred,truth)
            if sum(v['matched'] for v in sizes.values())!=row['counts']['numpy']['tp']:
                raise ValueError('Diagnostic matching differs from frozen evaluator')
            rows.append({'sample':row['sample'],'sizes':sizes})
            for name, values in sizes.items():
                for key,value in values.items():
                    totals[name][key] += value
        for value in totals.values():
            value['recall'] = value['matched']/value['gt'] if value['gt'] else None
        results[role] = {'totals':totals,'per_image':rows}
    result = {'evaluation_sha256':sha(source),'script_sha256':sha(Path(__file__)),
              'roles':results,'retuning_performed':False,
              'interpretation':'With minimum predicted component area 64 and IoU >= 0.5, a GT component below 32 pixels cannot match even if fully contained. Size strata describe missed objects; they do not replace full-population scores or justify removing small GT.',
              'caution':'Minimum area 64 was fixed in the physical protocol, inherited from the coursework search design; it is not an empirically established optimum for every sensor or resolution.'}
    (base/'size_diagnostics.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v['totals'] for k,v in results.items()},indent=2))


if __name__=='__main__':
    main()
