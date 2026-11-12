"""Export each member's complete Markdown handbook as a navigable Unicode PDF."""

import hashlib
import json
import re
from html import escape
from pathlib import Path
from urllib.parse import quote

import matplotlib
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    CondPageBreak,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/thanh_vien"
NAVY = colors.HexColor("#16324F")
TEAL = colors.HexColor("#167D9A")
MUTED = colors.HexColor("#526173")
LIGHT = colors.HexColor("#EDF4F8")
WIDTH = A4[0] - 3.8 * cm
GITHUB = "https://github.com/hotung9108/utc-sar-oil-detection/blob/main/"


def make_styles():
    """Embed library-supplied Unicode fonts, including Vietnamese and math symbols."""
    fonts = Path(matplotlib.get_data_path()) / "fonts/ttf"
    for name, filename in [
        ("Guide", "DejaVuSans.ttf"),
        ("GuideBold", "DejaVuSans-Bold.ttf"),
        ("GuideItalic", "DejaVuSans-Oblique.ttf"),
        ("GuideMono", "DejaVuSansMono.ttf"),
    ]:
        pdfmetrics.registerFont(TTFont(name, str(fonts / filename)))
    pdfmetrics.registerFontFamily(
        "Guide", normal="Guide", bold="GuideBold", italic="GuideItalic", boldItalic="GuideBold"
    )
    body = ParagraphStyle(
        "Body",
        fontName="Guide",
        fontSize=11.2,
        leading=16,
        spaceAfter=8,
        textColor=NAVY,
        alignment=TA_LEFT,
        splitLongWords=True,
    )
    return {
        "body": body,
        "title": ParagraphStyle(
            "Title", parent=body, fontName="GuideBold", fontSize=25, leading=33, spaceAfter=16
        ),
        "section": ParagraphStyle(
            "Section",
            parent=body,
            fontName="GuideBold",
            fontSize=17,
            leading=24,
            spaceAfter=14,
            textColor=TEAL,
            keepWithNext=True,
        ),
        "heading": ParagraphStyle(
            "Heading",
            parent=body,
            fontName="GuideBold",
            fontSize=13,
            leading=18,
            spaceBefore=10,
            spaceAfter=6,
            keepWithNext=True,
        ),
        "table": ParagraphStyle("Table", parent=body, fontSize=10.1, leading=14.8, spaceAfter=0),
        "small": ParagraphStyle("Small", parent=body, fontSize=9, leading=13.5, textColor=MUTED),
        "code": ParagraphStyle(
            "Code",
            parent=body,
            fontName="GuideMono",
            fontSize=9.1,
            leading=14,
            backColor=LIGHT,
            borderPadding=9,
            spaceBefore=6,
            spaceAfter=14,
        ),
        "list": ParagraphStyle("List", parent=body, leftIndent=17, firstLineIndent=-17),
    }


def inline(value, source):
    """Convert supported Markdown spans to escaped PDF markup with portable links."""
    pattern = r"(`[^`]+`|\*\*[^*]+\*\*|\[[^\]]+\]\([^)]+\))"
    pieces = []
    for part in re.split(pattern, value):
        if part.startswith("`") and part.endswith("`"):
            pieces.append('<font name="GuideMono" size="9.5">' + escape(part[1:-1]) + "</font>")
        elif part.startswith("**") and part.endswith("**"):
            pieces.append("<b>" + escape(part[2:-2]) + "</b>")
        elif re.fullmatch(r"\[[^\]]+\]\([^)]+\)", part):
            label, target = re.fullmatch(r"\[([^\]]+)\]\(([^)]+)\)", part).groups()
            if not target.startswith(("https://", "http://")):
                path = (source.parent / target).resolve()
                target = GITHUB + quote(path.relative_to(ROOT).as_posix(), safe="/")
            pieces.append(
                '<a href="'
                + escape(target, quote=True)
                + '" color="#167D9A">'
                + escape(label)
                + "</a>"
            )
        else:
            pieces.append(escape(part))
    return "".join(pieces)


def code_line(line):
    """Preserve indentation and use the body font for missing Vietnamese mono glyphs."""
    glyphs = pdfmetrics.getFont("GuideMono").face.charToGlyph
    return "".join(
        "&#160;"
        if char == " "
        else escape(char)
        if ord(char) in glyphs
        else '<font name="Guide">' + escape(char) + "</font>"
        for char in line
    )


