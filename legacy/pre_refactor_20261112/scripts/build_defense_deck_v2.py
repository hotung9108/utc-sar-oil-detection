"""Local PPTX fallback explicitly requested by the user after Spaces failure."""
from pathlib import Path
import json, csv
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/slides/v2'
DATA=json.loads((OUT/'loi_thuyet_trinh.json').read_text(encoding='utf-8'))
SPEECHES={x['slide']:x['speech'] for x in json.loads((OUT/'loi_noi_lien_mach.json').read_text(encoding='utf-8'))}
TEAM={x['id']:x['name'] for x in json.loads((ROOT/'docs/management/thanh_vien.json').read_text(encoding='utf-8'))}
NAVY='102C43'; TEAL='147D82'; GRAY='526577'; WHITE='FFFFFF'; PALE='EAF2F3'; RED='AD4A38'
prs=Presentation(); prs.slide_width=Inches(13.333); prs.slide_height=Inches(7.5)
prs.core_properties.title='Xử lý ảnh SAR — Bảo vệ BTL XLA v2'
prs.core_properties.author='Nhóm 4'
def color(h): return RGBColor.from_string(h)
def txt(s,t,x,y,w,h,size=23,c=NAVY,bold=False):
    sh=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h))
    f=sh.text_frame; f.word_wrap=True
    f.margin_left=f.margin_right=Inches(.02); f.margin_top=f.margin_bottom=0
    for i,line in enumerate(t.split('\n')):
        p=f.paragraphs[0] if i==0 else f.add_paragraph()
        p.text=line; p.font.name='Arial'; p.font.size=Pt(size); p.font.bold=bold; p.font.color.rgb=color(c)
        p.space_after=Pt(10); p.line_spacing=1.12
    return sh
def picture(s,path,x,y,w,h):
    iw,ih=Image.open(path).size; r=min(w/iw,h/ih)
    return s.shapes.add_picture(str(path),Inches(x+(w-iw*r)/2),Inches(y+(h-ih*r)/2),width=Inches(iw*r),height=Inches(ih*r))
def table(s,rows,x,y,w,h,widths=None,size=21):
    t=s.shapes.add_table(len(rows),len(rows[0]),Inches(x),Inches(y),Inches(w),Inches(h)).table
    if widths:
        for col,cw in zip(t.columns,widths): col.width=Inches(cw)
    for ri,row in enumerate(rows):
        for ci,val in enumerate(row):
            cell=t.cell(ri,ci); cell.text=str(val); cell.margin_left=Inches(.14);cell.margin_right=Inches(.12)
            cell.vertical_anchor=MSO_ANCHOR.MIDDLE
            cell.fill.solid();cell.fill.fore_color.rgb=color(NAVY if ri==0 else (PALE if ri%2 else WHITE))
            for p in cell.text_frame.paragraphs:
                p.font.name='Arial';p.font.size=Pt(size);p.font.bold=ri==0;p.font.color.rgb=color(WHITE if ri==0 else NAVY)
    return t
def slide(n,title=None):
    d=DATA['slides'][n-1];s=prs.slides.add_slide(prs.slide_layouts[6]);s.background.fill.solid();s.background.fill.fore_color.rgb=color(WHITE)
    txt(s,title or d['title'],.6,.38,12.1,1.0,32,bold=True)
    txt(s,f"{d['speaker']} · {TEAM[d['speaker']]}",.6,7.07,10,.25,11,c=GRAY)
    txt(s,f'{n:02d} / 18',11.6,7.07,1.1,.25,11,c=GRAY)
    s.notes_slide.notes_text_frame.text=SPEECHES[n]
    return s
def foot(s,t): txt(s,t,.65,6.48,12,.43,16,c=GRAY)

s=slide(1,'')
# Cover has its own title hierarchy.
for sh in list(s.shapes)[:1]:
    sh._element.getparent().remove(sh._element)
