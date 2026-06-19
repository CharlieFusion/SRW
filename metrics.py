from typing import Dict


def classification_metrics(
    tp: int,
    fp: int,
    tn: int,
    fn: int,
) -> Dict[str, float]:
    """
    Считает стандартные метрики классификации

    Returns:
        словарь с метриками
    """
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )

    accuracy = (
        (tp + tn) / (tp + tn + fp + fn)
        if (tp + tn + fp + fn) > 0
        else 0.0
    )

    false_positive_rate = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    false_negative_rate = fn / (fn + tp) if (fn + tp) > 0 else 0.0

    return {
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "accuracy": accuracy,
        "false_positive_rate": false_positive_rate,
        "false_negative_rate": false_negative_rate,
    }


if __name__ == "__main__":
    m = classification_metrics(tp=42, fp=5, tn=30, fn=3)

    for k, v in m.items():
        print(k, round(v, 3) if isinstance(v, float) else v)