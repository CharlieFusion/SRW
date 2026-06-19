# external_hashes.py
"""
Адаптеры для внешних алгоритмов с диагностикой.
"""

import ssdeep
import tlsh
from pathlib import Path
from typing import Dict, Any


class SSDeepAdapter:
    @staticmethod
    def build_signature(path: str) -> Dict[str, Any]:
        try:
            hash_str = ssdeep.hash_from_file(path)
            if hash_str:
                return {"path": path, "hash": hash_str, "type": "ssdeep"}
        except Exception as e:
            print(f"[SSDeep] Ошибка для {Path(path).name}: {e}")
        return {}

    @staticmethod
    def compare(sig1: Dict, sig2: Dict) -> float:
        if not sig1 or not sig2:
            return 0.0
        try:
            score = ssdeep.compare(sig1.get("hash", ""), sig2.get("hash", ""))
            return score / 100.0
        except Exception:
            return 0.0


class TLSHAdapter:
    """Адаптер для TLSH с поддержкой разных версий библиотеки."""

    @staticmethod
    def build_signature(path: str) -> Dict[str, Any]:
        try:
            with open(path, "rb") as f:
                data = f.read()

            # Попытка 1: новый стиль (4.x) — Tlsh(data) с методами is_valid / hexdigest
            try:
                t = tlsh.Tlsh(data)
                if hasattr(t, 'is_valid') and t.is_valid():
                    if hasattr(t, 'hexdigest'):
                        return {"path": path, "hash": t.hexdigest(), "type": "tlsh"}
            except TypeError:
                # Если TypeError — значит конструктор не принимает аргументы (старая версия)
                pass

            # Попытка 2: старый стиль (1.x – 3.x) — Tlsh() + update + final + get_hash
            try:
                t = tlsh.Tlsh()
                t.update(data)
                t.final()
                if hasattr(t, 'get_hash'):
                    h = t.get_hash()
                    if h is not None:
                        return {"path": path, "hash": h, "type": "tlsh"}
            except Exception:
                pass

            # Попытка 3: если есть функция tlsh.hash (некоторые версии)
            try:
                h = tlsh.hash(data)
                if h:
                    return {"path": path, "hash": h, "type": "tlsh"}
            except Exception:
                pass

        except Exception as e:
            print(f"[TLSH] Ошибка для {path}: {e}")

        return {}

    @staticmethod
    def compare(sig1: Dict, sig2: Dict) -> float:
        if not sig1 or not sig2:
            return 0.0
        try:
            # В старых версиях diff может принимать строки, в новых — тоже
            dist = tlsh.diff(sig1.get("hash", ""), sig2.get("hash", ""))
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