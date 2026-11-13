"""Build the readable defense script; does not modify slides or the report."""
from pathlib import Path
import json
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/slides/v2'
data = json.loads((OUT / 'loi_thuyet_trinh.json').read_text(encoding='utf-8'))
team = {x['id']: x['name'] for x in json.loads((ROOT / 'docs/management/thanh_vien.json').read_text(encoding='utf-8'))}
assert len(data['slides']) == 18
assert sum(s['seconds'] for s in data['slides']) == 720
assert sum(s['seconds'] for s in data['demo']) == 180
for name, file in [('TimesVN','times.ttf'), ('TimesVN-Bold','timesbd.ttf'), ('TimesVN-Italic','timesi.ttf')]:
    pdfmetrics.registerFont(TTFont(name, 'C:/Windows/Fonts/' + file))
pdfmetrics.registerFontFamily('TimesVN',normal='TimesVN',bold='TimesVN-Bold',italic='TimesVN-Italic',boldItalic='TimesVN-Bold')
styles = {
    'title': ParagraphStyle('title', fontName='TimesVN-Bold', fontSize=23, leading=29, textColor=colors.HexColor('#102C43'), spaceAfter=18),
    'heading': ParagraphStyle('heading', fontName='TimesVN-Bold', fontSize=17, leading=22, textColor=colors.HexColor('#102C43'), spaceAfter=12, keepWithNext=True),
    'body': ParagraphStyle('body', fontName='TimesVN', fontSize=13, leading=19, spaceAfter=10),
    'small': ParagraphStyle('small', fontName='TimesVN', fontSize=10, leading=14, textColor=colors.HexColor('#435869'), spaceAfter=8),
    'cue': ParagraphStyle('cue', fontName='TimesVN-Italic', fontSize=11.5, leading=16, textColor=colors.HexColor('#236C70'), spaceAfter=10),
}
story=[]
plain=[]
def p(text, style='body'):
    story.append(Paragraph(escape(text).replace('\n','<br/>'),styles[style]))
    plain.append(text+'\n')
def newpage():
    story.append(PageBreak())
    plain.append('\n'+'='*70+'\n')
def stamp(c,doc):
    c.setFont('TimesVN',9)
    c.setFillColor(colors.HexColor('#435869'))
    c.drawString(42,25,'BTL Xử lý ảnh • Nhóm 4 • Kịch bản bảo vệ v2')
    c.drawRightString(A4[0]-42,25,str(doc.page))
p('KỊCH BẢN THUYẾT TRÌNH\nBÀI TẬP LỚN XỬ LÝ ẢNH','title')
p('Từ khử nhiễu SAR đến vùng tối ứng viên','heading')
p(data['version'],'small')
p(data['scope'])
p('Cách dùng: đọc phần “Lời trình bày” khi luyện tập. Phần “Thao tác / chuyển lời” là chỉ dẫn, không đọc thành tiếng. Các câu hỏi cuối tài liệu dùng để ôn và trả lời chéo giữa thành viên. Khi bảo vệ nên nói tự nhiên theo ý, không đọc toàn bộ văn bản liên tục.')
p('Đây là kịch bản ngắn theo thứ tự 18 slide của BAO_VE_BTL_XLA_V2.pptx. Notes trong PowerPoint là bản giải thích dài, liền mạch, không giới hạn 12 phút. Chọn bản phù hợp với thời lượng thực tế khi luyện nói.','cue')
rows=[[Paragraph('Thành viên',styles['small']),Paragraph('Slide',styles['small']),Paragraph('Thời lượng',styles['small'])]]
for member,name in team.items():
    chosen=[s for s in data['slides'] if s['speaker']==member]
    sec=sum(s['seconds'] for s in chosen)
    rows.append([Paragraph(member+' — '+name,styles['small']),Paragraph(', '.join(str(s['n']) for s in chosen),styles['small']),Paragraph(f'{sec//60} phút {sec%60:02d} giây',styles['small'])])
t=Table(rows,colWidths=[250,150,100],hAlign='LEFT')
t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E7F1F3')),('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#236C70')),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
story.append(t)
p('Phân vai theo docs/management/thanh_vien.json: TV3 Hồ Việt Tùng phụ trách lọc/tăng cường; TV4 Nguyễn Hải Hiếu phụ trách biên/hình thái. Lịch nói ở đây giữ thứ tự 18 slide hiện có.','small')
elapsed=0
for s in data['slides']:
    newpage()
    p(f"SLIDE {s['n']:02d}\n{s['title']}",'heading')
    end=elapsed+s['seconds']
    p(f"{s['speaker']} — {team[s['speaker']]} • {s['seconds']} giây • Mốc {elapsed//60:02d}:{elapsed%60:02d}–{end//60:02d}:{end%60:02d}",'cue')
    p('Lời trình bày','small')
    p(s['script'])
    story.append(Spacer(1,12))
    p('Thao tác / chuyển lời: '+s['cue'],'cue')
    p('Nguồn để đối chiếu: '+s['source'],'small')
    elapsed=end
