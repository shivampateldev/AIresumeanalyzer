"""
personality_analyzer.py — Infers 8 professional competency scores (0–10) from resume text.

Fixed: expanded keyword lists and lowered base floor so realistic resumes
score meaningfully (not just 1.0–2.5/10 for standard resume language).
"""
import re
from modules.logger import logger


class PersonalityAnalyzer:

    _AXES: dict[str, dict] = {
        "Technical Depth": {
            "keywords": [
                "implemented", "architected", "engineered", "built", "optimized",
                "developed", "designed", "coded", "programmed", "deployed",
                "algorithm", "framework", "system", "infrastructure", "backend",
                "pipeline", "api", "database", "scalable", "performance",
                "microservices", "neural", "training", "model", "ml", "ai",
                "automation", "integration", "module", "component", "library",
                "debugging", "refactored", "migrated", "upgraded", "maintained",
                "application", "service", "platform", "tool", "script",
            ],
            "weight": 1.8,
        },
        "Problem Solving": {
            "keywords": [
                "solved", "resolved", "debugged", "diagnosed", "improved",
                "reduced", "fixed", "investigated", "analyzed", "identified",
                "root cause", "bottleneck", "challenge", "troubleshoot",
                "optimized", "refactored", "revamped", "eliminated", "mitigated",
                "enhanced", "increased", "decreased", "efficiency", "performance",
                "issue", "bug", "error", "problem", "solution",
            ],
            "weight": 1.5,
        },
        "Team Collaboration": {
            "keywords": [
                "collaborated", "team", "cross-functional", "pair programming",
                "mentored", "paired", "coordinated", "worked with", "partnered",
                "supported", "agile", "scrum", "sprint", "standup", "review",
                "code review", "peer", "colleague", "stakeholder", "member",
                "group", "together", "joint", "shared", "cooperative",
            ],
            "weight": 1.2,
        },
        "Communication": {
            "keywords": [
                "presented", "documented", "wrote", "reported", "communicated",
                "authored", "published", "blog", "article", "talk", "conference",
                "demo", "explained", "outlined", "proposal", "specification",
                "readme", "wiki", "report", "dashboard", "presentation",
                "stakeholder", "briefed", "discussed", "meeting", "email",
            ],
            "weight": 1.2,
        },
        "Leadership": {
            "keywords": [
                "led", "managed", "directed", "supervised", "coordinated",
                "owned", "spearheaded", "initiated", "founded", "established",
                "hired", "grew", "team lead", "tech lead", "managed team",
                "mentored", "onboarded", "drove", "championed", "guided",
                "influenced", "strategy", "decision", "responsibility",
            ],
            "weight": 1.0,
        },
        "System Design": {
            "keywords": [
                "designed", "architected", "scalable", "microservices", "api",
                "database", "schema", "distributed", "low latency", "high availability",
                "fault tolerant", "load balancing", "caching", "message queue",
                "event driven", "service oriented", "monolith", "modular",
                "rest", "grpc", "kafka", "rabbitmq", "architecture", "design",
                "pattern", "structure", "flow", "infrastructure",
            ],
            "weight": 1.6,
        },
        "Learning Ability": {
            "keywords": [
                "learned", "self-taught", "course", "certification", "studying",
                "research", "paper", "kaggle", "hackathon", "open source",
                "contributed", "blog", "workshop", "bootcamp", "udemy",
                "coursera", "mooc", "self-study", "read", "explored", "practiced",
                "experiment", "prototype", "side project", "personal project",
            ],
            "weight": 1.3,
        },
        "Project Ownership": {
            "keywords": [
                "owned", "delivered", "launched", "deployed", "shipped",
                "end-to-end", "from scratch", "led", "responsible for",
                "maintained", "operated", "production", "live", "released",
                "managed project", "drove", "accountability", "ownership",
                "built", "created", "developed", "implemented", "completed",
                "finished", "achieved", "project", "initiative",
            ],
            "weight": 1.5,
        },
    }

    def analyze(self, resume_text: str) -> dict[str, float]:
        """
        Score 8 competency axes on a 0–10 scale.

        Scoring uses log-scaled normalization so that even 2–3 keyword hits
        produce a meaningful score (3–5/10), and a rich resume can reach 8–10.

        Formula: score = min(log(hit+1) / log(threshold+1) * 10 * weight, 10)
        where threshold = 20% of keyword list (the "full match" calibration point).
        """
        import math
        text_lower = resume_text.lower()
        scores: dict[str, float] = {}

        for axis, config in self._AXES.items():
            keywords = config["keywords"]
            weight   = config["weight"]

            hit_count = 0
            for kw in keywords:
                if len(kw.split()) > 1:
                    if kw in text_lower:
                        hit_count += 1
                else:
                    if re.search(r"\b" + re.escape(kw) + r"\b", text_lower):
                        hit_count += 1

            # Calibrate: a hit rate of 20% of the keyword list = score of 10*weight
            threshold = max(len(keywords) * 0.20, 1)
            raw = math.log(hit_count + 1) / math.log(threshold + 1) * 10.0 * weight
            scores[axis] = round(min(raw, 10.0), 1)

        logger.info(f"PersonalityAnalyzer: {scores}")
        return scores
