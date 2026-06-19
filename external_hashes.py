# external_hashes.py (обновлённый)

import ssdeep
import tlsh
from pathlib import Path
from typing import Dict, Any

from language import detect_language
from normalize import normalize_code


def _normalize_file(path: str) -> str:
    """Читает файл, определяет язык и нормализует."""
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    lang, _ = detect_language(content)
    return normalize_code(content, lang)


class SSDeepAdapter:
    @staticmethod
    def build_signature(path: str) -> Dict[str, Any]:
        try:
            normalized = _normalize_file(path)
            if not normalized:
                return {}
            hash_str = ssdeep.hash(normalized)
            if hash_str:
                return {"path": path, "hash": hash_str, "type": "ssdeep"}
        except Exception as e:
            print(f"[SSDeep] Ошибка для {path}: {e}")
        return {}

    @staticmethod
    def compare(sig1: Dict, sig2: Dict) -> float:
        if not sig1 or not sig2:
            return 0.0
        try:
            score = ssdeep.compare(sig1.get("hash", ""), sig2.get("hash", ""))
            # Нелинейное масштабирование для повышения чувствительности
            return (score / 100.0) ** 0.6
        except Exception:
            return 0.0


class TLSHAdapter:
    @staticmethod
    def build_signature(path: str) -> Dict[str, Any]:
        try:
            normalized = _normalize_file(path)
            if not normalized or len(normalized) < 256:
                # TLSH требует минимум 256 байт
                return {}
            # Для старых версий TLSH
            t = tlsh.Tlsh()
            t.update(normalized.encode('utf-8'))
            t.final()
            if hasattr(t, 'get_hash'):
                h = t.get_hash()
                if h:
                    return {"path": path, "hash": h, "type": "tlsh"}
            # Для новых версий (если get_hash нет, пробуем hexdigest)
            if hasattr(t, 'hexdigest'):
                h = t.hexdigest()
                if h:
                    return {"path": path, "hash": h, "type": "tlsh"}
        except Exception as e:
            # Если ошибка "less than 256", мы её уже отсекли, но на всякий случай
            if "less than 256" not in str(e):
                print(f"[TLSH] Ошибка для {path}: {e}")
        return {}

    @staticmethod
    def compare(sig1: Dict, sig2: Dict) -> float:
        if not sig1 or not sig2:
            return 0.0
        try:
            dist = tlsh.diff(sig1.get("hash", ""), sig2.get("hash", ""))
            # Для нормализованного кода расстояние меньше
            max_dist = 150
            return max(0.0, 1.0 - (dist / max_dist))
        except Exception:
            return 0.0


class CustomAdapter:
    @staticmethod
    def build_signature(path: str) -> Dict[str, Any]:
        from signature import build_signature
        return build_signature(path)

    @staticmethod
    def compare(sig1: Dict, sig2: Dict) -> float:
        from compare import compare_signatures
        return compare_signatures(sig1, sig2)