txt(s,'BÀI TẬP LỚN XỬ LÝ ẢNH',.65,.72,8,.5,20,c=TEAL,bold=True)
txt(s,'Xử lý ảnh SAR',.65,1.6,8,1.0,46,bold=True)
txt(s,'Từ khử nhiễu đến\nvùng tối ứng viên',.65,2.75,8,1.65,36,bold=True)
txt(s,'Thuật toán cổ điển tự cài đặt bằng NumPy\nNhóm 4 · Trường Đại học Giao thông vận tải',.65,5.0,10.7,1.0,22)
picture(s,ROOT/'report_overleaf/v2/assets/utc_logo.png',10.15,1.65,2.2,2.2)
txt(s,'Báo cáo v2 · 12 phút trình bày · 3 phút demo',.65,6.25,11,.45,17,c=GRAY)

s=slide(2,'Bài toán và phạm vi')
table(s,[['Đầu vào','Đầu ra','Tiêu chí thực hiện'],['Ảnh SAR chuyển xám\n400 × 400, uint8','Ảnh lọc và tăng cường\nBản đồ biên\nMask vùng tối','Cài lõi bằng NumPy\nĐối chiếu thư viện\nPhân tích ca thất bại']],.65,1.65,12,3.2,[3.3,4.2,4.5],23)
txt(s,'Vùng tối cần thêm bằng chứng để xác nhận dầu',.7,5.35,11.9,.7,28,c=TEAL,bold=True)
foot(s,'Diện tích tính theo pixel; chưa quy đổi sang diện tích mặt biển.')

s=slide(3,'Phân công theo module')
roles=[['Thành viên','Phụ trách','Mã nguồn'],['Tiến Sơn Trần','Tích hợp và Streamlit','src/tv1/'],['Lương Tiến Dũng','Lý thuyết, kiểm chứng','src/tv2/'],['Hồ Việt Tùng','Lọc, tăng tương phản','src/tv3/'],['Nguyễn Hải Hiếu','Biên và hình thái','src/tv4/'],['Phạm Minh Tuấn','Dữ liệu, thực nghiệm','src/tv5/']]
table(s,roles,.65,1.5,12,4.65,[3.9,5.1,3],21)
foot(s,'Mỗi thành viên cần giải thích được toàn bộ pipeline khi vấn đáp.')

s=slide(4,'Dữ liệu và phạm vi đánh giá')
txt(s,'5.538',.65,1.55,5,1.15,62,c=TEAL,bold=True)
txt(s,'ảnh duy nhất trong bản cục bộ',.65,2.8,5.5,.6,22)
table(s,[['Nhãn thư mục','Số ảnh'],['Class_0: không dầu','3.695'],['Class_1: có dầu','1.843']],.65,3.6,5.7,2.2,[3.8,1.9],21)
txt(s,'10 ảnh: khảo sát phương pháp và tham số\n5.538 ảnh: một cấu hình mặc định\nChưa có mask chuẩn theo pixel\nBản cục bộ thiếu 92 ảnh so với bộ công bố',7.0,1.65,5.65,4.4,24)
foot(s,'CSIRO · DOI 10.25919/4v55-dn16 · CC BY-SA 4.0 theo metadata cục bộ')

s=slide(5,'Đặc điểm ảnh SAR')
txt(s,'I = R × η',.7,1.55,6,1,44,c=TEAL,bold=True)
txt(s,'I: ảnh quan sát\nR: tín hiệu phản xạ\nη: nhiễu nhân (mô hình làm việc)',.7,2.75,6.0,2.5,24)
txt(s,'Speckle gây dao động cục bộ\nLặng gió cũng có thể tạo vùng tối\nLọc mạnh có thể mất chi tiết\nTăng tương phản có thể làm rõ nền',7.1,1.65,5.5,4.4,24)
foot(s,'Ảnh JPEG trong dự án chưa được nhóm hiệu chuẩn như dữ liệu SAR thô.')

