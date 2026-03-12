import os
import time
from modules.utils import load_json, save_json
from modules.logger import logger


CACHE_TTL_SECONDS = 86400  # 24 hours


class CacheManager:
    """Manages on-disk caching of scraped job role skills to avoid re-scraping on every run."""

    def __init__(self, cache_path: str = None):
        if cache_path is None:
            base = os.path.join(os.path.dirname(__file__), "..")
            cache_path = os.path.join(base, "cache", "role_skill_cache.json")
        self.cache_path = cache_path
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        self._cache = load_json(self.cache_path)

    def _make_key(self, role: str, company: str) -> str:
        key = role.strip().lower()
        if company:
            key += f"__{company.strip().lower()}"
        return key

    def get(self, role: str, company: str = "") -> list | None:
        """Return cached skills if they exist and are not expired."""
        key = self._make_key(role, company)
        entry = self._cache.get(key)
        if not entry:
            return None
        age = time.time() - entry.get("timestamp", 0)
        if age > CACHE_TTL_SECONDS:
            logger.info(f"Cache expired for key '{key}' (age={age:.0f}s). Will re-scrape.")
            del self._cache[key]
            return None
        logger.info(f"Cache HIT for '{key}' ({len(entry['skills'])} skills cached).")
        return entry["skills"]

    def set(self, role: str, company: str, skills: list) -> None:
        """Store scraped skills in cache."""
        key = self._make_key(role, company)
        self._cache[key] = {
            "timestamp": time.time(),
            "skills": skills
        }
        save_json(self.cache_path, self._cache)
        logger.info(f"Cache SET for '{key}' with {len(skills)} skills.")

    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache = {}
        save_json(self.cache_path, self._cache)
