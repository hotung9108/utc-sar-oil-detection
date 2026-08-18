"""Compatibility import; implementation owned by TV2 in src/tv2/library_comparison.py."""

from src.tv2.library_comparison import *  # noqa: F401,F403
from src.tv2.library_comparison import run_comparisons

if __name__ == "__main__":
    result = run_comparisons()
    raise SystemExit(int((result.verdict == "FAIL").any()))
