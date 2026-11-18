"""User-facing explanations; no model selection or inference changes."""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "scripts"))

import io
import json

import streamlit as st
import numpy as np
from PIL import Image

from scripts.web.streamlit_service import ROOT, MAX_UPLOAD


def introduction(page):
    descriptions = {
        'Phân tích ảnh': ('01 · THỬ VỚI ẢNH SAR', 'Bắt đầu bằng một ảnh mẫu',
            'Chọn ảnh → chạy phân tích → xem vùng nghi dầu và đối chiếu nhãn. Ảnh mẫu đã có nhãn để bạn kiểm tra ngay kết quả.'),
        'Dầu và look-alike': ('02 · PHÂN BIỆT VÙNG TỐI', 'Vùng tối có phải là dầu?',
            'Dùng mẫu UAVSAR của QPOSD để phân biệt dầu và vùng tương tự dầu. Đây là mô hình riêng cho bộ dữ liệu này.'),
        'Sentinel-1 vật lý': ('03 · DỮ LIỆU CÓ METADATA', 'Theo dõi xử lý ảnh Sentinel-1',
            'Mẫu Cantarell có góc tới và gió đi kèm. Xem kết quả của chuỗi gamma0 → Lee → Niblack → SVM.'),
        'Bằng chứng thực nghiệm': ('04 · KIỂM CHỨNG', 'Các con số nói điều gì?',
            'Xem chất lượng trên toàn bộ tập kiểm tra, rồi mở bảng đối chứng để tìm hiểu cách chọn thuật toán.'),
        'Phạm vi và hướng dẫn': ('05 · TRỢ GIÚP', 'Chọn đúng dữ liệu, đọc đúng kết quả',
            'Hướng dẫn cho người mới dùng và giải thích các thuật ngữ xuất hiện trong ứng dụng.'),
    }
    eyebrow, title, text = descriptions[page]
    st.caption(eyebrow)
    st.header(title)
    st.write(text)


def preview(data):
    """Validate display input before enabling an expensive inference action."""
    if not data:
        st.info('Chưa có ảnh. Chọn ảnh mẫu hoặc tải một ảnh SAR PNG/JPEG để bắt đầu.')
        return False
    try:
        if len(data) > MAX_UPLOAD:
            raise ValueError('Ảnh vượt quá 16 MB.')
        with Image.open(io.BytesIO(data)) as image:
            if image.mode not in {'L', 'RGB', 'RGBA', 'P'}:
                raise ValueError('Cần ảnh hiển thị 8-bit; ảnh SAR 16-bit cần xử lý vật lý trước.')
            width, height = image.size
            if width * height > 1024 * 1024 or min(width, height) < 2:
                raise ValueError('Mỗi chiều ít nhất 2 pixel, tổng không quá 1.048.576 pixel.')
            image.load()
            left, right = st.columns([1, 3])
            left.image(image, caption=f'{width} × {height} pixel', width=160)
            with right:
                st.markdown('**Ảnh đã sẵn sàng**')
                st.write('Bấm **Phân tích ảnh** để tìm các vùng tối và phân lớp. Màu đỏ trong kết quả biểu thị vùng mô hình nghi là dầu.')
                st.caption('Ảnh màu được chuyển sang thang xám. Không thay đổi kích thước ảnh; không suy ra diện tích km² từ PNG.')
        return True
    except (OSError, ValueError, Image.DecompressionBombError) as exc:
        st.error(f'Không đọc được ảnh: {exc} Hãy chọn tệp PNG/JPEG 8-bit hợp lệ.')
        return False


def explain_config(selection):
    try:
        config = json.loads(selection.read_text(encoding='utf-8'))['config']
        filt, threshold = config['filter'], config['threshold']
        st.caption(f"Chuỗi xử lý: {filt['name'].upper()} → {threshold['name'].upper()} → 8 đặc trưng vùng → phân lớp.")
        with st.expander('Pipeline này làm gì?'):
            st.markdown('''1. **Lọc speckle:** giảm nhiễu hạt trong ảnh radar.
2. **Tìm vùng tối:** ngưỡng Otsu dùng toàn ảnh; Niblack dùng thống kê lân cận.
3. **Đo đặc trưng:** hình dạng, cường độ và tương phản với vùng xung quanh.
4. **Phân lớp:** SVM hoặc cây quyết định nhận/loại từng vùng ứng viên.

Cấu hình đã được chọn trong thực nghiệm. Trang này dùng mô hình đã lưu; không huấn luyện trên ảnh bạn tải lên.''')
            st.json(config, expanded=False)
    except (OSError, KeyError, ValueError):
        st.caption('Chưa đọc được mô tả cấu hình. Kiểm tra mô hình cục bộ trước khi chạy.')


