"""TV5: evaluate both dataset classes at image level, not pixel-mask accuracy.

Labels are the supplied directory labels, not independently verified oil identity.
This replaces heuristic CLEAN_BOUNDARY success labels with measured TP/FP/TN/FN.
"""

from src.tv5.experiments import run_dataset_evaluation

if __name__ == "__main__":
    run_dataset_evaluation()
