"""Validate report source anchors and citations; does not claim DOCX layout verification."""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "scripts"))


import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
folder = ROOT / "docs/report"
narrative = json.loads((folder / "narrative.json").read_text(encoding="utf-8"))
bibliography = json.loads((folder / "bibliography.json").read_text(encoding="utf-8"))
references = list(ROOT.glob("*12_11.docx"))
assert len(references) == 1, "Expected the single user-supplied report guide"
reference = references[0]
with ZipFile(reference) as archive:
    document = ET.fromstring(archive.read("word/document.xml"))
ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
paragraphs = document.findall("./w:body/w:p", ns)
anchors = [s["anchor"] for s in narrative["sections"]]
assert len(anchors) == len(set(anchors))
assert all(0 <= i < len(paragraphs) for i in anchors)
text = "\n".join(narrative["preface"] + [p for s in narrative["sections"] for p in s["paragraphs"]])
cited = {int(x) for x in re.findall(r"\[(\d+)\]", text)}
available = {r["number"] for r in bibliography}
assert cited == available, (cited, available)
assert len(bibliography) >= 10
assert sum("doi.org/10." in r["url"] for r in bibliography) >= 3
audit = {
    "reference_file": reference.name,
    "reference_sha256": hashlib.sha256(reference.read_bytes()).hexdigest(),
    "source_paragraphs": len(paragraphs),
    "replacement_blocks": len(anchors),
    "narrative_word_count": len(text.split()),
    "references": len(bibliography),
    "cited_numbers": sorted(cited),
    "anchors_valid": True,
    "citations_complete": True,
    "scope": "Narrative source only; document build and render audits are separate",
    "pending": [
        "Fill actual group cover metadata",
        "Collect real signed contribution and meeting records",
    ],
}
(folder / "source_audit.json").write_text(
    json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("Report source checks passed; this check does not verify document layout")
