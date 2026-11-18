"""Write QPOSD tables only from complete, provenance-checked frozen evidence."""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "src"))

import json
from pathlib import Path


from scripts._provenance import source_matches
from scripts._paths import resolve_path
from scripts.qposd.extract_qposd_regions import ROOT, digest
from scripts.qposd.evaluate_qposd_test import frozen_detection
from scripts.qposd.select_qposd_detection import frozen_classifier
from scripts.qposd.qposd_metrics import classification, summarize_detections

DEST = ROOT/'results/qposd'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def verified_results():
    evaluation = read(DEST/'evaluation.json')
    protocol = read(DEST/'protocol.json')
    assert evaluation['complete']
    assert [r['number'] for r in evaluation['images']] == protocol['splits']['test']
    for key, source in (
            ('script_sha256', 'scripts/qposd/evaluate_qposd_test.py'),
            ('pipeline_sha256', 'scripts/qposd/qposd_pipeline.py'),
            ('feature_code_sha256', 'scripts/qposd/qposd_fast_features.py'),
            ('metrics_sha256', 'scripts/qposd/qposd_metrics.py')):
        assert source_matches(ROOT/source, evaluation[key], digest(ROOT/source)), source
    for name, sha in evaluation['inputs_sha256'].items():
        assert source_matches(ROOT/name, sha, digest(ROOT/name)), name
    _, classifier = frozen_classifier()
    _, detector = frozen_detection(protocol, classifier)
    assert classifier == evaluation['classifier'] and detector == evaluation['detector']
    for backend in ('numpy', 'reference'):
        assert summarize_detections([r[backend] for r in evaluation['images']]) == evaluation[backend+'_summary']
    conditional = evaluation['conditional_rows']
    assert classification([r['truth'] for r in conditional],
                          [r['prediction'] for r in conditional]) == evaluation['conditional_classification']
    for row in evaluation['images']:
        for artifact in [*row['saved_masks'].values(), row['reference_region_features']]:
            assert source_matches(ROOT/artifact['path'], artifact['sha256'], digest(ROOT/artifact['path']))
    return protocol, read(DEST/'classifier_selection.json'), read(DEST/'detection_selection.json'), evaluation


def fmt(value):
    return 'Không xác định' if value is None else f'{value:.6f}'


