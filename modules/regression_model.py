"""
regression_model.py — 5-feature resume suitability scoring.

FIXED: Added input validation. If resume_skills is empty, returns None
instead of silently computing a misleading low score.
"""
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
from modules.logger import logger


class RegressionScoringModel:
    """
    Predicts resume suitability (0–1) using 5 features derived from the analysis.

    Features:
        1. skill_match_ratio    — matching / role skills count
        2. missing_skill_ratio  — 1 - skill_match_ratio
        3. skill_count_norm     — resume skill count normalized 0–1 (max assumed 50)
        4. keyword_density      — tech keyword density in resume text (0–1)
        5. experience_signal    — experience level inferred from text (0–1)
    """

    SKILL_COUNT_MAX = 50

    def __init__(self):
        self.model = LinearRegression()
        self.scaler = MinMaxScaler()
        self._train()

    def _train(self):
        """Train on a rich synthetic dataset simulating diverse candidates."""
        X = np.array([
            # [match, missing, skill_norm, kw_density, exp_signal]  → target
            [1.00, 0.00, 0.90, 0.28, 1.00],  # perfect senior
            [0.92, 0.08, 0.85, 0.25, 0.90],  # excellent
            [0.85, 0.15, 0.80, 0.22, 0.80],  # very good
            [0.78, 0.22, 0.70, 0.19, 0.70],  # good senior
            [0.72, 0.28, 0.65, 0.17, 0.60],  # solid mid
            [0.65, 0.35, 0.55, 0.15, 0.50],  # decent mid
            [0.58, 0.42, 0.45, 0.12, 0.40],  # average
            [0.50, 0.50, 0.40, 0.10, 0.30],  # borderline
            [0.40, 0.60, 0.35, 0.08, 0.20],  # below average
            [0.30, 0.70, 0.25, 0.06, 0.15],  # poor match
            [0.20, 0.80, 0.20, 0.04, 0.08],  # very poor
            [0.10, 0.90, 0.12, 0.02, 0.05],  # near zero match
            [0.00, 1.00, 0.08, 0.01, 0.00],  # no match
            [0.88, 0.12, 1.00, 0.30, 0.85],  # many extra skills
            [0.55, 0.45, 0.42, 0.13, 0.05],  # good skills, entry level
            [0.35, 0.65, 0.60, 0.11, 0.78],  # senior but poor match
            [0.70, 0.30, 0.60, 0.18, 0.55],  # competent mid-senior
        ])
        y = np.array([
            1.00, 0.95, 0.88, 0.82, 0.76, 0.68, 0.60,
            0.52, 0.42, 0.32, 0.22, 0.12, 0.04,
            0.92, 0.47, 0.40, 0.74,
        ])
        self.scaler.fit(X)
        self.model.fit(self.scaler.transform(X), y)
        logger.info("RegressionScoringModel trained on 17-sample synthetic dataset.")

    def predict(
        self,
        skill_match_ratio: float,
        missing_skill_ratio: float,
        skill_count: int,
        keyword_density: float,
        experience_signal: float,
        resume_skills: list | None = None,
    ) -> float | None:
        """
        Returns suitability score [0, 1] or None if resume_skills is empty.

        Args:
            resume_skills: Pass the list of extracted resume skills.
                           If empty, None is returned and scoring is aborted.
        """
        # Input validation (Error 5 fix)
        if resume_skills is not None and len(resume_skills) == 0:
            logger.warning("Scoring aborted: resume_skills is empty. Cannot produce a valid score.")
            print("  [!] WARNING: No skills detected in resume. Score cannot be computed reliably.")
            return None

        features = np.array([[
            max(0.0, min(1.0, skill_match_ratio)),
            max(0.0, min(1.0, missing_skill_ratio)),
            min(max(skill_count, 0) / self.SKILL_COUNT_MAX, 1.0),
            max(0.0, min(1.0, keyword_density)),
            max(0.0, min(1.0, experience_signal)),
        ]])
        raw = float(self.model.predict(self.scaler.transform(features))[0])
        score = round(max(0.0, min(1.0, raw)), 3)
        logger.debug(
            f"Score: {score} | match={skill_match_ratio:.2f}, missing={missing_skill_ratio:.2f}, "
            f"n_skills={skill_count}, kw={keyword_density:.3f}, exp={experience_signal:.2f}"
        )
        return score
