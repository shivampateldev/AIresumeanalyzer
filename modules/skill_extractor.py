"""
skill_extractor.py — Hybrid skill extraction: Regex + Vocabulary + Groq AI.

CRITICAL BUGS FIXED:
1. The bare "c" in vocabulary was matching inside "c++" because the lookbehind
   did not exclude "+" characters. Fixed by:
   a) Requiring single-char skills to be preceded/followed by whitespace or line start
   b) Removing ambiguous single-letter entries ("c", "r") from vocabulary matching
      and instead requiring them to be matched via special patterns only
2. C++ and other special tokens now use ORIGINAL text before cleaning for Pass 1
3. Added Groq AI layer for both extraction and validation

Pipeline:
  raw_text
    → Pass 0: Run on ORIGINAL text (before clean) for special tokens
    → Pass 1: Clean text → regex special patterns
    → Pass 2: Vocabulary matching (greedy, longest-first)
    → Pass 3: Groq AI extraction (if available)
    → Merge and deduplicate all results
"""
import re
import os
from modules.text_cleaner import clean_for_extraction
from modules.utils import load_json
from modules.logger import logger


# Skills that are single-char or ambiguous — only match in special ways
_AMBIGUOUS_SHORTS = {"c", "r", "c#"}

# Explicitly handled: matched on ORIGINAL text BEFORE cleaning
_ORIGINAL_TEXT_PATTERNS = [
    # These need to run on the ORIGINAL (pre-clean) text to avoid "c" matching "c++"
    (re.compile(r'\bC\+\+'),               "c++"),
    (re.compile(r'\bC#\b'),                "c#"),
    (re.compile(r'[.]NET\b', re.IGNORECASE),".net"),
    # These work fine on cleaned text too but keep here for safety
    (re.compile(r'\bR\b'),                 "r"),   # only match standalone R
]

# Matched on CLEANED (lowercase) text
_CLEANED_TEXT_PATTERNS = [
    (re.compile(r"(?<![a-z0-9\+])c\+\+(?![a-z0-9])"),          "c++"),
    (re.compile(r"(?<![a-z0-9])\.net\b"),                        ".net"),
    (re.compile(r"(?<![a-z0-9])node\.js(?![a-z0-9])"),           "node.js"),
    (re.compile(r"(?<![a-z0-9])next\.js(?![a-z0-9])"),           "next.js"),
    (re.compile(r"(?<![a-z0-9])react\.js(?![a-z0-9])"),          "react"),
    (re.compile(r"(?<![a-z0-9])vue\.js(?![a-z0-9])"),            "vue"),
    (re.compile(r"(?<![a-z0-9])express\.js(?![a-z0-9])"),        "express"),
    (re.compile(r"(?<![a-z0-9])scikit[\-\s]learn(?![a-z0-9])"),  "scikit-learn"),
    (re.compile(r"(?<![a-z0-9])power\s*bi(?![a-z0-9])"),         "power bi"),
    (re.compile(r"(?<![a-z0-9])rest\s*api(?![a-z0-9])"),         "rest api"),
    (re.compile(r"(?<![a-z0-9])pyspark(?![a-z0-9])"),            "spark"),
    (re.compile(r"(?<![a-z0-9])postgresql(?![a-z0-9])"),         "postgresql"),
    (re.compile(r"(?<![a-z0-9])postgres(?![a-z0-9])"),           "postgresql"),
    (re.compile(r"(?<![a-z0-9])mysql(?![a-z0-9])"),              "mysql"),
    (re.compile(r"(?<![a-z0-9])mongodb(?![a-z0-9])"),            "mongodb"),
    (re.compile(r"(?<![a-z0-9])fastapi(?![a-z0-9])"),            "fastapi"),
    (re.compile(r"(?<![a-z0-9])graphql(?![a-z0-9])"),            "graphql"),
    (re.compile(r"(?<![a-z0-9])ci\/cd(?![a-z0-9])"),             "ci/cd"),
    (re.compile(r"(?<![a-z0-9])cicd(?![a-z0-9])"),               "ci/cd"),
    (re.compile(r"(?<![a-z0-9])spring\s*boot(?![a-z0-9])"),      "spring boot"),
    (re.compile(r"(?<![a-z0-9])typescript(?![a-z0-9])"),         "typescript"),
    (re.compile(r"(?<![a-z0-9])javascript(?![a-z0-9])"),         "javascript"),
    (re.compile(r"(?<![a-z0-9])html5?(?![a-z0-9])"),             "html"),
    (re.compile(r"(?<![a-z0-9])css3?(?![a-z0-9])"),              "css"),
    (re.compile(r"(?<![a-z0-9])linux(?![a-z0-9])"),              "linux"),
    (re.compile(r"(?<![a-z0-9])github(?![a-z0-9])"),             "github"),
    (re.compile(r"(?<![a-z0-9])gitlab(?![a-z0-9])"),             "gitlab"),
    (re.compile(r"(?<![a-z0-9])langchain(?![a-z0-9])"),          "langchain"),
    (re.compile(r"(?<![a-z0-9])tensorflow(?![a-z0-9])"),         "tensorflow"),
    (re.compile(r"(?<![a-z0-9])pytorch(?![a-z0-9])"),            "pytorch"),
    (re.compile(r"(?<![a-z0-9])numpy(?![a-z0-9])"),              "numpy"),
    (re.compile(r"(?<![a-z0-9])pandas(?![a-z0-9])"),             "pandas"),
    (re.compile(r"(?<![a-z0-9])matplotlib(?![a-z0-9])"),         "matplotlib"),
    (re.compile(r"(?<![a-z0-9])flask(?![a-z0-9])"),              "flask"),
    (re.compile(r"(?<![a-z0-9])django(?![a-z0-9])"),             "django"),
    (re.compile(r"(?<![a-z0-9])kubernetes(?![a-z0-9])"),         "kubernetes"),
    (re.compile(r"(?<![a-z0-9])docker(?![a-z0-9])"),             "docker"),
    (re.compile(r"(?<![a-z0-9])terraform(?![a-z0-9])"),          "terraform"),
    (re.compile(r"(?<![a-z0-9])airflow(?![a-z0-9])"),            "airflow"),
    (re.compile(r"(?<![a-z0-9])kafka(?![a-z0-9])"),              "kafka"),
    (re.compile(r"(?<![a-z0-9])redis(?![a-z0-9])"),              "redis"),
    (re.compile(r"(?<![a-z0-9])elasticsearch(?![a-z0-9])"),      "elasticsearch"),
    (re.compile(r"(?<![a-z0-9])aws(?![a-z0-9])"),                "aws"),
    (re.compile(r"(?<![a-z0-9])gcp(?![a-z0-9])"),                "gcp"),
    (re.compile(r"(?<![a-z0-9])azure(?![a-z0-9])"),              "azure"),
    (re.compile(r"(?<![a-z0-9])flutter(?![a-z0-9])"),            "flutter"),
    (re.compile(r"(?<![a-z0-9])golang(?![a-z0-9])"),             "golang"),
    (re.compile(r"(?<![a-z0-9])kotlin(?![a-z0-9])"),             "kotlin"),
    (re.compile(r"(?<![a-z0-9])swift(?![a-z0-9])"),              "swift"),
    (re.compile(r"(?<![a-z0-9])rust(?![a-z0-9])"),               "rust"),
]


