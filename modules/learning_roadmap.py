class RoadmapGenerator:
    """Generates a learning roadmap for missing skills."""
    
    def __init__(self):
        # Basic mapping for predefined skills
        self.knowledge_base = {
            "tensorflow": {
                "topics": "Learn TensorFlow basics, Tensors, and Sequential Models",
                "practice": "Build a simple neural network for MNIST",
                "project": "Image classifier using CNN"
            },
            "docker": {
                "topics": "Learn Docker fundamentals (Images, Containers, Dockerfile)",
                "practice": "Write a Dockerfile for a basic web app",
                "project": "Containerize a Machine Learning model prediction API"
            },
            "kubernetes": {
                "topics": "Learn Pods, Deployments, and Services",
                "practice": "Deploy a local Minikube cluster",
                "project": "Deploy a microservice-based application"
            },
            "sql": {
                "topics": "Learn standard queries, Joins, Group By, Indexes",
                "practice": "Solve HackerRank SQL problems",
                "project": "Design a relational schema for an e-commerce platform"
            },
            "python": {
                "topics": "Learn Data Types, Functions, OOP, and Modules",
                "practice": "Complete Python crash course exercises",
                "project": "Build a CLI tool or web scraper"
            }
        }
        
    def generate(self, missing_skills: list) -> dict:
        """
        Generate a week-by-week roadmap for the given missing skills.
        """
        roadmap = {}
        for idx, skill in enumerate(missing_skills, start=1):
            s_lower = skill.lower()
            if s_lower in self.knowledge_base:
                info = self.knowledge_base[s_lower]
            else:
                info = {
                    "topics": f"Study the official documentation for {skill}",
                    "practice": f"Complete hands-on tutorials for {skill}",
                    "project": f"Build a small pet project utilizing {skill}"
                }
            roadmap[f"Week {idx} - {skill.capitalize()}"] = info
            
        return roadmap
