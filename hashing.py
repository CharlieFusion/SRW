import hashlib
from typing import List


# =========================
# SimHash
# =========================

def simhash(text: str, bits: int = 64) -> int:
    """
    Строит SimHash для текста
    """
    if not text:
        return 0

    tokens = text.split()
    vector = [0] * bits

    for token in tokens:
        h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)

        for i in range(bits):
            if h & (1 << i):
                vector[i] += 1
            else:
                vector[i] -= 1

    fingerprint = 0
    for i, weight in enumerate(vector):
        if weight > 0:
            fingerprint |= 1 << i

    return fingerprint


def simhash_similarity(a: int, b: int, bits: int = 64) -> float:
    """
    Схожесть двух SimHash ∈ [0,1]
    """
    if a == b:
        return 1.0

    distance = bin(a ^ b).count("1")
    return 1.0 - distance / bits


# =========================
# N-gram Winnowing
# =========================

def ngram_fingerprint(
    text: str,
    n: int = 5,
    window: int = 7,
    limit: int = 100,
) -> List[int]:
    """
    Фаззи-отпечаток на основе n-грамм (winnowing)

    Возвращает список хэшей
    """
    if len(text) < n:
        return []

    # 1. Строим хэши n-грамм
    hashes = []
    for i in range(len(text) - n + 1):
        ngram = text[i : i + n]
        h = hashlib.md5(ngram.encode("utf-8")).digest()
        hashes.append(int.from_bytes(h[:4], "big"))  # 32-bit

    if len(hashes) <= window:
        return hashes[:limit]

    # 2. Winnowing (минимум в окне)
    fingerprints = []
    min_pos = -1

    for i in range(len(hashes)):
        if i >= window:
            # если минимум вышел из окна — пересчитываем
            if min_pos <= i - window:
                window_slice = hashes[i - window + 1 : i + 1]
                min_val = min(window_slice)
                min_pos = i - window + 1 + window_slice.index(min_val)
            else:
                if hashes[i] < hashes[min_pos]:
                    min_pos = i
        else:
            if min_pos == -1 or hashes[i] < hashes[min_pos]:
                min_pos = i

        if not fingerprints or fingerprints[-1] != hashes[min_pos]:
            fingerprints.append(hashes[min_pos])

        if len(fingerprints) >= limit:
            break

    return fingerprints


def jaccard_similarity(a: List[int], b: List[int]) -> float:
    """
    Метрика Жаккара ∈ [0,1]
    """
    if not a or not b:
        return 0.0

    set_a, set_b = set(a), set(b)
    return len(set_a & set_b) / len(set_a | set_b)

if __name__ == "__main__":
    h1 = simhash("def foo(): print(1)")
    h2 = simhash("def foo(): print(2)")

    print(simhash_similarity(h1, h2))