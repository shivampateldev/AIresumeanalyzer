"""
interview_question_generator.py — Adaptive interview questions.

FIXED:
- Difficulty adapts based on resume_score + experience_signal
- Junior (score < 0.5) → conceptual fundamentals
- Senior (score >= 0.7) → advanced design / trade-off questions
- Questions are generated for BOTH resume skills (strength) and missing skills (gap test)
"""
import random
from modules.logger import logger


# (junior_questions, senior_questions) per skill
_QUESTION_BANK: dict[str, dict] = {
    "python": {
        "junior": {
            "conceptual": [
                "What is the difference between a list and a tuple in Python?",
                "Explain what a Python decorator is and give a simple example.",
                "What is the difference between `is` and `==` in Python?",
            ],
            "coding": [
                "Write a Python function to check if a string is a palindrome.",
                "Given a list of integers, return the two numbers that sum to a target.",
            ],
        },
        "senior": {
            "conceptual": [
                "Explain Python's GIL and its impact on multi-threaded vs multi-process programs.",
                "What are the trade-offs of using generators vs materializing a list?",
                "How does Python's memory management (reference counting + cyclic GC) work?",
            ],
            "coding": [
                "Implement a thread-safe LRU cache in Python using `functools.lru_cache` vs a manual implementation.",
                "Write an async web scraper using asyncio and aiohttp, with rate limiting.",
            ],
        },
    },
    "machine learning": {
        "junior": {
            "conceptual": [
                "What is the difference between supervised and unsupervised learning?",
                "Explain the bias-variance tradeoff in simple terms.",
                "What is cross-validation and why do we use it?",
            ],
            "scenario": [
                "Your model has 99% training accuracy and 60% test accuracy. What is the issue and how do you fix it?",
            ],
        },
        "senior": {
            "conceptual": [
                "Explain the trade-offs between gradient boosting and neural networks for tabular data.",
                "How does RLHF improve LLM alignment? What are its failure modes?",
                "When would you choose a Bayesian approach over frequentist statistics for model evaluation?",
            ],
            "scenario": [
                "Your ML model performs well offline but degrades in production over 3 months. Design a monitoring and retraining system.",
                "You have 100M training samples but GPU budget for only 1M. Design a data selection strategy.",
            ],
        },
    },
    "deep learning": {
        "junior": {
            "conceptual": [
                "What is a neural network and what is a neuron?",
                "What is dropout regularization and why does it reduce overfitting?",
                "Explain what backpropagation does in simple terms.",
            ],
        },
        "senior": {
            "conceptual": [
                "Explain the vanishing gradient problem and how ResNets, LSTMs, and Layer Norm address it.",
                "What are the trade-offs between batch normalization and layer normalization?",
                "How do you select learning rate schedules for Transformer training (warmup, cosine annealing)?",
            ],
            "scenario": [
                "Your neural network is not converging after 50 epochs. Walk me through your complete debugging process.",
            ],
        },
    },
    "sql": {
        "junior": {
            "conceptual": [
                "What is the difference between INNER JOIN and LEFT JOIN?",
                "Explain what a PRIMARY KEY and FOREIGN KEY are.",
                "What does GROUP BY do and when do you use HAVING vs WHERE?",
            ],
            "coding": [
                "Write a SQL query to find the second highest salary from an employees table.",
            ],
        },
        "senior": {
            "conceptual": [
                "Explain how MVCC (Multi-Version Concurrency Control) works in PostgreSQL.",
                "When would you use a clustered index vs a non-clustered index?",
                "What are window functions? Explain ROW_NUMBER vs RANK vs DENSE_RANK with an example.",
            ],
            "coding": [
                "Write a SQL query using CTEs to find the top 3 customers by revenue per region, excluding customers with < 3 orders.",
            ],
        },
    },
    "docker": {
        "junior": {
            "conceptual": [
                "What is the difference between a Docker Image and a Docker Container?",
                "What does the `EXPOSE` instruction in a Dockerfile do?",
                "What is docker-compose used for?",
            ],
        },
        "senior": {
            "conceptual": [
                "Explain the security implications of running containers as root and how to mitigate them.",
                "What is the difference between COPY and ADD in Dockerfile? When would you use each?",
                "How would you debug a container that keeps restarting with CrashLoopBackOff in Kubernetes?",
            ],
            "scenario": [
                "A Docker container in production is consuming 3× expected memory. Walk me through your diagnostic process.",
            ],
        },
    },
    "kubernetes": {
        "junior": {
            "conceptual": [
                "What is the difference between a Pod and a Deployment in Kubernetes?",
                "What does a Kubernetes Service do?",
            ],
        },
        "senior": {
            "scenario": [
                "Design a zero-downtime blue-green deployment strategy for a stateful Kubernetes application.",
                "Your cluster nodes are consistently hitting 80% memory. How do you diagnose and resolve this?",
            ],
            "conceptual": [
                "Explain the difference between StatefulSet and Deployment. When is each appropriate?",
                "How does Kubernetes handle resource requests vs limits and what happens when a pod exceeds its limit?",
            ],
        },
    },
    "system design": {
        "junior": {
            "conceptual": [
                "What is the difference between horizontal scaling and vertical scaling?",
                "What is a load balancer and why do we use one?",
            ],
        },
        "senior": {
            "scenario": [
                "Design a URL shortener like bit.ly that handles 100M requests/day with < 10ms latency.",
                "Design a real-time collaborative document editor (like Google Docs) supporting 100K concurrent users.",
                "Design a distributed rate limiter that works across multiple data centers.",
            ],
            "conceptual": [
                "Explain CAP theorem. Give a real-world example of a system that explicitly sacrifices availability for consistency.",
                "Compare eventual consistency vs strong consistency. What are the trade-offs for a payment system?",
            ],
        },
    },
    "aws": {
        "junior": {
            "conceptual": [
                "What is the difference between EC2, Lambda, and Fargate?",
                "What is an S3 bucket and what types of data would you store in it?",
            ],
        },
        "senior": {
            "scenario": [
                "Design a cost-optimized AWS architecture for a batch ML training workload with GPU instances.",
                "Your Lambda function is timing out at 15 seconds. What are the possible causes and solutions?",
            ],
            "conceptual": [
                "Explain the differences between SQS, SNS, and EventBridge. When would you use each?",
                "How does AWS IAM policy evaluation work for conflicting Allow and Deny statements?",
            ],
        },
    },
    "nlp": {
        "junior": {
            "conceptual": [
                "What is tokenization and why is it the first step in NLP pipelines?",
                "What is the difference between stemming and lemmatization?",
            ],
        },
        "senior": {
            "conceptual": [
                "Explain the attention mechanism and why it outperformed LSTMs for sequence modelling.",
                "Explain BERT's masked language modelling objective. How does it differ from GPT's causal LM?",
            ],
            "scenario": [
                "Your NER model achieves 92% F1 on your training domain but 55% F1 on a new domain. Design an adaptation strategy.",
            ],
        },
    },
    "large language models": {
        "junior": {
            "conceptual": [
                "What is a large language model and how is it different from a traditional ML model?",
                "What is prompt engineering and why does it matter?",
            ],
        },
        "senior": {
            "conceptual": [
                "Explain the difference between RAG and fine-tuning for domain adaptation. When would you choose each?",
                "What is RLHF and what alignment problems does it solve? What failure modes can it introduce?",
            ],
            "scenario": [
                "Your production LLM is hallucinating on 15% of requests. Design a complete mitigation and evaluation system.",
            ],
        },
    },
    "javascript": {
        "junior": {
            "conceptual": [
                "What is the difference between `var`, `let`, and `const` in JavaScript?",
                "Explain what a Promise is and how it differs from a callback.",
            ],
        },
        "senior": {
            "conceptual": [
                "Explain JavaScript's event loop, call stack, and microtask queue. What is the difference between setTimeout(fn, 0) and queueMicrotask?",
                "What are the pitfalls of using `this` in JavaScript and how do arrow functions address them?",
            ],
        },
    },
    "golang": {
        "junior": {
            "conceptual": [
                "What are goroutines and how are they different from OS threads?",
                "Explain Go's zero value concept.",
            ],
        },
        "senior": {
            "conceptual": [
                "Explain Go's memory model and how channels ensure safe concurrent communication.",
                "What is the difference between a goroutine leak and a memory leak in Go? How do you detect each?",
            ],
        },
    },
}

