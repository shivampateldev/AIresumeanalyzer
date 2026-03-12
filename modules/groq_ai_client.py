"""
groq_ai_client.py — Groq AI integration for hybrid skill extraction and role discovery.

Models (in priority order):
  1. llama-3.3-70b-versatile  (primary — best quality, current)
  2. llama-3.1-8b-instant      (fallback — fast, lightweight)

API key loaded from:
  1. GROQ_API_KEY environment variable (including PowerShell $env: set)
  2. .env file in project root
"""
import os
import json
import re
from modules.logger import logger

try:
    from groq import Groq
    _GROQ_AVAILABLE = True
except ImportError:
    _GROQ_AVAILABLE = False

# Models in priority order — first is tried first, second is fallback
_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
]
_TIMEOUT = 25


def _get_api_key() -> str | None:
    """Get Groq API key from environment variable or .env file."""
    # 1. Environment variable (works with $env:GROQ_API_KEY in PowerShell)
    key = os.environ.get("GROQ_API_KEY", "").strip()
    if key and key != "your_groq_api_key_here":
        return key
    # 2. .env file
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("GROQ_API_KEY="):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val and val != "your_groq_api_key_here":
                        return val
    return None


def _parse_json_list(text: str) -> list[str]:
    """Extract JSON array from LLM response (which may include prose)."""
    # Try to find the first JSON array
    match = re.search(r'\[.*?\]', text, re.DOTALL)
    if match:
        try:
            result = json.loads(match.group())
            if isinstance(result, list):
                return [str(s).lower().strip() for s in result if s and str(s).strip()]
        except json.JSONDecodeError:
            pass
    # Fallback: split by commas/newlines and clean up
    cleaned = text.replace('[', '').replace(']', '').replace('"', '').replace("'", '')
    items = [item.strip().lower() for item in re.split(r'[,\n]', cleaned) if item.strip()]
    # Filter out non-skill garbage (long sentences, single letters like 'a')
    return [s for s in items[:30] if 1 < len(s) <= 50]


class GroqAIClient:
    """
    Groq AI client — wraps llama-3.3-70b-versatile with llama-3.1-8b-instant fallback.

    Two functions:
      extract_resume_skills(text) → list of skills from resume
      get_role_skills(role, company) → list of required skills for a role
    """

    def __init__(self):
        self.api_key = _get_api_key()
        self.available = False
        self.client = None
        self.active_model = None

        if not _GROQ_AVAILABLE:
            logger.warning("groq package not installed. Run: pip install groq")
            return
        if not self.api_key:
            logger.warning("GROQ_API_KEY not found. Set env var or create .env file.")
            return

        try:
            self.client = Groq(api_key=self.api_key)
            # Verify connectivity by checking which model responds
            self.active_model = _MODELS[0]
            self.available = True
            logger.info(f"Groq AI ready. Primary model: {self.active_model}")
        except Exception as e:
            logger.warning(f"Groq client init failed: {e}")

    def _call(self, prompt: str, temperature: float = 0.1, max_tokens: int = 600) -> str:
        """
        Make a Groq API call, trying models in priority order.
        Returns raw response text or empty string on total failure.
        """
        for model in _MODELS:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=_TIMEOUT,
                )
                if model != self.active_model:
                    logger.info(f"Groq: switched to fallback model {model}")
                    self.active_model = model
                return response.choices[0].message.content.strip()
            except Exception as e:
                err_str = str(e)
                if "decommissioned" in err_str.lower() or "not found" in err_str.lower():
                    logger.warning(f"Model {model} unavailable: {e}. Trying next model...")
                    continue
                elif "rate_limit" in err_str.lower():
                    logger.warning(f"Groq rate limited. Waiting briefly...")
                    import time; time.sleep(2)
                    continue
                else:
                    logger.warning(f"Groq API error with {model}: {e}")
                    break
        return ""

    def extract_resume_skills(self, resume_text: str) -> list[str]:
        """
        Extract all technical skills from resume text via LLM.
        Returns lowercase skill list or [] on failure.
        """
        if not self.available:
            return []

        prompt = f"""You are a senior technical recruiter AI. Extract ALL technical skills mentioned in this resume.

IMPORTANT rules:
- Include programming languages (Python, Java, C++, C#, JavaScript, etc.)
- Include frameworks and libraries (React, Django, PyTorch, TensorFlow, etc.)
- Include databases (MySQL, PostgreSQL, MongoDB, Redis, etc.)
- Include cloud platforms and tools (AWS, Azure, GCP, Docker, Kubernetes, Git, etc.)
- Include methodologies (Machine Learning, Deep Learning, NLP, Agile, CI/CD, etc.)
- Preserve exact names: C++, C#, .NET, Node.js, Next.js
- Return ONLY a valid JSON array with no extra text
- Use lowercase except for proper nouns (C++, C#)

Resume text:
{resume_text[:4000]}

JSON array:"""

        raw = self._call(prompt, temperature=0.05, max_tokens=600)
        if not raw:
            return []
        skills = _parse_json_list(raw)
        logger.info(f"Groq resume extraction: {len(skills)} skills → {skills[:8]}")
        return skills

    def get_role_skills(self, role: str, company: str = "") -> list[str]:
        """
        Get top required skills for a job role.
        Returns ranked lowercase skill list or [] on failure.
        """
        if not self.available:
            return []

        company_ctx = f" at {company}" if company else ""
        prompt = f"""You are a technical hiring manager in 2025. List the top 20 most important technical skills required for a {role}{company_ctx} position.

IMPORTANT rules:
- Include specific technical skills: programming languages, frameworks, tools, platforms
- Rank them from most critical to least critical for this exact role
- Include both must-have and nice-to-have technical skills
- Return ONLY a valid JSON array with no extra text, no markdown, no explanation

Example format: ["python", "machine learning", "pytorch", "docker", "sql"]

JSON array for {role}:"""

        raw = self._call(prompt, temperature=0.15, max_tokens=500)
        if not raw:
            return []
        skills = _parse_json_list(raw)
        logger.info(f"Groq role skills for '{role}': {skills[:8]}")
        return skills
