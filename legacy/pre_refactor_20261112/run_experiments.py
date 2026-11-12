"""TV5: regenerate sample comparisons, parameter survey and adverse cases.

For all report evidence, including library checks and Class_0/Class_1, run
python reproduce.py. This entrypoint intentionally evaluates only demo samples.
"""

from src.tv5.experiments import run_sample_experiments

if __name__ == "__main__":
    run_sample_experiments()
