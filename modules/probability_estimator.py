import math
from modules.logger import logger


class ProbabilityEstimator:
    """
    Estimates the probability of being shortlisted/selected for a role using a logistic function.

    Inputs:
        resume_score      — from regression model (0–1)
        skill_match_ratio — matching_skills / role_skills (0–1)
        experience_signal — experience level feature (0–1)
        competition_factor — role competition proxy (0–1, higher = more competitive)

    Output:
        probability (0–100 %)
        confidence_band (±% margin)
        tier label (Strong / Competitive / Moderate / Low)
    """

    # Logistic regression coefficients (manually calibrated)
    _a = 3.5   # weight for resume_score
    _b = 2.0   # weight for skill_match_ratio
    _c = 1.2   # weight for experience_signal
    _d = 1.5   # penalty for competition_factor
    _bias = -2.5  # intercept shift to center probabilities realistically

    # Role competition proxies (how competitive a role is to get into)
    _ROLE_COMPETITION: dict[str, float] = {
        "machine learning": 0.85, "data scientist": 0.80, "ai engineer": 0.85,
        "software engineer": 0.75, "backend developer": 0.65, "frontend developer": 0.60,
        "full stack": 0.65, "devops": 0.70, "cloud": 0.68, "data engineer": 0.72,
        "nlp": 0.82, "mlops": 0.78, "product manager": 0.80, "security": 0.65,
        "site reliability": 0.70, "sre": 0.70,
    }

    def estimate(
        self,
        resume_score: float,
        skill_match_ratio: float,
        experience_signal: float,
        role: str = "",
    ) -> dict:
        """Return probability estimate dictionary."""
        competition = self._get_competition(role)

        logit = (
            self._a * resume_score
            + self._b * skill_match_ratio
            + self._c * experience_signal
            - self._d * competition
            + self._bias
        )
        probability = round(1.0 / (1.0 + math.exp(-logit)) * 100, 1)

        # Confidence band: wider when skill_match is further from 0.5
        confidence_margin = round(5.0 + 10.0 * abs(skill_match_ratio - 0.5), 1)
        low = max(0.0, round(probability - confidence_margin, 1))
        high = min(100.0, round(probability + confidence_margin, 1))

        # Tier classification
        if probability >= 70:
            tier = "Strong Candidate"
        elif probability >= 50:
            tier = "Competitive Candidate"
        elif probability >= 30:
            tier = "Moderate Chances"
        else:
            tier = "Low Probability — Skill Gap Too Large"

        logger.info(
            f"Probability estimate: score={resume_score}, match={skill_match_ratio}, "
            f"exp={experience_signal}, competition={competition} → {probability}%"
        )

        return {
            "probability": probability,
            "low": low,
            "high": high,
            "confidence_band": f"{low}% – {high}%",
            "tier": tier,
            "competition_factor": competition,
        }

    def _get_competition(self, role: str) -> float:
        role_lower = role.lower()
        for key, val in self._ROLE_COMPETITION.items():
            if key in role_lower:
                return val
        return 0.70  # default moderate competition
