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
    @staticmethod
    def build_signature(path: str) -> Dict[str, Any]:
        try:
            with open(path, "rb") as f:
                data = f.read()
            # Минимальная длина данных — 50 байт (для коротких файлов)
            t = tlsh.Tlsh(data, minimum_data_length=50)
            if t.is_valid():
                return {
                    "path": path,
                    "hash": t.hexdigest(),
                    "type": "tlsh"
                }
            else:
                # Логируем, но не выводим слишком много
                pass
        except Exception as e:
            print(f"[TLSH] Ошибка для {Path(path).name}: {e}")
        return {}

    @staticmethod
    def compare(sig1: Dict, sig2: Dict) -> float:
        if not sig1 or not sig2:
            return 0.0
        try:
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