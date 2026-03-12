"""
skill_gap_analyzer.py — Computes the gap between resume skills and role requirements.
"""
from modules.logger import logger


class SkillGapAnalyzer:
    """
    Analyzes gap between resume skills and role skills.
    All comparisons are done at lowercase canonical level.
    """

    def analyze(self, resume_skills: list[str], role_skills: list[str]) -> dict:
        """
        Returns:
            matching_skills   : skills in both resume and role
            missing_skills    : skills in role but NOT in resume
            extra_skills      : skills in resume but NOT required by role
            coverage_percentage: (matching / role_total) * 100
        """
        if not role_skills:
            logger.warning("SkillGapAnalyzer: role_skills is empty.")
            return {
                "matching_skills": [],
                "missing_skills": [],
                "extra_skills": list(resume_skills),
                "coverage_percentage": 0.0,
            }

        resume_set = {s.lower().strip() for s in resume_skills if s}
        role_set   = {s.lower().strip() for s in role_skills  if s}

        matching = sorted(resume_set & role_set)
        missing  = sorted(role_set - resume_set)
        extra    = sorted(resume_set - role_set)

        coverage = round(len(matching) / len(role_set) * 100, 2)

        logger.info(
            f"Gap: matching={len(matching)}, missing={len(missing)}, "
            f"extra={len(extra)}, coverage={coverage}%"
        )

        return {
            "matching_skills": matching,
            "missing_skills": missing,
            "extra_skills": extra,
            "coverage_percentage": coverage,
        }
