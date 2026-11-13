"""Generate the five executable teaching notebooks from the shared modules."""

from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
INTRO = """from pathlib import Path
import sys, json
ROOT=Path.cwd()
if not (ROOT/'src').exists(): ROOT=ROOT.parent
sys.path.insert(0,str(ROOT/'src'))
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display, HTML
from sar_oil import core, reference
from sar_oil.data import records, read_pair, MANIFEST
from sar_oil.experiments import OUT
def table(rows, columns):
    def value(x): return (f'{x:.3e}' if 0<abs(x)<1e-4 else f'{x:.6f}') if isinstance(x,float) else str(x)
    display(HTML('<table><tr>'+''.join('<th>'+c+'</th>' for c in columns)+'</tr>'+''.join('<tr>'+''.join('<td>'+value(r.get(c,''))+'</td>' for c in columns)+'</tr>' for r in rows)+'</table>'))
def load(name):
    p=OUT/name
    if not p.exists(): raise FileNotFoundError(f'Missing {p}. Run python scripts/sos.py reproduce first.')
    return json.loads(p.read_text(encoding='utf-8'))
"""


def notebook(name, title, cells):
    nb = nbf.v4.new_notebook(
        cells=[nbf.v4.new_markdown_cell(title), nbf.v4.new_code_cell(INTRO)]
        + [
            nbf.v4.new_markdown_cell(c[1]) if c[0] == "md" else nbf.v4.new_code_cell(c[1])
            for c in cells
        ]
    )
    nb.metadata.kernelspec = {"name": "python3", "display_name": "Python 3", "language": "python"}
    nb.metadata.language_info = {"name": "python", "version": "3.13"}
    path = ROOT / "notebooks" / name
    path.parent.mkdir(exist_ok=True)
    nbf.write(nb, path)


