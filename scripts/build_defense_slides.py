"""TV1/TV5: generate the 18-slide editable defense deck from measured results.

Run after reproduce.py. Needs the docs extra (python-pptx). No invented metrics.
"""

import json
from pathlib import Path

import pandas as pd
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/slides"
DATA = ROOT / "results/reproducible"
TEAM = json.loads((ROOT / "docs/management/thanh_vien.json").read_text(encoding="utf-8"))
SPEAKERS = {
    number: (m, seconds) for m in TEAM for number, seconds in zip(m["slides"], m["slide_seconds"])
}
NAVY = "16324F"
TEAL = "167D9A"
GOLD = "B86B31"
GRAY = "516173"
WHITE = "FFFFFF"


def text(slide, x, y, w, h, value, size=23, color=NAVY, bold=False):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.word_wrap = True
    for index, line in enumerate(value.split("\n")):
        p = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        p.text = line
        p.font.name = "Aptos"
        p.font.size = Pt(size)
        p.font.bold = bold
        p.font.color.rgb = RGBColor.from_string(color)
        p.space_after = Pt(12)
    return box


def panel(slide, x, y, w, h, title, body):
    rect = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h)
    )
    rect.fill.solid()
    rect.fill.fore_color.rgb = RGBColor.from_string("EDF4F8")
    rect.line.fill.background()
    text(slide, x + 0.2, y + 0.15, w - 0.4, 0.6, title, 21, TEAL, True)
    text(slide, x + 0.2, y + 0.95, w - 0.4, h - 1.05, body, 22)


