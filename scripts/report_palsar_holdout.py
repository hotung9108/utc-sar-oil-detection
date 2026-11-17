"""Verify complete frozen PALSAR results before writing the supplementary report."""
import json

from evaluate_palsar_holdout import ROOT, DEST, definition, digest, read, records, ensure_run, summarize


def verified_results():
    ensure_run()
    protocol = read(DEST / 'protocol.json')
    assert protocol == definition(), 'Frozen sources differ'
    expected = {r['id']: r for r in records('external_train')}
    assert len(expected) == 3101
    for row in expected.values():
        for key in ('image', 'mask'):
            assert digest(ROOT / row[key]) == row[key + '_sha256']
    results = {}
    for name in protocol['models']:
        report = read(DEST / f'{name}.json')
        rows = report['per_image']
        assert report['protocol_sha256'] == digest(DEST / 'protocol.json')
        assert report['complete'] and report['expected'] == report['completed'] == 3101
        assert len(rows) == 3101 and {r['id'] for r in rows} == set(expected)
        for row in rows:
            source = expected[row['id']]
            for key in ('image_sha256', 'mask_sha256'):
                assert row[key] == source[key]
            c = row['counts']
            assert c['images'] == 1
            assert all(isinstance(v, int) and v >= 0 for v in c.values())
            assert c['intersection'] <= min(c['predicted_pixels'], c['truth_pixels'])
            assert c['union'] == c['predicted_pixels'] + c['truth_pixels'] - c['intersection']
            assert c['union'] <= 256 * 256
            assert c['edge_tp'] + c['interior_tp'] == c['tp']
            assert c['edge_gt'] + c['interior_gt'] == c['tp'] + c['fn']
        assert summarize([r['counts'] for r in rows]) == report['metrics']
        results[name] = report
    return results


def main():
    results = verified_results()
    lines = ['# Đánh giá bổ sung trên 3.101 patch PALSAR', '',
             'Quần thể: toàn bộ `external_train` của manifest SOS. Đây là tập tác giả gọi',
             '`train`, nhưng không dùng để fit hoặc chọn cấu hình trong pipeline hiện tại.',
             'Hai mô hình được khóa trước suy luận; không chọn mô hình thắng hoặc chỉnh lại',
             'tham số từ phép thử này. Giao thức: `protocol.json`.', '',
             '| Nhánh NumPy | Ảnh | TP | FP | FN | Precision | Recall | F1 | IoU pixel |',
             '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for name, report in results.items():
        m = report['metrics']
        lines.append(f"| {name} | {m['images']} | {m['tp']} | {m['fp']} | {m['fn']} | {m['precision']:.6f} | {m['recall']:.6f} | {m['f1']:.6f} | {m['pixel_iou']:.6f} |")
    lines += ['', '## Giới hạn', '',
              '- Đây là phép thử bổ sung chuyển sensor, không phải tập Sentinel mới ngoài khơi Việt Nam.',
              '- Kiểm tra hash và pixel trùng hoàn toàn không chứng minh độc lập theo cảnh hoặc loại trừ patch chồng lấn.',
              '- Chưa xác minh lịch sử mọi lần xem thủ công dữ liệu; chỉ kiểm tra luồng fit/search và kết quả pipeline hiện tại.',
              '- Hai pipeline khác cả bộ lọc/tham số lẫn classifier; không quy chênh lệch riêng cho Otsu hoặc Niblack.',
              '- Nguồn nhãn SOS là dầu/nền, không phân biệt từng nguyên nhân look-alike.',
              '- Kết quả không thay thế các test SOS trước đó; không gộp các tập có khả năng chung cảnh.', '',
              '## Tái tạo', '', '```text',
              'python scripts/audit_palsar_holdout.py',
              'python scripts/evaluate_palsar_holdout.py --prepare',
              'python scripts/evaluate_palsar_holdout.py --run --workers 4',
              'python scripts/report_palsar_holdout.py', '```', '']
    (DEST / 'REPORT.md').write_text('\n'.join(lines), encoding='utf-8')
    audit = {'complete_population_verified': True, 'images_per_pipeline': 3101,
             'protocol_sha256': digest(DEST / 'protocol.json'),
             'result_sha256': {name: digest(DEST / f'{name}.json') for name in results},
             'metrics': {name: r['metrics'] for name, r in results.items()},
             'scene_independence_verified': False,
             'scope': 'Reaggregated counts and verified image/mask/model provenance, not an independent reimplementation of the object matcher.'}
    (ROOT / 'docs/management/palsar_evaluation_audit.json').write_text(json.dumps(audit, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(audit['metrics'], indent=2))


if __name__ == '__main__':
    main()
