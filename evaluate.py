# evaluate.py (дополненная версия)
from typing import List, Tuple, Dict, Any, Callable
from signature import build_signature
from compare import compare_signatures
from metrics import classification_metrics

Pair = Tuple[str, str, bool]


def evaluate_pairs(
    pairs: List[Pair],
    threshold: float = 0.7,
    build_sig_fn: Callable = build_signature,
    compare_sig_fn: Callable = compare_signatures,
    save_normalized: bool = False,
    normalized_dir: str | None = None,
) -> Dict[str, Any]:
    """
    Массовая оценка пар файлов с возможностью использовать разные алгоритмы.

    Args:
        pairs: [(file1, file2, expected_similar)]
        threshold: порог схожести
        build_sig_fn: функция для построения сигнатуры
        compare_sig_fn: функция для сравнения сигнатур

    Returns:
        словарь с метриками и деталями
    """
    signatures: Dict[str, dict] = {}

    tp = fp = tn = fn = 0
    results = []

    def get_signature(path: str) -> dict:
        if path not in signatures:
            sig = build_sig_fn(path)
            if sig:
                signatures[path] = sig
        return signatures.get(path, {})

    for file1, file2, expected_similar in pairs:
        sig1 = get_signature(file1)
        sig2 = get_signature(file2)

        if not sig1 or not sig2:
            continue  # пропускаем пары, где не удалось построить сигнатуру

        similarity = compare_sig_fn(sig1, sig2)
        predicted_similar = similarity >= threshold

        # Обновляем confusion matrix
        if expected_similar and predicted_similar:
            tp += 1
            outcome = "TP"
        elif not expected_similar and predicted_similar:
            fp += 1
            outcome = "FP"
        elif not expected_similar and not predicted_similar:
            tn += 1
            outcome = "TN"
        else:
            fn += 1
            outcome = "FN"

        results.append({
            "file1": file1,
            "file2": file2,
            "similarity": similarity,
            "expected_similar": expected_similar,
            "predicted_similar": predicted_similar,
            "outcome": outcome,
        })

    metrics = classification_metrics(tp, fp, tn, fn)

    return {
        "metrics": metrics,
        "threshold": threshold,
        "total_pairs": len(pairs),
        "results": results,
    }