s=slide(6,'Pipeline và ảnh tham chiếu')
picture(s,ROOT/'report_overleaf/v2/assets/pipeline.png',.6,1.45,12.1,3.85)
txt(s,'Ảnh sau lọc được giữ làm reference trước CLAHE',.7,5.45,12,.5,25,c=TEAL,bold=True)
foot(s,'Làm nét phục vụ quan sát. Chế độ biên không trả mask diện tích vùng dầu.')

s=slide(7,'Bộ lọc Lee')
txt(s,'σₙ² = μ² / L\nK = clip(1 − σₙ² / max(v, ε), 0, 1)\nJ = μ + K(I − μ)',.7,1.5,12,2.25,32,c=TEAL,bold=True)
table(s,[['Tham số / đại lượng','Ảnh hưởng'],['μ, v: trung bình, phương sai cục bộ','K gần 0: làm mịn về μ'],['Cửa sổ mặc định 5 × 5, L = 4','K gần 1: giữ nhiều giá trị gốc']],.7,4.05,11.9,1.95,[6.5,5.4],21)
foot(s,'ε tránh chia cho 0. Đối chứng Lee ghép moment SciPy với cùng công thức.')

s=slide(8,'CLAHE và tương phản cục bộ')
txt(s,'01   Histogram theo từng ô\n02   Cắt ngưỡng và phân phối phần dư\n03   Ánh xạ CDF\n04   Nội suy song tuyến giữa các ô',.7,1.55,8.2,3.6,27)
txt(s,'clip = 2\ngrid = 8 × 8',9.25,1.7,3.3,1.6,30,c=TEAL,bold=True)
txt(s,'Tăng tương phản có thể làm rõ cả kết cấu nền',.7,5.55,12,.6,27,c=TEAL,bold=True)
foot(s,'Đối chiếu cv2.createCLAHE cùng tham số; kiểm tra cả ảnh không chia hết cho lưới.')

s=slide(9,'Làm nét và phát hiện biên')
table(s,[['Làm nét để quan sát','Biên từ biến thiên mức xám'],['Unsharp: f + k(f − blur)\nLaplacian: f − α∇²f','Roberts, Prewitt, Sobel\nLoG: đổi dấu sau làm trơn\nCanny: gradient và liên kết biên']],.7,1.65,11.9,3.5,[5.95,5.95],24)
txt(s,'Cả vệt chính và nhiễu nhỏ đều có thể tạo biên',.7,5.6,11.9,.6,27,c=TEAL,bold=True)

s=slide(10,'Các bước của Canny')
txt(s,'1   Làm trơn Gaussian\n2   Tính gradient và hướng\n3   NMS: triệt tiêu điểm không cực đại\n4   Phân ngưỡng mạnh / yếu\n5   Hysteresis theo 8 láng giềng',.7,1.55,8.0,4.5,26)
txt(s,'Giữ gradient\nở kiểu float',9.1,1.75,3.5,1.5,31,c=TEAL,bold=True)
txt(s,'Canny và OpenCV có thể khác ở lượng tử hướng, điểm bằng nhau và biên ảnh.',9.1,3.65,3.5,2.5,21)
foot(s,'Kết quả đối chiếu biến thể được báo DESCRIPTIVE, không khẳng định trùng tuyệt đối.')

s=slide(11,'Phân ngưỡng Otsu')
txt(s,'t* = arg max  ω₀(t)ω₁(t)[μ₀(t) − μ₁(t)]²',.7,1.65,12,1.0,30,c=TEAL,bold=True)
txt(s,'ω: tỷ lệ pixel mỗi lớp\nμ: mức xám trung bình mỗi lớp\nMask tối: I ≤ t*',.7,3.0,5.8,2.25,24)
txt(s,'Ví dụ hai mức 50 và 200\nNgưỡng t = 50 giữ nhóm mức 50\nẢnh hằng thiếu bằng chứng tương phản',7.0,3.0,5.6,2.65,24)
foot(s,'Otsu tối ưu sự tách histogram. Vùng tối vẫn có thể là nền không dầu.')

