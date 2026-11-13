"""Write the DARTIS report only after validating every image and aggregate."""
import hashlib
import json
from pathlib import Path
from dartis_results import verified_results

ROOT = Path(__file__).resolve().parents[1]


def main():
    result = verified_results()
    rows = [('Toàn bộ', result['overall']), ('Bờ (nc)', result['by_subset']['nc']),
            ('Biển (nw)', result['by_subset']['nw'])]
    lines = ['# Kiểm tra báo nhầm trên DARTIS no-oil', '',
        'Mô hình SOS được giữ nguyên; không huấn luyện lại hoặc chọn tham số theo kết quả DARTIS.',
        'Giao thức đã cố định trước suy luận: `protocol.json`. Đầu vào giữ nguyên kích thước,',
        'PIL grayscale chia 255; một ảnh báo nhầm nếu có ít nhất một vùng được giữ là dầu.', '',
        '| Tập | Ảnh | Ảnh báo nhầm | Tỷ lệ báo nhầm | Vùng/ảnh | Pixel dự đoán dầu |',
        '|---|---:|---:|---:|---:|---:|']
    for label,r in rows:
        lines.append(f"| {label} | {r['images']} | {r['false_alarm_images']} | {r['false_alarm_rate']:.4%} | {r['retained_regions_per_image']:.4f} | {r['predicted_oil_pixel_fraction']:.4%} |")
    lines += ['', '## Theo cụm do nhà phát hành cung cấp', '',
        'Các mã cụm là nhóm K-means; không phải nhãn gió yếu, màng sinh học hay mưa.', '',
        '| Cụm | Ảnh | Ảnh báo nhầm | Tỷ lệ |', '|---|---:|---:|---:|']
    for key,r in sorted(result['by_cluster'].items()):
        lines.append(f"| {key} | {r['images']} | {r['false_alarm_images']} | {r['false_alarm_rate']:.4%} |")
    lines += ['', '## Giới hạn diễn giải', '',
        '- Tập này chỉ có nhãn no-oil: không ước lượng Recall dầu hoặc F1 toàn bài.',
        '- Báo nhầm mức ảnh không cùng đại lượng với Precision/Recall/F1 đối tượng SOS.',
        '- Có patch chung cảnh; không giả định các patch độc lập để tính khoảng tin cậy.',
        '- JPEG, độ phân giải và tiền xử lý DARTIS khác SOS. Không quy toàn bộ sai lệch cho một yếu tố.',
        '- Nhãn tham chiếu do nhà phát hành cung cấp; không phải xác nhận hiện trường của nhóm.',
        '- Chưa phải kiểm chứng theo từng loại look-alike vật lý hoặc vùng biển Việt Nam.', '',
        '## Bằng chứng và tái tạo', '',
        'Nguồn: [DARTIS, PANGAEA](https://doi.pangaea.de/10.1594/PANGAEA.980773).',
        'Kết quả từng ảnh, hash, số vùng và pixel: `evaluation.json`.',
        'Notebook: `notebooks/external/06_dartis_false_alarms.ipynb`.', '', '```text',
        'python scripts/download_dartis.py --workers 1',
        'python scripts/evaluate_dartis.py --workers 4',
        'python scripts/report_dartis.py',
        'python scripts/run_notebooks.py --notebook notebooks/external/06_dartis_false_alarms.ipynb',
        '```', '']
    directory = ROOT/'results/dartis'
    (directory/'REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
    audit = {'all_2290_images_present_and_hashed':True,'per_image_counts_reaggregated':True,
        'model_and_protocol_hashes_match':True,
        'evaluation_sha256':hashlib.sha256((directory/'evaluation.json').read_bytes()).hexdigest(),
        'report_sha256':hashlib.sha256((directory/'REPORT.md').read_bytes()).hexdigest(),
        'validator_sha256':hashlib.sha256((ROOT/'scripts/dartis_results.py').read_bytes()).hexdigest(),
        'scope':'Evidence consistency, not independent validation of publisher labels'}
    (ROOT/'docs/management/dartis_evaluation_audit.json').write_text(json.dumps(audit,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result['overall'],indent=2))


if __name__=='__main__': main()
