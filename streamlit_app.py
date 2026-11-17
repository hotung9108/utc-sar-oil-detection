"""Run with: uv run --frozen --extra web streamlit run streamlit_app.py."""
import json
import re

import streamlit as st
from scripts.web import streamlit_ux as ux

from scripts.desktop.demo_engine import SELECTIONS
from scripts.web.streamlit_service import (
    ROOT, assess_bytes, download_zip, examples, fingerprint, infer_bytes,
)


def show_evidence_markdown(path):
    """Serve local figures through Streamlit instead of broken relative web URLs."""
    source = path.read_text(encoding='utf-8')
    offset = 0
    for match in re.finditer(r'!\[([^\]]*)\]\(([^)]+)\)', source):
        st.markdown(source[offset:match.start()])
        asset = (path.parent / match.group(2)).resolve()
        if asset.is_relative_to(ROOT.resolve()) and asset.is_file():
            st.image(str(asset), caption=match.group(1), width='stretch')
        else:
            st.caption(f'Hình chưa có cục bộ: {match.group(1)}')
        offset = match.end()
    st.markdown(source[offset:])

st.set_page_config(page_title='SAR • Phát hiện dầu tràn', page_icon='🌊', layout='wide')
st.caption('PHÁT HIỆN DẦU TRÀN TỪ ẢNH SAR · Đề 18 · Xử lý ảnh NumPy')

with st.sidebar:
    st.header('Không gian làm việc')
    page = st.radio('Chức năng', ['Phân tích ảnh', 'Dầu và look-alike', 'Sentinel-1 vật lý', 'Bằng chứng thực nghiệm', 'Phạm vi và hướng dẫn'])
    st.caption('Ứng dụng phục vụ nghiên cứu và báo cáo môn học. Chưa được kiểm chứng cho cảnh báo ngoài thực địa.')
    with st.expander('Bắt đầu ở đâu?'):
        st.write('Lần đầu sử dụng: chọn **Phân tích ảnh**, giữ ảnh mẫu rồi bấm phân tích. Muốn hiểu các thuật ngữ, mở **Phạm vi và hướng dẫn**.')

ux.introduction(page)

if page == 'Phân tích ảnh':
    st.subheader('1. Chọn ảnh và cách xử lý')
    with st.expander('Cách xử lý · mặc định dùng SOS đã đánh giá test'):
        selection_name = st.selectbox('Pipeline đã lưu', list(SELECTIONS))
        ux.explain_config(SELECTIONS[selection_name])
    selection = SELECTIONS[selection_name]
    if 'chỉ validation' in selection_name:
        st.info('Đây là nhánh bổ sung mới đánh giá validation. Không coi điểm của nhánh này là kết quả test độc lập.')
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
    valid_input = ux.preview(data)
    try:
        identity = fingerprint(data, selection) if valid_input else None
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
        st.subheader('2. Đọc kết quả phân tích')
        ux.result_summary(result)
        regions = result['metadata']['regions']
        cols = st.columns(3)
        cols[0].metric('Vùng ứng viên', len(regions))
        cols[1].metric('Vùng được nhận là dầu', sum(r['oil'] for r in regions))
        cols[2].metric('Thời gian xử lý', f"{result['metadata']['seconds_including_preview']:.3f} s")
        visual, feature_tab, eval_tab = st.tabs(['Ảnh từng bước', 'Đặc trưng và điểm', 'Đối chiếu nhãn'])
        with visual:
            st.caption('Đọc từ ảnh gốc → lọc nhiễu → vùng tối → mask dự đoán → lớp phủ. Trắng trong mask là dầu dự đoán; đỏ trong lớp phủ là cùng vùng đó trên ảnh gốc.')
            columns = st.columns(3)
            for i, (key, caption) in enumerate([
                ('image', 'Ảnh đầu vào'), ('filtered', 'Sau lọc speckle'),
                ('candidates', 'Vùng tối ứng viên'), ('mask', 'Mask kết quả'), ('overlay', 'Vùng nghi dầu (đỏ)')]):
                columns[i % 3].image(result[key].astype(float), caption=caption, clamp=True, width='stretch')
        with feature_tab:
            ux.feature_help()
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
                    ux.truth_comparison(result, truth)
                    metrics = evaluation['metrics']
                    columns = st.columns(3)
                    for col, name in zip(columns, ['precision', 'recall', 'f1']):
                        value = metrics[name]
                        col.metric(f'Object {name}', 'Không xác định' if value is None else f'{value:.4f}')
                    ux.metric_help(metrics)
                    with st.expander('Tất cả số đo của ảnh này'):
                        st.json(metrics)
                    st.caption('Ghép đối tượng một-một IoU ≥0,5. Mask nhãn chỉ được dùng sau suy luận. Điểm một ảnh không thay thế đánh giá toàn tập.')
                except (OSError, ValueError) as exc:
                    st.error(f'Không thể đánh giá mask: {exc}')
            else:
                st.info('Chưa có mask tham chiếu; không tính độ chính xác từ ảnh chưa có nhãn.')
        st.caption('ZIP gồm ảnh gốc, ảnh lọc, ứng viên, mask, lớp phủ và regions.json chứa đặc trưng/cấu hình/đánh giá.')
        st.download_button('Tải kết quả ZIP', download_zip(result, evaluation),
                           file_name='sar_result.zip', mime='application/zip')