s=slide(12,'Hình thái học và vùng liên thông')
table(s,[['Bước','Mục đích / tham số'],['Mở: co rồi giãn','Loại cấu trúc nhỏ, đĩa r = 2'],['Đóng: giãn rồi co','Nối khe nhỏ, đĩa r = 4'],['Gán nhãn 8 liên thông','Run-length + union-find'],['Lọc vùng','Diện tích ≥ 300 px và đủ tương phản']],.7,1.55,11.9,4.55,[4.8,7.1],23)
foot(s,'Đóng quá mạnh có thể gộp nhầm vùng. Ít mảnh hơn chưa chứng minh mask đúng hơn.')

s=slide(13,'Tương phản giữa vùng và nền')
txt(s,'C_R = (μ_nền − μ_vùng) / μ_nền',.7,1.7,12,1.0,36,c=TEAL,bold=True)
txt(s,'Đo trên ảnh tham chiếu trước CLAHE\nTạo vành nền bằng kernel vuông 15 × 15\nNgưỡng mặc định C_R ≥ 0,1',.7,3.1,7.2,2.5,25)
txt(s,'Nền bị lẫn cấu trúc khác\ncó thể làm lệch phép đo',8.4,3.15,4.2,1.6,24,c=RED,bold=True)
foot(s,'C_R trong mã hiện tại là tương phản vùng/nền; không dùng định nghĩa độ tròn.')

s=slide(14,'Kiểm chứng thuật toán')
table(s,[['Phạm vi','Kết quả'],['33 phép toán × 18 ảnh','594 trường hợp'],['Đạt tiêu chí số học','558 PASS'],['Bilateral, Canny: so sánh biến thể','36 DESCRIPTIVE']],.7,1.55,11.9,2.8,[8.0,3.9],22)
txt(s,'Ví dụ Lee: 8 pixel = 100, tâm = 200; cửa sổ 3 × 3\nμ = 111,111; v = 987,654; L = 4 → K = 0 → J = 111',.7,4.7,12,1.2,23,c=TEAL,bold=True)
foot(s,'Ví dụ tính tay đã kiểm chứng bằng NumPy. Kiểm chứng số học chưa đo độ đúng nhãn dầu.')

s=slide(15,'Thí nghiệm trên 10 ảnh mẫu')
filters=list(csv.DictReader((ROOT/'results/reproducible/filters_summary.csv').open(encoding='utf-8-sig')))
lookup={r['method']:r for r in filters}
rows=[['Bộ lọc','SSI (TB ± SD)','EPI (TB ± SD)']]
for method in ['none','gaussian','lee']:
    r=lookup[method]; rows.append([{'none':'Ảnh gốc','gaussian':'Gaussian','lee':'Lee'}[method],f"{float(r['SSI_mean']):.3f} ± {float(r['SSI_std']):.3f}",f"{float(r['EPI_mean']):.3f} ± {float(r['EPI_std']):.3f}"])
table(s,rows,.65,1.7,6.3,2.7,[1.8,2.25,2.25],18)
txt(s,'SSI: tỷ lệ hệ số biến thiên\nEPI: tỷ lệ đáp ứng biên\nCả hai chưa đo độ đúng mask',.7,4.8,6.2,1.4,21)
survey=list(csv.DictReader((ROOT/'results/reproducible/clahe_summary.csv').open(encoding='utf-8-sig')))
grid8=sorted([r for r in survey if int(r['grid'])==8],key=lambda r:float(r['clip']))
cd=CategoryChartData();cd.categories=[str(int(float(r['clip']))) for r in grid8];cd.add_series('Diện tích vùng ứng viên (%)',[float(r['candidate_area_pct_mean']) for r in grid8])
chart=s.shapes.add_chart(XL_CHART_TYPE.LINE_MARKERS,Inches(7.25),Inches(2.0),Inches(5.35),Inches(3.8),cd).chart
chart.has_legend=False;chart.has_title=False;chart.value_axis.minimum_scale=0;chart.value_axis.maximum_scale=40
for ax in [chart.category_axis,chart.value_axis]: ax.tick_labels.font.name='Arial';ax.tick_labels.font.size=Pt(17)
chart.series[0].format.line.color.rgb=color(TEAL)
txt(s,'CLAHE, grid 8 × 8\nDiện tích ứng viên trung bình (%)',7.35,1.38,5.2,.95,18,c=TEAL,bold=True)
txt(s,'Clip limit',9.0,5.8,2.8,.35,17,c=GRAY)
foot(s,'So sánh phương pháp; khảo sát tham số; thử điều kiện bất lợi. Chưa có mask chuẩn.')