def markdown_blocks(content, source, styles):
    """Render the repository's headings, paragraphs, lists, tables and code fences."""
    lines = content.splitlines()
    blocks = []
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if line.startswith("```"):
            code = []
            index += 1
            while index < len(lines) and not lines[index].strip().startswith("```"):
                code.append(code_line(lines[index]))
                index += 1
            block = Paragraph("<br/>".join(code), styles["code"])
            blocks.append(KeepTogether([block]) if len(code) <= 40 else block)
            index += 1
            continue
        if line.startswith("|"):
            rows = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                cells = [c.strip() for c in lines[index].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", cell) for cell in cells):
                    rows.append(cells)
                index += 1
            count = len(rows[0])
            assert all(len(row) == count for row in rows), source
            weights = {2: [0.42, 0.58], 3: [0.16, 0.39, 0.45]}.get(count, [1 / count] * count)
            if count == 3 and rows[0][0] == "Slide":
                weights = [0.12, 0.12, 0.76]
            cells = [
                [
                    Paragraph(
                        ("<b>" if row_index == 0 else "")
                        + inline(cell, source)
                        + ("</b>" if row_index == 0 else ""),
                        styles["table"],
                    )
                    for cell in row
                ]
                for row_index, row in enumerate(rows)
            ]
            table = Table(
                cells, colWidths=[WIDTH * w for w in weights], repeatRows=1, hAlign="LEFT"
            )
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), LIGHT),
                        (
                            "ROWBACKGROUNDS",
                            (0, 1),
                            (-1, -1),
                            [colors.white, colors.HexColor("#F8FAFC")],
                        ),
                        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C6D2DC")),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 8),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                        ("TOPPADDING", (0, 0), (-1, -1), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ]
                )
            )
            blocks.extend([table, Spacer(1, 12)])
            continue
        if line.startswith("#"):
            text = re.sub(r"^#+\s*", "", line)
            heading = Paragraph(inline(text, source), styles["heading"])
            next_line = next((x.strip() for x in lines[index + 1 :] if x.strip()), "")
            if next_line.startswith("|"):
                # Keep room for a heading and the first rows, but let a long table
                # split across pages instead of moving the entire table forward.
                blocks.append(CondPageBreak(120))
                heading.keepWithNext = False
            blocks.append(heading)
            index += 1
            continue
        if re.match(r"^(\d+\.|-)\s", line):
            blocks.append(Paragraph(inline(line, source), styles["list"]))
            index += 1
            continue
        paragraph = [line]
        index += 1
        while (
            index < len(lines)
            and lines[index].strip()
            and not re.match(r"^(#|\||```|\d+\.\s|-\s)", lines[index].strip())
        ):
            paragraph.append(lines[index].strip())
            index += 1
        blocks.append(Paragraph(inline(" ".join(paragraph), source), styles["body"]))
    return blocks


class MemberDoc(BaseDocTemplate):
    """Create navigable PDF sections and repeat the member name in the page header."""

    def afterFlowable(self, flowable):
        """Register section bookmarks after their page positions are known."""
        if hasattr(flowable, "bookmark"):
            self.canv.bookmarkPage(flowable.bookmark)
            self.canv.addOutlineEntry(flowable.getPlainText(), flowable.bookmark, level=0)


