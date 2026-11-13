"""Restart and run every teaching notebook using this Python environment."""

import asyncio
import os
import sys
import tempfile
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
with tempfile.TemporaryDirectory(prefix="sos-kernel-") as tmp:
    import json

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
    for path in sorted((ROOT / "notebooks").glob("*.ipynb")):
        nb = nbformat.read(path, as_version=4)
        NotebookClient(
            nb, timeout=600, kernel_name="sos-local", resources={"metadata": {"path": str(ROOT)}}
        ).execute()
        nbformat.write(nb, path)
        print("Executed", path.name, flush=True)
