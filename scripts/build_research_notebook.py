"""Build and execute the independent research review notebook (06_algorithm_research_review.ipynb)."""

from pathlib import Path
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
NB_PATH = ROOT / "notebooks/06_algorithm_research_review.ipynb"

# Import fixed markdown cells from fix_katex
from fix_katex import (
    md_cell_0, md_cell_2, md_cell_5, md_cell_7,
    md_cell_9, md_cell_11, md_cell_13, md_cell_15
)

# Read current executed notebook to preserve code cell sources and outputs
current_nb = nbf.read(NB_PATH, as_version=4)

md_map = {
    0: md_cell_0,
    2: md_cell_2,
    5: md_cell_5,
    7: md_cell_7,
    9: md_cell_9,
    11: md_cell_11,
    13: md_cell_13,
    15: md_cell_15,
}

for idx, text in md_map.items():
    current_nb.cells[idx].source = text.strip()

nbf.write(current_nb, NB_PATH)
print(f"[OK] build_research_notebook updated notebook at: {NB_PATH}")
