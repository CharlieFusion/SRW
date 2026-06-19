import ssdeep
import tlsh
from pathlib import Path
from typing import Dict, Any, Optional


class SSDeepAdapter:
    """Адаптер для ssdeep."""

    @staticmethod
    def build_signature(path: str) -> Dict[str, Any]:
        """Генерирует сигнатуру ssdeep для файла."""
        try:
            hash_str = ssdeep.hash_from_file(path)
            if hash_str:
                return {
                    "path": path,
                    "hash": hash_str,
                    "type": "ssdeep"
                }
        except Exception:
            pass
        return {}

    @staticmethod
    def compare(sig1: Dict, sig2: Dict) -> float:
        """Сравнивает две ssdeep-сигнатуры. Возвращает схожесть ∈ [0,1]."""
        if not sig1 or not sig2:
            return 0.0
        try:
            score = ssdeep.compare(sig1.get("hash", ""), sig2.get("hash", ""))
            return score / 100.0  # ssdeep возвращает 0..100
        except Exception:
            return 0.0


class TLSHAdapter:
    """Адаптер для TLSH."""

    @staticmethod
    def build_signature(path: str) -> Dict[str, Any]:
        """Генерирует TLSH-хеш для файла."""
        try:
            with open(path, "rb") as f:
                data = f.read()
            t = tlsh.Tlsh(data)
            if t.is_valid():
                return {
                    "path": path,
                    "hash": t.hexdigest(),
                    "type": "tlsh"
                }
        except Exception:
            pass
        return {}

    @staticmethod
    def compare(sig1: Dict, sig2: Dict) -> float:
        """Сравнивает две TLSH-сигнатуры. Возвращает схожесть ∈ [0,1]."""
        if not sig1 or not sig2:
            return 0.0
        try:
            dist = tlsh.diff(sig1.get("hash", ""), sig2.get("hash", ""))
            # Максимальное расстояние в TLSH ~ 500, преобразуем в схожесть
            max_dist = 500
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