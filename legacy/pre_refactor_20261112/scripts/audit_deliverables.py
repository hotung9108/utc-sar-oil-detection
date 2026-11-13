"""Check current files and append a dated audit without rewriting team evidence."""

import ast
import hashlib
import json
import platform
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import openpyxl
import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill
from pptx import Presentation
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.tv2.library_comparison import registry  # noqa: E402
from src.tv5.experiments import code_digest  # noqa: E402


def main():
    """Assert measured requirements, then write the current audit and one new Excel sheet."""
    assert platform.python_version_tuple()[:2] == ("3", "13")
    report = ROOT / "docs/report"
    data = ROOT / "results/reproducible"
    manifest = json.loads((data / "manifest.json").read_text())
    assert manifest["completed_scope"] == "full"
    assert manifest["source_sha256"] == code_digest()
    checksums = json.loads((report / "evidence/checksums.json").read_text())
    for name, expected in checksums.items():
        assert hashlib.sha256((report / "evidence" / name).read_bytes()).hexdigest() == expected, (
            name
        )
    measured = pd.read_csv(ROOT / "results/verification/per_case.csv")
    assert set(measured.algorithm) == {item[0] for item in registry()}
    assert len(measured) == 594 and len(measured.algorithm.unique()) == 33
    counts = measured.verdict.value_counts().to_dict()
    assert counts == {"PASS": 558, "DESCRIPTIVE": 36}, counts
    hand = json.loads((ROOT / "results/verification/hand_examples.json").read_text())
    assert len(hand) == 5 and all(r["passed"] for r in hand)

    rows = pd.read_csv(data / "dataset_per_image.csv")
    assert len(rows) == 5538 and rows.image.is_unique
    assert rows.groupby("label").size().to_dict() == {0: 3695, 1: 1843}
    conf = json.loads((data / "confusion.json").read_text())
    for label, pred, key in [(0, 0, "TN"), (0, 1, "FP"), (1, 0, "FN"), (1, 1, "TP")]:
        assert int(((rows.label == label) & (rows.prediction == pred)).sum()) == conf[key]
    inventory = json.loads((data / "data_inventory.json").read_text())
    assert inventory["local_counts"] == {"Class_0": 3695, "Class_1": 1843}
    assert len(inventory["sample_exact_matches"]) == 10
    assert all(inventory["sample_exact_matches"].values())
    assert not inventory["exact_duplicate_groups"]
    assert inventory["local_image_files_including_copies"] == 5548
    assert len(inventory["additional_kaggle_copies"]) == 10
    assert all(inventory["additional_kaggle_copies"].values())

    tests = ET.parse(ROOT / ".cache/final_tests.xml").getroot()
    suite = tests.find("testsuite")
    assert int(suite.attrib["tests"]) == 23
    assert all(int(suite.attrib[k]) == 0 for k in ["errors", "failures", "skipped"])
    for folder in ["tv1", "tv2", "tv3", "tv4", "tv5"]:
        assert len(list((ROOT / "src" / folder).glob("*.py"))) >= 2
    for path in (ROOT / "src").glob("tv*/*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        assert all(
            ast.get_docstring(n) for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
        ), path

    pdf = PdfReader(report / "BAO_CAO_BTL_XLA.pdf")
    audit = json.loads((report / "report_audit.json").read_text(encoding="utf-8"))
    assert len(pdf.pages) == audit["total_pages"] and 30 <= len(pdf.pages) <= 60
    assert 25 <= audit["main_pages"] <= 40
    assert audit["chapter_3_4_fraction"] > 0.5
    first = audit["chapter_start_pdf_pages"]
    assert 4 <= first["1"] - 1 <= 6
    ends = {str(n): first[str(n + 1)] for n in range(1, 5)}
    ends["5"] = audit["page_map"]["Tài liệu tham khảo"]
    chapter_pages = {str(n): ends[str(n)] - first[str(n)] for n in range(1, 6)}
    for key, low, high in [("1", 3, 4), ("2", 5, 8), ("3", 6, 10), ("4", 7, 12), ("5", 1, 2)]:
        assert low <= chapter_pages[key] <= high, (key, chapter_pages)
    fonts = set()
    for page in pdf.pages:
        assert abs(float(page.mediabox.width) - 595.276) < 0.1
        assert abs(float(page.mediabox.height) - 841.89) < 0.1
        for ref in page["/Resources"]["/Font"].values():
            font = ref.get_object()
            fonts.add(str(font.get("/BaseFont")))
            if "TimesNewRoman" in str(font.get("/BaseFont")):
                assert "/FontFile2" in font["/FontDescriptor"].get_object()
    assert any("TimesNewRoman" in f for f in fonts), fonts
    content = json.loads((report / "report_content.json").read_text(encoding="utf-8"))
    equations = sum(i["type"] == "equation" for p in content for i in p["items"])
    assert equations == 15
    docx = zipfile.ZipFile(report / "BAO_CAO_BTL_XLA.docx")
    xml = ET.fromstring(docx.read("word/document.xml"))
    assert (
        len(xml.findall(".//{http://schemas.openxmlformats.org/officeDocument/2006/math}oMath"))
        == 15
    )
    refs = next(p for p in content if p["title"] == "Tài liệu tham khảo")["items"]
    refs += next(p for p in content if p["title"] == "Tài liệu tham khảo (tiếp)")["items"]
    assert sum(i["text"].startswith("[") for i in refs) >= 10
    assert sum("doi:" in i["text"] and "IEEE" in i["text"] for i in refs) >= 3

    deck = Presentation(ROOT / "docs/slides/BAO_VE_BTL_XLA.pptx")
    assert len(deck.slides) == 18
    assert all(s.has_notes_slide and s.notes_slide.notes_text_frame.text for s in deck.slides)
    assert len(PdfReader(ROOT / "docs/slides/BAO_VE_BTL_XLA.pdf").pages) == 18
    render = json.loads((ROOT / "docs/slides/render_audit.json").read_text(encoding="utf-8-sig"))
    assert render["overflow_count"] == 0

    path = ROOT / "docs/management/PHAN_CONG_VA_MINH_CHUNG_BTL.xlsx"
    workbook = openpyxl.load_workbook(path)
    original_names = list(workbook.sheetnames)
    preserved = {s.title: list(s.values) for s in workbook if s.title != "Cap_nhat_20261111"}
    peer = list(workbook["Danh_gia_cheo"].values)[6:]
    assert len(peer) == 20 and len({tuple(r[:2]) for r in peer}) == 20
    assert all(r[0] != r[1] and all(x is None for x in r[2:8]) for r in peer)
    team = json.loads((ROOT / "docs/management/thanh_vien.json").read_text(encoding="utf-8"))
    handbooks = json.loads((ROOT / "docs/thanh_vien/pdf_audit.json").read_text(encoding="utf-8"))
    assert {h["member"] for h in handbooks} == {m["id"] for m in team}
    for handbook in handbooks:
        assert handbook["chapters"] == 10 and handbook["review_questions"] >= 20
        assert handbook["word_count"] >= 7000
        pdf_path = ROOT / handbook["pdf"]
        assert pdf_path.with_suffix(".md") == ROOT / handbook["markdown"]
        assert hashlib.sha256(pdf_path.read_bytes()).hexdigest() == handbook["pdf_sha256"]
        assert len(PdfReader(pdf_path).pages) == handbook["pages"]
        assert handbook["source_hash_mode"] == "utf8-lf"
        for name, expected in handbook["source_sha256"].items():
            actual = hashlib.sha256(
                (ROOT / name).read_text(encoding="utf-8").encode("utf-8")
            ).hexdigest()
            assert actual == expected, name
    assert {slide for m in team for slide in m["slides"]} == set(range(1, 19))
    assert sum(sum(m["slide_seconds"]) for m in team) == 720
    for index, member in enumerate(team, 7):
        assert workbook["Thanh_vien"].cell(index, 2).value == member["name"]
        assert workbook["Thanh_vien"].cell(index, 4).value == member["github"]
        folder = ROOT / "docs/thanh_vien" / member["folder"]
        assert len(list(folder.glob("*.md"))) == 1
        assert len(list(folder.glob("*.pdf"))) == 1
    assert workbook["Hoi_cuu_1008_1111"].max_row == 73

    evidence = [
        (
            "Python 3.13 và môi trường",
            "Đạt",
            "Python " + platform.python_version() + "; uv.lock; pyproject.toml",
        ),
        (
            "TV1 trưởng nhóm, TV2–TV5",
            "Đạt",
            "src/tv1…tv5; PHAN_CONG_MA_NGUON.md; trách nhiệm hiện tại",
        ),
        (
            "Lõi NumPy, không ML/DL",
            "Đạt",
            "TV3/TV4/metrics dùng NumPy/Python; test AST; FFT là primitive số",
        ),
        (
            "Đối chiếu các thuật toán/chỉ số",
            "Đạt trong phạm vi đã nêu",
            "33 mục ×18 ca: 558 PASS, 36 DESCRIPTIVE, 0 FAIL; phân biệt API/ghép hàm/biến thể",
        ),
        ("Ví dụ số và hồi quy", "Đạt", "5 ví dụ gọi hàm thật; 23 tests pass gồm Streamlit"),
        (
            "PEP 8 và docstring",
            "Đạt phạm vi kiểm tra",
            "Ruff check/format cho code hiện tại; mọi hàm trong src/tv* có docstring; không chứng nhận mọi cách dùng đầu vào",
        ),
        (
            "Demo Streamlit",
            "Đạt",
            "streamlit_app.py; chọn ảnh, tham số, PNG/JSON; AppTest đổi Canny/morphology/00013",
        ),
        (
            "Báo cáo PDF và nguồn",
            "Đạt phần kỹ thuật",
            f"{len(pdf.pages)} trang; {audit['main_pages']} trang chính; C3+C4={audit['chapter_3_4_pages']} ({audit['chapter_3_4_fraction']:.2%}); DOCX và LaTeX",
        ),
        (
            "Cấu trúc 5 chương",
            "Đạt",
            f"Mở đầu {first['1'] - 1} trang; các chương {chapter_pages}; tham khảo 2 trang; phụ lục A/B/C",
        ),
        (
            "Định dạng và công thức",
            "Đạt",
            "A4; TNR nhúng, thân 13pt, giãn 1.3; lề 3/2/2.5/2.5; 15 công thức vector từ LaTeX và native OMML",
        ),
        (
            "Lý thuyết, giả mã, độ phức tạp",
            "Đã bổ sung",
            "Chương 2–3: công thức, dẫn xuất Lee, ví dụ HE/Lee, giả mã có số dòng và chi phí thời gian/bộ nhớ",
        ),
        (
            "Thực nghiệm và tái lập",
            "Đạt",
            "reproduce.py; so sánh lọc, CLAHE, nhiễu, ca lỗi, hai lớp; mean/std/count và seed 2026",
        ),
        (
            "Nguồn và nhãn dữ liệu",
            "Đã xác định từ hồ sơ cục bộ",
            "CSIRO DOI 10.25919/4v55-dn16; license CC BY-SA 4.0; 0 không dầu, 1 có dầu",
        ),
        (
            "Phạm vi dataset",
            "Có giới hạn đã công bố",
            "5.538 ảnh so với 5.630 công bố; thiếu 92; 10 mẫu là tập con; chưa có checksum gốc/mask/cảnh",
        ),
        (
            "Đánh giá không làm đẹp số liệu",
            "Đạt",
            "TN810 FP2885 FN204 TP1639; precision36.23%, recall88.93%; chỉ cấp ảnh",
        ),
        (
            "Tài liệu tham khảo",
            "Đạt số lượng; cần nhóm đọc nguồn",
            "13 mục IEEE, ít nhất 3 bài DOI; nguồn kế thừa hồ sơ dự án, không tuyên bố đã đọc toàn văn bên ngoài",
        ),
        (
            "Slide 15–20 trang",
            "Đạt",
            "18 slide PPTX/PDF, speaker notes; PowerPoint xuất PDF, 0 hộp chữ tràn; Canva MCP bị admin tắt",
        ),
        (
            "Kịch bản bảo vệ",
            "Đã chuẩn bị",
            "12 phút nói +3 phút demo +5 phút vấn đáp; nhóm cần diễn tập",
        ),
        (
            "Sổ tay học theo thành viên",
            "Đã xuất và kiểm nội dung",
            "5 Markdown + 5 PDF; mỗi sổ tay 10 chương, 20–25 câu hỏi có gợi ý, ví dụ tính tay và thực hành; hash trong pdf_audit.json",
        ),
        (
            "Bảng đánh giá chéo",
            "Đạt yêu cầu tạo mẫu",
            "20 cặp TV1–TV5; điểm/nhận xét/chữ ký chưa điền",
        ),
        (
            "Danh tính và đóng góp thật",
            "Tên/GitHub đã cập nhật; hồ sơ còn thiếu",
            "Tên do nhóm cung cấp, GitHub từ collaborators; MSSV/tỷ lệ/chữ ký chờ nhóm điền",
        ),
        ("Video 5–7 phút", "Hoãn theo yêu cầu", "Không tạo video trong đợt này"),
        (
            "Lịch sử Git 8 tuần",
            "Chưa đủ minh chứng",
            "Giữ nguyên lịch sử; không backdate/gán tác giả giả; cần giải trình theo quy định lớp",
        ),
        (
            "Nhật ký nhóm và kiểm tra trùng lặp",
            "Nhóm cần hoàn tất",
            "Khung 8 tuần là hồi cứu có ô minh chứng; chưa có kiểm tra trùng lặp của trường",
        ),
        (
            "Khai báo AI",
            "Đã bổ sung",
            "Phụ lục C nêu Codex, các phần hỗ trợ và kiểm tra; sinh viên cần tự đọc và chịu trách nhiệm",
        ),
    ]
    target = (
        workbook["Cap_nhat_20261111"]
        if "Cap_nhat_20261111" in original_names
        else workbook.create_sheet("Cap_nhat_20261111")
    )
    target.append(["ĐỐI CHIẾU SAU CẬP NHẬT 11/11/2026 — các sheet gốc giữ nguyên"])
    target.append(["Hạng mục", "Kết luận", "Minh chứng / giới hạn"])
    for row in evidence:
        target.append(row)
    target.freeze_panes = "A3"
    target.auto_filter.ref = f"A2:C{target.max_row}"
    for col, width in [("A", 35), ("B", 32), ("C", 105)]:
        target.column_dimensions[col].width = width
    for row in target:
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
    for cell in target[2]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="16324F")
    for index in range(3, target.max_row + 1):
        target.row_dimensions[index].height = 45
    if "Cap_nhat_20261111" not in original_names:
        workbook.save(path)
        reopened = openpyxl.load_workbook(path)
        assert all(list(reopened[name].values) == values for name, values in preserved.items())

    lines = [
        "# Đối chiếu hiện tại với hướng dẫn BTL",
        "",
        "Ngày kiểm tra: 11/11/2026. Bản này thay cho kết luận hiện trạng ở snapshot cũ; không sửa minh chứng lịch sử.",
        "",
        "**Phần mã và hồ sơ kỹ thuật đã được cập nhật. Chưa thể xác nhận toàn bộ bộ nộp của nhóm hoàn tất:** video đang hoãn, MSSV/chữ ký/đánh giá thật, diễn tập, kiểm tra trùng lặp và lịch sử 8 tuần còn cần nhóm xử lý. Họ tên và GitHub đã cập nhật theo nhóm và collaborators.",
        "",
        f"Hash mã và môi trường đã đo: `{manifest['source_sha256']}`. Báo cáo nguồn `docs/report/`; slide `docs/slides/`; số liệu đóng băng kèm checksum trong `docs/report/evidence/`.",
        "",
        "| Hạng mục | Kết luận | Minh chứng / giới hạn |",
        "| --- | --- | --- |",
    ]
    lines += ["| " + " | ".join(row) + " |" for row in evidence]
    lines += [
        "",
        "Excel đã cập nhật họ tên/GitHub/module hiện tại ở Thanh_vien; bảng đánh giá chéo có 20 cặp, mọi ô điểm/nhận xét/chữ ký vẫn trống. Sheet Hoi_cuu_1008_1111 có 70 dòng trống để bổ sung minh chứng thật. Các sheet lịch sử và Cap_nhat_20261111 giữ như snapshot trước lần bổ sung thành viên; không tự biến thành minh chứng công việc quá khứ.",
        "",
        "Mỗi thành viên có một sổ tay Markdown đầy đủ và một PDF cùng nội dung trong docs/thanh_vien/, thay cho ba đề cương ngắn. Mỗi bản có 10 chương, giải thích từ nền tảng, ví dụ tính tay, 20–25 câu hỏi có gợi ý và bài thực hành. Chương 8 chỉ rõ nơi lưu kết quả. Slide được chia đúng 720 giây cho năm người. Demo cho phép chọn mọi ảnh trong cả Class_0 và Class_1.",
        "",
        "Số liệu nguồn trong manifest cũ ghi nguồn/nhãn cần xác nhận tại lúc đo; lần kiểm kê sau đó tìm được metadata CSIRO trong cùng repo. Hồ sơ dữ liệu mới bổ sung nguồn và giới hạn 92 ảnh, không thay đổi kết quả đo thuật toán.",
        "",
        "Kiểm tra tự động không thay thế việc nhóm đọc và hiểu mọi dòng mã. Không có phép đo IoU/Dice, kết luận dầu đã xác nhận, hoặc chứng nhận đạt rubric từ giảng viên.",
    ]
    (ROOT / "docs/management/KIEM_TRA_HIEN_TAI.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    result = dict(
        python=platform.python_version(),
        tests=23,
        comparison_counts=counts,
        algorithms=33,
        dataset_count=len(rows),
        report_pages=len(pdf.pages),
        main_pages=audit["main_pages"],
        chapter_pages=chapter_pages,
        slide_count=18,
        equations=equations,
        peer_pairs=20,
        member_handbooks=[
            {key: h[key] for key in ["member", "pages", "chapters", "review_questions"]}
            for h in handbooks
        ],
        source_sha256=manifest["source_sha256"],
        pdf_fonts=sorted(fonts),
    )
    (ROOT / "docs/management/technical_audit.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
