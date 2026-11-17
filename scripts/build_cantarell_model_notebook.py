"""Build the final physical notebook only from complete frozen test evidence."""
import json
from pathlib import Path
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = ROOT / 'results/cantarell/evaluation.json'
    if not source.exists() or not json.loads(source.read_text())['complete']:
        raise ValueError('Complete Cantarell test evidence required; no placeholder notebook')
    path = ROOT / 'notebooks/external/12_cantarell_models_and_angle.ipynb'
    if path.exists():
        raise FileExistsError('Preserve executed notebook; create an explicit new version')
    cells = [
        nbf.v4.new_markdown_cell('''# 12 — Cantarell: phân lớp, đối chứng và góc tới

Notebook kiểm tra kết quả đã lưu, tính lại metric từ số đếm, vẽ bảng so sánh
và chạy lại một mẫu test với mô hình đã khóa. Không fit hoặc chọn lại theo test.

**Hai tầng đánh giá:** so sánh các cấu hình trên validation; đối chứng NumPy
và thư viện với cùng dữ liệu/định nghĩa. Pipeline chính bị ràng buộc gamma0 +
Niblack để thực hiện yêu cầu góc tới và phân ngưỡng thích nghi. Winner không
ràng buộc cũng được công bố để thấy mức đánh đổi.
'''),
        nbf.v4.new_code_cell('''from pathlib import Path
import json, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p/'src/sar_oil').is_dir())
sys.path.insert(0, str(ROOT/'scripts'))
from cantarell_experiment_data import load_manifest, sha, MANIFEST, require_committed
from evaluate_cantarell import scene_bootstrap
from sar_oil.evaluation import summarize
from scripts import streamlit_physical as physical
base = ROOT/'results/cantarell'
manifest, protocol = load_manifest()
selection = json.loads((base/'selection.json').read_text())
validation = json.loads((base/'validation.json').read_text())
evaluation = json.loads((base/'evaluation.json').read_text())
features = json.loads((base/'feature_verification.json').read_text())
bootstrap = json.loads((base/'angle_bootstrap.json').read_text())
assert evaluation['complete'] and validation['complete']
assert not validation['test_accessed'] and not selection['test_accessed']
assert evaluation['binding']['manifest_sha256'] == sha(MANIFEST)
assert evaluation['binding']['selection_sha256'] == sha(base/'selection.json')
assert evaluation['binding']['script_sha256'] == sha(ROOT/'scripts/evaluate_cantarell.py')
assert evaluation['binding']['helper_sha256'] == sha(ROOT/'scripts/train_cantarell.py')
assert selection['validation_sha256'] == sha(base/'validation.json')
assert evaluation['angle_bootstrap_sha256'] == sha(base/'angle_bootstrap.json')
assert len(validation['rows']) == validation['expected_model_pairs']
require_committed(base/'selection.json')
print('Eligible split:', manifest['counts'])
print('Model pairs:', len(validation['rows']))
'''),
        nbf.v4.new_markdown_cell('''## Mọi mô hình và trạng thái hội tụ

Fit scaler bằng train; giữ cùng hàng train cho hai backend. Lấy tối đa 10.000
vùng mỗi lớp, seed 2026; vùng GT giao nhau trung gian chỉ loại trong huấn luyện.
Mô hình lỗi hoặc không hội tụ vẫn có hàng trong bảng, không âm thầm bỏ kết quả.
'''),
        nbf.v4.new_code_cell('''rows = []
for r in validation['rows']:
    row = {'branch':r['branch'], 'candidate':r['config_id'], 'model':r['model_id'],
           'kind':r['model_config']['kind'], 'eligible':r['eligible'], 'error':r.get('error'),
           'agreement':r.get('classifier_agreement'), 'score_error':r.get('score_max_abs_error')}
    if r['eligible']:
        for backend in ['numpy','reference']:
            assert summarize([i['counts'][backend] for i in r['per_image']]) == r['metrics'][backend]
            row[backend+'_f1'] = r['metrics'][backend]['f1']
            row[backend+'_fit_s'] = r['diagnostics'][backend]['fit_seconds']
            row[backend+'_objective'] = r['diagnostics'][backend].get('objective')
        assert sha(ROOT/r['model_file']) == r['model_sha256']
    rows.append(row)
table = pd.DataFrame(rows)
display(table)
display(pd.DataFrame([{'role':role, 'branch':r['branch'], 'candidate':r['config_id'],
                      'model':r['model_id'], 'validation_f1':r['metrics']['numpy']['f1']}
                     for role,r in selection['winners'].items()]))
'''),
        nbf.v4.new_code_cell('''fig, axes = plt.subplots(1,2, figsize=(13,4), sharey=True)
for ax, branch in zip(axes, ['sigma0','gamma0']):
    subset = table[(table.branch==branch) & table.eligible]
    for candidate, part in subset.groupby('candidate'):
        ax.plot(part.model, part.numpy_f1, 'o-', label=f'candidate {candidate}')
    ax.set(title=branch, xlabel='Frozen model ID', ylabel='Validation object F1')
    ax.legend(fontsize=8); ax.grid(alpha=.2)
plt.show()
feature_table = pd.DataFrame([{'branch':r['branch'], 'candidate':r['config_id'], 'sample':r['sample'],
                              **r['reference']} for r in features['rows']])
assert feature_table.allclose.all() and feature_table.partition_match.all()
display(feature_table.groupby('branch')[['max_abs_error','max_relative_error','mse']].max())
print('Original NumPy cross-checks:', sum('original_numpy_check' in r for r in features['rows']))
assert all(r.get('original_numpy_check', True) for r in features['rows'])
'''),
        nbf.v4.new_markdown_cell('''## Đánh giá cuối trên test đã khóa

Không lọc GT nhỏ. Ghép một-một IoU ≥0,5. Số đối tượng là thành phần liên thông
trong từng tile, không phải số sự kiện dầu tràn độc nhất. Các tile trong cùng
cảnh có thể chứa lại một đối tượng.
'''),
        nbf.v4.new_code_cell('''test_ids = {r['sample'] for r in manifest['samples'] if r['split']=='test'}
summary = []
for role,r in evaluation['roles'].items():
    assert {i['sample'] for i in r['per_image']} == test_ids
    for backend in ['numpy','reference']:
        assert summarize([i['counts'][backend] for i in r['per_image']]) == r['metrics'][backend]
    summary.append({'role':role, **r['metrics']['numpy'], 'different_pixels':r['mask_disagreement_pixels']})
display(pd.DataFrame(summary)[['role','images','precision','recall','f1','fp_per_image','pixel_iou','different_pixels']])
'''),
        nbf.v4.new_markdown_cell('''## Ablation góc tới và bất định theo cảnh

Giữ cùng mô hình được train bằng gamma0, scaler, lọc và ngưỡng; chỉ đổi gamma0
thành sigma0. Hai winner tối ưu riêng không phải ablation cô lập góc tới.
Bootstrap ghép cặp theo toàn cảnh, 2.000 lượt. Với ít cảnh, khoảng tin cậy còn hạn chế.
CI chứa 0 không chứng minh có cải thiện; kết quả âm cũng phải giữ nguyên.
'''),
        nbf.v4.new_code_cell('''rebuilt = scene_bootstrap(evaluation['roles']['primary']['per_image'],
                          evaluation['roles']['paired_sigma_same_model']['per_image'],
                          repeats=2000, seed=2026)
assert all(rebuilt[k] == bootstrap[k] for k in rebuilt)
print('95% paired scene-bootstrap CI:', rebuilt['ci95'])
print('Undefined draws:', rebuilt['undefined_draws'])
values = [v for v in rebuilt['gamma_minus_sigma_f1'] if v is not None]
fig, ax = plt.subplots(figsize=(8,3))
ax.hist(values, bins=30); ax.axvline(0,color='black',linestyle='--')
ax.set(xlabel='F1 gamma0 - F1 sigma0 (fixed gamma-trained model)', ylabel='Bootstrap draws')
plt.show()
'''),
        nbf.v4.new_markdown_cell('''## Chạy lại ảnh test đầu tiên theo ID

Không chọn ảnh theo điểm đẹp. Hàm suy luận chỉ đọc bức xạ và góc tới;
GT được đọc riêng sau suy luận để tính lại metric.
'''),
        nbf.v4.new_code_cell('''sample = sorted(physical.samples(), key=lambda r:r['sample'])[0]
result = physical.run_sample(sample['sample'])
actual = physical.assess_sample(result)
saved = next(r for r in evaluation['roles']['primary']['per_image'] if r['sample']==sample['sample'])
assert actual['metrics'] == summarize([saved['counts']['numpy']])
assert not result['metadata']['ground_truth_used_for_inference']
fig, axes = plt.subplots(1,4, figsize=(16,4))
for ax, key in zip(axes, ['image','filtered','candidates','overlay']):
    ax.imshow(result[key], cmap='gray'); ax.set_title(key); ax.axis('off')
plt.show()
print(sample['sample'], actual['metrics'])
display(pd.DataFrame(result['metadata']['regions']))
'''),
        nbf.v4.new_markdown_cell('''## Giới hạn sử dụng

Cantarell là bằng chứng nhị phân dầu/nền có metadata vật lý, không thay thế
QPOSD về dầu/look-alike. ERA5 chỉ là bối cảnh, không làm nhãn nguyên nhân.
Gamma0 là hiệu chỉnh diện tích hình học; dữ liệu vẫn chưa xử lý thermal noise.
Kết quả không xác nhận khả năng cảnh báo tại biển miền Trung hoặc truy tìm tàu xả dầu.
'''),
    ]
    notebook = nbf.v4.new_notebook(cells=cells, metadata={'kernelspec':{'name':'python3','display_name':'Python 3','language':'python'}})
    nbf.write(notebook, path)
    print(path)


if __name__ == '__main__':
    main()