def result_summary(result):
    regions = result['metadata']['regions']
    oil = sum(bool(row['oil']) for row in regions)
    if oil:
        st.info(f'Mô hình nhận {oil}/{len(regions)} vùng ứng viên là nghi dầu. Hãy xem lớp phủ đỏ và đối chiếu nhãn nếu có; đây chưa phải xác nhận dầu ngoài thực địa.')
    else:
        st.info(f'Mô hình không nhận vùng nào là dầu trong {len(regions)} ứng viên. Kết quả này không chứng minh ảnh không có dầu: mô hình có thể bỏ sót.')


def metric_help(metrics):
    st.markdown(f"**Phát hiện đúng: {metrics['tp']} vùng · Báo nhầm: {metrics['fp']} vùng · Bỏ sót: {metrics['fn']} vùng**")
    st.caption('Precision: trong các vùng báo dầu, bao nhiêu vùng đúng? Recall: trong các vùng dầu thật, tìm được bao nhiêu? F1: cân bằng hai tỷ lệ. Giá trị từ 0 đến 1; cao hơn là tốt hơn.')
    with st.expander('Cách chấm điểm và ý nghĩa “không xác định”'):
        st.write('Mỗi vùng dự đoán chỉ ghép với một vùng nhãn, với IoU ≥ 0,5. IoU là diện tích giao chia diện tích hợp. Điểm không xác định khi mẫu số bằng 0; không tự thay bằng điểm hoàn hảo. Điểm ảnh hiện tại không đại diện cho toàn bộ tập kiểm tra.')


def truth_comparison(result, data):
    with Image.open(io.BytesIO(data)) as image:
        truth = np.asarray(image.convert('L')) >= 128
    prediction = result['mask'].astype(bool)
    # Pixel overlap is a visual diagnostic, not the object-level matching metric.
    overlay = np.repeat(result['image'][..., None], 3, axis=2) * .35
    overlay[truth & prediction] = [0, .8, .65]
    overlay[prediction & ~truth] = [1, .55, .1]
    overlay[truth & ~prediction] = [.65, .35, 1]
    left, right = st.columns(2)
    left.image(truth.astype(float), caption='Nhãn tham chiếu · trắng = dầu được gán nhãn', width='stretch')
    right.image(overlay, caption='So sánh pixel · xanh ngọc = trùng · cam = chỉ dự đoán · tím = chỉ nhãn', width='stretch')
    st.caption('Màu so sánh thể hiện giao nhau theo pixel. Các số TP/FP/FN bên dưới được chấm theo đối tượng, không phải đếm pixel màu.')


def feature_help():
    with st.expander('Đọc bảng đặc trưng như thế nào?'):
        st.markdown('''- **Area fraction:** diện tích vùng chia tổng số pixel ảnh, không phải km².
- **Elongation:** độ thuôn dài; **extent:** mức lấp đầy hình chữ nhật bao vùng.
- **Complexity:** độ phức tạp đường biên.
- **Mean / std:** cường độ trung bình và độ phân tán trong vùng.
- **Boundary gradient:** mức thay đổi cường độ tại biên.
- **Contrast:** khác biệt với nền lân cận.

`oil=True` là vùng mô hình nhận là dầu. `score` là điểm quyết định, **không phải phần trăm tin cậy**; không so trực tiếp score giữa các mô hình. Một đặc trưng riêng lẻ không đủ xác nhận dầu.''')


