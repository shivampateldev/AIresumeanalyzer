"""
internet_job_scraper.py — Multi-source scraper with Groq AI fallback.

Strategy:
  1. DuckDuckGo HTML search → extract SNIPPETS first (fast)
  2. Fetch top-3 page bodies for more detail  
  3. If internet fails → Groq AI role skill discovery
  4. If Groq also fails → return empty list (caller handles)
  5. Cache results 24h
"""
import re
import time
import random
import urllib.parse

import requests
from bs4 import BeautifulSoup
from collections import Counter

from modules.text_cleaner import clean_for_extraction
from modules.cache_manager import CacheManager
from modules.logger import logger

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
]

_TIMEOUT = 12
_SKIP_BODY_DOMAINS = [
    "linkedin.com", "glassdoor.com", "indeed.com/viewjob",
    "monster.com", "ziprecruiter.com",
]

_COMPANY_STACK: dict[str, list[str]] = {
    "google":     ["gcp", "tensorflow", "kubernetes", "golang", "bigquery", "vertex ai"],
    "microsoft":  ["azure", "c#", ".net", "typescript", "azure ml", "cosmos db"],
    "amazon":     ["aws", "java", "dynamodb", "s3", "lambda", "sagemaker", "redshift"],
    "meta":       ["pytorch", "react", "graphql", "python", "rocksdb"],
    "apple":      ["swift", "objective-c", "core ml", "xcode", "ios"],
    "netflix":    ["java", "spark", "kafka", "aws", "python", "elasticsearch"],
    "openai":     ["python", "pytorch", "kubernetes", "azure", "cuda", "rust"],
    "nvidia":     ["cuda", "c++", "python", "pytorch", "tensorflow"],
    "databricks": ["spark", "mlflow", "python", "scala", "sql"],
    "snowflake":  ["sql", "python", "spark", "dbt"],
    "stripe":     ["python", "ruby", "java", "postgresql", "kafka", "aws"],
}


