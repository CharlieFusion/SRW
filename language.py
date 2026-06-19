import re
from typing import Dict, Tuple

LANGUAGE_SIGNATURES = {
    "python": {
        "shebang": ["python"],
        "keywords": ["def ", "class ", "import ", "from ", "lambda ", "yield "],
        "patterns": [
            r"\bdef\s+\w+\s*\(",
            r"\bclass\s+\w+",
            r"^\s*import\s+\w+",
        ],
    },
    "bash": {
        "shebang": ["bash", "sh", "zsh"],
        "keywords": ["#!/bin/bash", "echo ", "$1", "if [", "fi", "done"],
        "patterns": [
            r"^\s*#!/bin/(ba)?sh",
            r"\$\{?\w+\}?",
            r"\bif\s+\[",
        ],
    },
    "javascript": {
        "shebang": ["node"],
        "keywords": ["function ", "const ", "let ", "=>", "console.log"],
        "patterns": [
            r"\bfunction\s+\w+\s*\(",
            r"\b(const|let|var)\s+\w+",
            r"=>",
        ],
    },
    "php": {
        "shebang": ["php"],
        "keywords": ["<?php", "$this->", "echo ", "namespace "],
        "patterns": [
            r"<\?php",
            r"\$\w+",
            r"->\w+\(",
        ],
    },
}


def _detect_by_shebang(first_line: str) -> str | None:
    if not first_line.startswith("#!"):
        return None

    shebang = first_line.lower()
    for lang, sig in LANGUAGE_SIGNATURES.items():
        if any(s in shebang for s in sig["shebang"]):
            return lang
    return None


def detect_language(content: str) -> Tuple[str, Dict[str, float]]:
    """
    Определяет язык программирования по содержимому файла

    Returns:
        (best_language, probability_distribution)
    """
    if not content.strip():
        return "unknown", {}

    lines = content.splitlines()
    if lines:
        by_shebang = _detect_by_shebang(lines[0])
        if by_shebang:
            return by_shebang, {by_shebang: 1.0}

    scores: Dict[str, float] = {}

    for lang, sig in LANGUAGE_SIGNATURES.items():
        score = 0.0
        lower = content.lower()

        for kw in sig["keywords"]:
            if kw.lower() in lower:
                score += 2

        for pattern in sig["patterns"]:
            score += len(re.findall(pattern, content, re.MULTILINE)) * 1.5

        if score > 0:
            scores[lang] = score

    if not scores:
        return "unknown", {}

    total = sum(scores.values())
    probs = {k: v / total for k, v in scores.items()}
    best = max(probs, key=probs.get)

    return best, probs