elif page == 'Dầu và look-alike':
    from scripts.web import streamlit_qposd as qposd
    st.subheader('QPOSD — dầu và vùng tương tự dầu')
    st.caption('UAVSAR T11 tuyến tính. Đỏ: dầu; xanh: look-alike chung. Chưa phân biệt gió yếu, màng sinh học và mưa.')
    st.write('Chọn một ảnh test rồi bấm **Phân tích QPOSD**. Lớp tương tự dầu là các vùng tối dễ gây nhầm; không có nghĩa đã xác định nguyên nhân gây tối.')
    try:
        available = qposd.samples()
        if not available:
            st.info('Chưa có ảnh QPOSD cục bộ. Xem bằng chứng thực nghiệm đã lưu ở trang bên cạnh.')
        else:
            number = st.selectbox('Ảnh test QPOSD đã có nhãn', available)
            if st.session_state.get('qposd_number') != number:
                st.session_state.pop('qposd_result', None)
                st.session_state['qposd_number'] = number
            if st.button('Phân tích QPOSD', type='primary'):
                with st.spinner('Đang đọc T11, tìm vùng và phân lớp bằng mô hình đã khóa…'):
                    st.session_state['qposd_result'] = qposd.run_sample(number)
            result = st.session_state.get('qposd_result')
            if result is not None:
                st.info('Đỏ = dầu dự đoán · Xanh lá = tương tự dầu dự đoán. Các vùng không tô màu chưa được nhận là một trong hai lớp; vẫn có thể có vùng bị bỏ sót.')
                columns = st.columns(3)
                for col, key, title in zip(columns, ['image', 'feature_image', 'overlay'],
                                           ['T11 hiển thị', 'Ảnh trích đặc trưng', 'Dầu / look-alike']):
                    col.image(result[key], caption=title, width='stretch', clamp=True)
                with st.expander('Xem vùng tối trước khi phân lớp'):
                    st.image(result['candidate_mask'].astype(float), caption='Trắng = ứng viên; chưa phải kết luận dầu', width='stretch')
                with st.expander('Đặc trưng và quyết định từng vùng'):
                    ux.feature_help()
                    st.dataframe(result['rows'], width='stretch')
                evaluation = qposd.assess_sample(result)
                st.markdown('**Đánh giá phát hiện sau suy luận**')
                metrics = evaluation['metrics']
                columns = st.columns(3)
                for col, label, value in zip(columns, ['F1 dầu', 'F1 look-alike', 'Macro-F1'],
                        [metrics['classes']['oil']['f1'], metrics['classes']['look_alike']['f1'], metrics['macro_f1']]):
                    col.metric(label, 'Không xác định' if value is None else f'{value:.4f}')
                st.dataframe([{'lớp':name, **{k:row[k] for k in ['tp','fp','fn','precision','recall','f1']}}
                              for name, row in metrics['classes'].items()], width='stretch')
                with st.expander('Ghép vùng và nhầm lẫn chi tiết'):
                    st.json(metrics)
                st.caption('Điểm trên vùng GT có sẵn khác với điểm phát hiện đầu-cuối ở đây. Nhãn không tham gia suy luận.')
                st.caption('TP = phát hiện đúng; FP = báo nhầm; FN = bỏ sót. Macro-F1 là trung bình F1 các lớp theo quy ước đánh giá; xem chi tiết khi có lớp không xác định. ZIP giữ riêng dầu và tương tự dầu, không gộp thành một lớp.')
                st.download_button('Tải kết quả QPOSD', qposd.export_zip(result, evaluation),
                                   file_name=f'qposd_{number}.zip', mime='application/zip')
    except (OSError, ValueError, KeyError) as exc:
        st.error(f'Không thể xử lý QPOSD: {exc}')

