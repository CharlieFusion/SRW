import re


def normalize_code(content: str, lang: str) -> str:
    content = _strip_bom(content)
    content = _normalize_newlines(content)
    content = _remove_comments(content, lang)
    content = _normalize_whitespace(content)
    content = _normalize_empty_lines(content)
    return content.strip()


def _strip_bom(text: str) -> str:
    return text.lstrip("\ufeff")


def _normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _normalize_whitespace(text: str) -> str:
    lines = []
    for line in text.split("\n"):
        stripped = line.rstrip()
        # схлопываем множественные пробелы (но не отступы)
        indent = len(stripped) - len(stripped.lstrip(" "))
        body = re.sub(r" {2,}", " ", stripped.lstrip(" "))
        lines.append(" " * indent + body)
    return "\n".join(lines)


def _normalize_empty_lines(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text)


def _remove_comments(text: str, lang: str) -> str:
    match lang:
        case "python":
            text = re.sub(r"#.*", "", text)
            text = re.sub(r'("""|\'\'\')[\s\S]*?\1', "", text)
        case "bash":
            text = re.sub(r"#.*", "", text)
        case "javascript":
            text = re.sub(r"//.*$", "", text, flags=re.MULTILINE)
            text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
        case "php":
            text = re.sub(r"//.*$", "", text, flags=re.MULTILINE)
            text = re.sub(r"#.*$", "", text, flags=re.MULTILINE)
            text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
        case _:
            pass

    return text
