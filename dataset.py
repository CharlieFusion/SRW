import random
import re
from pathlib import Path
from typing import List, Tuple


def load_files(source_dir: str, extensions: List[str] | None = None) -> List[str]:
    """
    Загружает список файлов из директории
    """
    root = Path(source_dir)
    files = []

    for path in root.rglob("*"):
        if path.is_file():
            if extensions is None or path.suffix in extensions:
                files.append(str(path))

    return files


# =========================
# Модификации
# =========================

def modify_comments(text: str) -> str:
    lines = text.splitlines()
    out = []

    for line in lines:
        if random.random() < 0.2:
            out.append(line)
            out.append("# auto comment")
        else:
            out.append(line)

    return "\n".join(out)


def modify_whitespace(text: str) -> str:
    lines = []
    for line in text.splitlines():
        if random.random() < 0.3:
            line = " " * random.randint(0, 4) + line.strip()
        lines.append(line)
    return "\n".join(lines)


def modify_strings(text: str) -> str:
    def repl(match):
        s = match.group(0)
        if len(s) > 4 and random.random() < 0.4:
            return s[:-1] + "_x" + s[-1]
        return s

    return re.sub(r"(\".*?\"|\'.*?\')", repl, text)


MODIFIERS = [
    modify_comments,
    modify_whitespace,
    modify_strings,
]


def apply_random_modification(text: str) -> str:
    modifier = random.choice(MODIFIERS)
    return modifier(text)


# =========================
# Генерация пар
# =========================

def generate_pairs(
    source_dir: str,
    output_dir: str = "generated",
    max_files: int = 20,
    mods_per_file: int = 5,
) -> List[Tuple[str, str, bool]]:
    """
    Генерирует positive и negative пары
    """
    source_dir = Path(source_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    files = load_files(source_dir)
    random.shuffle(files)
    files = files[:max_files]

    pairs: List[Tuple[str, str, bool]] = []

    # Positive пары
    for path in files:
        content = Path(path).read_text(encoding="utf-8", errors="ignore")

        for i in range(mods_per_file):
            modified = apply_random_modification(content)
            out_path = output_dir / f"{Path(path).stem}_mod_{i}{Path(path).suffix}"
            out_path.write_text(modified, encoding="utf-8")

            pairs.append((path, str(out_path), True))

    # Negative пары
    for i in range(len(files)):
        for j in range(i + 1, len(files)):
            pairs.append((files[i], files[j], False))

    return pairs