elif page == 'Sentinel-1 vật lý':
    from scripts.web import streamlit_physical as physical
    st.subheader('Sentinel-1 — góc tới và ngưỡng thích nghi')
    st.caption('Nhánh Cantarell: gamma0 + Niblack + mô hình được chọn trên validation. Gió ERA5 chỉ là thông tin bối cảnh.')
    with st.expander('Góc tới và gió giúp hiểu ảnh như thế nào?'):
        st.write('Góc tới là góc radar chiếu xuống bề mặt. Gamma0 hiệu chỉnh diện tích hình học trước lọc Lee và tìm vùng tối bằng Niblack. Gió ERA5 đi kèm để hiểu điều kiện quan sát; hiện không tham gia phân lớp và không xác nhận dầu. Dữ liệu ở Cantarell, chưa phải biển miền Trung.')
    if not physical.ready():
        st.info('Thực nghiệm Cantarell chưa hoàn tất đánh giá test. Chế độ suy luận vật lý sẽ khả dụng khi có kết quả đã kiểm chứng.')
    else:
        try:
            rows = physical.samples()
            sample = st.selectbox('Mẫu Sentinel-1 đã kiểm chứng', rows, format_func=lambda r:r['sample'])
            key = (sample['sample'], sample['sha256'], (ROOT/'results/cantarell/selection.json').read_bytes())
            if st.session_state.get('physical_key') != key:
                st.session_state.pop('physical_result', None)
                st.session_state['physical_key'] = key
            if st.button('Phân tích Sentinel-1', type='primary'):
                with st.spinner('Đang chạy pipeline vật lý đã khóa…'):
                    st.session_state['physical_result'] = physical.run_sample(sample['sample'])
            result = st.session_state.get('physical_result')
            if result is not None:
                ux.result_summary(result)
                columns = st.columns(3)
                for col, field, title in zip(columns, ['image', 'filtered', 'overlay'],
                                             ['Gamma0 hiển thị', 'Sau lọc và chuẩn hóa', 'Vùng nghi dầu']):
                    col.image(result[field], caption=title, width='stretch', clamp=True)
                angles = result['metadata']['incidence_degrees_min_max']
                wind = result['metadata']['wind_speed_m_s']
                st.write(f'Góc tới trong ảnh: **{angles[0]:.2f}–{angles[1]:.2f}°** · Gió ERA5: **{wind:.2f} m/s**'
                         if wind is not None else f'Góc tới: **{angles[0]:.2f}–{angles[1]:.2f}°** · Chưa có gió đi kèm')
                with st.expander('Xem vùng tối và mask cuối'):
                    before, after = st.columns(2)
                    before.image(result['candidates'].astype(float), caption='Ứng viên trước phân lớp', width='stretch')
                    after.image(result['mask'].astype(float), caption='Mask dầu sau phân lớp', width='stretch')
                with st.expander('Đặc trưng và quyết định từng vùng'):
                    ux.feature_help()
                    st.dataframe([{'id':r['id'], 'oil':r['oil'], 'score':r['score'], **r['features']}
                                  for r in result['metadata']['regions']], width='stretch')
                evaluation = physical.assess_sample(result)
                columns = st.columns(3)
                for col, name in zip(columns, ['precision','recall','f1']):
                    value = evaluation['metrics'][name]
                    col.metric(f'Object {name}', 'Không xác định' if value is None else f'{value:.4f}')
                ux.metric_help(evaluation['metrics'])
                with st.expander('Số đếm và đánh giá chi tiết'):
                    st.json(evaluation['metrics'])
                st.download_button('Tải kết quả Sentinel-1', download_zip(result, evaluation),
                                   file_name=f"{sample['sample']}.zip", mime='application/zip')
        except (OSError, ValueError, KeyError) as exc:
            st.error(f'Không thể xử lý dữ liệu vật lý: {exc}')