_BEHAVIORAL = [
    "Tell me about a time you had to learn a new technology very quickly to meet a project deadline.",
    "Describe a situation where you disagreed with a technical decision. How did you handle it?",
    "Tell me about your most challenging debugging experience and how you resolved it.",
    "Give an example of a project where you had to balance technical debt vs. delivery speed.",
    "Describe a time when you received critical feedback. How did you respond and what did you change?",
]


class InterviewQuestionGenerator:

    def generate(
        self,
        resume_skills: list[str],
        missing_skills: list[str],
        role: str,
        company: str = "",
        resume_score: float = 0.5,
        experience_signal: float = 0.3,
    ) -> list[dict]:
        """
        Generate role-specific, experience-adapted interview questions.

        Difficulty is adapted based on resume_score + experience_signal:
        - Junior  : score < 0.5 or experience < 0.3
        - Senior  : score >= 0.7 and experience >= 0.5
        - Mid     : everything in between
        """
        # Determine difficulty tier
        combined = (resume_score * 0.6) + (experience_signal * 0.4)
        if combined >= 0.65:
            difficulty = "senior"
        elif combined >= 0.35:
            difficulty = "mid"
        else:
            difficulty = "junior"

        logger.info(f"Interview difficulty: {difficulty} (combined={combined:.2f})")

        questions: list[dict] = []

        # Opener
        if company:
            questions.append({
                "type": "Behavioral",
                "question": f"Why are you interested in the {role.title()} role at {company.title()}?",
            })
        else:
            questions.append({
                "type": "Behavioral",
                "question": f"Walk me through your background and how it aligns with the {role.title()} role.",
            })

        # Technical questions from resume skills (strengths)
        asked: set[str] = set()
        for skill in resume_skills:
            sl = skill.lower()
            if sl not in _QUESTION_BANK or sl in asked:
                continue
            bank = _QUESTION_BANK[sl]
            tier = "senior" if difficulty == "senior" else "junior"
            t_bank = bank.get(tier, bank.get("junior", {}))
            for qtype in ["conceptual", "coding", "scenario"]:
                qs = t_bank.get(qtype, [])
                if qs:
                    questions.append({"type": qtype.title(), "question": random.choice(qs)})
            asked.add(sl)
            if len(questions) >= 10:
                break

        # Gap questions from missing skills (test if they know)
        for skill in missing_skills[:3]:
            sl = skill.lower()
            if sl not in _QUESTION_BANK or sl in asked:
                continue
            bank = _QUESTION_BANK[sl]
            # Always use junior tier for missing skills (they're expected to be weaker)
            t_bank = bank.get("junior", bank.get("senior", {}))
            qs = t_bank.get("conceptual", [])
            if qs:
                questions.append({
                    "type": "Conceptual",
                    "question": random.choice(qs) + " (Gap area — expected to explore this further)"
                })
            asked.add(sl)

        # Behavioral questions
        for bq in random.sample(_BEHAVIORAL, min(2, len(_BEHAVIORAL))):
            questions.append({"type": "Behavioral", "question": bq})

        # Fallback
        if len(questions) < 5:
            questions.append({
                "type": "Coding",
                "question": "Given an unsorted array, find the pair of numbers summing to a target. Provide the optimal O(n) solution."
            })

        logger.info(f"Generated {len(questions)} interview questions (difficulty={difficulty}).")
        return questions