def build_member(member, styles):
    """Render the canonical handbook, preserving all ten chapters and examples."""
    folder = OUT / member["folder"]
    output = folder / (member["folder"] + "_TAI_LIEU_HOC_VA_BAO_VE.pdf")
    source = output.with_suffix(".md")
    sources = [source, ROOT / "docs/management/thanh_vien.json", Path(__file__).resolve()]
    markdown = source.read_text(encoding="utf-8")
    sections = re.split(r"^## (.+)\n", markdown, flags=re.M)
    introduction = sections[0].split("\n", 1)[1].strip()
    headings = sections[1::2]
    contents = sections[2::2]
    assert len(headings) == len(contents) == 10, source
    assert [int(h.split(".", 1)[0]) for h in headings] == list(range(1, 11)), source
    question_count = len(re.findall(r"^\*\*Câu \d+ —", markdown, flags=re.M))
    assert question_count >= 20, source
    doc = MemberDoc(
        str(output),
        pagesize=A4,
        leftMargin=1.9 * cm,
        rightMargin=1.9 * cm,
        topMargin=2.1 * cm,
        bottomMargin=1.8 * cm,
        title=f"{member['id']} — {member['name']} — Tài liệu học và bảo vệ",
        author="Nhóm BTL Xử lý ảnh UTC",
        subject=member["role"],
    )

    def page(canvas, document):
        canvas.saveState()
        canvas.setFillColor(TEAL)
        canvas.rect(0, A4[1] - 0.22 * cm, A4[0], 0.22 * cm, fill=1, stroke=0)
        canvas.setFont("Guide", 8.3)
        canvas.setFillColor(MUTED)
        canvas.drawString(1.9 * cm, A4[1] - 1.2 * cm, f"{member['id']} · {member['name']}")
        canvas.drawRightString(A4[0] - 1.9 * cm, A4[1] - 1.2 * cm, "BTL Xử lý ảnh · UTC")
        canvas.drawString(1.9 * cm, 1.0 * cm, "Tài liệu học và bảo vệ · NumPy · Không ML/DL")
        canvas.drawRightString(A4[0] - 1.9 * cm, 1.0 * cm, f"Trang {document.page}")
        canvas.restoreState()

    frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        doc.width,
        doc.height,
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
    )
    doc.addPageTemplates(PageTemplate(id="Member", frames=[frame], onPage=page))
    blocks = [
        Paragraph("TÀI LIỆU HỌC<br/>VÀ BẢO VỆ BTL", styles["title"]),
        Paragraph(escape(member["id"] + " — " + member["name"]), styles["section"]),
        *markdown_blocks(introduction, source, styles),
        Paragraph(
            "Slide: "
            + ", ".join(map(str, member["slides"]))
            + f" · Tổng thời gian nói: {sum(member['slide_seconds'])} giây.",
            styles["body"],
        ),
        Spacer(1, 18),
        Paragraph(
            "Mỗi phần giải thích khái niệm, mục đích, lý do sử dụng, cách tính và giới hạn. "
            "Câu hỏi có gợi ý để tự kiểm; hãy trả lời trước khi đọc đáp án. "
            "Nội dung là tài liệu chuẩn bị, không xác nhận mức đóng góp cá nhân trong quá khứ.",
            styles["body"],
        ),
        PageBreak(),
        Paragraph("Mục lục", styles["section"]),
        Paragraph(
            "Bấm vào tên chương hoặc dùng dấu trang PDF để chuyển phần. "
            "Chương 8 giải thích nơi lưu CSV, JSON, PNG và cách xuất một bộ ảnh kết quả.",
            styles["body"],
        ),
    ]
    blocks += [
        Paragraph(f'<a href="#section_{i}" color="#167D9A">{escape(heading)}</a>', styles["body"])
        for i, heading in enumerate(headings)
    ]
    for index, content in enumerate(contents):
        heading = Paragraph(inline(headings[index], source), styles["section"])
        heading.bookmark = f"section_{index}"
        # Start a fresh page after substantial content, but use a sparse
        # continuation page instead of leaving it with just one short paragraph.
        blocks += [
            PageBreak() if index == 0 else CondPageBreak(doc.height * 0.65),
            Spacer(1, 10) if index else Spacer(1, 0),
            heading,
        ]
        blocks.extend(markdown_blocks(content, source, styles))
    doc.build(blocks)
    reader = PdfReader(output)
    texts = [p.extract_text() for p in reader.pages]
    assert all(len(t.strip()) > 100 for t in texts), output
    assert member["name"] in texts[0] and len(reader.outline) == 10
    assert all(
        marker in "\n".join(texts)
        for marker in ["Nền tảng", "Câu hỏi ôn tập", "GitHub", "result.json"]
    )
    body_text = "\n".join(t.split("\n", 4)[4] for t in texts)
    normalized = re.sub(r"\s+", "", body_text)
    # Check every prose paragraph, table cell and code line survived export.
    for block in markdown_blocks("\n".join(contents), source, styles):
        paragraphs = [block] if isinstance(block, Paragraph) else []
        if isinstance(block, KeepTogether):
            paragraphs = block._content
        if isinstance(block, Table):
            paragraphs = [cell for row in block._cellvalues for cell in row]
        for paragraph in paragraphs:
            expected = re.sub(r"\s+", "", paragraph.getPlainText())
            assert expected in normalized, (source, expected[:120])
    return {
        "member": member["id"],
        "name": member["name"],
        "pdf": output.relative_to(ROOT).as_posix(),
        "markdown": source.relative_to(ROOT).as_posix(),
        "pages": len(reader.pages),
        "chapters": len(headings),
        "review_questions": question_count,
        "word_count": len(markdown.split()),
        "pdf_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "source_hash_mode": "utf8-lf",
        "source_sha256": {
            p.relative_to(ROOT).as_posix(): hashlib.sha256(
                p.read_text(encoding="utf-8").encode("utf-8")
            ).hexdigest()
            for p in sources
        },
    }


def main():
    """Rebuild all five PDFs using only current project guides and installed fonts."""
    team = json.loads((ROOT / "docs/management/thanh_vien.json").read_text(encoding="utf-8"))
    styles = make_styles()
    results = [build_member(member, styles) for member in team]
    (OUT / "pdf_audit.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            [{k: r[k] for k in ["member", "name", "pdf", "pages"]} for r in results],
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
