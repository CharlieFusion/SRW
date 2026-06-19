from pathlib import Path
from typing import Dict, Any

from language import detect_language
from normalize import normalize_code
from hashing import simhash, ngram_fingerprint


def build_signature(
    path: str,
    save_normalized: bool = False,
    normalized_dir: str | None = None,
) -> Dict[str, Any]:
    """
    Строит сигнатуру файла.
    При необходимости сохраняет нормализованную версию.
    """
    file_path = Path(path)

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return {}

    if not content.strip():
        return {}

    lang, _ = detect_language(content)
    normalized = normalize_code(content, lang)

    if save_normalized and normalized_dir:
        _save_normalized_file(
            original_path=file_path,
            normalized_text=normalized,
            base_dir=Path(normalized_dir),
        )

    return {
        "path": str(file_path),
        "language": lang,
        "simhash": simhash(normalized),
        "ngrams": ngram_fingerprint(normalized),
        "length": len(normalized),
    }


def _save_normalized_file(
    original_path: Path,
    normalized_text: str,
    base_dir: Path,
) -> None:
    """
    Сохраняет нормализованный файл, повторяя структуру директорий
    """
    try:
        base_dir.mkdir(parents=True, exist_ok=True)

        # сохраняем относительную структуру
        relative = original_path.name
        out_path = base_dir / relative

        out_path.write_text(normalized_text, encoding="utf-8")
    except Exception:
        pass



if __name__ == "__main__":
    sig = build_signature("example.py")

    print(sig["language"])
    print(hex(sig["simhash"]))
    print(len(sig["ngrams"]))
