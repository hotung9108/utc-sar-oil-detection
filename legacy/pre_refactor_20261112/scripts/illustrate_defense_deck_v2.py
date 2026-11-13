"""Add measured image evidence to the existing local defense deck builder.

Images are actual project inputs/intermediates, not generated SAR examples.
The local PPTX workflow was explicitly selected by the user earlier.
"""
from pathlib import Path
import json
import sys
import hashlib
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.tv1.pipeline import process_image, PipelineConfig
from src.tv4 import morphology, edges, sharpening

ASSETS = ROOT / 'docs/slides/v2/illustrations'


def make_assets():
    ASSETS.mkdir(parents=True, exist_ok=True)
    source = ROOT / 'kaggle/data/Class_1/class_1_00013.jpg'
    raw = np.asarray(Image.open(source).convert('L'))
    captured = {}

    def capture(frame, event, arg):
        if event == 'return' and frame.f_code.co_name in {
            'detect_oil_slick_morphological', 'custom_canny'
        }:
            captured[frame.f_code.co_name] = dict(frame.f_locals)

    # Observe intermediate arrays from the actual functions, without editing them.
    sys.setprofile(capture)
    try:
        result = process_image(raw)
        canny = process_image(raw, PipelineConfig(edge_name='canny'))
    finally:
        sys.setprofile(None)
    seg = captured['detect_oil_slick_morphological']
    can = captured['custom_canny']
    assert result['stats']['total_area_px'] == 3328
    assert result['stats']['slicks_count'] == 1
    assert np.array_equal(result['mask'], seg['clean_mask'])
    assert np.array_equal(canny['boundary'], can['output'])
    assert result['stats']['otsu_threshold'] == 46
    manifest = {'input': str(source.relative_to(ROOT)),
                'input_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                'config': result['config'], 'stats': result['stats'], 'assets': {}}

    def save(name, arr, meaning, crop=None):
        if crop:
            x0,y0,x1,y1 = crop
            arr = arr[y0:y1,x0:x1]
        Image.fromarray(np.asarray(arr).astype(np.uint8)).save(ASSETS / f'{name}.png')
        manifest['assets'][name] = {'meaning': meaning, 'crop_xyxy': crop,
                                   'shape': list(arr.shape)}

    for key in ['raw','filtered','enhanced','mask','boundary','overlay']:
        save(key, result[key], f'process_image default: {key}')
    roi = (220,235,400,400)
    for key in ['raw','filtered','enhanced','overlay']:
        save('detail_'+key,result[key],f'Detail of {key}; same crop for comparison',roi)
    texture = (75,90,235,250)
    for key in ['raw','filtered','enhanced']:
        save('texture_'+key,result[key],f'Background detail of {key}',texture)
    save('sharp',sharpening.unsharp_masking(result['enhanced'],k=1),
         'Unsharp k=1 on enhanced image; demonstration, separate from default mask',roi)
    save('canny',canny['boundary'],'Canny low=35 high=90 on default enhanced image',roi)
    # One shared scale for both intermediate gradient maps, not per-image stretching.
    scale = max(float(can['mag'].max()),1.0)
    for name in ['mag','nms']:
        save('canny_'+name,np.round(np.clip(can[name]/scale,0,1)*255),
             f'Actual Canny {name}; shared display normalization / {scale:.6f}',roi)
    for name in ['dark_mask','opened','closed','clean_mask']:
        save(name,seg[name],f'Actual morphological pipeline intermediate: {name}',roi)
    save('seg_img',seg['seg_img'],'Selected image used to threshold; full image')
    save('otsu_dark',seg['dark_mask'],'Initial mask after actual threshold selection')
    comp = result['mask'] > 0
    ring = (morphology.custom_dilation(result['mask'], morphology.box_kernel(15), pad_val=0)>0)&~comp
    # False-color scientific overlay: teal = measured component, orange = measured ring.
    rgb = np.repeat(result['filtered'][...,None],3,axis=2)
    rgb[comp] = (20,125,130)
    rgb[ring] = (235,155,55)
    save('contrast_ring',rgb,'False-color overlay of actual component (teal) and 15x15 dilation ring (orange)',roi)
    mean_region=float(result['filtered'][comp].mean())
    mean_ring=float(result['filtered'][ring].mean())
    manifest['contrast']={'mean_region':mean_region,'mean_ring':mean_ring,
                         'ratio':(mean_ring-mean_region)/mean_ring}
    sea_path=ROOT/'data/sample/sea_surface/sea_surface_01.jpg'
    sea=process_image(np.asarray(Image.open(sea_path).convert('L')))
    assert sea['stats']['slicks_count'] == 2 and sea['stats']['area_pct'] == 19.31
    for name in ['raw','overlay']:
        save('sea_'+name,sea[name],f'{sea_path.relative_to(ROOT)}; default {name}')
    manifest['sea_stats']=sea['stats']
    (ASSETS/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    return manifest


def enrich(prs, txt, picture, table, foot, colors):
    """Keep existing titles, slide numbers, presenter footers, and full Notes."""
    from pptx.util import Inches
    TEAL, GRAY, RED = colors
    manifest=make_assets()

    def clear(n):
        s=prs.slides[n-1]
        for sh in list(s.shapes):
            if sh.top > Inches(1.35) and sh.top < Inches(7.0):
                sh._element.getparent().remove(sh._element)
        return s

    def img(s,name,label,x,y,w,h):
        picture(s,ASSETS/f'{name}.png',x,y,w,h)
        txt(s,label,x,y+h+.10,w,.55,18,c=GRAY)

    s=clear(2)
    for name,label,x in [('raw','Ảnh xám đầu vào',.7),('boundary','Biên: các nét viền',4.95),('mask','Mask: vùng được tô kín',9.2)]:
        img(s,name,label,x,1.5,3.4,3.4)
    txt(s,'400 × 400 pixel, uint8     •     Lõi NumPy     •     Đối chiếu thư viện',.7,5.65,12,.55,23,c=TEAL,bold=True)
    foot(s,'Ảnh 00013, cấu hình mặc định. Mask là vùng ứng viên; diện tích tính bằng pixel.')

    s=clear(4)
    txt(s,'5.538 ảnh duy nhất',.7,1.5,6.0,.7,34,c=TEAL,bold=True)
    table(s,[['Nhãn thư mục','Số ảnh'],['Class_0: không dầu','3.695'],['Class_1: có dầu','1.843']],.7,2.4,5.8,2.0,[3.9,1.9],20)
    txt(s,'10 ảnh khảo sát; 5.538 ảnh chạy mặc định\nChưa có mask chuẩn theo pixel\nThiếu 92 ảnh so với bộ công bố',.7,4.75,6.4,1.4,20)
    img(s,'raw','Mẫu lớp có dầu',7.35,1.65,2.25,2.25)
    img(s,'sea_raw','Mẫu nền biển',10.1,1.65,2.25,2.25)
    txt(s,'Nhãn cấp ảnh chưa cho biết\nđường bao của từng vùng.',7.35,4.65,5.25,1.2,23,c=TEAL,bold=True)
    foot(s,'Nguồn CSIRO: DOI 10.25919/4v55-dn16. Ảnh minh họa lấy từ dữ liệu cục bộ.')

    s=clear(5)
    txt(s,'I = R × η',.7,1.5,5,.75,38,c=TEAL,bold=True)
    txt(s,'I: ảnh quan sát\nR: tín hiệu phản xạ\nη: nhiễu nhân',.7,2.55,4.6,1.9,24)
    txt(s,'Nền vẫn có dao động mức xám.\nTăng tương phản làm chúng dễ thấy.',.7,4.85,5.1,1.2,22)
    img(s,'texture_raw','Cùng vùng nền: ảnh gốc',6.2,1.8,2.95,2.95)
    img(s,'texture_enhanced','Sau Lee + CLAHE',9.6,1.8,2.95,2.95)
    foot(s,'Phóng to cùng ROI của ảnh 00013. JPEG chưa được hiệu chuẩn như dữ liệu SAR thô.')

    s=clear(7)
    txt(s,'σₙ² = μ² / L\nK = clip(1 − σₙ² / max(v, ε), 0, 1)\nJ = μ + K(I − μ)',.7,1.55,6,2.1,25,c=TEAL,bold=True)
    txt(s,'K gần 0: kéo về trung bình μ\nK gần 1: giữ giá trị gốc I\nCửa sổ 5 × 5; L = 4',.7,4.1,5.5,1.6,23)
    img(s,'detail_raw','Trước Lee',6.6,1.9,2.8,2.8)
    img(s,'detail_filtered','Sau Lee',9.85,1.9,2.8,2.8)
    foot(s,'Cùng ROI, giữ thang xám 0–255. Lee giảm dao động nhưng có thể làm mờ chi tiết.')

    s=clear(8)
    txt(s,'1  Histogram theo ô\n2  Giới hạn, phân phối phần dư\n3  Ánh xạ CDF\n4  Nội suy giữa các ô',.7,1.65,5.2,2.9,24)
    txt(s,'clip = 2; grid = 8 × 8',.7,5.0,5.3,.6,26,c=TEAL,bold=True)
    img(s,'detail_filtered','Trước CLAHE',6.25,1.7,3.0,3.0)
    img(s,'detail_enhanced','Sau CLAHE',9.65,1.7,3.0,3.0)
    foot(s,'Cùng ROI ảnh 00013. CLAHE làm rõ cả vệt chính lẫn kết cấu nền; chưa xác nhận dầu.')

    s=clear(9)
    for name,label,x in [('detail_enhanced','Ảnh tăng tương phản',.7),('sharp','Unsharp, k = 1',4.95),('canny','Canny: bản đồ biên',9.2)]:
        img(s,name,label,x,1.65,3.4,3.2)
    txt(s,'Làm nét thay đổi ảnh xám; tìm biên đánh dấu biến thiên sáng tối.',.7,5.7,12,.55,24,c=TEAL,bold=True)
    foot(s,'Cùng ROI. Canny thấp/cao = 35/90; các điểm biên chưa tạo thành mask diện tích dầu.')

    s=clear(10)
    txt(s,'Gaussian  •  Gradient  •  NMS  •  Ngưỡng kép  •  Liên kết biên',.7,1.5,12,.65,24,c=TEAL,bold=True)
    for name,label,x in [('canny_mag','Độ lớn gradient',.7),('canny_nms','Sau NMS: làm mảnh',4.95),('canny','Sau ngưỡng kép và liên kết',9.2)]:
        img(s,name,label,x,2.4,3.4,2.9)
    foot(s,'ROI thật; gradient/NMS dùng cùng thang hiển thị. Tính toán giữ float; ngưỡng 35/90.')

    s=clear(11)
    txt(s,'t* = arg max  ω₀(t)ω₁(t)[μ₀(t) − μ₁(t)]²',.7,1.5,12,.65,29,c=TEAL,bold=True)
    img(s,'seg_img','Ảnh nguồn phân đoạn',.7,2.45,3.2,3.0)
    img(s,'otsu_dark','Mask tối ban đầu, t = 46',4.4,2.45,3.2,3.0)
    txt(s,'Pixel ≤ t được tô trắng\nω: tỷ lệ pixel mỗi lớp\nμ: trung bình mỗi lớp\nChọn ảnh và điều chỉnh\nngưỡng bằng quy tắc',8.25,2.6,4.35,2.95,22)
    foot(s,'Ảnh 00013, ngưỡng thực tế sau chọn nguồn/điều chỉnh. Otsu tách mức xám, chưa biết dầu.')

    s=clear(12)
    for name,label,x in [('dark_mask','1. Mask tối',.7),('opened','2. Mở, đĩa r = 2',3.8),('closed','3. Đóng, đĩa r = 4',6.9),('clean_mask','4. Lọc vùng',10.0)]:
        img(s,name,label,x,1.85,2.65,2.65)
    txt(s,'Liên thông 8 hướng; diện tích ≥ 300 px; C_R ≥ 0,10',.7,5.35,12,.65,26,c=TEAL,bold=True)
    foot(s,'Cùng ROI ở mỗi bước, lấy từ lần chạy thật. Mở/đóng có thể xóa vệt mảnh hoặc nối nhầm vùng.')

    s=clear(13)
    txt(s,'C_R = (μ_nền − μ_vùng) / μ_nền',.7,1.55,12,.65,32,c=TEAL,bold=True)
    img(s,'contrast_ring','Màu minh họa trên ảnh tham chiếu',.7,2.55,4.0,3.0)
    cr=manifest['contrast']
    txt(s,'Xanh: vùng đang xét\nCam: vành nền từ kernel 15 × 15',5.3,2.65,7.1,1.25,24)
    txt(s,f"μ_vùng ≈ {cr['mean_region']:.1f}; μ_nền ≈ {cr['mean_ring']:.1f}\nC_R ≈ {cr['ratio']:.2f} ≥ 0,10",5.3,4.15,7.1,1.25,27,c=TEAL,bold=True)
    foot(s,'Số đo thật của ảnh 00013. Vành có thể lẫn cấu trúc khác; tỷ số không phải xác suất dầu.')

    s=clear(14)
    table(s,[['Kiểm chứng','Số trường hợp'],['33 phép toán × 18 ảnh','594'],['Đạt tiêu chí số học','558 PASS'],['Bilateral, Canny: biến thể','36 DESCRIPTIVE']],.7,1.65,6.35,3.1,[4.25,2.1],19)
    # An editable numerical table, not an illustrative drawing.
    matrix=table(s,[['100','100','100'],['100','200','100'],['100','100','100']],8.05,1.8,3.25,2.25,[1.08,1.09,1.08],24)
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    for row in range(3):
        for col in range(3):
            cell=matrix.cell(row,col)
            center=row==col==1
            cell.fill.fore_color.rgb=RGBColor.from_string(TEAL if center else 'EAF2F3')
            for p in cell.text_frame.paragraphs:
                p.alignment=PP_ALIGN.CENTER
                p.font.bold=center
                p.font.color.rgb=RGBColor.from_string('FFFFFF' if center else '102C43')
    txt(s,'Cửa sổ 3 × 3 ở tâm ma trận 5 × 5',7.5,4.3,5.1,.6,20)
    txt(s,'μ = 111,111; v = 987,654; L = 4; K = 0; J ≈ 111',.7,5.6,12,.65,25,c=TEAL,bold=True)
    foot(s,'Ví dụ đã kiểm chứng bằng NumPy. Đúng phép tính chưa đồng nghĩa nhận diện dầu đúng.')

    s=clear(16)
    for name,label,x in [('detail_raw','Ảnh gốc',.7),('detail_filtered','Lee',3.8),('detail_enhanced','Lee + CLAHE',6.9),('detail_overlay','Biên vùng ứng viên',10.0)]:
        img(s,name,label,x,1.7,2.65,2.65)
    txt(s,'Phóng to cùng vùng vệt chính và nền lân cận',.7,4.95,12,.55,23)
    txt(s,'Toàn ảnh: 1 vùng • 3.328 px • 2,08%',.7,5.65,12,.6,28,c=TEAL,bold=True)
    foot(s,'Số liệu tính trên toàn ảnh 400 × 400. Nét đỏ có thể gồm viền quanh lỗ trong cùng một mask.')

    # Slide 17 retains the native confusion table and all metrics. Add a real failure example.
    s=clear(17)
    c=json.loads((ROOT/'results/reproducible/confusion.json').read_text(encoding='utf-8'))
    table(s,[['Nhãn thật','Không ứng viên','Có ứng viên'],['Không dầu',f"TN {c['TN']}",f"FP {c['FP']}"],['Có dầu',f"FN {c['FN']}",f"TP {c['TP']}"]],.7,1.6,7.1,2.25,[2.3,2.4,2.4],20)
    txt(s,f"Precision {100*c['precision']:.2f}%   Recall {100*c['recall']:.2f}%\nF1 {100*c['f1']:.2f}%   Accuracy {100*c['accuracy']:.2f}%",.7,4.25,7.2,1.3,24,c=TEAL,bold=True)
    img(s,'sea_overlay','Ca bất lợi: sea_surface_01',8.7,1.7,3.8,3.55)
    txt(s,'2 vùng ứng viên, 19,31% ảnh',8.45,5.75,4.2,.5,19,c=RED,bold=True)
    foot(s,'N = 5.538; có 2.885 ảnh âm vẫn tạo ứng viên. Nhãn cấp ảnh chưa kiểm chứng đường bao.')

    return manifest
