"""Create an executable notebook from the completed physical validation grid."""
from pathlib import Path
import json
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]


def main():
    result = json.loads((ROOT / 'results/cantarell/screen.json').read_text())
    if not result['complete'] or len(result['comparisons']) != 50:
        raise ValueError('Complete 50-comparison evidence required')
    path = ROOT / 'notebooks/external/11_cantarell_physical_candidates.ipynb'
    if path.exists():
        raise FileExistsError('Preserve executed notebook; use an explicit new version')
    cells = [
        nbf.v4.new_markdown_cell('''# 11 — Sentinel-1 vật lý: góc tới, lọc và ngưỡng

Notebook này kiểm tra dữ liệu và 50 so sánh **ứng viên trên validation**.
Chưa phải chất lượng pipeline sau phân lớp. SOS vẫn là benchmark chính;
Cantarell bổ sung bức xạ vật lý và gió có tọa độ/thời điểm.

Chia theo nhóm cảnh và liên kết đối tượng: 94 train / 35 validation / 25 test
sau các chốt chất lượng. Dầu tràn và dầu thấm tự nhiên cùng thuộc foreground.
Không gán dầu thấm thành look-alike. Gió chỉ cung cấp bối cảnh.

Code nguồn: `scripts/cantarell_pipeline.py`, `scripts/screen_cantarell.py`.
Notebook đọc bằng chứng đã lưu, kiểm tra hash và chạy lại một ví dụ validation;
không huấn luyện lại, không sử dụng test, không tự tải dữ liệu.
'''),
        nbf.v4.new_code_cell('''from pathlib import Path
import sys, json, hashlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p/'src/sar_oil').is_dir())
sys.path.insert(0, str(ROOT/'scripts'))
from cantarell_experiment_data import load_manifest, load_input, sha, MANIFEST
from cantarell_pipeline import candidates, normalize_power
from sar_oil.evaluation import counts, summarize
manifest, protocol = load_manifest()
screen = json.loads((ROOT/'results/cantarell/screen.json').read_text())
assert screen['complete'] and len(screen['comparisons']) == 50
assert screen['binding']['manifest_sha256'] == sha(MANIFEST)
assert screen['binding']['script_sha256'] == sha(ROOT/'scripts/screen_cantarell.py')
assert screen['binding']['operator_sha256'] == sha(ROOT/'scripts/cantarell_pipeline.py')
assert not screen['test_accessed']
print('Eligible samples:', manifest['counts'])
display(pd.DataFrame(manifest['excluded']))
'''),
        nbf.v4.new_markdown_cell('''## Kiểm tra lại toàn bộ số đếm và bảng xếp hạng

F1 mức đối tượng ghép một-một tại IoU ≥0,5. Không loại GT nhỏ theo diện tích
ứng viên. Mọi cấu hình giữ min_area=64 và không xử lý hình thái.
Lưới hữu hạn này không phải định lý chứng minh Lee hoặc Niblack luôn tốt nhất.
'''),
        nbf.v4.new_code_cell('''rows = []
validation_ids = {r['sample'] for r in manifest['samples'] if r['split']=='val'}
for c in screen['comparisons']:
    assert {r['sample'] for r in c['rows']} == validation_ids
    for backend in ['numpy','reference']:
        assert summarize([r['counts'][backend] for r in c['rows']]) == c['summary'][backend]
    rows.append({'branch':c['branch'], 'config':c['config_id'],
                 'filter':str(c['config']['filter']), 'threshold':str(c['config']['threshold']),
                 'precision':c['summary']['numpy']['precision'],
                 'recall':c['summary']['numpy']['recall'], 'f1':c['summary']['numpy']['f1'],
                 'reference_f1':c['summary']['reference']['f1'],
                 'different_pixels':c['mask_disagreement_pixels']})
table = pd.DataFrame(rows)
display(table.sort_values(['branch','f1'], ascending=[True,False]))
print('Total differing candidate pixels:', table.different_pixels.sum())
print('Retained candidate IDs:', screen['retained_candidate_ids'])
'''),
        nbf.v4.new_code_cell('''fig, ax = plt.subplots(figsize=(13,4))
for branch in ['sigma0','gamma0']:
    subset = table[table.branch==branch].sort_values('config')
    ax.plot(subset.config, subset.f1, marker='o', label=branch)
ax.set(xlabel='Frozen configuration ID', ylabel='Validation object F1 (candidates)',
       title='50 comparisons: 25 configurations × 2 radiometry branches')
ax.set_xticks(range(25)); ax.legend(); ax.grid(alpha=.2)
plt.show()
'''),
        nbf.v4.new_markdown_cell('''## Chạy lại một ví dụ validation, không chọn theo điểm đẹp

Dùng mẫu validation đầu tiên theo ID và cấu hình gamma0 tốt nhất ở bước ứng viên.
Thứ hạng này chưa phản ánh bước SVM/CART. Chuẩn hóa gamma0 hiệu chỉnh diện tích
hình học; không mặc định loại hết ảnh hưởng góc tới lên tán xạ mặt biển.
'''),
        nbf.v4.new_code_cell('''sample = sorted([r for r in manifest['samples'] if r['split']=='val'], key=lambda r:r['sample'])[0]
ordered = sorted([r for r in screen['comparisons'] if r['branch']=='gamma0'],
                 key=lambda r:(-r['summary']['numpy']['f1'], -r['summary']['numpy']['recall'], r['config_id']))
chosen = ordered[0]
power, truth = load_input(sample, 'gamma0')
outputs = {b:candidates(power, chosen['config'], b) for b in ['numpy','reference']}
stored = next(r for r in chosen['rows'] if r['sample']==sample['sample'])
for backend, output in outputs.items():
    assert counts(output['candidate_mask'], truth) == stored['counts'][backend]
assert np.count_nonzero(outputs['numpy']['candidate_mask'] != outputs['reference']['candidate_mask']) == stored['mask_disagreement_pixels']
raw_display, _ = normalize_power(power)
with np.load(ROOT/sample['file']) as arrays:
    incidence = arrays['incidence_degrees']
fig, axes = plt.subplots(1,5,figsize=(18,4))
for ax, image, title in zip(axes, [raw_display, incidence, outputs['numpy']['image'], outputs['numpy']['candidate_mask'], truth],
                          ['Gamma0 (display)', 'Incidence (degrees)', 'Filtered + normalized', 'Candidate mask', 'Ground truth']):
    plot = ax.imshow(image, cmap='viridis' if title.startswith('Incidence') else 'gray')
    ax.set_title(title); ax.axis('off')
    if title.startswith('Incidence'): fig.colorbar(plot, ax=ax, fraction=.045)
plt.show()
print(sample['sample'], chosen['config'])
print('Wind speed (m/s), context only:', sample['wind_speed_m_s'])
print('Candidate metrics:', summarize([stored['counts']['numpy']]))
'''),
        nbf.v4.new_markdown_cell('''## Giới hạn và bước tiếp theo

- Kết quả ứng viên còn thấp; không lựa chọn lại theo test để cải thiện bảng này.
- Tối đa 6 ứng viên/nhánh đi tiếp đến 7 cấu hình SVM/CART mỗi nhánh.
- So sánh NumPy/thư viện kiểm tra thực hiện phép tính; không chứng minh độ chính xác nhãn hay hiệu quả ngoài thực địa.
- Nhãn theo tile có thể đếm lại cùng đối tượng trong một cảnh. Bootstrap cuối phải theo cảnh.
- Dữ liệu chưa hiệu chỉnh thermal noise; đăng ký ảnh vẫn có giới hạn.
- Phải khóa model/selection trước khi đánh giá 25 ảnh test và ablation góc tới.
'''),
    ]
    notebook = nbf.v4.new_notebook(cells=cells, metadata={'kernelspec':{'name':'python3','display_name':'Python 3','language':'python'}})
    nbf.write(notebook, path)
    print(path)


if __name__ == '__main__':
    main()