def evidence_overview():
    st.markdown('### Chất lượng trên tập kiểm tra')
    rows = []
    sources = [('SOS · dầu/nền', 'results/sos/evaluation.json', ('test_final', 'metrics')),
               ('Cantarell · có lọc speckle', 'results/cantarell/evaluation.json', ('roles', 'filtered_adaptive', 'metrics', 'numpy'))]
    for name, filename, keys in sources:
        try:
            value = json.loads((ROOT / filename).read_text(encoding='utf-8'))
            for key in keys:
                value = value[key]
            rows.append({'Bộ kiểm tra': name, 'Số ảnh': value['images'],
                         'Precision': value['precision'], 'Recall': value['recall'], 'F1': value['f1']})
        except (OSError, KeyError, ValueError):
            st.info(f'Chưa đọc được kết quả {name}.')
    if rows:
        st.dataframe(rows, hide_index=True, width='stretch')
    try:
        q = json.loads((ROOT / 'results/qposd/evaluation.json').read_text(encoding='utf-8'))
        st.write(f"**QPOSD · Macro-F1 phát hiện đầu-cuối: {q['numpy_summary']['macro_f1']:.4f}**. Khi đã có sẵn vùng nhãn, Macro-F1 phân lớp là {q['conditional_classification']['macro_f1']:.4f}. Hai điểm này trả lời hai câu hỏi khác nhau; không dùng điểm phân lớp có sẵn vùng để thay thế điểm phát hiện.")
    except (OSError, KeyError, ValueError):
        pass
    st.write('Các tập dữ liệu và nhiệm vụ khác nhau nên không xếp hạng các pipeline bằng bảng này. Điểm còn thấp cho thấy mô hình bỏ sót/báo nhầm nhiều; cần xem cả Precision và Recall.')


def guide():
    st.markdown('### Tôi nên chọn màn hình nào?')
    st.dataframe([
        {'Bạn muốn': 'Thử nhanh hoặc tải ảnh SAR PNG/JPEG', 'Chọn': 'Phân tích ảnh', 'Dữ liệu': 'SOS · ảnh 8-bit; mask tùy chọn'},
        {'Bạn muốn': 'Xem dầu khác vùng tương tự dầu ra sao', 'Chọn': 'Dầu và look-alike', 'Dữ liệu': 'QPOSD · mẫu UAVSAR có sẵn'},
        {'Bạn muốn': 'Xem góc tới, gió và pipeline vật lý', 'Chọn': 'Sentinel-1 vật lý', 'Dữ liệu': 'Cantarell · mẫu đã xác minh'},
        {'Bạn muốn': 'Tìm số liệu và lý do chọn thuật toán', 'Chọn': 'Bằng chứng thực nghiệm', 'Dữ liệu': 'Kết quả thực nghiệm đã lưu'},
    ], hide_index=True, width='stretch')
    with st.expander('Chuẩn bị ảnh và mask tham chiếu', expanded=True):
        st.write('Ảnh phải là ảnh SAR hiển thị 8-bit PNG/JPEG, tối đa 16 MB và 1.048.576 pixel. Ảnh chụp biển thông thường không thuộc miền mô hình. Mask là PNG cùng kích thước và căn chỉnh: pixel ≥128 là dầu. Mask là nhãn do nguồn dữ liệu/người gán nhãn cung cấp, không phải mask dự đoán của chính mô hình.')
    with st.expander('Vì sao vùng tối chưa chắc là dầu?'):
        st.write('Dầu có thể làm mặt biển tối trên ảnh radar, nhưng gió yếu, màng sinh học hoặc mưa cũng có thể tạo vùng tối. SOS chỉ đánh giá dầu/nền; QPOSD có lớp tương tự dầu chung, chưa xác định riêng từng nguyên nhân.')
    with st.expander('Tải kết quả về để làm gì?'):
        st.write('ZIP chứa ảnh kết quả và regions.json lưu đặc trưng, cấu hình, nguồn mô hình, cùng điểm đối chiếu nếu có nhãn. SOS/Cantarell xuất mask dầu/nền; QPOSD xuất classes.png với 0=nền, 1=dầu, 2=tương tự dầu. Dùng các tệp này để kiểm tra lại, không coi chúng là nhãn chuẩn mới.')
    with st.expander('Đổi ảnh nhưng không thấy kết quả cũ?'):
        st.write('Kết quả được xóa khi đổi ảnh hoặc cấu hình để tránh gán kết quả cũ cho ảnh mới. Bấm phân tích lại. Nếu dữ liệu mẫu không có trên máy, hãy tải ảnh ở trang Phân tích ảnh hoặc đọc Bằng chứng thực nghiệm.')
    feature_help()