class SkillExtractor:
    """
    Hybrid skill extractor: Regex + Vocabulary + Groq AI.

    Extraction passes (all merged, deduplicated):
    - Pass 0: Special patterns on ORIGINAL text (C++, C#)
    - Pass 1: Special regex patterns on cleaned text
    - Pass 2: Vocabulary matching (greedy, longest-first, ambiguous-safe)
    - Pass 3: Groq AI extraction (if groq_client provided and available)
    """

    def __init__(self, categories_path: str = None, groq_client=None):
        if categories_path is None:
            categories_path = os.path.join(
                os.path.dirname(__file__), "..", "data", "skill_categories.json"
            )
        self.categories: dict[str, list] = load_json(categories_path)
        if not self.categories:
            logger.warning("skill_categories.json missing — extraction will use regex only.")
            self.categories = {}

        self.groq_client = groq_client

        # Build vocabulary: skip single-char entries ("c", "r") — handled by special patterns
        self._vocabulary: list[str] = []
        for cat_skills in self.categories.values():
            for s in cat_skills:
                sl = s.lower().strip()
                if sl and sl not in _AMBIGUOUS_SHORTS and sl not in self._vocabulary:
                    self._vocabulary.append(sl)

        # Longest first for greedy multi-word matching
        self._vocabulary.sort(key=len, reverse=True)
        logger.info(f"SkillExtractor ready: {len(self._vocabulary)} vocab + {len(_CLEANED_TEXT_PATTERNS)} patterns.")

    # ──────────────────────────────────────────────────────────────────────────
    # Public interface
    # ──────────────────────────────────────────────────────────────────────────

    def extract_skills(self, raw_text: str, extra_vocab: list[str] | None = None) -> list[str]:
        """
        Multi-pass skill extraction. Returns deduplicated lowercase skill list.
        """
        if not raw_text or not raw_text.strip():
            return []

        found: set[str] = set()

        # ── Pass 0: original text special patterns (C++, C#, R) ──────────────
        original_lower = raw_text.lower()
        # C++ — check original text with +
        if re.search(r'\bC\+\+', raw_text):
            found.add("c++")
        if re.search(r'\bC#\b', raw_text):
            found.add("c#")
        # R programming language — standalone word in original
        if re.search(r'(?<!\w)R(?!\w)', raw_text):
            # Extra check: make there's context suggesting it's a language
            if re.search(r'\b(?:programming|language|rstudio|tidyverse|ggplot|dplyr)\b', original_lower):
                found.add("r")

        # ── Pass 1: special regex on cleaned text ─────────────────────────────
        cleaned = clean_for_extraction(raw_text)
        for pattern, canonical in _CLEANED_TEXT_PATTERNS:
            if pattern.search(cleaned):
                found.add(canonical)

        # ── Pass 2: vocabulary matching ────────────────────────────────────────
        vocab = list(self._vocabulary)
        if extra_vocab:
            ext = [s.lower().strip() for s in extra_vocab
                   if s and s.lower().strip() not in _AMBIGUOUS_SHORTS]
            for sl in ext:
                if sl not in vocab:
                    vocab.append(sl)
            vocab.sort(key=len, reverse=True)

        for skill in vocab:
            if skill in found:
                continue
            if self._safe_match(skill, cleaned):
                found.add(skill)

        # ── Pass 3: Groq AI extraction (if available) ─────────────────────────
        if self.groq_client and self.groq_client.available:
            ai_skills = self.groq_client.extract_resume_skills(raw_text)
            for s in ai_skills:
                s_clean = s.lower().strip()
                if s_clean and len(s_clean) > 1:  # ignore bare 'c'
                    found.add(s_clean)

        result = sorted(found)
        logger.info(f"Extracted {len(result)} skills total.")
        return result

    def _safe_match(self, skill: str, cleaned_text: str) -> bool:
        """
        Safe word-boundary match that handles special characters properly.

        For single-character skills (that survive ambiguous filter), require
        they be surrounded by whitespace or begin/end of text only.
        """
        if len(skill) <= 2:
            # Very short skills: require strict word boundaries (space/start/end)
            pattern = r'(?:^|\s){}(?:\s|$)'.format(re.escape(skill))
        else:
            # Multi-char skills: standard word-boundary (exclude alphanumeric and +-.)
            escaped = re.escape(skill)
            pattern = r'(?<![a-z0-9\+\-\.]){}(?![a-z0-9\+\-\.])'.format(escaped)
        return bool(re.search(pattern, cleaned_text))

    # ──────────────────────────────────────────────────────────────────────────
    # Vocabulary expansion
    # ──────────────────────────────────────────────────────────────────────────

    def expand_vocabulary(self, new_skills: list[str]) -> int:
        existing = set(self._vocabulary)
        added = 0
        for s in new_skills:
            sl = s.lower().strip()
            if sl and len(sl) > 1 and sl not in existing and sl not in _AMBIGUOUS_SHORTS:
                self._vocabulary.append(sl)
                existing.add(sl)
                added += 1
        if added:
            self._vocabulary.sort(key=len, reverse=True)
        return added

    # ──────────────────────────────────────────────────────────────────────────
    # Category mapping
    # ──────────────────────────────────────────────────────────────────────────

    def get_skill_categories(self, skills: list[str]) -> dict[str, list[str]]:
        skills_lower = {s.lower() for s in skills}
        result: dict[str, list] = {}
        for cat, cat_skills in self.categories.items():
            matched = [cs.lower() for cs in cat_skills if cs.lower() in skills_lower]
            if matched:
                result[cat] = matched
        # Collect uncategorized
        all_cat = {s.lower() for cat in self.categories.values() for s in cat}
        uncategorized = [s for s in skills_lower if s not in all_cat]
        if uncategorized:
            result["Other"] = uncategorized
        return result

    # ──────────────────────────────────────────────────────────────────────────
    # Feature helpers for ML model
    # ──────────────────────────────────────────────────────────────────────────

    def keyword_density(self, raw_text: str) -> float:
        words = raw_text.lower().split()
        if not words:
            return 0.0
        skills = self.extract_skills(raw_text)
        token_count = sum(len(s.split()) for s in skills)
        return round(min(token_count / len(words), 1.0), 4)

    def experience_signal(self, raw_text: str) -> float:
        text_lower = raw_text.lower()
        score = 0.0
        year_matches = re.findall(
            r'(\d+)\+?\s*(?:years?|yrs?)[\s\w]{0,20}(?:experience|exp\b|work)',
            text_lower
        )
        if year_matches:
            score += min(max(int(y) for y in year_matches) / 10.0, 0.6)
        elif re.search(r'\d+\s*(?:years?|yrs?)', text_lower):
            nums = re.findall(r'(\d+)\s*(?:years?|yrs?)', text_lower)
            if nums:
                score += min(max(int(n) for n in nums) / 12.0, 0.4)
        seniority = {
            "intern": 0.0, "junior": 0.05, "associate": 0.08,
            "mid level": 0.1, "senior": 0.2, "lead": 0.25,
            "principal": 0.3, "architect": 0.3, "director": 0.35,
        }
        for term, boost in seniority.items():
            if term in text_lower:
                score = max(score, boost)
        verbs = [
            "led", "built", "architected", "deployed", "optimized",
            "mentored", "published", "scaled", "delivered", "designed",
            "implemented", "created", "launched", "managed",
        ]
        score += min(sum(1 for v in verbs if v in text_lower) * 0.04, 0.25)
        return round(min(score, 1.0), 4)
