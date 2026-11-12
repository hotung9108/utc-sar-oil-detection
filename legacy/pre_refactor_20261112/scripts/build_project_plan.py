"""Build the team's dated retrospective work plan without asserting past completion."""

import argparse
import datetime as dt
import json
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo

ROOT = Path(__file__).resolve().parents[1]
START = dt.date(2026, 8, 10)
END = dt.date(2026, 11, 11)
OUTPUT = ROOT / "docs/management/KE_HOACH_PHAN_CONG_1008_1111_2026.xlsx"

# Each stage has five distinct responsibilities, in TV1 through TV5 order.
STAGES = [
    (
        "Chốt yêu cầu và phạm vi",
        "Có bảng yêu cầu, phân công và giới hạn không ML/DL",
        [
            "Đọc quy định chung; chốt mục tiêu BTL, vai trò và danh sách sản phẩm nộp|docs/management/PHAN_CONG_MA_NGUON.md",
            "Tách yêu cầu tự cài NumPy và đối chiếu thư viện thành checklist|docs/management/DOI_CHIEU_YEU_CAU_BTL.md",
            "Học pixel, dtype, kernel, padding; chọn các bộ lọc cần khảo sát|Sổ tay TV3, chương nền tảng",
            "Phân biệt làm nét, biên và mask; xác định đầu ra cần có|Sổ tay TV4, chương nền tảng",
            "Tìm nguồn SAR, đọc metadata và giấy phép; phân biệt nhãn ảnh/mask|kaggle/metadata/",
        ],
    ),
    (
        "Thiết lập môi trường và dữ liệu",
        "Chạy được môi trường, đọc ảnh và kiểm kê dữ liệu",
        [
            "Thiết lập Python, uv và cấu trúc module; hướng dẫn chạy trên Windows|pyproject.toml; uv.lock; run_app.bat",
            "Thiết kế ma trận đối chiếu: phép toán, đầu vào, reference, sai số|src/tv2/library_comparison.py",
            "Cài phép lấy cửa sổ và box filter; giải thích reflect/symmetric|src/tv3/filters.py",
            "Thiết kế ảnh tổng hợp: hằng, cạnh ngang/dọc/chéo, vùng có lỗ|tests/test_core.py",
            "Kiểm đếm hai lớp, kích thước và hash bản sao; chọn mẫu khảo sát|scripts/audit_dataset.py",
        ],
    ),
    (
        "Lọc cơ bản và đạo hàm",
        "Ví dụ số nhỏ khớp phép tính và không tràn uint8",
        [
            "Xây hàm đọc ảnh, kiểm đầu vào và hợp đồng đầu ra pipeline|src/tv1/utils.py; src/tv1/validation.py",
            "Tính ví dụ HE, trung bình và Sobel bằng tay; ghi expected|src/tv2/verification.py",
            "Cài Gaussian tách được, median và bilateral bằng NumPy|src/tv3/filters.py",
            "Cài Roberts, Prewitt và Sobel; giữ gradient dạng float|src/tv4/edges.py",
            "Định nghĩa ROI, ENL và SSI; tính ví dụ mean/variance nhỏ|src/tv5/metrics.py",
        ],
    ),
    (
        "Lọc thích nghi SAR và làm nét",
        "Nêu đúng công thức từng biến thể và ca thất bại",
        [
            "Tạo cấu hình lọc và kết nối nhánh raw → filtered|src/tv1/pipeline.py",
            "Đối chiếu box/Gaussian/median; chuẩn hóa padding và rounding|src/tv2/library_comparison.py",
            "Cài Lee, Kuan và Frost; kiểm tác động window/L/damping|src/tv3/filters.py",
            "Cài unsharp, high-boost và Laplacian sharpening|src/tv4/sharpening.py",
            "Cài RMS, entropy, AMBE, EPI; nêu giới hạn và mẫu số bằng 0|src/tv5/metrics.py",
        ],
    ),
    (
        "Tăng tương phản và biên nhiều bước",
        "LUT/histogram và từng bước biên được giải thích bằng ví dụ",
        [
            "Nối filtered → enhanced; lưu các ảnh trung gian riêng|src/tv1/pipeline.py",
            "Đối chiếu HE/log/CLAHE; kiểm clip, grid và tile không vuông|src/tv2/library_comparison.py",
            "Cài HE, log và CLAHE: clipping, phân phối dư, nội suy LUT|src/tv3/enhancement.py",
            "Cài LoG và Canny: Gaussian, gradient, NMS, hysteresis|src/tv4/edges.py",
            "Thiết kế bảng CSV theo ảnh và thống kê mean/std/count|src/tv5/experiments.py",
        ],
    ),
    (
        "Phân đoạn vùng tối",
        "Mask vùng được tách rõ khỏi bản đồ biên",
        [
            "Tách nhánh displayed khỏi segmentation; quy định mask=None ở chế độ biên|src/tv1/pipeline.py",
            "Kiểm Otsu và hình thái bằng ví dụ tính tay; giải thích tie/endpoints|src/tv2/verification.py",
            "Cài lọc đồng hình: log1p, FFT, mặt nạ, nghịch đảo, chuẩn hóa|src/tv3/filters.py",
            "Cài Otsu, erosion/dilation, opening/closing và liên thông 8|src/tv4/morphology.py",
            "Thiết lập khảo sát bộ lọc trên cùng ảnh, tắt enhancement khi cần|src/tv5/experiments.py",
        ],
    ),
    (
        "Lọc vùng và phân tích ảnh 00013",
        "Giải thích được đốm CLAHE và không gọi mọi vùng tối là dầu",
        [
            "Tích hợp stats, mask, boundary và overlay; kiểm ý nghĩa từng khóa|src/tv1/pipeline.py",
            "Phân loại reference trực tiếp, ghép hàm và biến thể; đặt tolerance|src/tv2/library_comparison.py",
            "Phân tích Lee + CLAHE trên 00013 bằng ROI/lát cắt và ảnh trước–sau|Sổ tay TV3; results/reproducible/roi_00013.png",
            "Lọc min_area/C_R; dùng ảnh tham chiếu trước CLAHE; kiểm quy tắc chọn ảnh|src/tv4/morphology.py",
            "Chuẩn bị ca biển sạch/lookalike và tiêu chí báo nhầm cấp ảnh|src/tv5/experiments.py",
        ],
    ),
    (
        "Giao diện và kiểm chứng tích hợp",
        "Demo dùng chung pipeline với thực nghiệm",
        [
            "Xây Streamlit: chọn ảnh, upload, tham số, hiển thị và tải PNG/JSON|streamlit_app.py",
            "Chạy registry đối chiếu; phân tích PASS/DESCRIPTIVE/FAIL|results/verification/per_case.csv",
            "Kiểm đầu vào và trường hợp ảnh hằng cho các bộ lọc/tăng cường|src/tv3/; tests/test_core.py",
            "Kiểm Canny ngưỡng 0, vùng chạm mép và nhãn liên thông|src/tv4/; tests/test_core.py",
            "Khảo sát clip/grid CLAHE; giữ nguyên các yếu tố còn lại|results/reproducible/clahe_per_image.csv",
        ],
    ),
    (
        "Khảo sát tham số và ca lỗi",
        "Có số liệu theo ảnh, cấu hình và nhận xét cả ca tốt/lỗi",
        [
            "Viết kiểm thử tích hợp và AppTest; kiểm upload ưu tiên và đổi chế độ|tests/test_streamlit.py",
            "Rà sai số mép ảnh, dtype, footprint; sửa đối chứng không tương đương|src/tv2/library_comparison.py",
            "So lọc có kiểm soát; giải thích đánh đổi làm mượt/giữ vệt mảnh|results/reproducible/filters_per_image.csv",
            "Khảo sát min_area/min_contrast/closing; phân tích vùng mất hoặc bị gộp|results/reproducible/failure_cases_per_image.csv",
            "Khảo sát biên theo mức nhiễu; dùng seed và ảnh nhiễu chung giữa phương pháp|results/reproducible/edge_noise_per_image.csv",
        ],
    ),
    (
        "Đánh giá toàn tập và tái lập",
        "Không bỏ lớp âm; không suy diễn chỉ số ảnh thành độ đúng mask",
        [
            "Hoàn thiện entrypoint tái lập, xử lý lỗi và điều kiện full/samples|reproduce.py",
            "Rà kết quả 33 phép toán × 18 ca; kiểm 5 ví dụ số độc lập|results/verification/",
            "Giải thích các ca lọc/tăng cường làm giảm chất lượng hoặc tăng nhiễu|Sổ tay TV3; ghi chú ca thất bại",
            "Đối chiếu mask/biên và quy tắc lọc vùng trên ca dương/âm|Sổ tay TV4; ghi chú FP/FN",
            "Chạy hai lớp; lưu per-image, confusion, manifest và kiểm 5.538 hàng|results/reproducible/",
        ],
    ),
    (
        "Viết báo cáo theo bằng chứng",
        "Mọi bảng/hình truy về nguồn; không tự điền đóng góp cá nhân",
        [
            "Tổng hợp báo cáo 5 chương; kiểm số trang, mục tiêu và giới hạn|docs/report/",
            "Viết lý thuyết, ví dụ tay và phương pháp đối chiếu; rà trích dẫn|scripts/report_content.py",
            "Viết phần lọc/tăng cường, giả mã, độ phức tạp và phân tích tham số|scripts/report_content.py",
            "Viết phần biên/Otsu/hình thái và lý do không xác nhận mọi vùng là dầu|scripts/report_content.py",
            "Viết nguồn dữ liệu, thiếu hụt 92 ảnh, thiết kế thí nghiệm và kết quả|docs/report/evidence/",
        ],
    ),
    (
        "Hoàn thiện sản phẩm nộp",
        "PDF, demo và số liệu nhất quán; các hồ sơ chưa có được ghi rõ",
        [
            "Rà README, launcher và bộ nộp; tổng hợp slide 15–20 trang|docs/slides/; README.md",
            "Đối chiếu rubric và kiểm nội dung báo cáo; rà lỗi thuật ngữ/công thức|docs/management/KIEM_TRA_HIEN_TAI.md",
            "Soạn sổ tay TV3, ví dụ Lee/CLAHE và bài thực hành tham số|docs/thanh_vien/TV3_Ho_Viet_Tung/",
            "Soạn sổ tay TV4, ví dụ Sobel/Otsu/hình thái và câu hỏi sâu|docs/thanh_vien/TV4_Nguyen_Hai_Hieu/",
            "Đóng băng CSV/JSON, kiểm checksum; soạn sổ tay dữ liệu/chỉ số TV5|docs/report/evidence/; sổ tay TV5",
        ],
    ),
    (
        "Diễn tập và hỏi chéo",
        "Mỗi người tự thao tác demo và trả lời được phần của người khác",
        [
            "Soạn sổ tay TV1; điều phối 12 phút trình bày, 3 phút demo, 5 phút hỏi|Sổ tay TV1; docs/slides/KICH_BAN_BAO_VE.md",
            "Soạn sổ tay TV2; hỏi chéo cả nhóm và ghi câu trả lời còn thiếu|Sổ tay TV2; biên bản diễn tập thực tế",
            "Tập slide 7/8/16 trong 140 giây; giải thích CLAHE tạo đốm|Slide và phiếu tự kiểm TV3",
            "Tập slide 9–13 trong 160 giây; thao tác morphology ↔ Canny|Slide và phiếu tự kiểm TV4",
            "Tập slide 4/15/17 trong 170 giây; giải thích FP và precision/recall|Slide và phiếu tự kiểm TV5",
        ],
    ),
    (
        "Chốt hiện trạng đến 11/11",
        "Có danh sách còn thiếu và người nhận việc; chỉ xác nhận bằng chứng thật",
        [
            "Chốt phiên bản, kiểm bộ nộp; xác định người phụ trách video còn thiếu|Checklist bàn giao; video 5–7 phút khi thực hiện",
            "Kiểm lần cuối và tổng hợp lỗi; thu bảng đánh giá chéo có xác nhận thật|docs/management/; kết quả kiểm tra",
            "Sửa phần lọc/tăng cường còn vướng; tự kiểm toàn bộ câu hỏi TV3|Sổ tay TV3 và ghi chú sửa lỗi thực tế",
            "Sửa phần biên/phân đoạn còn vướng; tự kiểm toàn bộ câu hỏi TV4|Sổ tay TV4 và ghi chú sửa lỗi thực tế",
            "Xác nhận vị trí đầu ra, hash và phạm vi dữ liệu; bàn giao số liệu|results/README.md; manifest; evidence",
        ],
    ),
]


