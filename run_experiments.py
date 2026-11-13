"""Reproduce the implemented SOS experiments, reports and executed notebooks."""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Verify saved artifacts and tests; does not reproduce experiments",
    )
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("workers must be positive")
    commands = (
        []
        if args.verify_only
        else [
            ["scripts/sos.py", "reproduce", "--workers", str(args.workers)],
            ["scripts/explain_selection.py", "--workers", str(args.workers)],
            ["scripts/adaptive_experiment.py", "--workers", str(args.workers)],
            ["scripts/analyze_failures.py"],
            ["scripts/worked_example.py"],
            ["scripts/summarize_results.py"],
            ["scripts/build_notebooks.py"],
            ["scripts/run_notebooks.py"],
        ]
    )
    commands += [["scripts/verify_outputs.py"], ["-m", "unittest", "discover", "-s", "tests", "-v"]]
    log = {"mode": "verify_only" if args.verify_only else "reproduce", "steps": []}
    destination = (
        ROOT
        / "results/sos"
        / ("runner_verify.json" if args.verify_only else "runner_reproduce.json")
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    for command in commands:
        print("Running:", sys.executable, *command, flush=True)
        start = time.perf_counter()
        process = subprocess.run([sys.executable, *command], cwd=ROOT, check=False)
        log["steps"].append(
            {
                "command": command,
                "exit_code": process.returncode,
                "seconds": time.perf_counter() - start,
            }
        )
        log["passed"] = process.returncode == 0 and len(log["steps"]) == len(commands)
        destination.write_text(json.dumps(log, indent=2), encoding="utf-8")
        if process.returncode:
            raise SystemExit(process.returncode)


if __name__ == "__main__":
    main()
