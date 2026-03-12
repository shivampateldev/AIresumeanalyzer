class SkillVectorizer:
    """Converts resume and role skill lists into binary one-hot vectors over a shared universe."""

    def build_vectors(
        self,
        resume_skills: list[str],
        role_skills: list[str],
    ) -> tuple[list[str], list[int], list[int]]:
        """
        Build skill universe = union(resume_skills, role_skills).

        Returns:
            universe   : ordered list of all unique skills
            resume_vec : binary vector over universe
            role_vec   : binary vector over universe
        """
        resume_set = set(s.lower() for s in resume_skills)
        role_set = set(s.lower() for s in role_skills)

        # Universe: role skills first (priority), then extra resume skills
        universe: list[str] = []
        seen = set()
        for s in role_skills:
            key = s.lower()
            if key not in seen:
                universe.append(key)
                seen.add(key)
        for s in resume_skills:
            key = s.lower()
            if key not in seen:
                universe.append(key)
                seen.add(key)

        resume_vec = [1 if s in resume_set else 0 for s in universe]
        role_vec = [1 if s in role_set else 0 for s in universe]

        return universe, resume_vec, role_vec

    def similarity_score(self, resume_vec: list[int], role_vec: list[int]) -> float:
        """Cosine similarity between two binary vectors."""
        import math
        dot = sum(a * b for a, b in zip(resume_vec, role_vec))
        mag_r = math.sqrt(sum(a * a for a in resume_vec)) or 1e-9
        mag_j = math.sqrt(sum(b * b for b in role_vec)) or 1e-9
        return round(dot / (mag_r * mag_j), 4)