newpage()
p('DEMO TRỰC TIẾP — 3 PHÚT','title')
p('Chuẩn bị trước: từ thư mục gốc dự án chạy .venv\\Scripts\\python -m streamlit run streamlit_app.py. Mở địa chỉ mà terminal hiển thị. Kiểm tra ảnh 00013, ảnh nền biển bất lợi và các nút cần dùng trước khi bảo vệ. Không khởi động chương trình lần đầu ngay trong ba phút demo.','body')
elapsed=0
for demo_index,item in enumerate(data['demo']):
    if demo_index == 3:
        newpage()
        p('DEMO — PHÂN TÍCH LỖI VÀ KẾT THÚC','title')
    end=elapsed+item['seconds']
    p(f"{elapsed//60:02d}:{elapsed%60:02d}–{end//60:02d}:{end%60:02d} • {team[item['speaker']]}",'heading')
    p(item['action'],'cue')
    p(item['script'])
    elapsed=end
newpage()
p('CÂU HỎI ÔN VÀ VẤN ĐÁP','title')
p('Mọi thành viên cần giải thích được toàn bộ pipeline. Người phụ trách chuẩn bị câu trả lời sâu hơn và chỉ được vị trí mã nguồn hoặc số liệu khi cần. Các câu trả lời dưới đây là gợi ý kiến thức, không phải kịch bản đoán trước câu hỏi của giảng viên.','body')
for i,(q,a) in enumerate(data['questions'],1):
    if i in (6,10):
        newpage()
        p('CÂU HỎI ÔN VÀ VẤN ĐÁP (TIẾP)','title')
    start=len(story)
    p(f'{i}. {q}','heading')
    p(a)
    group=story[start:]
    del story[start:]
    story.append(KeepTogether(group))
newpage()
p('KIỂM TRA TRƯỚC KHI BẢO VỆ','title')
for txt in [
    'Diễn tập một lượt có bấm giờ. Mốc 12 phút là mục tiêu, cần điều chỉnh tốc độ và khoảng dừng theo giọng đọc thực tế. Ưu tiên giữ giải thích về phạm vi dữ liệu, kiểm chứng và hạn chế báo nhầm.',
    'Mỗi thành viên tự diễn đạt lại phần của một bạn khác. Đặc biệt luyện phân biệt biên với mask, tăng tương phản với độ đúng, và kiểm chứng số học với hiệu quả nhận diện.',
    'Chuẩn bị ảnh demo, nguồn điện và trình duyệt. Lưu sẵn kết quả tại results/reproducible/ và hình trong report_overleaf/v2/assets/. Nếu dùng ảnh chạy trước thay demo trực tiếp, nói rõ với người nghe.',
    'Đối chiếu số liệu trước khi đổi cấu hình: TN 810, FP 2.885, FN 204, TP 1.639 trên 5.538 ảnh. Không ghép số đo của cấu hình khác vào cùng bảng.',
    'Không nói đã có mask chuẩn, đã kiểm thử độc lập theo cảnh, hoặc đã chứng minh nhận diện dầu chính xác. Những điều này chưa có bằng chứng trong thực nghiệm hiện tại.',
    'Tài liệu báo cáo v2: report_overleaf/v2/BAO_CAO_BTL_XLA.pdf. Nguồn số liệu: results/reproducible/confusion.json, results/verification/per_case.csv. Không cần đọc đường dẫn hay DOI khi trình bày, nhưng phải biết chỗ tra lại.',
]: p(txt)
pdf=OUT/'KICH_BAN_THUYET_TRINH_V2.pdf'
SimpleDocTemplate(str(pdf),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=42,bottomMargin=45,title='Kịch bản thuyết trình BTL Xử lý ảnh v2',author='Nhóm 4').build(story,onFirstPage=stamp,onLaterPages=stamp)
(OUT/'KICH_BAN_THUYET_TRINH_V2.txt').write_text('\n'.join(plain),encoding='utf-8')
from pypdf import PdfReader
reader=PdfReader(pdf)
assert all(s['title'] in '\n'.join(p.extract_text() for p in reader.pages) for s in data['slides'])
print(json.dumps({'pdf':str(pdf),'pages':len(reader.pages),'slides':len(data['slides']),'presentation_seconds':720,'demo_seconds':180},ensure_ascii=False))
