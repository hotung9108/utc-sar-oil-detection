"""TV5: one command to regenerate all current report measurements.

python reproduce.py                 # full verification, samples, both classes
python reproduce.py --samples-only  # explicitly partial development run
"""

import argparse

from src.tv5.experiments import run_dataset_evaluation, run_sample_experiments, write_manifest
from src.verification import main as verify


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples-only", action="store_true")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    write_manifest(scope="in_progress", workers=args.workers)
    verify()
    run_sample_experiments()
    if not args.samples_only:
        run_dataset_evaluation(args.workers)
    write_manifest(scope="samples" if args.samples_only else "full", workers=args.workers)


if __name__ == "__main__":
    main()
