"""Build notebook 10 only after the frozen five-image QPOSD test completes."""
import json
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]


def main():
    result = ROOT/'results/qposd/evaluation.json'
    if not result.exists() or not json.loads(result.read_text(encoding='utf-8')).get('complete'):
        raise SystemExit('QPOSD test evaluation is incomplete; no notebook with placeholder scores created')
    output = ROOT/'notebooks/external/10_qposd_classification_detection.ipynb'
    if output.exists():
        raise SystemExit('Notebook already exists; preserve executed evidence')
    cells = [
        nbf.v4.new_markdown_cell('''# 10 — QPOSD: phân lớp và phát hiện dầu/tương tự dầu

SOS vẫn là dữ liệu chính; đây là kiểm tra bổ sung trên UAVSAR L-band.
Nguồn: [QPOSD](https://zenodo.org/records/19258036), CC BY 4.0.
Chia theo ảnh nguồn, chưa chứng minh độc lập cảnh. Nhãn tương tự dầu là lớp
chung, chưa phân biệt gió yếu, màng sinh học hay mưa.

**Hai kết quả khác nhau:** phân lớp có sẵn vùng tham chiếu và phát hiện
đầu-cuối từ ảnh. Chỉ bước thứ hai đo đầy đủ việc tìm vùng, hình học và phân
lớp. Toàn bộ lựa chọn dùng validation; test chỉ chạy sau khi đã lưu lựa chọn.
Notebook đọc bằng chứng đã lưu, kiểm tra hash, tổng hợp lại số đếm và chạy
lại suy luận của hai backend trên năm ảnh test, không fit lại mô hình.
'''),
        nbf.v4.new_code_cell('''from pathlib import Path
import io, json, sys
import numpy as np
from PIL import Image as PILImage
import matplotlib.pyplot as plt
from IPython.display import display, Markdown, Image
ROOT=next(p for p in [Path.cwd(),*Path.cwd().parents] if (p/'src/sar_oil').is_dir())
sys.path.insert(0,str(ROOT/'scripts'))
from extract_qposd_regions import digest, load_pair
from qposd_metrics import detection, summarize_detections, classification
from qposd_pipeline import infer
from select_qposd_detection import frozen_classifier
from evaluate_qposd_test import frozen_detection
base=ROOT/'results/qposd'
protocol=json.loads((base/'protocol.json').read_text())
evaluation=json.loads((base/'evaluation.json').read_text())
classifiers=json.loads((base/'classifier_selection.json').read_text())
candidates=json.loads((base/'detection_selection.json').read_text())
assert evaluation['complete']
assert [r['number'] for r in evaluation['images']]==protocol['splits']['test']
assert evaluation['script_sha256']==digest(ROOT/'scripts/evaluate_qposd_test.py')
assert evaluation['pipeline_sha256']==digest(ROOT/'scripts/qposd_pipeline.py')
assert evaluation['metrics_sha256']==digest(ROOT/'scripts/qposd_metrics.py')
for name,sha in evaluation['inputs_sha256'].items(): assert digest(ROOT/name)==sha
model,model_record=frozen_classifier()
config,detector_record=frozen_detection(protocol,model_record)
assert model_record==evaluation['classifier'] and detector_record==evaluation['detector']
print('Tập ảnh:',protocol['splits'])
print('Bộ phân lớp:',model_record['config'])
print('Cấu hình tạo vùng:',config)
def show(fig):
    buf=io.BytesIO(); fig.savefig(buf,format='png',dpi=110)
    display(Image(data=buf.getvalue())); plt.close(fig)
'''),
        nbf.v4.new_markdown_cell('''## So sánh 10 bộ phân lớp trên validation

Đặc trưng và thống kê chuẩn hóa chỉ lấy từ train. Hai cài đặt nhận cùng
ma trận đặc trưng NumPy để tách riêng khác biệt của mô hình. Cấu hình NumPy
không hội tụ không được chọn. Hòa điểm dùng thứ tự cố định, không dựa test.
'''),
        nbf.v4.new_code_cell('''rows=classifiers['configurations']
names=[str(r['index'])+': '+r['config']['kind']+' '+str(r['config']['params']) for r in rows]
fig,ax=plt.subplots(figsize=(11,6),layout='constrained')
y=np.arange(len(rows)); width=.36
ax.barh(y-width/2,[r['numpy_validation']['macro_f1'] for r in rows],width,label='NumPy')
ax.barh(y+width/2,[r['reference_validation']['macro_f1'] for r in rows],width,label='Library')
ax.set_yticks(y,names); ax.set_xlim(0,1); ax.set_xlabel('Conditional classification macro-F1')
ax.set_title('Validation only — reference-region geometry supplied'); ax.legend(); show(fig)
table=['| ID | Hội tụ NumPy | Đồng thuận dự đoán | Sai số score lớn nhất |', '|---:|---|---:|---:|']
for r in rows:
    table.append(f"| {r['index']} | {r['numpy_converged']} | {r['prediction_agreement']:.6f} | {r['score_max_abs_difference']:.6g} |")
display(Markdown(chr(10).join(table)))
print('Cấu hình được chọn:',classifiers['winner_index'])
'''),
        nbf.v4.new_markdown_cell('''## So sánh 10 cấu hình tìm vùng trên validation

Cùng bộ phân lớp đã chọn; lọc/chuẩn hóa/ngưỡng/liên thông/đặc trưng có hai
cách tính. Điểm là macro-F1 của hai lớp sau khi cộng TP/FP/FN toàn validation.
Ngưỡng diện tích 64 chỉ lọc ứng viên, không bỏ nhãn nhỏ khỏi ground truth.
'''),
        nbf.v4.new_code_cell('''rows=candidates['configurations']
fig,ax=plt.subplots(figsize=(10,4),layout='constrained')
x=np.arange(len(rows)); width=.38
ax.bar(x-width/2,[r['numpy_summary']['macro_f1'] for r in rows],width,label='NumPy operators')
ax.bar(x+width/2,[r['reference_summary']['macro_f1'] for r in rows],width,label='Library operators')
ax.set_xticks(x,[str(r['index']) for r in rows]); ax.set_ylim(0,1)
ax.set_xlabel('Predeclared configuration ID'); ax.set_ylabel('Object macro-F1, IoU >= 0.5')
ax.set_title('Validation only — same frozen classifier'); ax.legend(); show(fig)
for r in rows: print(r['index'],r['config'])
print('Cấu hình được chọn:',candidates['winner_index'])
'''),
        nbf.v4.new_markdown_cell('''## Chạy lại và xem toàn bộ năm ảnh test

Mỗi hình gồm T11 đổi thang log để hiển thị, nhãn gốc và mask dự đoán NumPy.
Mask dự đoán dùng xanh lam=nền, đỏ=dầu, xanh lá=tương tự dầu. Nhãn thật còn
có đen=đất liền; không dùng đất liền trong nhãn để che dự đoán. Suy luận
không nhận nhãn thật. Đối chiếu lại cả mask NumPy và thư viện từng pixel.
'''),
        nbf.v4.new_code_cell('''recomputed={'numpy':[],'reference':[]}
for row in evaluation['images']:
    number=row['number']; raw,truth,source=load_pair(number)
    assert source['mat_sha256']==row['mat_sha256'] and source['mask_sha256']==row['mask_sha256']
    for backend in ('numpy','reference'):
        predicted=infer(raw,config,model,backend)['prediction']
        saved=row['saved_masks'][backend]; path=ROOT/saved['path']
        assert digest(path)==saved['sha256']
        with PILImage.open(path) as im: stored=np.asarray(im)
        assert np.array_equal(predicted,stored)
        metric=detection(predicted,truth); assert metric==row[backend]
        recomputed[backend].append(metric)
        if backend=='numpy': final=predicted
    visible=10*np.log10(np.maximum(raw,1e-12)); lo,hi=np.percentile(visible,[1,99])
    palette=np.array([[0,0,255],[255,0,0],[0,255,0],[0,0,0]],dtype=np.uint8)
    reference_rgb=np.full((*truth.shape,3),255,dtype=np.uint8)
    for value in range(4): reference_rgb[truth==value]=palette[value]
    fig,axes=plt.subplots(1,3,figsize=(13,4.5),layout='constrained')
    axes[0].imshow(visible,cmap='gray',vmin=lo,vmax=hi)
    axes[1].imshow(reference_rgb); axes[2].imshow(palette[final])
    for ax,title in zip(axes,('T11 display log','Original reference','NumPy predicted classes')):
        ax.set_title(title); ax.axis('off')
    fig.suptitle(f'Test source image {number}'); show(fig)
for backend in recomputed:
    assert summarize_detections(recomputed[backend])==evaluation[backend+'_summary']
print('Đã chạy lại, mask và số đếm của hai backend khớp bằng chứng đã lưu.')
'''),
        nbf.v4.new_markdown_cell('''## Điểm test và nhầm lẫn

Ma trận nhầm lẫn của phát hiện chỉ tính trong các đối tượng ghép được về
không gian; số bỏ sót/phát hiện thừa được ghi riêng. Không dùng tỉ lệ nhầm
lớp có điều kiện để thay thế Recall phát hiện. Các số trên năm ảnh còn dễ
biến động; số đối tượng không phải số cảnh độc lập.
'''),
        nbf.v4.new_code_cell('''conditional=evaluation['conditional_rows']
recomputed_classification=classification([r['truth'] for r in conditional],[r['prediction'] for r in conditional])
assert recomputed_classification==evaluation['conditional_classification']
table=['| Phép đo | Lớp | Precision | Recall | F1 |','|---|---|---:|---:|---:|']
def fmt(value): return 'Không xác định' if value is None else f'{value:.6f}'
for label,result in [('Phân lớp có sẵn vùng',recomputed_classification),('Phát hiện đầu-cuối',evaluation['numpy_summary'])]:
    for name,row in result['classes'].items():
        table.append('| '+label+' | '+name+' | '+' | '.join(fmt(row[k]) for k in ('precision','recall','f1'))+' |')
display(Markdown(chr(10).join(table)))
print('Ma trận phân lớp có sẵn vùng:',recomputed_classification)
print('Ghép không gian và đối tượng không ghép:',evaluation['numpy_summary']['spatial_confusion'])
for name,row in evaluation['numpy_summary']['classes'].items():
    print(name,'GT <64:',row['below_64'],'GT >=64:',row['at_least_64'])
''')]
    nb = nbf.v4.new_notebook(cells=cells)
    nb.metadata.kernelspec = {'name': 'python3', 'display_name': 'Python 3', 'language': 'python'}
    nb.metadata.language_info = {'name': 'python', 'version': '3.13'}
    nbf.validate(nb)
    nbf.write(nb, output)
    print(output)


if __name__ == '__main__':
    main()