s=slide(16,'Ảnh 00013: vệt chính và kết cấu nền')
picture(s,ROOT/'results/reproducible/class_1_00013_clahe.png',.55,1.55,12.25,3.5)
txt(s,'1 vùng ứng viên   ·   3.328 px   ·   2,08% ảnh',.7,5.25,12,.65,28,c=TEAL,bold=True)
foot(s,'CLAHE làm rõ dao động nền còn lại sau Lee. Một vùng ứng viên chưa chứng minh đường bao đúng.')

s=slide(17,'Đánh giá toàn tập ở cấp ảnh')
c=json.loads((ROOT/'results/reproducible/confusion.json').read_text(encoding='utf-8'))
table(s,[['Nhãn thật','Không ứng viên','Có ứng viên'],['Không dầu',f"TN  {c['TN']:,}",f"FP  {c['FP']:,}"],['Có dầu',f"FN  {c['FN']:,}",f"TP  {c['TP']:,}"]],.7,1.7,7.35,2.5,[2.65,2.35,2.35],22)
txt(s,f"Precision  {100*c['precision']:.2f}%\nRecall       {100*c['recall']:.2f}%\nF1              {100*c['f1']:.2f}%\nAccuracy   {100*c['accuracy']:.2f}%",8.6,1.65,4,3.3,25,c=TEAL,bold=True)
txt(s,'2.885 ảnh không dầu vẫn tạo vùng ứng viên',.7,4.75,12,.65,29,c=RED,bold=True)
foot(s,'N = 5.538. Chỉ số đếm đúng/sai cũng dùng được với quy tắc xử lý ảnh cố định, không cần ML.')

s=slide(18,'Kết luận và hướng phát triển')
txt(s,'Đã triển khai và đối chiếu lõi NumPy\nCó demo và kết quả thực nghiệm tái lập\nBáo nhầm còn nhiều: chưa đủ xác nhận dầu',.7,1.55,12,2.4,28)
txt(s,'Hướng tiếp theo',.7,4.0,12,.55,26,c=TEAL,bold=True)
txt(s,'Chọn nền cục bộ thích nghi\nKhảo sát nhiều kích thước cấu trúc\nGán mask độc lập để đánh giá đường bao',.7,4.7,10.9,1.65,24)
foot(s,'Tiếp theo: demo 3 phút, vấn đáp 5 phút. Tài liệu: Lee (1980), Otsu (1979), Canny (1986).')
from illustrate_defense_deck_v2 import enrich
enrich(prs, txt, picture, table, foot, (TEAL, GRAY, RED))
OUT.mkdir(exist_ok=True,parents=True)
path=OUT/'BAO_VE_BTL_XLA_V2.pptx';prs.save(path)
check=Presentation(path)
assert len(check.slides)==18
for n,s in enumerate(check.slides,1):
    assert s.notes_slide.notes_text_frame.text == SPEECHES[n]
    assert '\n' not in SPEECHES[n]
assert sum(len(s.shapes) for s in check.slides)>70
(OUT/'SPEAKER_NOTES_DAY_DU.txt').write_text(('\n\n'+'='*80+'\n\n').join(f"SLIDE {n}: {DATA['slides'][n-1]['title']}\n\n{s.notes_slide.notes_text_frame.text}" for n,s in enumerate(check.slides,1)),encoding='utf-8')
print(path)
