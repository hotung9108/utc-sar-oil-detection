"""Run with: uv run --frozen --extra web streamlit run streamlit_app.py."""
import json

import streamlit as st

from scripts.demo_engine import SELECTIONS
from scripts.streamlit_service import (
    ROOT, assess_bytes, download_zip, examples, fingerprint, infer_bytes,
)

st.set_page_config(page_title='SAR • Phát hiện dầu tràn', page_icon='🌊', layout='wide')
st.title('Phát hiện dầu tràn từ ảnh SAR')
st.caption('Đề 18 · Xử lý ảnh NumPy · Kết quả thực nghiệm có nhãn tham chiếu')

with st.sidebar:
    st.header('Không gian làm việc')
    page = st.radio('Chức năng', ['Phân tích ảnh', 'Bằng chứng thực nghiệm', 'Phạm vi và hướng dẫn'])
    st.caption('Ứng dụng phục vụ nghiên cứu và báo cáo môn học. Chưa được kiểm chứng cho cảnh báo ngoài thực địa.')

if page == 'Phân tích ảnh':
    st.subheader('Tìm vùng nghi dầu')
    selection_name = st.selectbox('Pipeline đã lưu', list(SELECTIONS))
    selection = SELECTIONS[selection_name]
    source = st.radio('Nguồn ảnh', ['Ảnh mẫu có nhãn', 'Tải ảnh của bạn'], horizontal=True)
    data, truth, input_name = None, None, None
    if source == 'Ảnh mẫu có nhãn':
        rows = examples()
        if rows:
            chosen = st.selectbox('Mẫu test SOS (12 ảnh đầu theo manifest, không chọn theo điểm)',
                                  rows, format_func=lambda r: r['id'])
            data = (ROOT / chosen['image']).read_bytes()
            truth = (ROOT / chosen['mask']).read_bytes()
            input_name = chosen['id']
        else:
            st.info('Chưa có dữ liệu mẫu cục bộ. Bạn có thể tải ảnh lên ở lựa chọn bên cạnh.')
    else:
        uploaded = st.file_uploader('Ảnh SAR hiển thị 8-bit (PNG/JPEG)', type=['png', 'jpg', 'jpeg'])
        if uploaded:
            data, input_name = uploaded.getvalue(), uploaded.name
        truth_upload = st.file_uploader('Mask tham chiếu tùy chọn (PNG; dầu ≥128)', type=['png'])
        if truth_upload:
            truth = truth_upload.getvalue()
    st.caption('Không tự đổi kích thước. Tối đa 1.048.576 pixel và 16 MB. PNG không chứa đủ thông tin để hiệu chỉnh góc tới.')
    try:
        identity = fingerprint(data, selection) if data else None
    except (OSError, ValueError, KeyError) as exc:
        st.error(f'Không đọc được cấu hình/mô hình: {exc}')
        identity = None
    if st.session_state.get('identity') != identity:
        st.session_state.pop('result', None)
        st.session_state['identity'] = identity
    if st.button('Phân tích ảnh', type='primary', disabled=identity is None):
        try:
            with st.spinner('Đang lọc, tìm vùng và phân lớp bằng NumPy…'):
                result = infer_bytes(data, selection)
                result['metadata']['input_file'] = input_name
                st.session_state['result'] = result
        except (OSError, ValueError, RuntimeError) as exc:
            st.error(f'Không thể phân tích: {exc}')
    result = st.session_state.get('result')
    if result is not None:
        regions = result['metadata']['regions']
        cols = st.columns(3)
        cols[0].metric('Vùng ứng viên', len(regions))
        cols[1].metric('Vùng được nhận là dầu', sum(r['oil'] for r in regions))
        cols[2].metric('Thời gian xử lý', f"{result['metadata']['seconds_including_preview']:.3f} s")
        visual, feature_tab, eval_tab = st.tabs(['Ảnh từng bước', 'Đặc trưng và điểm', 'Đối chiếu nhãn'])
        with visual:
            columns = st.columns(3)
            for i, (key, caption) in enumerate([
                ('image', 'Ảnh đầu vào'), ('filtered', 'Sau lọc speckle'),
                ('candidates', 'Vùng tối ứng viên'), ('mask', 'Mask kết quả'), ('overlay', 'Vùng nghi dầu (đỏ)')]):
                columns[i % 3].image(result[key].astype(float), caption=caption, clamp=True, width='stretch')
        with feature_tab:
            st.caption('Score là điểm quyết định, không phải xác suất. Nhãn âm không xác định nguyên nhân look-alike.')
            st.dataframe([{'id': r['id'], 'oil': r['oil'], 'score': r['score'], **r['features']}
                          for r in regions], width='stretch')
            with st.expander('Cấu hình và nguồn gốc kết quả'):
                st.json(result['metadata'])
        evaluation = None
        with eval_tab:
            if truth:
                try:
                    evaluation = assess_bytes(result, truth)
                    metrics = evaluation['metrics']
                    columns = st.columns(3)
                    for col, name in zip(columns, ['precision', 'recall', 'f1']):
                        value = metrics[name]
                        col.metric(f'Object {name}', 'Không xác định' if value is None else f'{value:.4f}')
                    st.json(metrics)
                    st.caption('Ghép đối tượng một-một IoU ≥0,5. Mask nhãn chỉ được dùng sau suy luận. Điểm một ảnh không thay thế đánh giá toàn tập.')
                except (OSError, ValueError) as exc:
                    st.error(f'Không thể đánh giá mask: {exc}')
            else:
                st.info('Chưa có mask tham chiếu; không tính độ chính xác từ ảnh chưa có nhãn.')
        st.download_button('Tải kết quả ZIP', download_zip(result, evaluation),
                           file_name='sar_result.zip', mime='application/zip')