def render(protocol, classifiers, candidates, evaluation):
    lines = ['# QPOSD: phân lớp và phát hiện dầu/tương tự dầu', '',
             'Dữ liệu bổ sung UAVSAR L-band; SOS vẫn là tập chính. Nguồn:',
             '[QPOSD, CC BY 4.0](https://zenodo.org/records/19258036).', '',
             '## Dữ liệu và cách chọn', '',
             '24/41 cặp có kích thước ảnh–nhãn phù hợp; loại 17 cặp không khớp, không resize nhãn.',
             'Đã kiểm tra đủ MAT, CRC/hash, giá trị hữu hạn và xem 24 cặp ảnh/nhãn.',
             'Giao thức v2 giữ nguyên nhóm giao trùng chính xác {19,20} và {21,22,33,35}.',
             'Không có điểm test từ v1. Kiểm tra giao trùng không chứng minh độc lập cảnh.', '']
    for split, numbers in protocol['splits'].items():
        lines.append(f'- {split}: {numbers}')
    lines += ['', 'Chọn mô hình bằng macro-F1 phân lớp trên vùng tham chiếu validation, sau đó',
              'chọn cấu hình tìm vùng bằng macro-F1 đối tượng validation. Cố định IoU ≥ 0,5,',
              'ghép một-một; hòa điểm dùng thứ tự cấu hình. Không chọn theo test.', '',
              '## Mười bộ phân lớp (cùng đặc trưng NumPy)', '',
              '| ID | Cấu hình | Macro-F1 NumPy | Macro-F1 thư viện | Đồng thuận |',
              '|---:|---|---:|---:|---:|']
    for r in classifiers['configurations']:
        lines.append(f"| {r['index']} | {r['config']} | {fmt(r['numpy_validation']['macro_f1'])} | {fmt(r['reference_validation']['macro_f1'])} | {fmt(r['prediction_agreement'])} |")
    lines += ['', f"Được chọn: ID {classifiers['winner_index']}. Đây là phân lớp có sẵn vùng, không phải phát hiện.", '',
              '## Mười cấu hình tìm vùng (cùng mô hình NumPy đã khóa)', '',
              '| ID | Cấu hình | Macro-F1 NumPy | Macro-F1 thư viện |',
              '|---:|---|---:|---:|']
    for r in candidates['configurations']:
        lines.append(f"| {r['index']} | {r['config']} | {fmt(r['numpy_summary']['macro_f1'])} | {fmt(r['reference_summary']['macro_f1'])} |")
    lines += ['', f"Được chọn: ID {candidates['winner_index']}.", '',
              '## Toàn bộ năm ảnh test', '',
              '| Phép đo | Lớp | TP | FP | FN | Precision | Recall | F1 |',
              '|---|---|---:|---:|---:|---:|---:|---:|']
    for title, result in [('Phân lớp có sẵn vùng', evaluation['conditional_classification']),
                          ('Phát hiện NumPy', evaluation['numpy_summary']),
                          ('Phát hiện thư viện', evaluation['reference_summary'])]:
        for name, row in result['classes'].items():
            lines.append('| '+title+' | '+name+' | '+' | '.join(
                str(row[k]) for k in ('tp', 'fp', 'fn'))+' | '+' | '.join(
                fmt(row[k]) for k in ('precision', 'recall', 'f1'))+' |')
    cm = evaluation['conditional_classification']
    spatial = evaluation['numpy_summary']['spatial_confusion']
    lines += ['', '## Nhầm lẫn và đối tượng nhỏ', '',
              f"Phân lớp có sẵn vùng: dầu → tương tự dầu = {fmt(cm['oil_as_look_alike_rate'])}; tương tự dầu → dầu = {fmt(cm['look_alike_as_oil_rate'])}.",
              'Tỷ lệ là phân số từ 0 đến 1. Ma trận có hàng thật, cột dự đoán.',
              f"Ma trận phân lớp [tương tự dầu, dầu]: `{cm['confusion_true_by_predicted']}`.",
              f"Ma trận ghép không gian [dầu, tương tự dầu]: `{spatial['true_by_predicted']}`.",
              f"GT không ghép: `{spatial['unmatched_truth']}`; dự đoán không ghép: `{spatial['unmatched_predictions']}`.",
              'Ma trận ghép không gian chỉ mô tả đối tượng ghép được, không thay thế Recall.', '',
              '| Lớp | Kích thước GT | GT | TP | Recall |', '|---|---|---:|---:|---:|']
    for name, row in evaluation['numpy_summary']['classes'].items():
        for size in ('below_64', 'at_least_64'):
            r = row[size]
            lines.append(f"| {name} | {size} | {r['gt']} | {r['tp']} | {fmt(r['recall'])} |")
    lines += ['', '## Giới hạn và tái tạo', '',
              '- Nhãn tương tự dầu là lớp chung; không có nhãn nguyên nhân gió yếu/màng sinh học/mưa.',
              '- Năm ảnh test đã được xem để kiểm tra ảnh–nhãn; không gọi đây là đánh giá mù.',
              '- Phân đoạn liên thông từ mask không tương đương số sự kiện dầu độc lập.',
              '- Diện tích tối thiểu 64 chỉ áp dụng ứng viên; giữ cả GT nhỏ khi đánh giá.',
              '- Không suy góc tới hoặc gió từ T11. Chưa kiểm chứng trên vùng biển Việt Nam.',
              '- Nhánh thư viện dùng cùng classifier NumPy để tách khác biệt phép xử lý ảnh.',
              '- Thời gian từng lượt không phải benchmark kiểm soát tải máy.', '',
              'Chạy `python scripts/qposd/report_qposd.py` sau khi có đủ kết quả. Script xác minh hash,',
              'lựa chọn đã khóa, số ảnh, mask đã lưu và tổng hợp lại các số đếm trước khi viết bảng.',
              'Notebook 10 chạy lại suy luận hai backend, đối chiếu mask từng pixel và hiển thị năm ảnh test.', '']
    return '\n'.join(lines)


def main():
    result = verified_results()
    path = DEST/'REPORT.md'
    path.write_text(render(*result), encoding='utf-8')
    print(path)


if __name__ == '__main__':
    main()
