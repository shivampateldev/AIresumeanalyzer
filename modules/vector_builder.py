class VectorBuilder:
    """Converts a list of skills into boolean vectors based on a skill universe."""
    
    @staticmethod
    def build_vector(skills: list, skill_universe: list) -> list:
        """
        Given a universe of skills and a specific subset, return a one-hot encoded vector.
        """
        skills_set = set([s.lower() for s in skills])
        universe_lower = [s.lower() for s in skill_universe]
        
        vector = []
        for s in universe_lower:
            if s in skills_set:
                vector.append(1)
            else:
                vector.append(0)
                
        return vector
