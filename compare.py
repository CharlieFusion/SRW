from hashing import simhash_similarity, jaccard_similarity


def compare_signatures(a: dict, b: dict) -> float:
    """
    Сравнивает две сигнатуры файлов

    Returns:
        similarity ∈ [0,1]
    """
    if not a or not b:
        return 0.0

    # Если языки разные — резко понижаем схожесть
    if a.get("language") != b.get("language"):
        return 0.1

    scores = []

    # SimHash (основной сигнал)
    if "simhash" in a and "simhash" in b:
        scores.append(
            0.6 * simhash_similarity(a["simhash"], b["simhash"])
        )

    # N-gram fingerprints
    if "ngrams" in a and "ngrams" in b:
        scores.append(
            0.4 * jaccard_similarity(a["ngrams"], b["ngrams"])
        )

    if not scores:
        return 0.0

    return sum(scores)

if __name__ == "__main__":
    from signature import build_signature

    a = build_signature("a.py")
    b = build_signature("a_modified.py")

    print(compare_signatures(a, b))