class InternetJobScraper:

    def __init__(self, skill_extractor=None, groq_client=None):
        self.cache = CacheManager()
        self._extractor = skill_extractor
        self._groq = groq_client

    def fetch_skills(self, role: str, company: str = "") -> tuple[list[str], bool]:
        """
        Returns (skills_list, internet_used_bool).
        Order of attempts:
          1. Cache
          2. DuckDuckGo scraping
          3. Groq AI fallback
        """
        # 1. Cache
        cached = self.cache.get(role, company)
        if cached:
            print(f"  [Cache] Using cached skills for '{role}'.")
            return cached, True

        # 2. Internet scraping
        skills, ok = self._try_internet_scraping(role, company)
        if ok and len(skills) >= 3:
            self.cache.set(role, company, skills)
            return skills, True

        # 3. Groq AI fallback
        if self._groq and self._groq.available:
            print(f"  [Groq] Internet unavailable — using AI for role skill discovery...")
            ai_skills = self._groq.get_role_skills(role, company)
            if ai_skills:
                # Apply company bias on top of Groq results
                ai_skills = self._apply_company_bias(ai_skills, company)
                logger.info(f"Groq provided {len(ai_skills)} role skills for '{role}'.")
                self.cache.set(role, company, ai_skills)
                return ai_skills, True  # True because AI provided valid data

        logger.warning(f"Both internet and Groq failed for role '{role}'.")
        return [], False

    def _try_internet_scraping(self, role: str, company: str) -> tuple[list[str], bool]:
        """Attempt DuckDuckGo scraping. Returns (skills, success_bool)."""
        queries = self._build_queries(role, company)
        skill_counter: Counter = Counter()
        internet_ok = False

        for query in queries[:4]:  # limit to 4 queries for speed
            snippets, urls = self._duckduckgo_snippets_and_urls(query)
            if snippets:
                internet_ok = True
                for text in snippets:
                    for sk in self._extract(text):
                        skill_counter[sk] += 2  # snippets weighted x2

            for url in urls[:2]:  # 2 pages per query max
                body = self._fetch_body(url)
                if body:
                    for sk in self._extract(body):
                        skill_counter[sk] += 1

            time.sleep(0.3)

        if skill_counter and internet_ok:
            ranked = self._apply_company_bias(
                [sk for sk, _ in skill_counter.most_common(25)], company
            )
            print(f"  [Web] Found {len(ranked)} skills online for '{role}'.")
            return ranked, True

        return [], False

    def _build_queries(self, role: str, company: str) -> list[str]:
        queries = [
            f"skills required for {role} job",
            f"top technical skills {role} 2024",
            f"{role} job description requirements",
            f"how to become {role} skills needed",
        ]
        if company:
            queries.insert(0, f"{company} {role} tech stack requirements")
        return queries

    def _apply_company_bias(self, skills: list[str], company: str) -> list[str]:
        company_lower = company.lower() if company else ""
        bias_skills = []
        for comp, comp_skills in _COMPANY_STACK.items():
            if comp in company_lower:
                bias_skills = [s.lower() for s in comp_skills]
                break
        if bias_skills:
            # Prepend company-specific skills not already in list
            existing = set(skills)
            for bs in bias_skills:
                if bs not in existing:
                    skills = [bs] + skills
        return skills[:25]

    def _duckduckgo_snippets_and_urls(self, query: str) -> tuple[list[str], list[str]]:
        encoded = urllib.parse.quote_plus(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded}"
        headers = {
            "User-Agent": random.choice(_USER_AGENTS),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml",
        }
        snippets: list[str] = []
        urls: list[str] = []
        try:
            resp = requests.get(url, headers=headers, timeout=_TIMEOUT)
            if resp.status_code != 200:
                logger.debug(f"DDG HTTP {resp.status_code} for '{query}'")
                return snippets, urls
            soup = BeautifulSoup(resp.text, "html.parser")
            for div in soup.select(".result__snippet")[:8]:
                txt = div.get_text(separator=" ").strip()
                if txt:
                    snippets.append(txt)
            for div in soup.select(".result__title")[:8]:
                txt = div.get_text(separator=" ").strip()
                if txt:
                    snippets.append(txt)
            for a in soup.select("a.result__url")[:6]:
                href = a.get("href", "").strip()
                if href.startswith("http"):
                    urls.append(href)
                elif href:
                    urls.append("https://" + href)
            if not urls:
                for a in soup.find_all("a", href=True):
                    h = a["href"]
                    if h.startswith("http") and "duckduckgo" not in h:
                        urls.append(h)
                    if len(urls) >= 6:
                        break
            logger.debug(f"DDG '{query}': {len(snippets)} snippets, {len(urls)} URLs")
        except Exception as e:
            logger.warning(f"DDG request failed for '{query}': {e}")
        return snippets, urls

    def _fetch_body(self, url: str) -> str:
        if any(b in url for b in _SKIP_BODY_DOMAINS):
            return ""
        headers = {"User-Agent": random.choice(_USER_AGENTS)}
        try:
            resp = requests.get(url, headers=headers, timeout=_TIMEOUT, allow_redirects=True)
            if resp.status_code != 200:
                return ""
            if "text/html" not in resp.headers.get("Content-Type", ""):
                return ""
            soup = BeautifulSoup(resp.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()
            return soup.get_text(separator=" ")[:5000]
        except Exception as e:
            logger.debug(f"Body fetch failed for {url}: {e}")
            return ""

    def _extract(self, text: str) -> list[str]:
        if self._extractor:
            return self._extractor.extract_skills(text)
        # Minimal fallback without extractor
        import os
        from modules.utils import load_json
        cats_path = os.path.join(os.path.dirname(__file__), "..", "data", "skill_categories.json")
        cats = load_json(cats_path)
        vocab = [s.lower() for skills in cats.values() for s in skills if len(s) > 2]
        cleaned = clean_for_extraction(text)
        found = []
        for s in vocab:
            pat = r'(?<![a-z0-9]){}(?![a-z0-9])'.format(re.escape(s))
            if re.search(pat, cleaned):
                found.append(s)
        return found
