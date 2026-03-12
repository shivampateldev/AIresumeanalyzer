"""
text_cleaner.py — Text normalization utilities for resume and scraped content.
"""
import re


# Special tech tokens that must survive cleaning (case-sensitive patterns)
_SPECIAL_TOKENS = {
    # Exact replacements to protect before lowercasing
    r"\bC\+\+\b": "c++",
    r"\bC#\b": "c#",
    r"\.NET\b": ".net",
    r"\bNode\.js\b": "node.js",
    r"\bNext\.js\b": "next.js",
    r"\bReact\.js\b": "react",
    r"\bVue\.js\b": "vue",
    r"\bExpress\.js\b": "express",
    r"\bNuxt\.js\b": "nuxt",
    r"\bP(ython)": "python",  # avoid PYthon typos
}


def clean_for_extraction(text: str) -> str:
    """
    Prepare text for skill extraction:
    1. Protect special tokens (C++, C#, .NET, Node.js)
    2. Lowercase
    3. Remove markdown/bullet formatting
    4. Normalize punctuation
    5. Collapse whitespace
    """
    if not text:
        return ""

    # Step 1: Protect special tokens before any casing change
    protected = text
    protected = re.sub(r"\bC\+\+\b", "__CPP__", protected)
    protected = re.sub(r"\bC#\b", "__CSHARP__", protected)
    protected = re.sub(r"\b\.NET\b", "__DOTNET__", protected)
    protected = re.sub(r"\bNode\.js\b", "__NODEJS__", protected)
    protected = re.sub(r"\bNext\.js\b", "__NEXTJS__", protected)
    protected = re.sub(r"\bReact\.js\b", "__REACTJS__", protected)
    protected = re.sub(r"\bVue\.js\b", "__VUEJS__", protected)
    protected = re.sub(r"\bExpress\.js\b", "__EXPRESSJS__", protected)

    # Step 2: Lowercase everything
    protected = protected.lower()

    # Step 3: Remove markdown bullets and heading hashes
    protected = re.sub(r"^[•\-\*\#]+\s*", " ", protected, flags=re.MULTILINE)

    # Step 4: Replace common separators and punctuation with spaces
    # Keep + and # and . for tech tokens, remove others
    protected = re.sub(r"[^\w\s\+\#\.]", " ", protected)

    # Step 5: Restore special tokens (lowercase canonical forms)
    protected = protected.replace("__cpp__", " c++ ")
    protected = protected.replace("__csharp__", " c# ")
    protected = protected.replace("__dotnet__", " .net ")
    protected = protected.replace("__nodejs__", " node.js ")
    protected = protected.replace("__nextjs__", " next.js ")
    protected = protected.replace("__reactjs__", " react ")
    protected = protected.replace("__vuejs__", " vue ")
    protected = protected.replace("__expressjs__", " express ")

    # Step 6: Collapse whitespace
    protected = re.sub(r"\s+", " ", protected)
    return protected.strip()


def clean_for_display(text: str) -> str:
    """Light normalization for display only (preserve case)."""
    return re.sub(r"\s+", " ", text).strip()


def normalize_encoding(text: str) -> str:
    """Fix common PDF encoding artifacts."""
    replacements = {
        "\u2019": "'", "\u2018": "'",
        "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-",
        "\ufb01": "fi", "\ufb02": "fl",
        "\u00e2\u0080\u0099": "'",
        "\xa0": " ",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return text
