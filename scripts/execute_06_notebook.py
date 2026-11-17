"""Execute 06_algorithm_research_review.ipynb and save outputs."""

import asyncio
import os
import sys
import tempfile
from pathlib import Path
import json
import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
NB_PATH = ROOT / "notebooks/06_algorithm_research_review.ipynb"

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

with tempfile.TemporaryDirectory(prefix="sos-kernel-") as tmp:
    directory = Path(tmp) / "kernels/sos-local"
    directory.mkdir(parents=True)
    (directory / "kernel.json").write_text(
        json.dumps(
            {
                "argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
                "display_name": "SOS local",
                "language": "python",
            }
        )
    )
    os.environ["JUPYTER_PATH"] = tmp + os.pathsep + os.environ.get("JUPYTER_PATH", "")
    for name, subdir in [
        ("IPYTHONDIR", "ipython"),
        ("JUPYTER_RUNTIME_DIR", "runtime"),
        ("MPLCONFIGDIR", "matplotlib"),
    ]:
        location = Path(tmp) / subdir
        location.mkdir()
        os.environ[name] = str(location)
    
    print(f"[*] Đang thực thi {NB_PATH.name}...")
    nb = nbformat.read(NB_PATH, as_version=4)
    client = NotebookClient(
        nb, timeout=1200, kernel_name="sos-local", resources={"metadata": {"path": str(ROOT)}}
    )
    client.execute()
    nbformat.write(nb, NB_PATH)
    print(f"[OK] Đã thực thi và lưu thành công {NB_PATH.name}!")