elif page == 'Bằng chứng thực nghiệm':
    ux.evidence_overview()
    st.subheader('Kết quả đã lưu của dự án')
    with st.expander('Sentinel-1 vật lý — Cantarell', expanded=False):
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
            st.caption('filtered_adaptive là nhánh có đủ lọc speckle, góc tới và ngưỡng thích nghi. primary là winner theo giao thức ban đầu, có thể không lọc. Các nhánh paired giữ nguyên mô hình và chỉ đổi đầu vào bức xạ.')
            st.dataframe([{'vai trò': name, **{k:r['metrics']['numpy'][k]
                for k in ('precision', 'recall', 'f1', 'fp_per_image')}}
                for name, r in evaluation['roles'].items()], width='stretch')
            for name, filename in [('Winner ban đầu','angle_bootstrap.json'),
                                   ('Nhánh có lọc speckle','angle_bootstrap_filtered.json')]:
                path = ROOT/'results/cantarell'/filename
                if path.exists():
                    interval = json.loads(path.read_text())
                    st.write({'ablation':name, 'CI 95% của F1 gamma0 − sigma0':interval['ci95'],
                              'số cảnh':len(interval['scenes'])})
            st.caption('CI chứa 0 không chứng minh gamma0 cải thiện F1. Đây là phép đo trên mô hình cố định và số cảnh ít, không phải kết luận phổ quát.')
            diagnostics_path = ROOT/'results/cantarell/size_diagnostics.json'
            if diagnostics_path.exists():
                diagnostics = json.loads(diagnostics_path.read_text())
                st.markdown('**Đối tượng nhỏ và bỏ sót — nhánh có lọc**')
                st.dataframe([{'diện tích GT (pixel)':name, **row}
                    for name,row in diagnostics['roles']['filtered_adaptive']['totals'].items()], width='stretch')
                st.caption('Ứng viên tối thiểu 64 pixel không thể ghép IoU ≥0,5 với GT dưới 32 pixel. Các GT này vẫn được giữ trong điểm toàn tập; không loại để làm đẹp số liệu.')
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
                show_evidence_markdown(path)
            else:
                st.info(f'Chưa có {relative}')
else:
    ux.guide()
    st.subheader('Phạm vi sử dụng')
    st.markdown('''
1. Chọn ảnh mẫu hoặc tải PNG/JPEG SAR hiển thị 8-bit lên.
2. Chọn pipeline đã huấn luyện và bấm **Phân tích ảnh**.
3. Xem các bước, đặc trưng, mask và tải ZIP kết quả.
4. Nếu có mask dầu/nền cùng kích thước, xem đánh giá sau suy luận.

**SOS:** nhãn dầu/nền; chưa có góc tới, tọa độ/thời gian hay nhãn nguyên nhân look-alike.

**QPOSD:** trang Dầu và look-alike chạy suy luận trên ảnh test UAVSAR T11 cục bộ đã xác minh; dùng mô hình riêng, không áp dụng trực tiếp cho PNG Sentinel-1.

**Cantarell:** trang Sentinel-1 vật lý dùng nhánh đã xác minh có đủ Lee, gamma0, Niblack và SVM. Chất lượng test còn thấp; nhánh không lọc có điểm cao hơn và được giữ trong bảng đối chứng. Gió ERA5 là thông tin bối cảnh, không phải nhãn look-alike.

Kết quả hiện có chưa chứng minh hiệu quả cảnh báo tại biển miền Trung. Ứng dụng không suy ra tàu xả thải hoặc nguyên nhân vùng tối từ một mask.
''')
