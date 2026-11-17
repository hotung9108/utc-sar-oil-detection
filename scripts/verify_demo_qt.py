"""Run the Qt event loop offscreen against real data and saved SOS evidence."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import hashlib
import json
import tempfile
import time
from pathlib import Path
import numpy as np
from PIL import Image
from PyQt6.QtWidgets import QApplication
import demo_engine as engine
from demo_qt import Window, configure_app
from sar_oil.data import records


def main():
    app=QApplication([]); configure_app(app)
    window=Window(); window.show(); app.processEvents()
    window.sample()
    sample=records('test')[0]
    evidence=json.loads((engine.ROOT/'results/sos/evaluation.json').read_text())
    expected=next(r['counts'] for r in evidence['test_final']['per_image'] if r['id']==sample['id'])
    preview=engine.ROOT/'.cache/gui'; preview.mkdir(parents=True,exist_ok=True)
    checks=[]
    for branch in range(2):
        window.choice.setCurrentIndex(branch); window.run_button.click()
        deadline=time.monotonic()+90
        while window.worker.isRunning():
            app.processEvents(); time.sleep(0.01)
            if time.monotonic()>deadline: raise TimeoutError('GUI inference did not finish in 90 seconds')
        app.processEvents()
        assert window.result is not None,window.status.text()
        assert window.run_button.isEnabled() and window.save_button.isEnabled()
        assert window.metrics is not None,window.status.text()
        if branch==0:
            assert all(window.metrics[k]==expected[k] for k in expected)
        assert window.table.rowCount()==len(window.result['metadata']['regions'])
        before=window.result['mask'].copy()
        with tempfile.TemporaryDirectory() as tmp:
            directory=engine.export(window.result,Path(tmp)/'export',window.metrics,window.truth_path)
            mask=np.asarray(Image.open(directory/'mask.png'))>=128
            assert np.array_equal(mask,window.result['mask'])
            payload=json.loads((directory/'regions.json').read_text(encoding='utf-8'))
            assert payload['ground_truth_used_for_inference'] is False
            assert payload['post_inference_evaluation']==window.metrics
            empty=Path(tmp)/'empty.png'; Image.fromarray(np.zeros(before.shape,dtype='uint8')).save(empty)
            engine.assess(window.result,empty)
            assert np.array_equal(before,window.result['mask'])
            wrong=Path(tmp)/'wrong.png'; Image.fromarray(np.zeros((2,2),dtype='uint8')).save(wrong)
            try: engine.assess(window.result,wrong)
            except ValueError: pass
            else: raise AssertionError('Mismatched mask dimensions accepted')
            dn=Path(tmp)/'dn.tif'; Image.fromarray(np.zeros((4,4),dtype='uint16')).save(dn)
            try: engine.load_image(dn)
            except ValueError: pass
            else: raise AssertionError('Raw DN image silently normalized as SOS PNG')
        window.tabs.setCurrentIndex(0); app.processEvents()
        window.grab().save(str(preview/f'branch-{branch}.png'))
        if branch==0:
            window.tabs.setCurrentIndex(1); app.processEvents(); window.grab().save(str(preview/'ground-truth.png'))
            window.tabs.setCurrentIndex(2); app.processEvents(); window.grab().save(str(preview/'features.png'))
        checks.append({'branch':window.choice.currentText(),'sample':sample['id'],
            'candidate_regions':window.table.rowCount(),'metrics':window.metrics,
            'thread_completed':True,'export_mask_equal':True,'ground_truth_did_not_change_prediction':True,
            'shape_mismatch_rejected':True,'raw_uint16_rejected':True})
    failure_checks=[]
    window.choice.setCurrentIndex(0)
    for action_index,identifier in [(1,'val/sentinel_440'),(2,'val/sentinel_591')]:
        window.sample_button.menu().actions()[action_index].trigger()
        window.run_button.click(); deadline=time.monotonic()+90
        while window.worker.isRunning():
            app.processEvents(); time.sleep(0.01)
            if time.monotonic()>deadline: raise TimeoutError('Failure-case demo timed out')
        app.processEvents(); assert window.result is not None
        expected=next(r['counts'] for r in evidence['test_final']['per_image'] if r['id']==identifier)
        assert all(window.metrics[k]==expected[k] for k in expected)
        window.tabs.setCurrentIndex(1); app.processEvents()
        window.grab().save(str(preview/f'failure-{action_index}.png'))
        failure_checks.append({'sample':identifier,'matches_saved_test_counts':True})
    window.remove_truth(); assert window.metrics is None
    window.choice.setCurrentIndex(1); assert window.result is None and not window.save_button.isEnabled()
    window.close(); app.processEvents()
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    audit={'passed':True,'mode':f"Qt {os.environ['QT_QPA_PLATFORM']} event loop; automated widget actions, no manual file-dialog test",
        'checks':checks,'failure_cases':failure_checks,'otsu_counts_equal_saved_sos_test':True,'font':app.font().family(),
        'source_sha256':{p.name:sha(p) for p in [engine.ROOT/'scripts/demo_qt.py',engine.ROOT/'scripts/demo_engine.py']},
        'screenshots':{p.name:sha(p) for p in preview.glob('*.png')}}
    (engine.ROOT/'docs/management/gui_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'passed':True,'branches':len(checks),'otsu_counts_equal_saved_sos_test':True}))


if __name__=='__main__': main()
