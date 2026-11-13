# Contract for the SAR course report

Reference: D:/Codin/utc-code/HK4_1/XLA/BTL/hướng dẫn viết báo cáo BTL XLA_12_11.docx
SHA-256: 3f02d4a480267f093eeed08cd9ca2dfc9034a1e45c7c979caae1e196cb6b915d
Reference render: ../report-template-render/page-1.png through page-22.png.
All 22 pages inspected during this continuation. Package inventory, complete XML
styles, paragraph properties, tables and section definitions: template_inventory.json.
Stable slots are zero-based direct body paragraph/table indices in that inventory;
do not recalculate indices while editing. Retain original reference byte-for-byte.

## Page and style system

Five source sections, A4 portrait 11906 by 16838 twips; top/bottom/right 1134,
left 1701, header/footer 708 twips; one column, gutter zero. Remove the entire
first instructional section (paragraphs 0 through 16 and table 0). Retain four
sections: framed cover, unframed subcover, prelims roman starting i, main decimal
starting 1. Preserve footer parts and relationships. Cover double frame 12 eighth
points with 12-point offset. Source has no embedded logo; remove logo placeholder,
do not invent a university logo. Preserve cover spacing and black centered type.

Body Times New Roman 13 pt, line spacing 1.3. Keep original styles.xml and
numbering.xml byte-for-byte. Heading1 14 pt bold black centered and page start;
Heading2/3 hierarchy and numbering as in source. Use original body paragraph 67
as paragraph pattern, 114 as pseudocode pattern, 73/87 as caption patterns.
Preserve the actual source paragraph and run formatting for cover/title roles.
Use existing title style for the topic title with source cover direct formatting.
Tables have black borders, bold centered header, white cells, body text 13 pt.
Clone source table properties but adapt column grid to semantic content, within
16 cm available width. Repeat headers and prohibit row splitting. Keep captions
with following table or previous figure. Figure slots are inline, centered.
No decorative color system. Mathematical expressions must be editable OMML.

## Slots and flow

Paragraphs 17–32 and 33–48: cover/subcover. Replace titles, known team names;
leave instructor, class, group, IDs blank until confirmed. Keep section breaks.
Paragraphs 49–62: declaration, preface, TOC, figures, tables, abbreviations.
Declaration must disclose AI assistance; no fabricated signature or personal
attestation. Signature cells blank. Preface from narrative.json, <=1 page.
Three TOC SDT controls remain intact; only field result updating is permitted.
Abbreviation table 4 uses only terms actually appearing in report.
Main paragraph anchors 67,70,77,81,91,93,96,103,109,113,123,132,134,139,142,145,149
receive corresponding narrative.json blocks, cloning body pattern for overflow.
Heading placeholders 90 and 92 receive the block headings. Remove instructional
blue paragraphs, sample PSNR equation and unrelated examples. Retain main chapter
headings and their original numbering. Main text target 25–35 pages (20–35 in
latest template, stricter lower bound from earlier course guide).
Tables 5–9: functions/owners, splits, input/output/config, NumPy comparison,
actual quantitative results from JSON. Clone additional table/caption patterns
for full filter comparison, model metrics and evidence map.
Images at 85/105/125: data examples, pipeline, intermediate stages. Add actual
parameter plot and 3 distinct failure images at chapter 4 relevant anchors.
Use chapter-local SEQ fields with explicit cached values so initial render is
meaningful; update TOC/caption fields in Word before final export.
Paragraph 97 equation pattern may be cloned for Lee, threshold, SVM and metrics;
explain symbols immediately. Pseudocode 114–119 is replaced with <=20 lines per
algorithm, linked to real function names. References 152–156 replaced with all
verified entries from bibliography.json (13 after the physical/GUI/data-audit
update). No invented references. Anchor 145 also records the separate physical,
wind and GUI demonstrations and the QPOSD audit, without claiming labelled
physical detection validation. Preserve the existing section style and flow.
Appendix A: tables 10/11 planned assignments and unfilled actual peer scores.
Appendix B: no invented meeting records; remove sample minutes paragraphs
167–173 and table12, preserve section with a truthful pending note.
Appendix C table13: actual Codex assistance disclosed, distinguish automated
checks from human review not yet verified. Appendix D: actual reproducible commands.
Appendices <=10 pages excluding real minutes. Known missing submission information
is tracked separately; document remains a draft until verified and filled.

## Package fidelity and gates

All parts preserve-only except word/document.xml, its relationships, settings,
and content types (new inline PNGs). New media allowed. Field refresh additionally
appends Word-generated TOC1–TOC3 and TableofFigures styles that the source lacks;
every existing style node must remain byte-for-byte identical when serialized.
This is needed for the source's existing TOC controls to render separate entries.
Repack untouched parts
from original ZIP after python-docx authoring; assert hashes for all preserve-only
parts. Preserve existing relationships, add only media relationships. No original
drawings, comments or footnotes; SDT count3 retained. Settings updateFields=true.
Do not use LibreOffice save to refresh fields. Word refresh if available; otherwise
record deferred field update. Render draft with render_docx.py; inspect EVERY final
page, check figures readable, no clipping/blank overflow, correct numbering and
references. Record page ranges and main-content count from rendered artifact.
No final delivery until rendering, page inspection and structural checks pass.
