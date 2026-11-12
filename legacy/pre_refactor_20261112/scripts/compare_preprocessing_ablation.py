"""Paired 2x2 preprocessing study; existing ten samples plus a separate 00013 case."""
from pathlib import Path
import sys,json,csv,hashlib,platform
from datetime import datetime
from time import perf_counter
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.tv1.pipeline import PipelineConfig,process_image

OUT=ROOT/'results/preprocessing_ablation'
CONFIGS={'A_raw':('none','none'),'B_lee':('lee','none'),
         'C_clahe':('none','clahe'),'D_lee_clahe':('lee','clahe')}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    paths=sorted((ROOT/'data/sample').glob('*/*.jpg'))
    assert len(paths)==10
    extra=ROOT/'kaggle/data/Class_1/class_1_00013.jpg'
    rows=[];sources=[]
    for path in paths+[extra]:
        image=np.asarray(Image.open(path).convert('L'))
        assert image.shape==(400,400)
        scope='sample10' if path in paths else 'case00013'
        sources.append({'path':path.relative_to(ROOT).as_posix(),'scope':scope,
                        'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        for name,(f,e) in CONFIGS.items():
            start=perf_counter()
            r=process_image(image,PipelineConfig(filter_name=f,enhancement_name=e))
            elapsed=(perf_counter()-start)*1000
            edge=process_image(image,PipelineConfig(filter_name=f,enhancement_name=e,edge_name='canny'))
            rows.append(dict(image=path.stem,scope=scope,config=name,
                             regions=r['stats']['slicks_count'],area_pct=r['stats']['area_pct'],
                             canny_density_pct=100*float(np.mean(edge['boundary']>0)),
                             RMS=r['metrics']['RMS_Contrast'],SSI=r['metrics']['SSI'],
                             EPI=r['metrics']['EPI'],AMBE=r['metrics']['AMBE'],
                             otsu_threshold=r['stats']['otsu_threshold'],runtime_ms=elapsed))
            if path in [extra,ROOT/'data/sample/sea_surface/sea_surface_01.jpg']:
                folder=OUT/path.stem;folder.mkdir(exist_ok=True)
                for key in ['enhanced','mask','overlay']:
                    Image.fromarray(r[key]).save(folder/f'{name}_{key}.png')
                Image.fromarray(edge['boundary']).save(folder/f'{name}_canny.png')
    def csvout(name,records):
        with (OUT/name).open('w',encoding='utf-8-sig',newline='') as stream:
            w=csv.DictWriter(stream,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    csvout('per_image.csv',rows)
    summaries=[]
    for name in CONFIGS:
        group=[r for r in rows if r['scope']=='sample10' and r['config']==name]
        summary={'config':name,'n':len(group)}
        for key in ['regions','area_pct','canny_density_pct','RMS','SSI','EPI','AMBE','runtime_ms']:
            values=np.array([r[key] for r in group]);summary[key+'_mean']=float(values.mean());summary[key+'_std']=float(values.std(ddof=1))
        summaries.append(summary)
    csvout('summary.csv',summaries)
    (OUT/'manifest.json').write_text(json.dumps({
        'executed_at':datetime.now().astimezone().isoformat(),'python':platform.python_version(),
        'sources':sources,'configs':{n:vars(PipelineConfig(filter_name=f,enhancement_name=e)) for n,(f,e) in CONFIGS.items()},
        'scope':'Paired exploratory sample of ten existing demo images, plus 00013 separately; not full dataset.',
        'controls':'Same images, downstream thresholds/morphology, no sharpening. Reference follows filter output as in production.',
        'limitations':'No clean reference or pixel masks. Image statistics and candidate area do not establish detection accuracy. Runtime one pass, descriptive only.',
        'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'src/tv1/pipeline.py',ROOT/'src/tv3/filters.py',ROOT/'src/tv3/enhancement.py',ROOT/'src/tv4/morphology.py',ROOT/'src/tv4/edges.py']}
    },ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summaries,ensure_ascii=False,indent=2))
    print('CASE 00013:',json.dumps([r for r in rows if r['scope']=='case00013']))

if __name__=='__main__':main()