def build():
    required = [
        "confusion.json",
        "manifest.json",
        "filters_summary.csv",
        "failure_cases_per_image.csv",
    ]
    for name in required:
        if not (DATA / name).exists():
            raise FileNotFoundError(f"Run reproduce.py first: missing {name}")
    confusion = json.loads((DATA / "confusion.json").read_text())
    manifest = json.loads((DATA / "manifest.json").read_text())
    if manifest.get("completed_scope") != "full":
        raise RuntimeError("Run the full reproduce.py before building the defense deck")
    verification = pd.read_csv(ROOT / "results/verification/per_case.csv")
    assert not (verification.verdict == "FAIL").any()
    failures = pd.read_csv(DATA / "failure_cases_per_image.csv")
    case = failures[
        (failures.image.str.contains("00013")) & (failures.enhancement == "clahe")
    ].iloc[0]
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    notes = []

    def slide(title, source, note):
        s = prs.slides.add_slide(prs.slide_layouts[6])
        rect = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.12))
        rect.fill.solid()
        rect.fill.fore_color.rgb = RGBColor.from_string(TEAL)
        rect.line.fill.background()
        text(s, 0.5, 0.35, 12.3, 0.9, title, 30, NAVY, True)
        text(s, 0.5, 6.9, 11.6, 0.4, source, 10, GRAY)
        text(s, 12.1, 6.9, 0.7, 0.4, f"{len(prs.slides):02d}", 12, TEAL, True)
        member, seconds = SPEAKERS[len(prs.slides)]
        s.notes_slide.notes_text_frame.text = (
            f"{member['id']} — {member['name']} ({member['github']}). {seconds} giây.\n"
            + note
            + "\nNguồn: "
            + source
        )
        notes.append((title, note, source))
        return s

    s = slide(
        "Xử lý ảnh SAR: từ khử nhiễu đến vùng tối ứng viên",
        "BTL Xử lý ảnh · UTC · Đề kết hợp đã đăng ký",
        "Giới thiệu bài toán tăng cường, lọc và biên. Nhấn mạnh đây là thực hành xử lý ảnh có thể giải thích, không huấn luyện mô hình nhận diện dầu.",
    )
    text(
        s,
        0.6,
        1.6,
        7.8,
        2.6,
        "NumPy tự cài\nDemo Streamlit\nKhông Machine Learning / Deep Learning",
        28,
    )
    text(
        s,
        0.6,
        4.4,
        7,
        1.3,
        "Nhóm 5 thành viên · Python 3.13\nTV1 — Tiến Sơn Trần, trưởng nhóm",
        21,
        GRAY,
    )
    s.shapes.add_picture(
        str(ROOT / "kaggle/data/Class_1/class_1_00013.jpg"),
        Inches(9),
        Inches(1.6),
        width=Inches(3.5),
        height=Inches(3.5),
    )

    s = slide(
        "Mục tiêu có giới hạn rõ ràng",
        "README.md; hướng dẫn BTL XLA",
        "Phân biệt tăng cường khả năng quan sát với kết luận vật lý. Diện tích đo bằng pixel, không đổi sang km² khi thiếu độ phân giải mặt đất.",
    )
    panel(
        s,
        0.6,
        1.6,
        5.9,
        4.7,
        "Đầu vào → đầu ra",
        "Ảnh xám SAR, demo 400×400\nẢnh lọc/tăng cường, bản đồ biên\nVùng tối, diện tích px, tương phản",
    )
    panel(
        s,
        6.8,
        1.6,
        5.9,
        4.7,
        "Tiêu chí thực hiện",
        "Tự cài và đối chiếu thư viện\nSo sánh, khảo sát, phân tích lỗi\nKhông đồng nhất vùng tối với dầu",
    )

    s = slide(
        "Mã nguồn được chia theo 5 vai trò",
        "docs/management/PHAN_CONG_MA_NGUON.md",
        "Nêu trách nhiệm được phân công, không gán tác giả của lịch sử commit. Mỗi người phải hiểu cả pipeline để trả lời vấn đáp chéo.",
    )
    roles = [
        ("TV1 — Trưởng nhóm", "Tích hợp, Streamlit, cấu hình"),
        ("TV2", "Lý thuyết và kiểm chứng"),
        ("TV3", "Lọc và tăng cường tương phản"),
        ("TV4", "Biên, làm nét, hình thái"),
        ("TV5", "Dữ liệu, chỉ số, thực nghiệm"),
    ]
    for i, (member, (_, body)) in enumerate(zip(TEAM, roles)):
        text(
            s, 0.7, 1.55 + i * 0.97, 5.5, 0.5, f"{member['id']} — {member['name']}", 22, TEAL, True
        )
        text(s, 0.7, 2.05 + i * 0.97, 5.5, 0.35, member["github"], 14, GRAY)
        text(s, 6.3, 1.65 + i * 0.97, 6.4, 0.65, body, 21)

    s = slide(
        "Dữ liệu và phạm vi đánh giá",
        "CSIRO · DOI 10.25919/4v55-dn16 · CC BY-SA 4.0 theo metadata cục bộ",
        "Nguồn CSIRO theo metadata cục bộ, DOI 10.25919/4v55-dn16; license.html ghi CC BY-SA 4.0. Bản repo ít hơn bộ công bố 92 ảnh. Nhãn 0 không dầu, 1 có dầu; không có mask pixel để báo IoU/Dice.",
    )
    panel(
        s,
        0.6,
        1.6,
        5.9,
        4.7,
        "Tập dữ liệu trong dự án",
        "Class_0: 3.695 ảnh\nClass_1: 1.843 ảnh\nDemo: 10 ảnh con của dataset",
    )
    panel(
        s,
        6.8,
        1.6,
        5.9,
        4.7,
        "Không có nhãn đường biên",
        "Nhãn lớp ≠ mask chuẩn\nKhông chia train/test để học\nTham số cố định, ghi nguồn mã",
    )

    s = slide(
        "Vì sao ảnh SAR khó phân đoạn?",
        "Cơ sở lý thuyết SAR; src/tv3/filters.py",
        "Mô hình nhiễu nhân là mô hình làm việc, không chứng minh JPEG đã hiệu chuẩn vật lý. Vùng lặng gió hoặc kết cấu nền cũng có thể tối.",
    )
    panel(
        s,
        0.6,
        1.6,
        5.9,
        4.7,
        "Mô hình làm việc",
        "I = R × η\nLee sử dụng thống kê cục bộ\nVùng tối có thể là nhiều hiện tượng",
    )
    panel(
        s,
        6.8,
        1.6,
        5.9,
        4.7,
        "Đánh đổi",
        "Lọc mạnh làm mất chi tiết\nCLAHE có thể làm rõ nhiễu\nNgưỡng toàn cục dễ nhận nhầm nền",
    )

    s = slide(
        "Pipeline tách hiển thị và phân đoạn",
        "src/tv1/pipeline.py",
        "Làm nét chỉ tác động ảnh quan sát. Phân đoạn dùng ảnh trước làm nét; ảnh đã lọc trước CLAHE được giữ làm reference.",
    )
    for x, label in [(0.6, "Ảnh gốc"), (3.8, "Lọc NumPy"), (7.0, "CLAHE"), (10.2, "Hiển thị")]:
        panel(s, x, 1.7, 2.6, 1.8, label, "")
    text(
        s,
        1.1,
        4.0,
        11.5,
        1.4,
        "Ảnh sau lọc ── reference ──► Otsu + hình thái\nĐo tương phản trên reference → mask ứng viên → biên",
        26,
    )

    s = slide(
        "Lee: làm mịn có trọng số thích nghi",
        "src/tv3/filters.py; Lee (1980)",
        "Giải thích mean, variance và L. Khi variance nhỏ hơn mean²/L, K bằng 0 và kết quả là trung bình cục bộ. Đây không phải loại nhiễu hoàn hảo.",
    )
    text(
        s,
        0.8,
        1.6,
        11.8,
        2.2,
        "K = clip(1 − μ² / (L × σ²), 0, 1)\nR̂ = μ + K × (I − μ)",
        32,
        TEAL,
        True,
    )
    text(
        s,
        0.8,
        4.1,
        11.7,
        1.8,
        "Mặc định: cửa sổ 5×5, L = 4\nĐối chiếu: SciPy tính moment cục bộ + công thức\nKhông có API Lee trực tiếp trong bộ thư viện đối chứng",
        23,
    )

    s = slide(
        "CLAHE: tăng tương phản có giới hạn",
        "src/tv3/enhancement.py; cv2.createCLAHE",
        "Mô tả bốn bước. Code dùng histogram nguyên, phân phối dư, đệm reflect101 và nội suy; kiểm tra cả kích thước không chia hết và lưới 1×1.",
    )
    panel(
        s,
        0.6,
        1.6,
        5.9,
        4.7,
        "Tự cài",
        "Histogram theo tile\nCắt ngưỡng + phân phối dư\nCDF và nội suy song tuyến",
    )
    panel(
        s,
        6.8,
        1.6,
        5.9,
        4.7,
        "Đối chiếu / hạn chế",
        "cv2.createCLAHE cùng tham số\nNgưỡng sai khác: ≤1 mức xám\nTăng chi tiết cũng tăng kết cấu nền",
    )

    s = slide(
        "Làm nét và các toán tử biên",
        "src/tv4/sharpening.py; src/tv4/edges.py",
        "Unsharp/high-boost tăng thành phần cao tần; gradient hoặc đổi dấu không tự phân loại dầu. Diễn giải LoG cần xét ngưỡng và xử lý gần zero số học.",
    )
    panel(
        s,
        0.6,
        1.6,
        5.9,
        4.7,
        "Làm nét",
        "Unsharp: f + k(f − blur)\nLaplacian: f − α∇²f\nSobel: thêm độ lớn gradient",
    )
    panel(
        s,
        6.8,
        1.6,
        5.9,
        4.7,
        "Bản đồ biên",
        "Roberts, Prewitt, Sobel\nLoG và zero crossing\nBiên không phải mask diện tích dầu",
    )

    s = slide(
        "Canny: giữ đúng thông tin gradient",
        "src/tv4/edges.py; đối chiếu cv2.Canny",
        "Nêu sửa lỗi cắt gradient về uint8 trước NMS. Góc trong hệ tọa độ ảnh phải chọn đúng cặp chéo. Khác biệt lượng tử hướng, tie và biên ảnh được báo descriptive.",
    )
    text(
        s,
        0.8,
        1.7,
        11.8,
        2.1,
        "Gauss → Gradient float → NMS\n→ Ngưỡng kép → Hysteresis 8 láng giềng",
        30,
        TEAL,
        True,
    )
    text(
        s,
        0.8,
        4.0,
        11.8,
        1.7,
        "Không clip gradient trước khi làm mảnh\nẢnh hằng không có biên, kể cả ngưỡng bằng 0\nSo sánh biến thể: không tự tuyên bố khớp tuyệt đối",
        23,
    )

    s = slide(
        "Otsu: tối ưu mức xám, không tối ưu nhãn dầu",
        "src/tv4/morphology.py; Otsu (1979)",
        "Hai lớp theo ngưỡng gồm I<=t và I>t. Sửa lỗi loại endpoint tối. Ảnh hằng không đủ bằng chứng tương phản; eta cao không chứng minh đúng đối tượng.",
    )
    panel(
        s,
        0.6,
        1.6,
        5.9,
        4.7,
        "Bài toán Otsu",
        "Cực đại phương sai giữa lớp\nNhóm tối: I ≤ t\nHai mức 50/200 → t = 50",
    )
    panel(
        s,
        6.8,
        1.6,
        5.9,
        4.7,
        "Giới hạn",
        "Histogram đẹp ≠ nhận diện đúng\nẢnh tham chiếu giảm tác động CLAHE\nNgưỡng thích ứng là heuristic",
    )

    s = slide(
        "Hình thái và gán nhãn tự cài",
        "src/tv4/morphology.py; OpenCV đối chứng",
        "Phân biệt opening loại cấu trúc nhỏ với closing nối/lấp. Closing cũng có thể gộp nhầm. Run-length union-find thay lời gọi SciPy trong lõi.",
    )
    panel(
        s,
        0.6,
        1.6,
        5.9,
        4.7,
        "Chuỗi xử lý",
        "Opening đĩa r=2\nClosing đĩa r=4 mặc định\nRun-length union-find, 8 liên thông",
    )
    panel(
        s,
        6.8,
        1.6,
        5.9,
        4.7,
        "Lọc và trích biên",
        "Lọc diện tích ≥300 px\nLọc tương phản vùng/nền\nβ(A) = A − erode(A), gồm cả lỗ",
    )

    s = slide(
        "C_R là tương phản, không phải độ tròn",
        "src/tv4/morphology.py; tests/test_core.py",
        "Sửa sự không khớp giữa báo cáo cũ và code. Không tự hạ CR xuống 0.07 khi vùng lớn. Nếu không có vòng nền, không đủ dữ liệu đo tương phản.",
    )
    text(s, 0.8, 1.7, 11.8, 1.2, "C_R = (μ_nền − μ_vùng) / μ_nền", 34, TEAL, True)
    text(
        s,
        0.8,
        3.4,
        11.8,
        2.2,
        "Đo trên ảnh tham chiếu trước CLAHE\nMọi diện tích đều phải đạt min_contrast đã chọn\nKiểm thử: vùng tối hơn 8% bị loại nếu ngưỡng là 40%",
        25,
    )

    s = slide(
        "Kiểm chứng: số đo thật, phạm vi rõ",
        "results/verification/per_case.csv; hand_examples.json",
        "Phân biệt 558 pass kiểm tra số học với 36 descriptive. Các compositions chỉ kiểm chứng phép tính dựa trên primitive thư viện; không phải 33 API thuật toán độc lập.",
    )
    panel(
        s,
        0.6,
        1.6,
        5.9,
        4.7,
        "33 thuật toán / chỉ số",
        "8 ảnh tổng hợp + 10 ảnh mẫu\n"
        + str(len(verification))
        + " phép đối chiếu\n5 ví dụ tính tay gọi hàm thật",
    )
    counts = verification.verdict.value_counts()
    panel(
        s,
        6.8,
        1.6,
        5.9,
        4.7,
        "Không gộp kết quả khác loại",
        f"{counts.get('PASS', 0)} PASS theo giới hạn số học\n{counts.get('DESCRIPTIVE', 0)} DESCRIPTIVE: biến thể\nKhông phải độ chính xác dầu",
    )

    s = slide(
        "Thực nghiệm có thể tái tạo",
        "python reproduce.py; results/reproducible/",
        "Một lệnh chạy kiểm chứng, bộ mẫu và cả hai lớp. Mean/std tính trên từng ảnh; thời gian là toàn pipeline. ENL dùng ROI cố định nên không bảo đảm ROI đồng nhất.",
    )
    panel(
        s,
        0.6,
        1.6,
        5.9,
        4.7,
        "Thiết kế",
        "So sánh 7 bộ lọc + ảnh gốc\nCLAHE: grid 4/8/16, clip 1–5\nGauss σ=10/20/30 và ảnh sạch",
    )
    panel(
        s,
        6.8,
        1.6,
        5.9,
        4.7,
        "Bằng chứng tái lập",
        "Lưu kết quả từng ảnh\nTổng hợp trung bình ± std\nSeed 2026 + hash nguồn + môi trường",
    )

    s = slide(
        "Ca 00013: tăng tương phản không tạo bằng chứng dầu",
        "results/reproducible/class_1_00013_clahe.png",
        f"Hiện tại giữ {int(case.candidates)} vùng, {case.area_pct:.2f}% diện tích. Quan sát vệt chính phù hợp hơn bản cũ nhưng không khẳng định IoU khi thiếu mask chuẩn.",
    )
    s.shapes.add_picture(
        str(DATA / "class_1_00013_clahe.png"), Inches(0.4), Inches(1.5), width=Inches(12.5)
    )
    text(
        s,
        0.7,
        5.8,
        12,
        0.8,
        f"{int(case.candidates)} vùng ứng viên · {case.area_pct:.2f}% ảnh · Nền tối nhỏ vẫn có thể bị nhận nhầm",
        23,
        GOLD,
        True,
    )

    s = slide(
        "Đánh giá toàn tập và demo Streamlit",
        "results/reproducible/confusion.json; streamlit_app.py",
        "Nhấn mạnh chỉ số cấp ảnh và giả định nhãn thư mục. Demo trực tiếp riêng 3 phút: ảnh mẫu, 00013, đổi clip/CR, xem lỗi và tải kết quả. Video chưa làm theo yêu cầu.",
    )
    panel(
        s,
        0.6,
        1.6,
        5.9,
        4.7,
        f"{confusion['n']:,} ảnh — cấp ảnh",
        f"TP {confusion['TP']} · FP {confusion['FP']}\nFN {confusion['FN']} · TN {confusion['TN']}\nPrecision {confusion['precision']:.3f} · Recall {confusion['recall']:.3f}\nKhông phải đánh giá mask pixel",
    )
    panel(
        s,
        6.8,
        1.6,
        5.9,
        4.7,
        "Demo 3 phút riêng",
        "Chọn/tải ảnh và đổi tham số\nSo sánh ảnh, histogram/lát cắt\nTải PNG, cấu hình và chỉ số",
    )

    s = slide(
        "Kết luận và nguồn tham khảo",
        "Hướng dẫn BTL UTC; Lee 1980; Otsu 1979; Canny 1986; OpenCV/SciPy docs",
        "Kết luận theo bằng chứng: triển khai và đối chiếu, còn giới hạn báo nhầm. Hướng tiếp theo vẫn xử lý ảnh: ROI nền thích nghi, ngưỡng cục bộ, đánh giá mask gán tay. Không hứa dùng ML/DL.",
    )
    panel(
        s,
        0.6,
        1.6,
        5.9,
        4.7,
        "Đã thực hiện",
        "Lõi NumPy và demo Streamlit\nKiểm chứng + tái lập số liệu\nGiải thích được các ca thất bại",
    )
    panel(
        s,
        6.8,
        1.6,
        5.9,
        4.7,
        "Giới hạn / hướng tiếp theo",
        "Báo nhầm vùng tối không phải dầu\nROI nền và ngưỡng cục bộ\nGán mask để đánh giá đường biên",
    )

    OUT.mkdir(parents=True, exist_ok=True)
    destination = OUT / "BAO_VE_BTL_XLA.pptx"
    prs.save(destination)
    assert len(Presentation(destination).slides) == 18
    lines = [
        "# Kịch bản bảo vệ BTL XLA",
        "",
        "18 slide = 12 phút theo phân bổ từng người bên dưới. Demo trực tiếp 3 phút riêng; vấn đáp 5 phút. Điều chỉnh nhịp khi diễn tập.",
        "",
        "Canva MCP đã được kiểm tra nhưng bị quản trị viên vô hiệu hóa. Slide được tạo cục bộ bằng python-pptx, text/shape sửa được.",
        "",
        f"Nguồn số liệu: source SHA256 `{manifest['source_sha256']}`. Tên đã cập nhật; MSSV chờ bổ sung; chưa tạo video. Tài liệu cá nhân: [docs/thanh_vien](../thanh_vien/README.md).",
        "",
    ]
    for i, (title, note, source) in enumerate(notes, 1):
        member, seconds = SPEAKERS[i]
        lines.extend(
            [
                f"## {i}. {title}",
                "",
                f"{member['id']} — {member['name']} · {seconds} giây.",
                "",
                note,
                "",
                f"Nguồn: `{source}`",
                "",
            ]
        )
    (OUT / "KICH_BAN_BAO_VE.md").write_text("\n".join(lines), encoding="utf-8")
    print(destination)


if __name__ == "__main__":
    build()
