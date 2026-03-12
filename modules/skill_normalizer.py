"""
skill_normalizer.py — Canonical skill form normalization via alias lookup.
"""
import os
from modules.utils import load_json
from modules.logger import logger


class SkillNormalizer:
    """Maps alias skill variants to their canonical lowercase form."""

    def __init__(self, aliases_path: str = None):
        if aliases_path is None:
            aliases_path = os.path.join(
                os.path.dirname(__file__), "..", "data", "skill_aliases.json"
            )
        raw = load_json(aliases_path)
        self.alias_map: dict[str, str] = {
            k.lower().strip(): v.lower().strip() for k, v in raw.items()
        }
        logger.info(f"SkillNormalizer: {len(self.alias_map)} aliases loaded.")

    def normalize(self, skill: str) -> str:
        """Return canonical form of a single skill."""
        cleaned = skill.lower().strip()
        return self.alias_map.get(cleaned, cleaned)

    def normalize_list(self, skills: list[str]) -> list[str]:
        """Normalize and deduplicate a list of skills, preserving order."""
        seen: set[str] = set()
        result: list[str] = []
        for s in skills:
            canonical = self.normalize(s)
            if canonical and canonical not in seen:
                seen.add(canonical)
                result.append(canonical)
        return result
