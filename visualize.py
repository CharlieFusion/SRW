# visualize.py
import matplotlib.pyplot as plt

from typing import List, Tuple
from evaluate import evaluate_pairs


Pair = Tuple[str, str, bool]


def compute_roc(
    pairs: List[Pair],
    thresholds: List[float],
):
    """
    Считает точки ROC-кривой
    """
    tpr = []
    fpr = []

    for th in thresholds:
        report = evaluate_pairs(pairs, threshold=th)
        m = report["metrics"]

        print(f"\nTHRESHOLD: {th}")
        print("=== РЕЗУЛЬТАТЫ ===")
        print(f"Всего пар:\t{report['total_pairs']}")
        print(f"Precision:\t{m['precision']:.3f}")
        print(f"Recall:\t\t{m['recall']:.3f}")
        print(f"F1-score:\t{m['f1']:.3f}")
        print(f"Accuracy:\t{m['accuracy']:.3f}")
        print(f"FPR:\t\t\t{m['false_positive_rate']:.3f}")
        print(f"FNR:\t\t\t{m['false_negative_rate']:.3f}")

        tpr.append(m["recall"])                  # True Positive Rate
        fpr.append(m["false_positive_rate"])     # False Positive Rate

    return fpr, tpr


def plot_similarity_histogram(results):
    similar = [r["similarity"] for r in results if r["expected_similar"]]
    # different = [r["similarity"] for r in results if not r["expected_similar"]]

    plt.figure()
    plt.hist(similar, bins=20, alpha=0.7, label="Similar")
    # plt.hist(different, bins=20, alpha=0.7, label="Different")

    plt.xlabel("Similarity")
    plt.ylabel("Count")
    plt.legend()
    plt.title("Similarity distribution")
    plt.show()



def plot_roc(fpr, tpr, title="ROC Curve"):
    plt.figure()
    plt.plot(fpr, tpr, marker="o", label="Similarity model")
    plt.plot([0, 1], [0, 1], linestyle="--", label="Random guess")

    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
