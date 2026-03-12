"""
resume_improvement_advisor.py — Generates professional resume bullet points.

FIXED: Bullet templates are now organized by SKILL CATEGORY so:
- Git (DevOps) → version control bullet, NOT "deployment" bullet
- Docker (Deployment) → containerization bullet
- PostgreSQL (Database) → schema optimization bullet
etc.
"""

from modules.logger import logger


# Category → (skill → templates) mapping
_BY_SKILL: dict[str, list[str]] = {

    # ── Deployment & DevOps ───────────────────────────────────────────
    "docker": [
        "Containerized a machine learning inference API using Docker and FastAPI, enabling reproducible deployments across environments.",
        "Authored multi-stage Dockerfiles reducing image size by 70%, improving CI/CD pipeline speed.",
    ],
    "kubernetes": [
        "Deployed and orchestrated a microservices architecture on Kubernetes (EKS) with Horizontal Pod Autoscaling and zero-downtime rollouts.",
        "Wrote Helm charts to package and deploy services across staging and production clusters.",
    ],
    "terraform": [
        "Automated cloud infrastructure provisioning across AWS using Terraform modules, eliminating manual setup and reducing config drift.",
    ],
    "ansible": [
        "Automated server configuration and application deployment across 50+ nodes using Ansible playbooks.",
    ],
    "ci/cd": [
        "Built a GitHub Actions CI/CD pipeline with automated test coverage gates, Docker builds, and zero-downtime deployments.",
    ],
    "jenkins": [
        "Designed and maintained Jenkins pipelines for automated build, test, and deployment of microservices.",
    ],
    "github actions": [
        "Implemented GitHub Actions workflows for automated linting, testing, and Docker image publishing on every pull request.",
    ],

    # ── Cloud ────────────────────────────────────────────────────────
    "aws": [
        "Architected a serverless ML inference pipeline on AWS (Lambda + S3 + SageMaker) processing 10K daily predictions at near-zero cost.",
        "Reduced cloud infrastructure cost by 40% using EC2 Spot Instances and right-sizing recommendations.",
    ],
    "gcp": [
        "Built an end-to-end ML training and serving pipeline on Google Cloud Vertex AI, reducing model deployment time by 60%.",
        "Engineered a real-time analytics dashboard using BigQuery and Looker Studio, serving 50K daily active users.",
    ],
    "azure": [
        "Deployed a production ML model endpoint on Azure ML with automated retraining triggers and data drift monitoring.",
    ],
    "lambda": [
        "Built serverless event-driven APIs using AWS Lambda and API Gateway, achieving sub-50ms response times at scale.",
    ],

    # ── Databases ────────────────────────────────────────────────────
    "postgresql": [
        "Designed and optimized relational schemas using PostgreSQL, implementing advanced indexing strategies that reduced query latency by 65%.",
        "Implemented row-level security and partitioning in PostgreSQL to support a multi-tenant SaaS application.",
    ],
    "mysql": [
        "Optimized MySQL database queries and schema design, reducing page load time by 50% for a high-traffic e-commerce platform.",
    ],
    "mongodb": [
        "Designed a MongoDB document schema with compound indexes for a real-time analytics system handling 1M+ events/day.",
    ],
    "redis": [
        "Implemented Redis caching layer for a REST API, reducing average response time from 300ms to 12ms.",
    ],
    "elasticsearch": [
        "Built a full-text search system using Elasticsearch handling 500K documents with sub-200ms query response.",
    ],
    "sql": [
        "Optimized complex SQL queries using window functions and execution plan analysis, achieving 5× throughput improvement.",
    ],
    "vector database": [
        "Implemented a vector similarity search pipeline using Pinecone for semantic document retrieval in a RAG system.",
    ],

    # ── Git / Version Control ─────────────────────────────────────────
    "git": [
        "Established Git branching strategy (Gitflow) and code review process for a 10-person engineering team, reducing merge conflicts by 80%.",
        "Contributed to multiple open-source repositories via fork, feature branches, and pull requests following conventional commits.",
    ],
    "github": [
        "Maintained public GitHub repositories with comprehensive READMEs, issue templates, and automated CI pipelines attracting 500+ stars.",
    ],

    # ── ML Frameworks ────────────────────────────────────────────────
    "tensorflow": [
        "Trained and deployed a TensorFlow image classification model achieving 94% accuracy on a custom 50K-image dataset.",
        "Implemented a TensorFlow Serving pipeline for real-time model inference with gRPC, handling 1K requests/second.",
    ],
    "pytorch": [
        "Built and fine-tuned a PyTorch BERT model for multi-label text classification achieving 91% micro-F1 score.",
        "Implemented custom PyTorch training loops with mixed-precision (AMP), reducing training time by 40%.",
    ],
    "scikit-learn": [
        "Built a production scikit-learn ML pipeline with custom transformers, cross-validation, and hyperparameter tuning via Optuna.",
    ],
    "xgboost": [
        "Trained an XGBoost ensemble model for churn prediction achieving 0.94 AUC-ROC on a 2M-row customer dataset.",
    ],
    "hugging face": [
        "Fine-tuned a HuggingFace DistilBERT model for domain-specific NER, improving F1 by 15% over the base checkpoint.",
    ],

    # ── Data Tools ───────────────────────────────────────────────────
    "spark": [
        "Developed PySpark ETL pipelines processing 5TB of daily event data with 3× throughput improvement over single-node pandas.",
    ],
    "kafka": [
        "Designed a Kafka-based event streaming pipeline handling 1M messages/day for a real-time anomaly detection system.",
    ],
    "airflow": [
        "Orchestrated a 12-step ML retraining pipeline using Apache Airflow with Slack alerting and automatic retries on failure.",
    ],
    "dbt": [
        "Built dbt data transformation pipelines with 100% test coverage and documentation, enabling self-serve analytics.",
    ],
    "pandas": [
        "Engineered efficient pandas data pipelines for processing 10M+ row datasets with optimized dtypes reducing memory by 70%.",
    ],

    # ── AI / LLM ────────────────────────────────────────────────────
    "langchain": [
        "Built a RAG-based enterprise Q&A system using LangChain and FAISS over 10K internal documents, achieving 89% answer accuracy.",
    ],
    "large language models": [
        "Fine-tuned a Llama-2 7B model on domain-specific data using QLoRA, matching GPT-3.5 performance at 10% of inference cost.",
    ],
    "rag": [
        "Implemented a Retrieval-Augmented Generation pipeline with hybrid dense+sparse retrieval, reducing LLM hallucination rate by 40%.",
    ],
    "nlp": [
        "Developed an NLP pipeline for multi-label text classification using Hugging Face Transformers, achieving 92% micro-F1 score.",
    ],
    "machine learning": [
        "Built an end-to-end machine learning pipeline from feature engineering to model deployment, serving 50K daily predictions.",
    ],
    "deep learning": [
        "Designed and trained deep learning models achieving state-of-the-art results on benchmark datasets, reducing error rate by 22%.",
    ],

    # ── Web Frameworks ────────────────────────────────────────────────
    "fastapi": [
        "Built a production-ready FastAPI REST API with OAuth2 authentication, background tasks, and OpenAPI docs serving 5K RPS.",
    ],
    "react": [
        "Developed a responsive React dashboard with real-time WebSocket updates and Recharts visualizations for 20K daily active users.",
    ],
    "typescript": [
        "Refactored a 20K-line JavaScript codebase to TypeScript strict mode, reducing runtime type errors by 85%.",
    ],
    "django": [
        "Built a multi-tenant SaaS application using Django REST Framework with Celery, Redis, and PostgreSQL serving 10K users.",
    ],

    # ── Software Engineering ─────────────────────────────────────────
    "system design": [
        "Designed a distributed notification service handling 1M events/sec using Redis Pub/Sub, Kafka, and microservices.",
    ],
    "mlops": [
        "Implemented a full MLOps pipeline with MLflow experiment tracking, model registry, and automated canary deployments.",
    ],
    "algorithms": [
        "Solved 200+ LeetCode problems (Medium/Hard) and implemented optimized algorithms reducing time complexity from O(n²) to O(n log n).",
    ],
    "data structures": [
        "Implemented custom data structures (trie, segment tree, union-find) in Python to solve real-world optimization problems.",
    ],
}


class ResumeImprovementAdvisor:
    """Generates professional resume bullet-point suggestions for each missing skill."""

    def generate_suggestions(self, missing_skills: list[str]) -> list[str]:
        suggestions = []
        for skill in missing_skills:
            sl = skill.lower()
            if sl in _BY_SKILL:
                suggestions.append(_BY_SKILL[sl][0])
            else:
                suggestions.append(
                    f"Built and deployed a production-grade system leveraging {skill.title()}, "
                    f"demonstrating hands-on proficiency with its core APIs and best practices."
                )
        logger.info(f"Generated {len(suggestions)} resume improvement suggestions.")
        return suggestions
