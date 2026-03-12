import json
import os
import re


def clean_text(text: str) -> str:
    """Clean and normalize raw text for skill matching."""
    if not text:
        return ""
    # Lowercase
    text = text.lower()
    # Preserve common tech symbols: #, +, ., /
    text = re.sub(r"[^\w\s#\+\.\-/]", " ", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_encoding(text: str) -> str:
    """Fix common encoding artifacts from PDF extraction."""
    replacements = {
        "\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-", "\u00e2\u0080\u0099": "'",
        "\ufb01": "fi", "\ufb02": "fl", "\u00e9": "e",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return text


def load_json(file_path: str) -> dict:
    """Load a JSON file with error handling."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        print(f"[WARN] JSON parse error in {file_path}: {e}")
        return {}


def save_json(file_path: str, data: dict) -> None:
    """Save a dict as a JSON file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def truncate_list(lst: list, max_items: int = 20) -> list:
    """Return at most max_items elements from a list."""
    return lst[:max_items]


def deduplicate(lst: list) -> list:
    """Remove duplicates while preserving order."""
    seen = set()
    result = []
    for item in lst:
        key = item.lower() if isinstance(item, str) else item
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result