def sheet(wb, name, headers, widths):
    """Create a filtered, printable sheet with readable wrapped cells."""
    ws = wb.create_sheet(name)
    ws.append(headers)
    ws.freeze_panes = "A2"
    for i, width in enumerate(widths, 1):
        ws.column_dimensions[ws.cell(1, i).column_letter].width = width
    for cell in ws[1]:
        cell.fill = PatternFill("solid", fgColor="16324F")
        cell.font = Font(bold=True, color="FFFFFF", size=11)
        cell.alignment = Alignment(wrap_text=True, vertical="center")
    ws.row_dimensions[1].height = 32
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.orientation = "landscape"
    ws.page_setup.paperSize = ws.PAPERSIZE_A3
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.print_title_rows = "1:1"
    return ws


def main():
    """Generate 70 assigned tasks, member views, weekly gates and progress formulas."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace an existing plan, including manually entered updates",
    )
    args = parser.parse_args()
    if OUTPUT.exists() and not args.overwrite:
        raise SystemExit(
            "Plan already exists. Use --overwrite only after backing up manual updates."
        )
    team = json.loads((ROOT / "docs/management/thanh_vien.json").read_text(encoding="utf-8"))
    wb = Workbook()
    wb.remove(wb.active)
    intro = sheet(wb, "Huong_dan", ["Mục", "Nội dung"], [28, 115])
    for row in [
        ("Phạm vi", "10/08/2026–11/11/2026: 94 ngày, 14 khoảng tuần; không phải 8 tuần."),
        ("Ngày lập", END),
        (
            "Bản chất",
            "Kế hoạch phân bổ hồi cứu lập từ dự án hiện tại. Ngày dự kiến không xác nhận ngày thực hiện, người viết mã hoặc đóng góp quá khứ.",
        ),
        (
            "Cách cập nhật",
            "Chỉ cập nhật ô vàng N:R tại Ke_hoach. Các sheet TV1–TV5 và Tien_do lấy dữ liệu từ bảng này bằng công thức.",
        ),
        (
            "Trạng thái ban đầu",
            "Chưa xác nhận ở toàn bộ nhiệm vụ. File hiện có không tự chứng minh ai hoàn thành nhiệm vụ hoặc hoàn thành đúng mốc.",
        ),
        (
            "Hoàn thành",
            "Chỉ chọn Hoàn thành sau khi có sản phẩm đạt tiêu chí, ngày xong thực tế, liên kết minh chứng và người kiểm tra xác nhận trong ghi chú.",
        ),
        (
            "Minh chứng",
            "Ghi đường dẫn/URL commit thật, bản nháp, biên bản hoặc ảnh demo. Không dùng commit mô phỏng làm bằng chứng thời gian/đóng góp.",
        ),
        (
            "Ước lượng",
            "Giờ ở cột L là dự kiến để cân tải, không phải giờ đã làm. Giờ thực tế để trống đến khi thành viên cập nhật.",
        ),
        (
            "Phụ thuộc",
            "ID ở cột J là đầu vào cần có trước khi nghiệm thu. Người phụ trách chủ động học/chuẩn bị song song; không tự đánh dấu việc phụ thuộc đã xong.",
        ),
        (
            "Phân công",
            "Một người chịu trách nhiệm chính mỗi nhiệm vụ. Người kiểm tra hỗ trợ nghiệm thu, không thay người thực hiện. Cả nhóm phải hiểu toàn pipeline.",
        ),
        (
            "Nguồn",
            "thanh_vien.json; PHAN_CONG_MA_NGUON.md; README; module src/tv1…tv5 và bộ hồ sơ hiện tại.",
        ),
        (
            "Cách chạy demo",
            r"Chạy run_app.bat tại gốc repo; hoặc .venv\Scripts\python.exe -m streamlit run streamlit_app.py; mở http://localhost:8501",
        ),
        (
            "Lưu ý số liệu",
            "Không ML/DL. Precision/recall chỉ đánh giá quy tắc cổ điển cấp ảnh; chưa có mask chuẩn để đánh giá đúng vị trí dầu.",
        ),
    ]:
        intro.append(row)
    members = sheet(
        wb,
        "Thanh_vien",
        ["Mã", "Họ tên", "GitHub", "Trách nhiệm", "Module", "Slide", "Giây nói"],
        [9, 24, 22, 52, 40, 22, 14],
    )
    for m in team:
        members.append(
            [
                m["id"],
                m["name"],
                m["github"],
                m["role"],
                m["modules"],
                ", ".join(map(str, m["slides"])),
                sum(m["slide_seconds"]),
            ]
        )
    headers = [
        "ID",
        "Tuần",
        "Từ ngày dự kiến",
        "Đến ngày dự kiến",
        "Mã TV",
        "Người phụ trách",
        "Nhiệm vụ cụ thể",
        "Sản phẩm / nơi lưu dự kiến",
        "Tiêu chí nghiệm thu",
        "Phụ thuộc ID",
        "Người kiểm tra",
        "Giờ dự kiến",
        "Ưu tiên",
        "Trạng thái thực tế",
        "Ngày xong thực tế",
        "Giờ thực tế",
        "Minh chứng thực tế",
        "Ghi chú / xác nhận kiểm tra",
    ]
    master = sheet(
        wb,
        "Ke_hoach",
        headers,
        [13, 9, 16, 16, 9, 24, 58, 52, 65, 22, 24, 14, 12, 20, 17, 14, 45, 45],
    )
    master.freeze_panes = "G2"
    calendar = sheet(
        wb,
        "Lich_tuan",
        ["Tuần", "Từ ngày", "Đến ngày", "Giai đoạn", "Điều kiện chốt tuần"]
        + [m["id"] for m in team],
        [10, 15, 15, 35, 55] + [45] * 5,
    )
    reviewer = [1, 0, 1, 1, 0]
    for week, (phase, gate, tasks) in enumerate(STAGES, 1):
        begin = START + dt.timedelta(weeks=week - 1)
        end = min(begin + dt.timedelta(days=6), END)
        calendar.append([week, begin, end, phase, gate] + [t.split("|")[0] for t in tasks])
        for i, (m, task) in enumerate(zip(team, tasks)):
            title, artifact = task.split("|")
            deps = [] if week == 1 else [f"W{week - 1:02d}-{m['id']}"]
            if week > 2 and i != reviewer[i]:
                deps.append(f"W{week - 1:02d}-TV{reviewer[i] + 1}")
            criteria = (
                gate
                + ". Người kiểm tra xem sản phẩm, ghi sai khác/giới hạn và xác nhận minh chứng của nhiệm vụ."
            )
            hours = (6 if week <= 2 or week >= 12 else 8) + (2 if i == 0 else 0)
            if week == 14:
                hours = 4 + (2 if i == 0 else 0)
            master.append(
                [
                    f"W{week:02d}-{m['id']}",
                    week,
                    begin,
                    end,
                    m["id"],
                    m["name"],
                    title,
                    artifact,
                    criteria,
                    ", ".join(deps) or "Không",
                    team[reviewer[i]]["name"],
                    hours,
                    "Cao" if week in (1, 10, 14) else "Thường",
                    "Chưa xác nhận",
                    None,
                    None,
                    None,
                    None,
                ]
            )
    states = '"Chưa xác nhận,Chưa bắt đầu,Đang làm,Chờ kiểm tra,Cần sửa,Hoàn thành"'
    dv = DataValidation(type="list", formula1=states)
    dv.errorTitle = "Trạng thái không hợp lệ"
    dv.error = "Chọn một trạng thái trong danh sách."
    dv.showErrorMessage = True
    dv.errorStyle = "stop"
    master.add_data_validation(dv)
    dv.add("N2:N71")
    hours_validation = DataValidation(
        type="decimal", operator="greaterThanOrEqual", formula1=0, allow_blank=True
    )
    hours_validation.showErrorMessage = True
    hours_validation.errorStyle = "stop"
    master.add_data_validation(hours_validation)
    hours_validation.add("P2:P71")
    table = Table(displayName="NhiemVu", ref="A1:R71")
    table.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
    master.add_table(table)
    progress = sheet(
        wb,
        "Tien_do",
        [
            "Mã TV",
            "Họ tên",
            "Số việc",
            "Giờ dự kiến",
            "Hoàn thành xác nhận",
            "Tỷ lệ việc hoàn thành",
            "Giờ thực tế đã nhập",
            "Thiếu minh chứng/ngày/xác nhận",
        ],
        [10, 25, 14, 18, 23, 24, 24, 38],
    )
    for i, m in enumerate(team, 2):
        progress.append(
            [
                m["id"],
                m["name"],
                f"=COUNTIF(Ke_hoach!E2:E71,A{i})",
                f"=SUMIF(Ke_hoach!E2:E71,A{i},Ke_hoach!L2:L71)",
                f'=COUNTIFS(Ke_hoach!E2:E71,A{i},Ke_hoach!N2:N71,"Hoàn thành")',
                f"=IFERROR(E{i}/C{i},0)",
                f"=SUMIF(Ke_hoach!E2:E71,A{i},Ke_hoach!P2:P71)",
                f'=SUMPRODUCT((Ke_hoach!E2:E71=A{i})*(Ke_hoach!N2:N71="Hoàn thành")*(((Ke_hoach!O2:O71="")+(Ke_hoach!Q2:Q71="")+(Ke_hoach!R2:R71=""))>0))',
            ]
        )
        progress.cell(i, 6).number_format = "0%"
    progress.conditional_formatting.add(
        "H2:H6",
        CellIsRule(
            operator="greaterThan", formula=["0"], fill=PatternFill("solid", fgColor="FFC7CE")
        ),
    )
    columns = [1, 2, 3, 4, 7, 8, 9, 11, 12, 14, 17]
    for index, m in enumerate(team):
        view = sheet(
            wb,
            m["id"],
            [headers[c - 1] for c in columns],
            [13, 8, 15, 15, 54, 44, 55, 24, 12, 20, 40],
        )
        for week in range(14):
            source_row = 2 + week * 5 + index
            view.append(
                [
                    f'=IF(Ke_hoach!{master.cell(1, c).column_letter}{source_row}="","",Ke_hoach!{master.cell(1, c).column_letter}{source_row})'
                    for c in columns
                ]
            )
        view.sheet_properties.tabColor = ["167D9A", "548235", "BF9000", "7030A0", "C65911"][index]
    for ws in wb:
        for row in ws.iter_rows(min_row=2):
            for cell in row:
                cell.font = Font(name="Calibri", size=11, color="16324F")
                cell.alignment = Alignment(wrap_text=True, vertical="top")
                if cell.row % 2 == 0:
                    cell.fill = PatternFill("solid", fgColor="EDF4F8")
                if isinstance(cell.value, (dt.date, dt.datetime)):
                    cell.number_format = "dd/mm/yyyy"
            ws.row_dimensions[row[0].row].height = (
                85
                if ws.title in ("Ke_hoach", "Lich_tuan", "TV1", "TV2", "TV3", "TV4", "TV5")
                else 54
            )
        ws.auto_filter.ref = ws.dimensions
        ws.print_options.horizontalCentered = True
        ws.oddFooter.center.text = "Trang &P / &N"
        ws.oddFooter.left.text = "Kế hoạch hồi cứu — cập nhật trạng thái theo minh chứng"
    for row in master.iter_rows(min_row=2, min_col=14, max_col=18):
        for cell in row:
            cell.fill = PatternFill("solid", fgColor="FFF2CC")
        row[1].number_format = "dd/mm/yyyy"
    for m in team:
        for row in wb[m["id"]].iter_rows(min_row=2, min_col=3, max_col=4):
            for cell in row:
                cell.number_format = "dd/mm/yyyy"
    wb.save(OUTPUT)
    check = load_workbook(OUTPUT)
    assert check["Ke_hoach"].max_row == 71
    ids = {row[0] for row in check["Ke_hoach"].iter_rows(min_row=2, values_only=True)}
    assert len(ids) == 70
    for row in check["Ke_hoach"].iter_rows(min_row=2, values_only=True):
        assert row[2].date() >= START and row[3].date() <= END
        assert row[13] == "Chưa xác nhận" and all(v is None for v in row[14:18])
        assert row[5] != row[10]
        assert row[9] == "Không" or set(row[9].split(", ")) <= ids
    assert all(
        sum(row[4] == m["id"] for row in check["Ke_hoach"].iter_rows(min_row=2, values_only=True))
        == 14
        for m in team
    )
    print(OUTPUT)
    print("Validated: 10 sheets, 70 tasks, 14 weeks, 5 members; no fabricated completion.")


if __name__ == "__main__":
    main()
