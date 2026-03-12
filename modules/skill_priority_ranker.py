"""
skill_priority_ranker.py — Ranks missing skills by importance for the candidate to learn.

Priority formula (user-specified):
    priority = job_importance * 0.5 + learning_speed * 0.3 + market_demand * 0.2

job_importance  : position of skill in role_skills list (first = most important)
learning_speed  : estimated ease of learning (hand-curated + default)
market_demand   : industry demand signal (hand-curated + default)
"""

from modules.logger import logger


# Market demand scores (0–1) — higher = more in-demand in 2024
_MARKET_DEMAND: dict[str, float] = {
    "python": 0.98, "machine learning": 0.97, "deep learning": 0.95,
    "llm": 0.95, "large language models": 0.95, "rag": 0.93,
    "mlops": 0.92, "docker": 0.92, "kubernetes": 0.91, "aws": 0.93,
    "gcp": 0.88, "azure": 0.88, "tensorflow": 0.87, "pytorch": 0.92,
    "sql": 0.90, "spark": 0.82, "kafka": 0.83, "airflow": 0.80,
    "react": 0.88, "typescript": 0.85, "fastapi": 0.82, "ci/cd": 0.84,
    "git": 0.96, "system design": 0.90, "algorithms": 0.85, "nlp": 0.91,
    "langchain": 0.82, "kubernetes": 0.91, "terraform": 0.84,
    "linux": 0.85, "golang": 0.82, "rust": 0.78, "postgresql": 0.84,
    "mongodb": 0.80, "redis": 0.80, "elasticsearch": 0.77,
    "data structures": 0.86, "oop": 0.80, "microservices": 0.86,
    "computer vision": 0.82, "generative ai": 0.93,
}

# Learning speed scores (0–1) — higher = easier / faster to learn
_LEARNING_SPEED: dict[str, float] = {
    "git": 0.95, "html": 0.90, "css": 0.88, "sql": 0.85, "linux": 0.72,
    "bash": 0.70, "python": 0.80, "javascript": 0.72, "react": 0.68,
    "fastapi": 0.78, "flask": 0.82, "django": 0.70, "pandas": 0.78,
    "numpy": 0.78, "matplotlib": 0.82, "docker": 0.72, "scikit-learn": 0.74,
    "postgresql": 0.66, "mongodb": 0.70, "redis": 0.72, "typescript": 0.68,
    "tensorflow": 0.58, "pytorch": 0.58, "kubernetes": 0.48, "spark": 0.55,
    "kafka": 0.52, "machine learning": 0.50, "deep learning": 0.44,
    "system design": 0.40, "algorithms": 0.44, "aws": 0.60, "terraform": 0.55,
    "golang": 0.62, "rust": 0.38, "mlops": 0.50,
}

_DEFAULT_DEMAND = 0.65
_DEFAULT_SPEED = 0.55


class SkillPriorityRanker:
    """Ranks a list of missing skills by learning priority."""

    def rank(
        self,
        missing_skills: list[str],
        role_skills: list[str],
    ) -> list[dict]:
        """
        Returns a list of dicts, sorted by priority (highest first):
            [{skill, priority_score, job_importance, learning_speed, market_demand}]
        """
        role_lower = [s.lower() for s in role_skills]
        n = max(len(role_lower), 1)

        ranked = []
        for skill in missing_skills:
            sl = skill.lower()

            # job_importance: first skill in role list = 1.0, last = 0.3
            try:
                idx = role_lower.index(sl)
                importance = round(1.0 - (idx / n) * 0.7, 4)
            except ValueError:
                importance = 0.5

            speed  = _LEARNING_SPEED.get(sl, _DEFAULT_SPEED)
            demand = _MARKET_DEMAND.get(sl, _DEFAULT_DEMAND)
            priority = round(importance * 0.5 + speed * 0.3 + demand * 0.2, 4)

            ranked.append({
                "skill": skill,
                "priority_score": priority,
                "job_importance": importance,
                "learning_speed": speed,
                "market_demand": demand,
            })

        ranked.sort(key=lambda x: x["priority_score"], reverse=True)
        logger.info(f"Ranked {len(ranked)} missing skills by priority.")
        return ranked
