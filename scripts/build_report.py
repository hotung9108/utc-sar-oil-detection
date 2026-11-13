"""Build the report draft from the retained course template and measured evidence.

Run with the documents skill bundled Python. Rendering and human page review are
separate mandatory gates; this command never marks the report ready to submit.
"""
import hashlib
import io
import json
from copy import deepcopy
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt
from docx.enum.text import WD_TAB_ALIGNMENT
from docx.text.paragraph import Paragraph

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.cache/report'
OUT.mkdir(parents=True, exist_ok=True)
REF = next(ROOT.glob('*12_11.docx'))
EXPECTED = '3f02d4a480267f093eeed08cd9ca2dfc9034a1e45c7c979caae1e196cb6b915d'
assert hashlib.sha256(REF.read_bytes()).hexdigest() == EXPECTED
assert (ROOT / 'docs/report/template_contract.md').exists()


def load(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8'))


doc = Document(REF)
paragraphs = list(doc.paragraphs)
tables = list(doc.tables)
body_pattern = deepcopy(paragraphs[67]._p)
code_pattern = deepcopy(paragraphs[114]._p)
data = load('docs/report/narrative.json')
members = load('docs/management/thanh_vien.json')
evidence = load('results/sos/selection_evidence/evidence.json')
evaluation = load('results/sos/evaluation.json')
captions = []
for instruction in doc._element.xpath('//w:sdt//w:instrText'):
    if instruction.text and 'TOC \\a' in instruction.text:
        instruction.text = instruction.text.replace('TOC \\a', 'TOC \\c')


def clear(p):
    for child in list(p._p):
        if child.tag != qn('w:pPr'):
            p._p.remove(child)


def text(p, value, keep_format=False):
    rpr = deepcopy(p.runs[0]._r.rPr) if keep_format and p.runs and p.runs[0]._r.rPr is not None else None
    clear(p)
    run = p.add_run(str(value))
    if rpr is not None:
        run._r.insert(0, rpr)
    return p


def remove(element):
    node = getattr(element, '_element', element)
    if node.getparent() is not None:
        node.getparent().remove(node)


def after(anchor, value, code=False):
    element = deepcopy(code_pattern if code else body_pattern)
    anchor._p.addnext(element)
    p = Paragraph(element, doc._body)
    text(p, value)
    if code:
        for run in p.runs:
            run.font.name = 'Courier New'
            run.font.size = Pt(10)
    return p


def block(anchor, values):
    p = paragraphs[anchor]
    p._p.get_or_add_pPr().clear()
    p.style = 'Normal'
    text(p, values[0])
    for value in values[1:]:
        p = after(p, value)
    return p


def field(p, instruction, cached):
    for tag, val in [('begin', None), ('instr', instruction), ('separate', None), ('text', str(cached)), ('end', None)]:
        r = OxmlElement('w:r')
        if tag in ('begin', 'separate', 'end'):
            child = OxmlElement('w:fldChar')
            child.set(qn('w:fldCharType'), tag)
        elif tag == 'instr':
            child = OxmlElement('w:instrText')
            child.set(qn('xml:space'), 'preserve')
            child.text = ' ' + val + ' '
        else:
            child = OxmlElement('w:t')
            child.text = val
        r.append(child)
        p._p.append(r)


def caption(p, kind, chapter, number, title):
    text(p, f'{kind} {chapter}.')
    # Explicit reset avoids the source template's cross-chapter sequence drift.
    field(p, f'SEQ {kind} \\r {number}', number)
    p.add_run('. ' + title)
    p.alignment = 1
    p.paragraph_format.keep_with_next = kind == 'Bảng'
    for run in p.runs:
        run.bold = kind == 'Bảng'
        run.italic = kind == 'Hình'
    captions.append(f'{kind} {chapter}.{number}. {title}')
    return p


def fill_table(table, rows, widths=None):
    # Reuse table furniture and resize cells without touching source styles.
    while len(table.rows) > 1:
        table._tbl.remove(table.rows[-1]._tr)
    prototype = deepcopy(table.rows[0]._tr)
    columns = len(rows[0])
    for tr in (table.rows[0]._tr, prototype):
        cells = tr.findall(qn('w:tc'))
        for c in cells[columns:]:
            tr.remove(c)
        while len(tr.findall(qn('w:tc'))) < columns:
            tr.append(deepcopy(cells[-1]))
    grid = table._tbl.tblGrid
    for child in list(grid):
        grid.remove(child)
    widths = widths or [16 / columns] * columns
    for width in widths:
        c = OxmlElement('w:gridCol')
        c.set(qn('w:w'), str(round(width * 567)))
        grid.append(c)
    for _ in rows[1:]:
        table._tbl.append(deepcopy(prototype))
    table.autofit = False
    total_width = table._tbl.tblPr.find(qn('w:tblW'))
    total_width.set(qn('w:type'), 'dxa')
    total_width.set(qn('w:w'), str(round(sum(widths) * 567)))
    for i, (row, values) in enumerate(zip(table.rows, rows)):
        trpr = row._tr.get_or_add_trPr()
        for old in list(trpr):
            if old.tag in (qn('w:tblHeader'), qn('w:trHeight')):
                trpr.remove(old)
        trpr.append(OxmlElement('w:cantSplit'))
        if i == 0:
            trpr.append(OxmlElement('w:tblHeader'))
        for cell, value, width in zip(row.cells, values, widths):
            cell.width = Cm(width)
            cell.text = str(value)
            p = cell.paragraphs[0]
            p.alignment = 1 if i == 0 else 0
            p.paragraph_format.keep_with_next = i == 0
            for run in p.runs:
                run.font.name = 'Times New Roman'
                run.font.size = Pt(13)
                run.bold = i == 0
    return table


def new_table(anchor, rows, chapter, number, title, widths=None):
    cap = caption(after(anchor, ''), 'Bảng', chapter, number, title)
    node = deepcopy(tables[9]._tbl)
    cap._p.addnext(node)
    from docx.table import Table
    fill_table(Table(node, doc._body), rows, widths)
    return Paragraph(node.getnext(), doc._body) if node.getnext() is not None and node.getnext().tag == qn('w:p') else cap


def picture(p, path, chapter, number, title):
    clear(p)
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.left_indent = Cm(0)
    p.paragraph_format.right_indent = Cm(0)
    p.alignment = 1
    # Remove template dashed placeholder border, retain paragraph placement.
    for b in p._p.xpath('./w:pPr/w:pBdr'):
        b.getparent().remove(b)
    p.add_run().add_picture(str(ROOT / path), width=Cm(15.8))
    caption(after(p, ''), 'Hình', chapter, number, title)


# Remove instructions section, retaining subsequent source section definitions.
first_end = paragraphs[16]._p
for node in list(doc._element.body):
    remove(node)
    if node is first_end:
        break
for index in (24, 40):
    text(paragraphs[index], data['title'], True)
    paragraphs[index].style = 'Title'
for index in (20, 36):
    text(paragraphs[index], '')
for index in (25, 41):
    text(paragraphs[index], 'Giảng viên hướng dẫn: ____________________', True)
for index in (26, 42):
    text(paragraphs[index], 'Lớp học phần: ___________________________', True)
for index in (27, 43):
    text(paragraphs[index], 'Nhóm: __________________________________', True)
for index in (31, 47):
    text(paragraphs[index], 'Hà Nội, tháng 11 năm 2026', True)
for table in tables[1:4]:
    rows = [[c.text for c in table.rows[0].cells]]
    rows += [[str(i + 1), m['name'], '', ''] for i, m in enumerate(members)]
    fill_table(table, rows, [1.6, 6.4, 4, 4])
text(paragraphs[50], 'Báo cáo trình bày thực nghiệm phát hiện vết dầu tràn trên biển từ ảnh SAR với bộ Refined SOS. Nguồn dữ liệu, thuật toán tham khảo và công cụ hỗ trợ được khai báo trong tài liệu tham khảo và Phụ lục C.')
text(paragraphs[51], 'Số liệu được tạo bằng mã nguồn và lưu cùng kết quả từng ảnh để kiểm tra lại. Thành viên cần đối chiếu kết quả, xác nhận phần đóng góp thực tế và ký trước khi nộp. Việc hỗ trợ bằng AI không được tính thay cho đóng góp cá nhân đã xác minh.')
text(paragraphs[52], 'Xác nhận của các thành viên')
text(paragraphs[53], 'Hà Nội, ngày ____ tháng ____ năm ______', True)
block(56, data['preface'])
tails = {}
for section in data['sections']:
    tails[section['anchor']] = block(section['anchor'], section['paragraphs'])
    if 'heading' in section:
        text(paragraphs[section['anchor'] - 1], section['heading'], True)

fill_table(tables[4], [['Từ viết tắt', 'Tiếng Anh', 'Tiếng Việt'],
    ['CART', 'Classification and Regression Trees', 'Cây phân lớp và hồi quy'],
    ['FN / FP / TP', 'False negative / false positive / true positive', 'Bỏ sót / báo sai / phát hiện đúng'],
    ['IoU', 'Intersection over Union', 'Tỷ lệ giao trên hợp'],
    ['MSE', 'Mean Squared Error', 'Sai số bình phương trung bình'],
    ['SAR', 'Synthetic Aperture Radar', 'Radar khẩu độ tổng hợp'],
    ['SVM', 'Support Vector Machine', 'Máy vector hỗ trợ']], [2.6, 6.1, 7.3])
caption(paragraphs[73], 'Bảng', 1, 1, 'Chức năng và người phụ trách theo kế hoạch')
fill_table(tables[5], [['Bước', 'Chức năng và tình trạng', 'Phụ trách'],
    ['Tiền xử lý', 'Lọc NumPy; chưa có dữ liệu để chuẩn hóa góc tới', 'TV3'],
    ['Ứng viên', 'So sánh Otsu và Niblack; liên thông và hình thái', 'TV3, TV4'],
    ['Phân lớp', 'Tám đặc trưng; CART và SVM; nhãn dầu/nền', 'TV4, TV2'],
    ['Đánh giá', 'Precision, Recall, F1 đối tượng; IoU pixel; chưa có nhãn từng loại look-alike', 'TV5'],
    ['Tích hợp', 'CLI, notebook, mask và danh sách vùng', 'TV1']], [2.5, 10.5, 3])
after(paragraphs[71], 'Bảng 1.1 phân biệt chức năng đã cài với phần chưa đủ dữ liệu. Phân công là kế hoạch kiểm tra và bàn giao, không thay cho xác nhận công việc đã làm của mỗi người.')
caption(paragraphs[82], 'Bảng', 2, 1, 'Các tập dữ liệu sử dụng trong thực nghiệm')
fill_table(tables[6], [['Tập', 'Số ảnh', 'Vai trò'],
    ['Sentinel train', 2683, 'Fit classifier và chuẩn hóa đặc trưng'],
    ['Sentinel validation', 671, 'Chọn thuật toán và tham số'],
    ['Sentinel test', 839, 'Đánh giá cấu hình đã khóa'],
    ['PALSAR train', 3101, 'Chưa dùng huấn luyện'],
    ['PALSAR external test', 776, 'Đánh giá chuyển miền']], [6, 2.5, 7.5])
picture(paragraphs[85], 'results/sos/report_figures/dataset_examples.png', 2, 1, 'Sáu cặp ảnh và mask validation với seed 2026')
text(paragraphs[87], 'Hình 2.1 cho thấy cả vùng dầu mảnh, vùng lớn và ảnh không có nhãn dầu. Bảng 2.1 là phép chia cố định của thực nghiệm; mọi ảnh đều có kích thước 256×256 và định dạng PNG.')
picture(paragraphs[105], 'results/sos/report_figures/pipeline.png', 3, 1, 'Luồng suy luận tách biệt với ground truth')
text(paragraphs[107], 'Hình 3.1 tách đường suy luận khỏi đường đánh giá; mask tham chiếu không được truyền vào hàm predict.')
caption(paragraphs[110], 'Bảng', 3, 1, 'Đầu vào và đầu ra các bước của nhánh đã khóa')
fill_table(tables[7], [['Bước', 'Đầu vào', 'Phép toán', 'Đầu ra'],
    ['Đọc ảnh', 'PNG uint8', 'Chia 255', 'Float [0,1]'],
    ['Lọc', 'Float [0,1]', 'Lee 7×7, L=4', 'Ảnh lọc'],
    ['Ngưỡng', 'Ảnh lọc', 'Otsu 256 bins', 'Mask bool'],
    ['Vùng', 'Mask bool', 'Liên thông 8, diện tích ≥64', 'Label nguyên'],
    ['Đặc trưng', 'Vùng và ảnh', '8 đặc trưng', 'Ma trận n×8'],
    ['Phân lớp', 'Đặc trưng', 'SVM C=10', 'Mask, score, vùng']], [2.3, 4.2, 5.3, 4.2])

# Editable math, inserted adjacent to the theory it explains.
def equation(anchor, value, number):
    p = after(anchor, '')
    p.alignment = 0
    p.paragraph_format.tab_stops.add_tab_stop(Cm(8), WD_TAB_ALIGNMENT.CENTER)
    p.paragraph_format.tab_stops.add_tab_stop(Cm(16), WD_TAB_ALIGNMENT.RIGHT)
    p.add_run('\t')
    omath = OxmlElement('m:oMath')
    run = OxmlElement('m:r')
    token = OxmlElement('m:t')
    token.text = value
    run.append(token)
    omath.append(run)
    p._p.append(omath)
    p.add_run('\t(2.')
    field(p, f'SEQ CT \\r {number}', number)
    p.add_run(')')
    return p

p = tails[91]
for i, (formula, explanation) in enumerate([
    ('v = max(E[I²] − m², 0);  n = m²/L', 'm là trung bình trong cửa sổ, v là phương sai cục bộ, n là phương sai nhiễu xấp xỉ. L là tham số thử nghiệm trên PNG, chưa xác minh là số looks vật lý.'),
    ('w = max(v − n, 0)/max(v, ε);  J = m + w(I − m)', 'J là ảnh lọc và ε=10⁻¹² tránh chia 0. Công thức (2.1) và (2.2) tương ứng filter_image trong core.py; trọng số nhỏ làm kết quả gần trung bình, trọng số lớn giữ chênh lệch.'),
    ('T(x,y) = m(x,y) − k·s(x,y);  M = [J < T]', 'Công thức (2.3) là ngưỡng Niblack [6], với s là độ lệch chuẩn cục bộ. Đối tượng tối được lấy bằng phép so sánh nhỏ hơn; cửa sổ và k phải được chọn trên validation.')], 1):
    p = equation(p, formula, i)
    p = after(p, explanation)
p = after(p, 'Ví dụ kiểm chứng Lee dùng ma trận 5×5 có nền 0,2 và ô tâm 0,9. Cửa sổ 3×3 tại tâm cho m=5/18, v=98/2025 và n=25/1296 khi L=4. Từ đó w=943/1568 và J=1643/2520≈0,651984126984. scripts/worked_example.py tính các phân số chính xác và lưu toàn bộ ma trận trong example.json. Đây là ví dụ tổng hợp để kiểm tra công thức, không phải bằng chứng chất lượng phát hiện trên ảnh SAR.')
matrix = load('results/sos/worked_example/example.json')['input']
p = after(p, 'Bảng 2.2 là toàn bộ đầu vào của ví dụ; hàng và cột đánh số từ 0. Ô (2,2) là ô duy nhất khác nền. Tại ô tâm, cửa sổ không chạm biên; khi đối chiếu cả ma trận, hai triển khai phải dùng cùng đệm reflect/mirror như đã quy định.')
new_table(p, [['y / x', '0', '1', '2', '3', '4']] + [[str(i)] + [f'{x:.1f}' for x in row] for i, row in enumerate(matrix)], 2, 2, 'Ma trận 5×5 dùng kiểm chứng Lee')
for value in [
    'Có thể giải thích dạng trọng số bằng một mô hình cục bộ đơn giản. Giả sử Y=X+N, E[N]=0, Cov(X,N)=0 và m=E[X]=E[Y]. X là tín hiệu cần ước lượng, Y là quan sát, N là nhiễu. Xét riêng họ ước lượng tuyến tính X̂=m+a(Y−m), với a là một số thực trong cửa sổ đang xét. Những giả thiết này là điều kiện của phép dẫn xuất, không phải điều đã được kiểm chứng trên PNG SOS.',
    'Đặt Xc=X−m. Khi đó X̂−X=(a−1)Xc+aN. Bình phương rồi lấy kỳ vọng cho rủi ro R(a)=(a−1)²Var(X)+a²Var(N), vì hạng chéo có kỳ vọng bằng 0 theo giả thiết không tương quan. Đạo hàm R′(a)=2(a−1)Var(X)+2aVar(N). Với tổng phương sai dương, nghiệm R′(a)=0 là a=Var(X)/(Var(X)+Var(N)). Đạo hàm bậc hai bằng hai lần tổng phương sai và dương, nên đây là cực tiểu trong họ ước lượng tuyến tính đang xét.',
    'Do Var(Y)=Var(X)+Var(N), trọng số cũng viết thành a=1−Var(N)/Var(Y). Thay phương sai tổng thể bằng thống kê mẫu cục bộ đưa đến cấu trúc của (2.2). Khi ước lượng nhiễu lớn hơn phương sai quan sát, phép chặn max(v−n,0) tránh trọng số âm. Khi phương sai gần 0, ε giúp phép chia xác định. Đây là hai lựa chọn kỹ thuật của bản cài; chúng không tự tạo ra một định lý tối ưu cho ảnh thực.',
    'Speckle SAR thường được xét dưới mô hình nhân; việc thay Var(N) bằng m²/L là xấp xỉ trong biến thể đang khảo sát. Vì vậy chứng minh tuyến tính ở trên chỉ giải thích cơ chế giảm ảnh hưởng của sai lệch pixel theo tỷ lệ phương sai. Nó không chứng minh PNG là cường độ radar tuyến tính, không suy ra số looks thật, và không chọn được L=4 hoặc cửa sổ 7×7. Những tham số đó chỉ được bàn luận dựa trên validation ở Chương 4.',
    'Ví dụ số đã được kiểm chứng bằng NumPy: scripts/worked_example.py dùng Fraction để tính chính xác kết quả tâm rồi so với core.filter_image và bản ghép SciPy. Sai số lớn nhất của hai ma trận là khoảng 1,943×10⁻¹⁶, MSE khoảng 6,933×10⁻³³. Một ví dụ hữu tỉ giúp bắt lỗi công thức và quy ước phương sai; tập ảnh validation và các ca biên kiểm tra những đầu vào khác. Không dùng kết quả trên ma trận tổng hợp để thay cho số liệu chất lượng phát hiện.'
]:
    p = after(p, value)
p = equation(p, 'V(t) = ω₀(t)ω₁(t)[μ₀(t)−μ₁(t)]²', 4)
p = after(p, 'Trong (2.4), ω₀ và ω₁ là tỷ lệ số pixel ở hai phía ngưỡng histogram; μ₀ và μ₁ là trung bình mức xám của hai nhóm. Otsu [5] chọn ngưỡng làm phương sai giữa lớp V lớn nhất. Code core.otsu dùng số đếm tích lũy thay xác suất; tiêu chí tương đương về argmax vì chỉ khác một thừa số dương không phụ thuộc t. Các ngưỡng tạo nhóm rỗng bị loại để tránh chia 0.')
p = after(p, 'Histogram dùng đúng 256 bin trên [0,1] và tâm bin làm đại diện mức xám. Việc chọn tâm bin đầu tiên khi hòa là một phần của định nghĩa cài đặt. Nếu tự động thay miền histogram theo min/max của từng ảnh, ngưỡng có thể khác dù vẫn gọi là Otsu; vì vậy reference.otsu được cấu hình cùng histogram khi kiểm chứng. Chi phí tạo histogram là O(HW), phần quét ngưỡng O(B) với B=256 và bộ nhớ phụ O(B).')
p = after(p, 'Với phép lọc Gaussian, kernel một chiều gồm năm giá trị tỉ lệ exp(−x²/(2σ²)) cho x từ −2 đến 2, sau đó chuẩn hóa tổng bằng 1 và tương quan lần lượt theo hai trục. Đây là cửa sổ cắt cố định, không phải mọi cách chọn truncate của thư viện đều tương đương. Median lấy trung vị các pixel trong cửa sổ lẻ; mean lấy trung bình bằng tổng tích phân. Những khác biệt định nghĩa được cố định trước khi đo sai số giữa các triển khai.')
p = equation(tails[93], 'Q(w) = [½‖w‖² + C Σ max(0,1 − yᵢxᵢᵀw)²]/n', 5)
p = after(p, 'Trong (2.5), n là số ứng viên train, yᵢ∈{−1,+1}, xᵢ gồm các đặc trưng chuẩn hóa và một cột hằng. Bias được regularize như bản LinearSVC đối chứng. models.py dùng objective này cho gradient và kiểm tra hội tụ, không chỉ đối chiếu nhãn đầu ra.')
p = equation(p, 'G(p)=2p(1−p);  Δ=nG−nL·GL−nR·GR', 6)
p = after(p, 'Công thức (2.6) là Gini nhị phân và mức giảm có trọng số mẫu dùng trong CART [7]. p là tỷ lệ nhãn dương ở nút; n, nL và nR là số ứng viên ở nút cha và hai nhánh. Tại một nút cố định, nhân gain với n không đổi thứ tự điểm chia so với gain chuẩn hóa. models.CART dùng dạng số đếm để tính đồng thời các điểm chia từ tổng nhãn tích lũy. Cột đặc trưng, giá trị ngưỡng và min_leaf quyết định các điểm chia hợp lệ.')
p = after(p, 'Bảng 2.3 mô tả đúng tám cột đầu vào của classifier. Với vùng R, A=|R|, H×W là kích thước ảnh, μR và σR là trung bình và độ lệch chuẩn mức xám của vùng. Các đại lượng hình học đo bằng pixel, chưa chuyển sang mét do SOS không có độ phân giải mặt đất cho từng patch.')
new_table(p, [['Đặc trưng', 'Định nghĩa trong code', 'Ý nghĩa và giới hạn'],
    ['area_fraction', 'A/(H×W)', 'Tỷ lệ ảnh bị vùng chiếm; không phải diện tích km²'],
    ['elongation', '√((λmax+ε)/(λmin+ε))', 'λ là trị riêng hiệp phương sai tọa độ; ε=10⁻⁶'],
    ['extent', 'A/diện tích hộp bao', 'Mức lấp đầy hộp bao trục song song ảnh'],
    ['complexity', 'P²/(4πA)', 'P là chu vi đếm cạnh lưới; không phải đường bao liên tục'],
    ['mean', 'μR', 'Mức xám trung bình trên ảnh lọc'],
    ['std', 'σR với ddof=0', 'Độ phân tán trong vùng'],
    ['boundary_gradient', 'Mean độ lớn Sobel trên biên', 'Kernel Sobel chia 8; biên lấy bằng R trừ erosion'],
    ['background_\ncontrast', '(μB−μR)/(|μB|+ε)', 'B là vành ngoài bán kính 5, chỉ lấy pixel label=0']],
    2, 3, 'Định nghĩa và giới hạn đặc trưng vùng', [4, 5, 7])
p = after(p, 'Nếu vành ngoài không có pixel nền, code dùng toàn bộ nền của ảnh; nếu cả ảnh không có nền, dùng trung bình toàn ảnh. Quy tắc dự phòng này tránh NaN nhưng làm đặc trưng tương phản mất ý nghĩa nền cục bộ trong trường hợp vùng phủ gần hết ảnh. Bản NumPy và bản tham chiếu cùng dùng quy tắc đó, vì khác định nghĩa vùng nền có thể tạo sai số dù cả hai chương trình đều chạy đúng.')
p = after(p, 'Nhóm đặc trưng hình dạng dùng bốn cột đầu; nhóm cường độ dùng bốn cột cuối; nhóm đầy đủ dùng cả tám. So sánh ba nhóm giữ cùng cách tạo ứng viên nhằm đo ảnh hưởng của thông tin đầu vào classifier. Chuẩn hóa z-score dùng trung bình và độ lệch chuẩn chỉ tính trên tập train; cột gần hằng có hệ số chia bảo vệ. Một vùng ở test được biến đổi bằng chính các thống kê train đã lưu.')
p = equation(tails[96], 'Precision = TP/(TP+FP);  Recall = TP/(TP+FN)', 7)
p = equation(p, 'F1 = 2TP/(2TP+FP+FN);  IoU = |A∩B|/|A∪B|', 8)
after(p, 'Các công thức (2.7)–(2.8) có miền [0,1] khi mẫu số dương; giá trị lớn hơn là tốt hơn. A và B là hai mask. TP, FP, FN được đếm sau ghép một–một đối tượng với IoU≥0,5. Trường hợp mẫu số bằng 0 được lưu null và công bố số ảnh xác định khi tính trung bình, không tự thay bằng 1.')
p = after(p, 'Đơn vị đối tượng được suy ra bằng thành phần liên thông 8 trên mask nhị phân. Mỗi đối tượng dự đoán chỉ ghép với tối đa một đối tượng tham chiếu. Thuật toán ghép tối đa số cặp đạt IoU≥0,5 trước, rồi mới ưu tiên tổng IoU trong các phương án có cùng số cặp. Cách này tránh để một cặp IoU rất cao chiếm chỗ của hai cặp hợp lệ khác. evaluation.py thực hiện quy tắc đó bằng bài toán gán; tests kiểm tra sự thống nhất giữa số đếm từ vùng và từ mask.')
p = after(p, 'Ví dụ minh họa quy tắc chấm: nếu một đối tượng GT bị chia thành ba mảnh dự đoán và chỉ một mảnh đạt IoU≥0,5, kết quả là một TP và hai FP, không phải ba TP. Nếu cả ba mảnh đều dưới ngưỡng, kết quả là ba FP và một FN. Dù phần lớn pixel vẫn nằm trong GT, F1 đối tượng có thể thấp. Ví dụ này giải thích cơ chế độ đo, không phải một hàng kết quả mới trên SOS.')
after(p, 'Micro F1 cộng TP, FP, FN của toàn tập rồi tính một lần; macro F1 tính riêng từng ảnh rồi lấy trung bình trên các ảnh xác định. Hai cách trả lời hai câu hỏi khác nhau: micro nhấn mạnh tổng số đối tượng, còn macro cho mỗi ảnh trọng số như nhau. Báo cáo dùng micro để chọn cấu hình và công bố thêm độ phân tán từng ảnh, không thay đổi cách gộp để làm kết quả trông tốt hơn.')
for i in (97, 98, 99):
    remove(paragraphs[i])

# Compact pseudocode with explicit source linkage, no pasted implementation.
algorithms = [
    ['Thuật toán 1  Lee với tổng tích phân', 'Vào: ảnh I float, cửa sổ lẻ k, L>0', '1. Đệm reflect không lặp biên.', '2. Tính m=mean(I), q=mean(I²) bằng tổng tích phân.', '3. v=max(q−m²,0); n=m²/L.', '4. w=max(v−n,0)/max(v,1e−12).', '5. Trả về m+w·(I−m).', 'Mã: core.mean_filter và core.filter_image.'],
    ['Thuật toán 2  CART tại một nút', 'Vào: X, y, depth, min_leaf', '1. Nếu lá thuần hoặc đạt giới hạn sâu: tạo lá.', '2. Với từng cột: sắp xếp ổn định các mẫu.', '3. Tính tổng nhãn tích lũy và Gini hai nhánh.', '4. Bỏ điểm chia vi phạm min_leaf.', '5. Chọn gain lớn nhất theo quy tắc hòa xác định.', '6. Nếu gain không dương: tạo lá; nếu không: đệ quy.', 'Mã: models.py, lớp CART.'],
    ['Thuật toán 3  SVM squared hinge', 'Vào: X đã chuẩn hóa, y∈{−1,+1}, C, tol', '1. Thêm cột hằng và khởi tạo trọng số.', '2. Tính Q và gradient theo (2.5).', '3. Backtracking để chọn bước giảm Q hợp lệ.', '4. Cập nhật trọng số với tăng tốc và restart.', '5. Dừng nếu chuẩn gradient đạt tol.', '6. Nếu hết vòng lặp: lưu trạng thái chưa hội tụ.', 'Mã: models.py, lớp LinearSVM.']]
p = paragraphs[114]
for algorithm_index, lines in enumerate(algorithms):
    for line_index, line in enumerate(lines):
        if algorithm_index == 0 and line_index == 0:
            text(p, line)
        else:
            p = after(p, line, code=True)
        p.paragraph_format.keep_together = True
        p.paragraph_format.keep_with_next = line_index < len(lines) - 1
        if line_index == 0:
            p.paragraph_format.space_before = Pt(10)
            for run in p.runs:
                run.bold = True
for i in range(115, 120):
    remove(paragraphs[i])
caption(paragraphs[120], 'Bảng', 3, 3, 'Sai số đối chiếu trên tám ảnh validation')
checks = load('results/sos/verification_real.json')['checks']
groups = {}
for check in checks:
    if check['operation'] != 'filter':
        continue
    name = check['config']['name']
    groups.setdefault(name, []).append(check)
rows = [['Bộ lọc', 'Max |Δ|', 'MSE lớn nhất', 'NumPy ms', 'Tham chiếu ms']]
for name, values in groups.items():
    rows.append([name, f"{max(v['max_abs_error'] for v in values):.2e}", f"{max(v['mse'] for v in values):.2e}",
                 f"{1000*sum(v['numpy_seconds'] for v in values)/len(values):.2f}",
                 f"{1000*sum(v['reference_seconds'] for v in values)/len(values):.2f}"])
fill_table(tables[8], rows, [2.4, 3, 3.6, 3.5, 3.5])
model_comparison = load('results/sos/model_comparison.json')
p = after(tails[113], 'Bảng 3.2 giữ đặc trưng đầu vào như nhau giữa NumPy và scikit-learn, rồi so sánh đầu ra và thời gian fit. Agreement=1 chỉ mô tả tập ứng viên validation đã kiểm tra. Kiểm tra toàn pipeline NumPy được thực hiện riêng để phát hiện sai khác có thể xuất hiện trước bước phân lớp.')
rows = [['Classifier', 'F1 NumPy', 'F1 thư viện', 'Agreement', 'Fit NumPy / thư viện (s)']]
for row in model_comparison:
    rows.append([row['kind'].upper(), f"{row['metrics']['f1']:.6f}", f"{row['reference_metrics']['f1']:.6f}",
                 f"{row['agreement']:.6f}", f"{row['timings']['numpy_fit_seconds']:.4f} / {row['timings']['reference_fit_seconds']:.4f}"])
new_table(p, rows, 3, 2, 'Đối chiếu classifier trên cùng đặc trưng validation', [3, 3, 3, 3, 4])
after(tails[113], 'Bảng 3.3 gộp các cấu hình trong từng họ lọc: lấy sai số lớn nhất và thời gian trung bình của các lượt đã ghi. Thời gian một lượt chịu ảnh hưởng tải máy, không phải benchmark tốc độ lặp nhiều lần. Bản tham chiếu Lee ghép thống kê SciPy với cùng công thức; độ khớp không chứng minh độ chính xác phát hiện dầu.')
diagnostic_images = sorted((ROOT / 'results/sos/diagnostics').glob('*.png'))
diagnostic_cases = {case['figure']: case for case in load('results/sos/diagnostics/diagnostics.json')['failure_cases']}
assert len(diagnostic_images) >= 3
picture(paragraphs[125], str(diagnostic_images[0].relative_to(ROOT)), 3, 2, 'Ảnh đầu vào và các bước tạo mask trong một ca thất bại')
text(paragraphs[127], 'Hình 3.2 đặt các bước ở cùng thang để phân biệt lỗi tạo ứng viên và lỗi giữ hoặc loại vùng; các ca cụ thể được phân tích tiếp trong Chương 4.')
p = after(paragraphs[127], 'Bảng 3.4 ánh xạ từng trách nhiệm trong pipeline sang file thực thi. Tách bộ đo khỏi hàm suy luận giúp kiểm tra luồng dữ liệu: module pipeline không được nhận mask để lựa chọn đầu ra, trong khi experiments có thể dùng mask của train để tạo nhãn và mask validation để chọn cấu hình.')
new_table(p, [['Module', 'Trách nhiệm', 'Bằng chứng đầu ra'],
    ['data.py', 'Đọc cặp ảnh–mask, manifest và split', 'Danh sách ID cố định; ảnh float và mask bool'],
    ['core.py', 'Bộ lọc, ngưỡng, hình thái, liên thông và đặc trưng NumPy', 'Ảnh trung gian, label và ma trận đặc trưng'],
    ['reference.py', 'Đối chứng cùng quy ước bằng SciPy và scikit-image', 'Sai số, MSE trên cùng đầu vào'],
    ['models.py', 'Chuẩn hóa train; CART và SVM; lưu trạng thái', 'Model JSON và chẩn đoán hội tụ'],
    ['pipeline.py', 'Ghép các bước suy luận độc lập GT', 'Mask cuối và danh sách vùng'],
    ['evaluation.py', 'Ghép đối tượng và cộng số đếm', 'TP, FP, FN, Precision, Recall, F1'],
    ['experiments.py', 'Sàng lọc, fit, chọn cấu hình và đánh giá', 'screen, validation, selected, evaluation'],
    ['provenance.py', 'Kiểm tra nguồn, môi trường và dữ liệu của checkpoint', 'Từ chối cache không khớp run']],
    3, 4, 'Trách nhiệm module và đường đi bằng chứng', [3.5, 6.6, 5.9])
p = after(p, 'Các notebook không chứa một phiên bản thuật toán tách biệt. Chúng gọi module dùng chung, đọc kết quả đã lưu và hiển thị bảng hoặc hình. Cách tổ chức này tránh việc sửa CLI nhưng quên sửa notebook, hoặc báo cáo đọc một cấu hình khác cấu hình dùng để dự đoán. run_experiments.py gọi các bước theo thứ tự và ghi mã thoát; dừng ngay khi một bước thất bại.')
after(p, 'Checkpoint giúp không huấn luyện lại khi chỉ sửa phần trình bày. Kiểm tra provenance phải thành công trước khi tái sử dụng số liệu: cache cũ không được đổi tên thành kết quả mới. Thực nghiệm bổ sung được lưu trong nhánh riêng và công bố rõ thực hiện sau lựa chọn. Sự phân tách này đặc biệt cần thiết khi tập test đã được xem, vì chạy lại cùng test không khôi phục tính độc lập của một đánh giá chưa từng sử dụng.')
caption(paragraphs[135], 'Bảng', 4, 1, 'Kết quả pipeline đã khóa và các đối chứng')
rows = [['Tập hoặc đối chứng', 'Precision', 'Recall', 'F1', 'IoU pixel']]
for name, value in evaluation.items():
    if name == 'provenance':
        continue
    metric = value['metrics']
    rows.append([name.replace('_', ' '), *[f'{metric[k]:.5f}' for k in ('precision', 'recall', 'f1', 'pixel_iou')]])
fill_table(tables[9], rows, [5.6, 2.6, 2.6, 2.6, 2.6])
environment = load('docs/report/environment.json')
after(tails[132], f"Máy được ghi nhận khi chuẩn bị báo cáo: {environment['cpu']}; {environment['logical_cpus']} CPU logic; RAM {environment['ram_bytes']/2**30:.2f} GiB; {environment['os']}; Python {environment['python']}. Đây là thông tin máy tại thời điểm ghi nhận, không phải nhật ký tải máy của mỗi lượt benchmark. Không dùng một lần đo để khẳng định hơn kém tốc độ một cách phổ quát.")
p = after(tails[139], 'Bảng 4.2 so sánh chỉ thay bộ lọc và giữ Otsu, không hình thái, min_area=16. Các số là F1 tạo ứng viên, chưa qua classifier. Hình 4.1 cho thấy ảnh hưởng cửa sổ và tham số ngưỡng trên validation.')
controlled = evidence.get('controlled_filters', evidence.get('controlled_comparison'))
if controlled is None:
    controlled = next(v for v in evidence.values() if isinstance(v, list) and v and isinstance(v[0], dict) and 'lee_minus_filter_f1' in v[0])
rows = [['Bộ lọc', 'TP', 'FP', 'FN', 'F1']]
for row in controlled:
    cfg, metric = row['filter'], row['metrics']
    label = cfg['name'] + (' '+str(cfg['size']) if 'size' in cfg else '') + (' L='+str(cfg['looks']) if 'looks' in cfg else '') + (' σ='+str(cfg['sigma']) if 'sigma' in cfg else '')
    rows.append([label, metric['tp'], metric['fp'], metric['fn'], f"{metric['f1']:.5f}"])
new_table(p, rows, 4, 2, 'Đối chứng bộ lọc trên 671 ảnh validation', [6, 2.5, 2.5, 2.5, 2.5])
p = after(p, 'Việc bổ sung mean7 và median7 kiểm tra một khả năng giải thích khác: ưu thế quan sát được có thể đến từ cửa sổ 7×7 thay vì riêng cơ chế thích nghi của Lee. Mean7 đạt F1 gần Lee7,L4. Khoảng bootstrap của chênh lệch chứa 0 nên dữ liệu hiện có chưa tách được rõ hai phương án. Kết luận đúng là Lee đáng giữ làm cấu hình đã khảo sát, không phải Lee đã được chứng minh vượt mọi bộ lọc.')
p = after(p, 'Bootstrap lấy mẫu lại cùng chỉ số ảnh cho hai bộ lọc để giữ cấu trúc so sánh cặp. Mỗi lần cộng số đếm của các ảnh được lấy rồi tính lại micro F1, sau đó lấy phân vị 2,5% và 97,5% của hiệu số. Phân tích dùng 2000 lần và seed=2026. Do chưa có mã cảnh gốc, các patch có thể phụ thuộc nhau; khoảng này không phải khoảng tin cậy theo cảnh và chưa hiệu chỉnh việc thử nhiều cấu hình.')
after(p, 'Các phép thử gốc được chia giai đoạn để giới hạn chi phí: chọn ba cấu hình ứng viên rồi mới khảo sát classifier. Vì vậy một bộ lọc có F1 ứng viên thấp nhưng tạo vùng dễ phân lớp có thể bị loại sớm. Đây là giới hạn thiết kế cần ghi nhận. Muốn kết luận tốt nhất toàn pipeline, cần mở rộng cùng ngân sách khảo sát cho các họ lọc và đánh giá trên tập test mới; không dùng lại test đã xem như bằng chứng độc lập.')
p = after(tails[134], '')
picture(p, 'results/sos/report_figures/parameter_study.png', 4, 1, 'Ảnh hưởng tham số trên tập validation')
p = after(tails[142], 'Hình 4.2 minh họa sự phân mảnh ở sentinel_440, Hình 4.3 cho thấy lỗi trên cấu trúc hẹp ở sentinel_25, còn Hình 4.4 cho thấy classifier loại bỏ ứng viên ở sentinel_591. Các hình được chọn theo quy tắc lỗi đã lưu, không phải một mẫu ngẫu nhiên đại diện cho toàn bộ test.')
for i, path in enumerate(diagnostic_images[:3], 2):
    p = after(p, '')
    picture(p, str(path.relative_to(ROOT)), 4, i, 'Phân tích lỗi trên ảnh ' + diagnostic_cases[path.name]['id'])
    p = Paragraph(p._p.getnext(), doc._body)
p = after(p, 'Bảng 4.3 bổ sung phân bố từng ảnh của nhánh test đã khóa. Mỗi độ đo có số ảnh xác định riêng vì quy tắc mẫu số bằng 0. Đây là thống kê mô tả trên toàn tập test, không phải khoảng tin cậy của hiệu năng ở một vùng biển mới. Độ lệch chuẩn lớn của F1 phản ánh mức chênh lệch giữa các patch và phù hợp với các trường hợp thất bại đã minh họa.')
distribution = load('results/sos/diagnostics/diagnostics.json')['experiments']['test_final']['per_image']
rows = [['Độ đo từng ảnh', 'Trung bình ± SD', 'Min – Max', 'Số ảnh xác định']]
for key, label in [('precision', 'Precision'), ('recall', 'Recall'), ('f1', 'F1'), ('pixel_iou', 'IoU pixel'), ('dice', 'Dice'), ('fp_per_image', 'FP/ảnh')]:
    r = distribution[key]
    rows.append([label, f"{r['mean']:.5f} ± {r['std_population']:.5f}", f"{r['min']:.5f} – {r['max']:.5f}", f"{r['defined']}/839"])
new_table(p, rows, 4, 3, 'Thống kê từng ảnh test với độ lệch chuẩn tổng thể', [3.5, 5.2, 4.3, 3])
p = after(p, 'Micro F1=0,28052 không bằng trung bình F1 từng ảnh=0,34912 vì hai cách gộp có trọng số khác nhau. Không nên chọn cách gộp sau khi xem điểm nào lớn hơn. Khi so sánh với bài báo khác còn phải giữ cùng quy tắc đối tượng, ngưỡng ghép, tập kiểm tra và cách xử lý ảnh rỗng. Do các điều kiện đó chưa được chứng minh tương đương với kết quả CBD-Net [3], báo cáo không lập bảng tuyên bố hơn hoặc kém mô hình công bố chỉ từ các con số khác giao thức.')
after(p, 'Dice pixel được tính bằng 2|A∩B|/(|A|+|B|), còn FP/ảnh là tổng số đối tượng dự đoán không ghép được chia số ảnh. Các độ đo pixel và đối tượng bổ sung cho nhau: Dice hoặc IoU cao vẫn có thể đi cùng nhiều FP đối tượng do phân mảnh. MSE trong Bảng 3.3 lại đo sai khác giữa hai triển khai, không đo chất lượng phân đoạn so với mask. Cần giữ riêng ba câu hỏi về độ phủ, số đối tượng và tính đúng cài đặt.')

# References and appendices retain source locations and formatting.
for index in range(153, 157):
    remove(paragraphs[index])
reference_end = block(152, [f"[{r['number']}] {r['citation']} {r['url']}" for r in load('docs/report/bibliography.json')])
reference_node = paragraphs[152]._p
while True:
    reference_paragraph = Paragraph(reference_node, doc._body)
    reference_paragraph.alignment = 0
    reference_paragraph.paragraph_format.keep_together = True
    if reference_node is reference_end._p:
        break
    reference_node = reference_node.getnext()
caption(paragraphs[160], 'Bảng', 'PL', 1, 'Phân công kiểm tra và bàn giao')
fill_table(tables[10], [['Thành viên', 'Nhiệm vụ', 'Sản phẩm kiểm tra']] + [[m['name'], m['role'], m['modules']] for m in members], [3.8, 5.4, 6.8])
caption(paragraphs[163], 'Bảng', 'PL', 2, 'Xác nhận đóng góp thực tế')
fill_table(tables[11], [['Thành viên', 'Mã SV', 'Điểm đồng đội', 'Tỷ lệ %', 'GV xác nhận']] + [[m['name'], '', '', '', ''] for m in members], [4.4, 2.4, 3.5, 2.5, 3.2])
text(paragraphs[166], 'Biên bản họp cần được lập từ buổi họp thực tế và có xác nhận của người tham dự. Không dùng kế hoạch phân công hoặc nhật ký chạy tự động thay cho biên bản họp.')
for i in range(167, 174):
    remove(paragraphs[i])
remove(tables[12])
caption(paragraphs[176], 'Bảng', 'PL', 3, 'Khai báo hỗ trợ bằng AI')
fill_table(tables[13], [['Công cụ', 'Phần hỗ trợ', 'Kiểm tra đã chạy', 'Xác nhận con người'],
    ['Codex', 'Refactor, cài đặt NumPy, thực nghiệm, notebook và báo cáo', 'Tests, đối chiếu thư viện, thống kê từng ảnh, render tài liệu', 'Thành viên cần đọc mã, chạy lại và xác nhận phần mình phụ trách']], [2.1, 5.2, 4.6, 4.1])
text(paragraphs[179], 'Repository: https://github.com/hotung9108/utc-sar-oil-detection. Dữ liệu: Refined SOS [2]. Ảnh nguồn không được đóng gói lại trong mã nguồn; xem data/README.md để bố trí thư mục.')
commands = ['python -m venv .venv', '.venv/Scripts/python.exe -m pip install -r requirements.txt', '.venv/Scripts/python.exe run_experiments.py --workers 6', '.venv/Scripts/python.exe run_experiments.py --verify-only']
for i, value in zip(range(180, 184), commands):
    text(paragraphs[i], value, True)
text(paragraphs[184], 'Bảng 4.1 đọc evaluation.json; Bảng 4.2 được tái tạo bằng scripts/explain_selection.py; ví dụ số dùng scripts/worked_example.py. Mã ở src/sar_oil, lệnh chạy ở scripts, notebook ở notebooks và mọi số liệu ở results/sos. Lệnh verify-only chỉ kiểm tra kết quả đã lưu, không phải chạy lại toàn bộ thực nghiệm.')

# Delete all remaining instructional paragraphs, not real bracket citations.
for p in list(doc.paragraphs):
    if p.text.startswith(('[Hướng dẫn', '[Độ dài')):
        remove(p)
setting = doc.settings.element.find(qn('w:updateFields'))
if setting is None:
    setting = OxmlElement('w:updateFields')
    doc.settings.element.append(setting)
setting.set(qn('w:val'), 'true')
buffer = io.BytesIO()
doc.save(buffer)
editable = {'word/document.xml', 'word/_rels/document.xml.rels', 'word/settings.xml', '[Content_Types].xml'}
destination = OUT / 'Bao_cao_SAR_SOS.docx'
with ZipFile(REF) as source, ZipFile(buffer) as changed, ZipFile(destination, 'w', ZIP_DEFLATED) as result:
    for name in source.namelist():
        result.writestr(name, changed.read(name) if name in editable else source.read(name))
    for name in changed.namelist():
        if name not in source.namelist():
            result.writestr(name, changed.read(name))
with ZipFile(REF) as source, ZipFile(destination) as result:
    preserved = [name for name in source.namelist() if name not in editable]
    assert all(source.read(name) == result.read(name) for name in preserved)
audit = {'reference_sha256': EXPECTED, 'output': str(destination), 'preserved_parts': preserved,
         'source_sections': 5, 'output_sections': len(doc.sections), 'captions': captions,
         'layout_verified': False, 'fields_need_word_update': True,
         'missing_metadata': ['instructor', 'class', 'group', 'student_ids', 'signatures', 'peer_scores', 'meeting_minutes']}
assert len(doc.sections) == 4
(OUT / 'build_audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')
print('Built report draft; preserve-only parts match. Rendering and field updates pending.')
