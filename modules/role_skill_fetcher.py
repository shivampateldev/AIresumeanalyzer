import os
import requests
from bs4 import BeautifulSoup
from modules.utils import load_json
from modules.skill_extractor import SkillExtractor

class RoleSkillFetcher:
    """Fetches role skills from the internet or fallbacks to local dataset."""
    
    def __init__(self, fallback_path: str = "data/fallback_role_skills.json"):
        full_path = os.path.join(os.path.dirname(__file__), "..", fallback_path)
        self.fallback_skills = load_json(full_path)
        self.skill_extractor = SkillExtractor()
        
        # Simple company bias dictionary
        self.company_stack = {
            "google": ["gcp", "tensorflow", "kubernetes", "golang"],
            "microsoft": ["azure", "c#", ".net", "typescript"],
            "amazon": ["aws", "java", "dynamodb"],
            "meta": ["react", "pytorch", "php", "graphql"],
            "apple": ["swift", "objective-c", "ios"]
        }

    def fetch_skills(self, role: str, company: str = "") -> list:
        """
        Attempt to scrape skills for the given role.
        Fallback to local dataset if scraping fails.
        """
        role_lower = role.lower()
        company_lower = company.lower() if company else ""
        skills = []
        
        # 1. Try to scrape (Simulated attempt for demonstration)
        # In a real-world scenario, you would query a specific job board URL.
        # Here we attempt to fetch a Wikipedia page as a proxy for "the internet".
        try:
            search_query = role.replace(" ", "_")
            url = f"https://en.wikipedia.org/wiki/{search_query}"
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                text = soup.get_text()
                scraped_skills = self.skill_extractor.extract_skills(text)
                if scraped_skills:
                    skills.extend(scraped_skills)
        except Exception as e:
            # Silently fail and use fallback
            pass
            
        # 2. Fallback if scrape yielded nothing or failed
        if not skills:
            # Check for exact match or partial match in fallback dataset
            matched_fallback = False
            for fallback_role, fallback_reqs in self.fallback_skills.items():
                if fallback_role in role_lower or role_lower in fallback_role:
                    skills.extend(fallback_reqs)
                    matched_fallback = True
                    break
            
            # If still no match, provide generic baseline skills
            if not matched_fallback:
                skills.extend(["python", "sql", "git"])
                
        # 3. Apply company bias if company is provided
        if company_lower in self.company_stack:
            skills.extend(self.company_stack[company_lower])
            
        # Remove duplicates
        return list(set(skills))