elif page == 'Bằng chứng thực nghiệm':
    st.subheader('Kết quả đã lưu của dự án')
    with st.expander('Sentinel-1 vật lý — Cantarell', expanded=True):
        physical = ROOT / 'docs/management/cantarell_physical_verification.json'
        screen = ROOT / 'results/cantarell/screen.json'
        trained = ROOT / 'results/cantarell/validation.json'
        evaluated = ROOT / 'results/cantarell/evaluation.json'
        if physical.exists():
            audit = json.loads(physical.read_text(encoding='utf-8'))
            st.write({'mẫu hợp lệ': audit['eligible_counts'], 'số cảnh': audit['eligible_scene_counts']})
            st.caption('Dầu thấm tự nhiên được gộp với dầu tràn; không đổi thành look-alike.')
        if screen.exists():
            candidates = json.loads(screen.read_text(encoding='utf-8'))
            st.markdown('**So sánh bước tìm vùng trên validation**')
            st.dataframe([{'nhánh': r['branch'], 'cấu hình': r['config_id'],
                'lọc': str(r['config']['filter']), 'ngưỡng': str(r['config']['threshold']),
                'F1 NumPy': r['summary']['numpy']['f1'],
                'F1 thư viện': r['summary']['reference']['f1'],
                'pixel khác': r['mask_disagreement_pixels']} for r in candidates['comparisons']], width='stretch')
            st.caption('Đây là điểm ứng viên trước phân lớp, không phải kết quả detector cuối.')
        if trained.exists():
            training = json.loads(trained.read_text(encoding='utf-8'))
            st.markdown('**So sánh SVM/CART trên validation**')
            st.dataframe([{'nhánh': r['branch'], 'cấu hình': r['config_id'], 'mô hình': r['model_id'],
                'hợp lệ': r['eligible'], 'F1': r.get('metrics', {}).get('numpy', {}).get('f1'),
                'đồng thuận': r.get('classifier_agreement'), 'lỗi': r.get('error')}
                for r in training['rows']], width='stretch')
        else:
            st.info('Chưa hoàn tất bảng so sánh mô hình Cantarell.')
        if evaluated.exists():
            evaluation = json.loads(evaluated.read_text(encoding='utf-8'))
            st.markdown('**Kết quả test sau khi khóa lựa chọn**')
            st.dataframe([{'vai trò': name, **{k:r['metrics']['numpy'][k]
                for k in ('precision', 'recall', 'f1', 'fp_per_image')}}
                for name, r in evaluation['roles'].items()], width='stretch')
        else:
            st.caption('Chưa có kết quả test Cantarell. Không dùng test để lựa chọn cấu hình.')
    path = ROOT / 'results/sos/evaluation.json'
    if path.exists():
        results = json.loads(path.read_text(encoding='utf-8'))
        table = [{'experiment': name, **{k: item['metrics'].get(k) for k in
                  ['images', 'precision', 'recall', 'f1', 'fp_per_image', 'pixel_iou']}}
                 for name, item in results.items() if isinstance(item, dict) and 'metrics' in item]
        st.dataframe(table, width='stretch')
        st.caption('Nguồn: results/sos/evaluation.json. Các miền dữ liệu không được gộp thành một điểm chung.')
    else:
        st.warning('Chưa có kết quả đánh giá SOS.')
    reports = {
        'Vì sao chọn Lee?': 'results/sos/selection_evidence/REPORT.md',
        'SOS và giới hạn': 'results/sos/REPORT.md',
        'Dầu và look-alike — QPOSD': 'results/qposd/REPORT.md',
        'Báo động giả — DARTIS': 'results/dartis/REPORT.md',
    }
    for title, relative in reports.items():
        with st.expander(title):
            path = ROOT / relative
            if path.exists():
                st.markdown(path.read_text(encoding='utf-8'))
            else:
                st.info(f'Chưa có {relative}')
else:
    st.subheader('Phạm vi sử dụng')
    st.markdown('''
1. Chọn ảnh mẫu hoặc tải PNG/JPEG SAR hiển thị 8-bit lên.
2. Chọn pipeline đã huấn luyện và bấm **Phân tích ảnh**.
3. Xem các bước, đặc trưng, mask và tải ZIP kết quả.
4. Nếu có mask dầu/nền cùng kích thước, xem đánh giá sau suy luận.

**SOS:** nhãn dầu/nền; chưa có góc tới, tọa độ/thời gian hay nhãn nguyên nhân look-alike.

**QPOSD:** bằng chứng bổ sung dầu/look-alike chung trên UAVSAR; chưa tích hợp suy luận QPOSD trong trang phân tích ảnh này.

**Cantarell:** nhánh Sentinel-1 vật lý riêng, cần hoàn tất kiểm chứng và mô hình trước khi đưa vào giao diện.

Kết quả hiện có chưa chứng minh hiệu quả cảnh báo tại biển miền Trung. Ứng dụng không suy ra tàu xả thải hoặc nguyên nhân vùng tối từ một mask.
''')
