"""Recompute the full-source inventory summary from saved audit evidence."""
import csv
import hashlib
import io
import json
from collections import Counter, defaultdict

from audit_cantarell_all import fetch
from audit_cantarell_source import ROOT


def main():
    folder = ROOT / 'docs/management'
    inventory = json.loads((folder / 'cantarell_full_inventory.json').read_text())
    scenes = json.loads((folder / 'cantarell_scenes_audit.json').read_text())
    for evidence, name in ((inventory, 'audit_cantarell_all.py'), (scenes, 'resolve_cantarell_scenes.py')):
        if hashlib.sha256((ROOT / 'scripts' / name).read_bytes()).hexdigest() != evidence['script_sha256']:
            raise ValueError('Audit script changed; regenerate evidence')
    if not inventory['complete_inventory'] or not scenes['complete']:
        raise ValueError('Cannot publish complete inventory for incomplete evidence')
    samples = inventory['samples']
    if len(samples) != inventory['expected_samples'] or len({r['sample'] for r in samples}) != len(samples):
        raise ValueError('Inventory count mismatch')
    group_to_scene = {r['group']: r for r in scenes['results']}
    for sample in samples:
        if group_to_scene[sample['group']]['split'] != sample['split']:
            raise ValueError('Scene/sample split mismatch')
    pixels = sum((Counter(r['mask_counts']) for r in samples), Counter())
    vector_ids = Counter(p['ID_POLY'] for r in samples for p in r['vector_properties'])
    raw, _ = fetch('CSV/Oil_Stats_manual_windows_16bits_800x600.csv')
    csv_rows = list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig')), delimiter=';'))
    csv_ids = Counter(r['ID_POLY'] for r in csv_rows)
    missing, extra = set(csv_ids)-set(vector_ids), set(vector_ids)-set(csv_ids)
    if missing or extra:
        raise ValueError(f'CSV/vector ID coverage differs: {missing=}, {extra=}')
    split_images, split_scenes = Counter(r['split'] for r in samples), Counter(r['split'] for r in scenes['results'])
    cross_ids = defaultdict(set)
    for sample in samples:
        for prop in sample['vector_properties']:
            cross_ids[prop['ID_POLY']].add(sample['split'])
    crossing = {k: sorted(v) for k, v in cross_ids.items() if len(v)>1}
    rows = '\n'.join(f'| {s} | {split_images[s]} | {split_scenes[s]} |' for s in ('train', 'val', 'test'))
    ambiguous = [r for r in samples if r['oil_seepage_vector_overlap_pixels']]
    details = '\n'.join(f"- `{r['sample']}`: {r['oil_seepage_vector_overlap_pixels']} pixel hai lớp vector chồng nhau." for r in ambiguous)
    collision_details = '\n'.join(f"- `{r['ID_POLY']}` trong `{r['IMG_FNAME']}`: tâm ({r['CENTR_KM_LAT']}, {r['CENTR_KM_LON']}), diện tích {r['AREA_KM2']} km²."
                                  for r in csv_rows if r['ID_POLY'] in crossing)
    text = f'''# Kiểm kê toàn bộ Cantarell trước thí nghiệm

Nguồn được ghim tại revision `{inventory['revision']}`. Tái tạo bằng `python scripts/report_cantarell_inventory.py` sau hai script kiểm kê. Không có chỉ số phát hiện hoặc lựa chọn thuật toán trong báo cáo này.

| Tập | Tile | Cảnh Sentinel đầy đủ |
|---|---:|---:|
{rows}

- Đã đọc {len(samples)}/{inventory['expected_samples']} TIFF, mask và GeoJSON; không có lỗi tải/đọc.
- Kiểu ảnh: {dict(Counter(r['dtype'] for r in samples))}; tổng pixel không hữu hạn: {sum(r['nonfinite_pixels'] for r in samples)}.
- Pixel mask: {dict(sorted(pixels.items()))}. 0=nền; 1=dầu tràn; 2=dầu thấm tự nhiên, theo đối chiếu vector bên dưới.
- Sai khác nhị phân giữa mask > 0 và polygon tại tâm pixel: {sum(r['foreground_vector_mask_disagreement'] for r in samples)} pixel trên toàn bộ tập.
- TIFF trùng nguyên tệp: {len(inventory['identical_tiff_groups'])} nhóm. Đây không thay thế phát hiện mọi kiểu crop/biến đổi trùng nhau.
- Cặp bounding box chồng nhau trong cùng cảnh: {len(inventory['same_source_overlapping_pairs'])}; trong đó khác split: {sum(r['cross_split'] for r in inventory['same_source_overlapping_pairs'])}.
- Mã cảnh đầy đủ xuất hiện ở nhiều split: {scenes['cross_split_full_scene_ids']}.
- Mã polygon xuất hiện ở nhiều split: {crossing}.

## Mã lớp và polygon trùng

{details}

Khi xét từng lớp riêng, hai mẫu trên có sai khác vì polygon dầu và dầu thấm chồng nhau. Quy tắc thử nghiệm “lớp dầu thấm ưu tiên ở phần chồng” cho số mẫu còn sai khác: **{len(inventory['seepage_priority_encoding_disagreement_samples'])}**. Đây là đối chiếu encoding của tệp; không sửa nhãn và không biến dầu thấm thành look-alike.

Bảng CSV có {len(csv_rows)} dòng nhưng {len(csv_ids)} mã polygon duy nhất; mã lặp trong CSV: {dict((k,v) for k,v in csv_ids.items() if v>1)}. Các GeoJSON chứa {sum(vector_ids.values())} lượt polygon, {len(vector_ids)} mã duy nhất; {sum(v>1 for v in vector_ids.values())} mã xuất hiện ở nhiều tile. Không được cộng các lượt này thành số sự kiện dầu độc lập. Tập mã CSV và vector khớp hoàn toàn.

### Mã polygon lặp qua split

{collision_details}

Hai bản ghi có thời điểm, vị trí và diện tích khác nhau. Mã lặp tự nó chưa chứng minh trùng ảnh hoặc cùng sự kiện, nhưng cũng không được bỏ qua khi chia tập. Trước khi khóa thí nghiệm, phải xử lý nhóm mã chưa rõ này hoặc ghi rõ giới hạn về độc lập sự kiện; chưa tự đổi split của tác giả trong kiểm kê này.

## Giới hạn

24 ID cảnh đã đối chiếu catalog ASF và productInfo công khai; phân tách theo cảnh không chứng minh độc lập sự kiện dầu hoặc thời tiết. Phép kiểm kê hình học đã chạy đủ tập, chưa xem trực quan từng ảnh. Chưa khôi phục ảnh DN/góc tới cho toàn bộ 173 tile; mới hai tile cùng cảnh có kiểm tra căn chỉnh. Chưa xác nhận toàn bộ lịch sử xử lý hoặc đơn vị TIFF xuất. SOS vẫn là bộ dữ liệu chính; gói review v4 không thay đổi.

Chứng cứ chi tiết: `cantarell_full_inventory.json`, `cantarell_scenes_audit.json`; từng tài nguyên có URL, SHA-256 và kiểm tra Git LFS khi áp dụng.
'''
    destination = folder / 'CANTARELL_FULL_INVENTORY.md'
    destination.write_text(text, encoding='utf-8')
    print(destination)


if __name__ == '__main__':
    main()
