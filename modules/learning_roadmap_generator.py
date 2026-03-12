class LearningRoadmapGenerator:
    """
    Generates a week-by-week personalized learning plan for priority-ranked missing skills.
    Topics, practice tasks, and mini-projects are dynamically generated per skill.
    """

    # Curated knowledge base for common skills; others are generated dynamically
    _KB: dict[str, dict] = {
        "tensorflow": {
            "topics": "TensorFlow Basics, Tensors, Keras Sequential API, tf.data pipelines",
            "practice": "Build a digit classifier on MNIST using Keras",
            "project": "Train and export an image classification model with SavedModel format",
        },
        "pytorch": {
            "topics": "Tensors, Autograd, nn.Module, DataLoader, Training loops",
            "practice": "Implement a feedforward neural network on CIFAR-10",
            "project": "Build a custom image segmentation model and export to ONNX",
        },
        "docker": {
            "topics": "Images, Containers, Dockerfile, docker-compose, Volumes, Networking",
            "practice": "Containerize a FastAPI app with multi-stage Dockerfile",
            "project": "Deploy a containerized ML model inference API with health checks",
        },
        "kubernetes": {
            "topics": "Pods, Deployments, Services, ConfigMaps, Ingress, Helm charts",
            "practice": "Deploy a web app on local Minikube cluster",
            "project": "Orchestrate a multi-service ML pipeline with auto-scaling",
        },
        "aws": {
            "topics": "IAM, EC2, S3, Lambda, RDS, VPC, CloudWatch, SageMaker basics",
            "practice": "Deploy a serverless API using Lambda + API Gateway",
            "project": "Build an end-to-end ML pipeline on SageMaker",
        },
        "gcp": {
            "topics": "GCP IAM, Cloud Run, BigQuery, Vertex AI, Cloud Storage, Pub/Sub",
            "practice": "Deploy a containerized app on Cloud Run",
            "project": "Train and serve an ML model using Vertex AI pipelines",
        },
        "azure": {
            "topics": "Azure AD, Azure ML, Azure Blob Storage, Azure Functions, AKS",
            "practice": "Set up an Azure ML workspace and run a training job",
            "project": "Deploy an ML model endpoint on Azure ML with monitoring",
        },
        "mlops": {
            "topics": "Model versioning, MLflow, CI/CD for ML, Model monitoring, Drift detection",
            "practice": "Track experiments with MLflow and register a model",
            "project": "Build a full CI/CD pipeline for an ML model with Evidently AI monitoring",
        },
        "spark": {
            "topics": "RDDs, DataFrames, Spark SQL, SparkML, Structured Streaming",
            "practice": "Process a 10M-row dataset with PySpark DataFrames",
            "project": "Build a real-time streaming analytics pipeline with Kafka + Spark",
        },
        "kafka": {
            "topics": "Topics, Partitions, Producers, Consumers, Consumer Groups, Kafka Streams",
            "practice": "Build a producer-consumer system for log aggregation",
            "project": "Real-time event-driven pipeline with Kafka + Spark Streaming",
        },
        "airflow": {
            "topics": "DAGs, Operators, Hooks, Connections, XCom, task dependencies",
            "practice": "Build a DAG that ETLs data from an API into PostgreSQL",
            "project": "Orchestrate a full ML retraining pipeline with Airflow",
        },
        "sql": {
            "topics": "SELECT, JOINs, GROUP BY, Window Functions, Indexes, Query Optimization",
            "practice": "Solve 20 HackerRank SQL problems (medium and above)",
            "project": "Design a normalized relational schema for an e-commerce platform",
        },
        "postgresql": {
            "topics": "MVCC, Indexes, EXPLAIN ANALYZE, Partitions, Full-text Search, PL/pgSQL",
            "practice": "Optimize a slow query using EXPLAIN ANALYZE",
            "project": "Build a multi-tenant SaaS database schema with row-level security",
        },
        "python": {
            "topics": "OOP, Decorators, Generators, Context managers, Type hints, asyncio",
            "practice": "Build a CLI tool using Click and write pytest unit tests",
            "project": "Build a web scraper with async I/O and store results in SQLite",
        },
        "fastapi": {
            "topics": "Path operations, Pydantic models, Dependency injection, middleware, Auth",
            "practice": "Build a CRUD API for a Todos app with SQLAlchemy + Alembic",
            "project": "Deploy a production FastAPI ML inference service with Docker + NGINX",
        },
        "react": {
            "topics": "JSX, Components, Props/State, Hooks (useState, useEffect), Context API",
            "practice": "Build a weather dashboard consuming a public REST API",
            "project": "Full-stack app with React frontend + FastAPI backend + PostgreSQL",
        },
        "typescript": {
            "topics": "Types, Interfaces, Generics, Enums, Type guards, tsconfig",
            "practice": "Refactor a JavaScript project to TypeScript with strict mode",
            "project": "Build a strongly-typed REST API client with TypeScript",
        },
        "golang": {
            "topics": "Goroutines, Channels, Interfaces, Error handling, Structs, Go modules",
            "practice": "Build a concurrent web scraper using goroutines",
            "project": "Write a high-performance REST API with Go + PostgreSQL",
        },
        "terraform": {
            "topics": "HCL syntax, Providers, Resources, Modules, State management, workspaces",
            "practice": "Provision an EC2 + RDS infrastructure on AWS with Terraform",
            "project": "Write reusable Terraform modules for a multi-environment AWS setup",
        },
        "langchain": {
            "topics": "Chains, Agents, Retrievers, Memory, Prompt templates, LLM integration",
            "practice": "Build a Q&A chatbot over PDF documents using RAG",
            "project": "Build a multi-agent research assistant with tool use and memory",
        },
        "large language models": {
            "topics": "Transformer architecture, Fine-tuning, RLHF, Prompt engineering, RAG",
            "practice": "Fine-tune a DistilBERT model on a custom classification task",
            "project": "Build a domain-specific QA system using RAG + vector database",
        },
        "machine learning": {
            "topics": "Supervised/Unsupervised learning, Feature engineering, Cross-validation, Ensembles",
            "practice": "Complete the Kaggle Titanic challenge end-to-end",
            "project": "Build a production-ready prediction API with scikit-learn + FastAPI",
        },
        "deep learning": {
            "topics": "CNNs, RNNs, LSTMs, Transformers, Backpropagation, Regularization",
            "practice": "Implement a text classifier using an LSTM from scratch",
            "project": "Train a custom object detection model using YOLO on a real dataset",
        },
        "nlp": {
            "topics": "Tokenization, POS tagging, NER, Embeddings, BERT, Text classification",
            "practice": "Build a sentiment analyzer using Hugging Face transformers",
            "project": "Build a multilingual document summarization pipeline",
        },
        "git": {
            "topics": "Branching, Merging, Rebasing, Pull Requests, Cherry-pick, Hooks",
            "practice": "Contribute to an open-source project via fork + PR",
            "project": "Set up a monorepo with git submodules and automated CI hooks",
        },
        "ci/cd": {
            "topics": "GitHub Actions, GitLab CI, Jenkins, Build pipelines, Automated testing",
            "practice": "Create a GitHub Actions workflow that runs tests on every PR",
            "project": "Full CI/CD pipeline for a Dockerized app: test → build → deploy",
        },
        "system design": {
            "topics": "CAP theorem, Load balancing, Databases, Caching, Sharding, Microservices",
            "practice": "Design a URL shortener with scalability analysis",
            "project": "Design a complete system design for a real-time notification service",
        },
    }

    def generate(self, missing_skills: list[str], priority_scores: dict[str, float]) -> dict[str, dict]:
        """Return a week-by-week learning plan keyed by 'Week N–M: SkillName'."""
        roadmap: dict[str, dict] = {}
        week = 1

        for skill in missing_skills:
            skill_key = skill.lower()
            info = self._KB.get(skill_key) or self._auto_generate(skill)
            week_label = f"Week {week}–{week+1}: {skill.title()}"
            roadmap[week_label] = {
                "skill": skill.title(),
                "priority_score": priority_scores.get(skill_key, 0.5),
                "topics": info["topics"],
                "practice": info["practice"],
                "project": info["project"],
            }
            week += 2

        return roadmap

    def _auto_generate(self, skill: str) -> dict:
        """Dynamically generate generic but structured roadmap entries."""
        return {
            "topics": f"Core concepts of {skill.title()}: architecture, fundamentals, and best practices",
            "practice": f"Complete the official {skill.title()} tutorial and at least 3 hands-on exercises",
            "project": f"Build a small end-to-end project that demonstrates practical use of {skill.title()}",
        }