notebook(
    "01_data_and_ground_truth.ipynb",
    "# 01 · Dữ liệu và ground truth — TV5\nMask SOS là nhãn tham chiếu semantic, không phải xác nhận hiện trường. Không có metadata góc tới, gió hay mã cảnh.",
    [
        (
            "code",
            """from collections import Counter
manifest=json.loads(MANIFEST.read_text())
table([dict(split=k,images=v) for k,v in Counter(r['split'] for r in manifest['records']).items()],['split','images'])
assert len(records('train'))==2683 and len(records('validation'))==671 and len(records('test'))==839
assert not (set(r['image_sha256'] for r in records('train')) & set(r['image_sha256'] for r in records('test')))
print('seed:',manifest['seed'],'mask threshold:',manifest['mask_threshold'])""",
        ),
        (
            "md",
            "Chia theo patch, phân tầng mask rỗng; chưa chứng minh độc lập theo cảnh. 853 mask train Sentinel có giá trị trung gian. Mặc định >=128; 64/192 chỉ khảo sát độ nhạy nhãn.",
        ),
        (
            "code",
            """rows=records('validation')
examples=[next(r for r in rows if r['empty']),next(r for r in rows if not r['empty'])]
fig,axes=plt.subplots(2,3,figsize=(11,7))
for i,r in enumerate(examples):
    a,g=read_pair(r); axes[i,0].imshow(a,cmap='gray'); axes[i,0].set_title(r['id'])
    axes[i,1].imshow(g,cmap='gray',vmin=0,vmax=1); axes[i,1].set_title('SOS mask >=128')
    axes[i,2].imshow(a,cmap='gray'); axes[i,2].imshow(np.ma.masked_where(~g,g),alpha=.5,cmap='autumn'); axes[i,2].set_title('Overlay')
for ax in axes.flat: ax.axis('off')
plt.tight_layout(); plt.show()""",
        ),
    ],
)
notebook(
    "02_filter_threshold_benchmark.ipynb",
    "# 02 · Lọc và phân ngưỡng — TV3\nSo sánh 110 cấu hình trên cùng 671 ảnh validation. Lee trên PNG là phép thử công thức, không phải lọc sigma0 đã hiệu chuẩn.",
    [
        (
            "md",
            "## Vì sao chọn Lee?\nChạy `python scripts/explain_selection.py --workers 6` để tái tạo bằng chứng. So sánh dưới đây giữ Otsu, morphology none, min_area16 cố định, chỉ thay bộ lọc trên toàn bộ 671 ảnh validation. Đây là đánh giá tạo ứng viên, chưa chứng minh bộ lọc tối ưu cho mọi classifier. F1-band 0.005 là quy ước, không phải định lý.",
        ),
        (
            "code",
            """evidence=load('selection_evidence/evidence.json')
table([dict(filter=str(r['filter']),**r['metrics'],delta_f1=r['lee_minus_filter_f1'],bootstrap_interval=r['paired_patch_bootstrap_95_interval']) for r in evidence['controlled_filters']],['filter','tp','fp','fn','precision','recall','f1','delta_f1','bootstrap_interval'])
from IPython.display import Image as NotebookImage
display(NotebookImage(filename=str(OUT/'selection_evidence/filters_fixed_otsu.png')))
print('Lấy mẫu lại theo patch, sau lựa chọn; chưa bảo đảm độc lập cảnh hoặc hiệu chỉnh nhiều so sánh.')
for row in evidence['controlled_filters']:
    if row['filter'] in ({'name':'mean','size':7},{'name':'lee','size':7,'looks':1}):
        low,high=row['paired_patch_bootstrap_95_interval']
        print('Lee7,L4 so với',row['filter'],':',f'ΔF1={row["lee_minus_filter_f1"]:.6f}, interval=[{low:.6f}, {high:.6f}]')
        if low<=0<=high: print('Chưa có bằng chứng rõ ràng Lee7,L4 vượt phương án này trong phân tích hiện tại.')
print('Mean7 và median7 là đối chứng bổ sung sau lựa chọn; không đổi mô hình đã khóa.')
print('Đối chiếu NumPy cho đối chứng bổ sung:',evidence['supplementary_numpy_checks'])
print('Bằng chứng và số đếm từng ảnh:',OUT/'selection_evidence/per_image.json')""",
        ),
        (
            "md",
            "Lee đang cài: noise=m²/L; w=max(v−noise,0)/max(v,1e−12); output=m+w·(input−m). Ở vùng phương sai nhỏ, đầu ra gần trung bình cục bộ; ở vùng phương sai lớn, giữ một phần chênh lệch. Đây là lý do khảo sát, không phải bảo đảm tăng F1. L trên PNG là tham số thực nghiệm, chưa phải số looks vật lý đã xác minh.",
        ),
        (
            "code",
            """import inspect
print(inspect.getsource(core.filter_image))
strict=evidence['strict_f1_winner']; selected=load('selected.json')
table([dict(choice='Tối đa F1',filter=str(strict['config']['filter']),model=str(strict['params']),**strict['metrics']),dict(choice='Quy tắc đã dùng',filter=str(selected['config']['filter']),model=str(selected['params']),**selected['metrics'])],['choice','filter','model','recall','f1'])
print('Quy tắc:',evidence['selection_rule'])
print('C=10 và C=1 có cùng F1/Recall tại cấu hình đã chọn; tie-break thời gian một lần chưa chứng minh C=10 tốt hơn.')""",
        ),
        (
            "code",
            """rows=load('screen.json')
table([dict(filter=str(r['config']['filter']),threshold=str(r['config']['threshold']),**r['metrics'],seconds=r['seconds']) for r in rows[:15]],['filter','threshold','precision','recall','f1','pixel_iou','seconds'])
fig,ax=plt.subplots(figsize=(10,3)); ax.plot(sorted([r['metrics']['f1'] or 0 for r in rows],reverse=True)); ax.set(xlabel='Xếp theo F1',ylabel='Object F1',title='110 cấu hình — validation'); plt.show()""",
        ),
        (
            "md",
            "Mean cục bộ dùng summed-area table. Niblack: I < mean − k·std. Otsu dùng 256 bin cố định [0,1]. Đệm reflect không lặp pixel mép. Lee reference ghép công thức bằng SciPy, không phải API Lee độc lập.",
        ),
        (
            "code",
            """a,g=read_pair(next(r for r in records('validation') if not r['empty']))
best=rows[0]['config']; n=core.filter_image(a,**best['filter']); r=reference.filter_image(a,**best['filter'])
print('Sai số lọc lớn nhất:',np.max(np.abs(n-r)))
fig,axes=plt.subplots(1,4,figsize=(13,3))
for ax,img,title in zip(axes,[a,n,core.threshold(n,**best['threshold']),g],['PNG /255','Lọc NumPy','Ngưỡng NumPy','Ground truth']): ax.imshow(img,cmap='gray',vmin=0,vmax=1); ax.set_title(title); ax.axis('off')
plt.tight_layout(); plt.show()
checks=load('verification_real.json')['checks']
aggregated=[]
for config in {json.dumps(c['config'],sort_keys=True) for c in checks if c['operation']=='filter'}:
    same=[c for c in checks if c['operation']=='filter' and json.dumps(c['config'],sort_keys=True)==config]
    aggregated.append(dict(config=config,max_abs_error=max(c['max_abs_error'] for c in same),numpy_seconds=np.mean([c['numpy_seconds'] for c in same]),reference_seconds=np.mean([c['reference_seconds'] for c in same]),passed=all(c['passed'] for c in same)))
table(sorted(aggregated,key=lambda c:c['config']),['config','max_abs_error','numpy_seconds','reference_seconds','passed'])
print('Đối chiếu trên 8 ảnh SOS validation thật; thời gian trung bình/ảnh.')""",
        ),
    ],
)
notebook(
    "03_regions_and_features.ipynb",
    "# 03 · Vùng ứng viên và đặc trưng — TV4\n8 đặc trưng: diện tích tương đối, độ thuôn dài, extent, độ phức tạp biên, mean, std, gradient biên và tương phản nền.",
    [
        (
            "md",
            "Đối tượng là thành phần liên thông 8 của mask semantic. Chu vi đếm cạnh lưới, không dùng perimeter mặc định khác định nghĩa. Nền là vành đĩa bán kính 5 ngoài mọi ứng viên; nếu rỗng dùng nền toàn ảnh, sau đó toàn ảnh. Không bỏ đối tượng GT nhỏ khi đánh giá.",
        ),
        (
            "code",
            """from sar_oil.pipeline import candidates
selected=load('selected.json')
a,g=read_pair(next(r for r in records('validation') if not r['empty']))
f,l=candidates(a,selected['config']); X,ids=core.features(f,l); R,_=reference.features(f,l)
print('Sai số đặc trưng:',np.max(np.abs(X-R)) if X.size else 0)
table([dict(region=i,**dict(zip(core.FEATURES,x))) for i,x in zip(ids,X)][:15],['region']+core.FEATURES)
fig,axes=plt.subplots(1,3,figsize=(11,3))
for j,(ax,img,title) in enumerate(zip(axes,[a,l,g],['Ảnh','Ứng viên','Ground truth'])): ax.imshow(img,cmap='tab20' if j==1 else 'gray',vmin=0,vmax=max(1,l.max()) if j==1 else 1); ax.set_title(title); ax.axis('off')
plt.show()""",
        ),
        (
            "code",
            """rows=load('validation.json')
best_by_group=[next(r for r in rows if r['group']==group) for group in ('shape','intensity','all')]
table([dict(group=r['group'],kind=r['kind'],morphology=str(r['config']['morphology']),**r['metrics']) for r in best_by_group],['group','kind','morphology','precision','recall','f1'])""",
        ),
    ],
)
notebook(
    "04_cart_svm_numpy.ipynb",
    "# 04 · CART và SVM tự cài — TV2\nCART tối ưu Gini; SVM tuyến tính squared hinge, L2, bias được regularize như cột hằng. Chuẩn hóa fit trên train.",
    [
        (
            "md",
            "Ứng viên train có purity >=0.5 là dầu, <=0.05 là nền; phần còn lại bỏ khỏi train, vẫn tính đầy đủ khi đánh giá. Tối đa 10.000 vùng mỗi lớp, seed 2026. SVM tối ưu cùng mục tiêu với LinearSVC: (0.5||w||² + C∑max(1−y·Xw,0)²)/n. CART có thể khác tie-break/precision của sklearn; báo agreement và F1 thực tế.",
        ),
        (
            "code",
            """rows=load('model_comparison.json')
table([dict(kind=r['kind'],group=r['group'],params=str(r['params']),agreement=r['agreement'],converged=r['converged'],numpy_f1=r['metrics']['f1'],reference_f1=r['reference_metrics']['f1']) for r in rows],['kind','group','params','agreement','converged','numpy_f1','reference_f1'])
svm=next(r for r in rows if r['kind']=='svm')
print({k:svm[k] for k in ('objective','reference_objective','gradient_max','iterations')})
for row in rows:
    print(row['kind'],'timing:',row['timings'],'candidate confusion:',row['candidate_confusion'])
h=np.asarray(svm['history'])
if h[-1,0]!=svm['iterations']-1: h=np.vstack([h,[svm['iterations']-1,svm['objective'],svm['gradient_max']]])
fig,axes=plt.subplots(1,2,figsize=(9,3)); axes[0].plot(h[:,0],h[:,1]); axes[0].set_title('SVM objective'); axes[1].semilogy(h[:,0],h[:,2]); axes[1].set_title('Max absolute gradient'); plt.show()""",
        ),
        (
            "code",
            """from sar_oil.models import RegionModel
selected=load('selected.json'); model=RegionModel.load(OUT/selected['model_file'])
print('Cấu hình NumPy được chọn trên validation:',selected['kind'],selected['params'])
print('Kiểm chứng thuật toán:',load('verification.json')['passed'])
# Huấn luyện lại trên vùng train thật. Cache chỉ tiết kiệm bước trích đặc trưng.
from sar_oil.experiments import region_data, training_arrays, GROUPS
X,y,training=training_arrays(region_data(selected['config'],'train',workers=1))
retrained=RegionModel(selected['kind'],GROUPS[selected['group']],**selected['params']).fit(X,y)
reference_model=RegionModel(selected['kind'],GROUPS[selected['group']],backend='reference',**selected['params']).fit(X,y)
print('Số vùng train:',training)
print('Agreement trên train (không phải test):',np.mean(retrained.predict(X)==reference_model.predict(X)))
assert retrained.converged
assert np.array_equal(retrained.predict(X),model.predict(X))""",
        ),
    ],
)
notebook(
    "05_final_pipeline.ipynb",
    "# 05 · Pipeline cuối và phân tích lỗi — TV1\nKhông chọn lại thuật toán theo test. Kết quả phản ánh SOS oil/background, không đo nhầm lẫn riêng vùng gió yếu, màng sinh học, mưa.",
    [
        (
            "code",
            """evaluation=load('evaluation.json')
table([dict(experiment=k,**v['metrics'],seconds=v['seconds']) for k,v in evaluation.items() if k!='provenance'],['experiment','images','precision','recall','f1','pixel_iou','fp_per_image','seconds'])
print('Provenance:',evaluation['provenance'])""",
        ),
        (
            "md",
            "TP được ghép một-một với IoU >=0.5, ưu tiên số cặp rồi tổng IoU. Báo F1 micro, không trung bình F1 từng ảnh. Baseline và bỏ classifier là ablation; PALSAR chỉ đánh giá ngoài miền với cấu hình đóng băng. Không giả lập góc tới hoặc gió.",
        ),
        (
            "code",
            """from sar_oil.models import RegionModel
from sar_oil.pipeline import predict
selected=load('selected.json'); model=RegionModel.load(OUT/selected['model_file'])
per=evaluation['test_final']['per_image']; ordered=sorted(per,key=lambda r:r['counts']['fp']+r['counts']['fn'],reverse=True)
by_id={r['id']:r for r in records('test')}; chosen=[ordered[0],ordered[len(ordered)//2],ordered[-1]]
fig,axes=plt.subplots(3,4,figsize=(12,9))
for i,row in enumerate(chosen):
    a,g=read_pair(by_id[row['id']]); p,regions=predict(a,selected['config'],model)
    errors=np.zeros((*g.shape,3)); errors[p&g]=[0,1,0]; errors[p&~g]=[1,0,0]; errors[~p&g]=[0,0,1]
    for ax,img,title in zip(axes[i],[a,g,p,errors],[row['id'],'GT','NumPy prediction','Pixel: TP xanh; FP đỏ; FN lam']): ax.imshow(img,cmap='gray',vmin=0,vmax=1); ax.set_title(title,fontsize=9); ax.axis('off')
plt.tight_layout(); plt.show()""",
        ),
        (
            "md",
            "Chạy lại toàn bộ số liệu: `python scripts/sos.py reproduce --workers 6`. Notebook đọc kết quả benchmark đã thực thi và chạy trực tiếp các ví dụ, không tự khởi động lại hàng trăm thí nghiệm khi Run All. Xem giao thức trong docs/GIAO_THUC_THUC_NGHIEM.md.",
        ),
    ],
)
diagnostic_path = ROOT / "notebooks/05_final_pipeline.ipynb"
diagnostic_nb = nbf.read(diagnostic_path, as_version=4)
diagnostic_nb.cells.extend(
    [
        nbf.v4.new_markdown_cell(
            "## Ba ca thất bại và độ phân tán trên toàn tập\nChạy `python scripts/analyze_failures.py` để tái tạo. Các ca được chọn theo ba tiêu chí lỗi đã công bố, không dùng để thay mô hình. Macro chỉ tính các ảnh có mẫu số xác định; micro vẫn là chỉ số chính."
        ),
        nbf.v4.new_code_cell("""from IPython.display import Image as DiagnosticImage
diagnostics=load('diagnostics/diagnostics.json')
adaptive=load('adaptive/selected.json')
print('Nhánh thích nghi bổ sung (chỉ validation):',adaptive['config'],adaptive['kind'],adaptive['params'])
print('F1 adaptive validation:',adaptive['metrics']['f1'],'; không dùng kết quả test Otsu cho nhánh này.')
table([dict(experiment=k,micro_f1=v['micro']['f1'],**v['per_image']['f1']) for k,v in diagnostics['experiments'].items()],['experiment','micro_f1','mean','std_population','defined','undefined'])
for case in diagnostics['failure_cases']:
    print(case['id'],case['selection_rule'])
    print('Proposal:',case['proposal_counts'],'Final:',case['final_counts'])
    print('GT pixels absent from proposals:',case['truth_pixels_missing_from_proposals'],'GT pixels removed by classifier:',case['truth_pixels_removed_by_classifier'])
    display(DiagnosticImage(filename=str(OUT/'diagnostics'/case['figure'])))"""),
    ]
)
nbf.write(diagnostic_nb, diagnostic_path)
print("Created five notebooks")
