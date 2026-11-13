"""Restart and run every teaching notebook using this Python environment."""

import asyncio
import argparse
import os
import sys
import tempfile
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--notebook', type=Path, action='append',
                    help='Notebook path relative to project root; repeat to run several. Default: five SOS notebooks.')
args = parser.parse_args()
paths = args.notebook or sorted((ROOT / 'notebooks').glob('*.ipynb'))
paths = [(ROOT / p).resolve() if not p.is_absolute() else p.resolve() for p in paths]
for path in paths:
    if not path.is_relative_to((ROOT / 'notebooks').resolve()) or not path.is_file():
        parser.error(f'Notebook must exist inside notebooks/: {path}')
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
    for path in paths:
        nb = nbformat.read(path, as_version=4)
        NotebookClient(
            nb, timeout=600, kernel_name="sos-local", resources={"metadata": {"path": str(ROOT)}}
        ).execute()
        nbformat.write(nb, path)
        print("Executed", path.name, flush=True)
