import urllib.parse


class ResourceFinder:
    """
    Generates curated free learning resource links for each missing skill.
    No internet calls needed — builds smart URL patterns for well-known platforms.
    """

    # Official documentation URLs for common skills
    _OFFICIAL_DOCS: dict[str, str] = {
        "python": "https://docs.python.org/3/tutorial/",
        "tensorflow": "https://www.tensorflow.org/learn",
        "pytorch": "https://pytorch.org/tutorials/",
        "scikit-learn": "https://scikit-learn.org/stable/getting_started.html",
        "docker": "https://docs.docker.com/get-started/",
        "kubernetes": "https://kubernetes.io/docs/tutorials/",
        "aws": "https://aws.amazon.com/getting-started/",
        "gcp": "https://cloud.google.com/docs",
        "azure": "https://learn.microsoft.com/en-us/azure/",
        "sql": "https://www.w3schools.com/sql/",
        "postgresql": "https://www.postgresql.org/docs/current/tutorial.html",
        "mongodb": "https://www.mongodb.com/docs/manual/tutorial/",
        "react": "https://react.dev/learn",
        "fastapi": "https://fastapi.tiangolo.com/tutorial/",
        "flask": "https://flask.palletsprojects.com/en/latest/quickstart/",
        "django": "https://docs.djangoproject.com/en/stable/intro/tutorial01/",
        "golang": "https://go.dev/tour/welcome/1",
        "rust": "https://doc.rust-lang.org/book/",
        "typescript": "https://www.typescriptlang.org/docs/handbook/intro.html",
        "spark": "https://spark.apache.org/docs/latest/quick-start.html",
        "kafka": "https://kafka.apache.org/quickstart",
        "airflow": "https://airflow.apache.org/docs/apache-airflow/stable/tutorial/index.html",
        "terraform": "https://developer.hashicorp.com/terraform/tutorials",
        "git": "https://git-scm.com/doc",
        "linux": "https://linuxcommand.org/tlcl.php",
        "langchain": "https://python.langchain.com/docs/get_started/introduction",
        "mlflow": "https://mlflow.org/docs/latest/tutorials-and-examples/index.html",
        "wandb": "https://docs.wandb.ai/quickstart",
        "hugging face": "https://huggingface.co/learn/nlp-course/chapter1/1",
        "nlp": "https://huggingface.co/learn/nlp-course/chapter1/1",
        "machine learning": "https://developers.google.com/machine-learning/crash-course",
        "deep learning": "https://d2l.ai/",
        "large language models": "https://github.com/Hannibal046/Awesome-LLM",
        "system design": "https://github.com/donnemartin/system-design-primer",
        "algorithms": "https://neetcode.io/",
        "data structures": "https://visualgo.net/en",
    }

    # GitHub awesome-list repos for each skill
    _GITHUB_REPOS: dict[str, str] = {
        "machine learning": "https://github.com/josephmisiti/awesome-machine-learning",
        "deep learning": "https://github.com/ChristosChristofidis/awesome-deep-learning",
        "python": "https://github.com/vinta/awesome-python",
        "docker": "https://github.com/veggiemonk/awesome-docker",
        "kubernetes": "https://github.com/ramitsurana/awesome-kubernetes",
        "system design": "https://github.com/donnemartin/system-design-primer",
        "nlp": "https://github.com/keon/awesome-nlp",
        "react": "https://github.com/enaqx/awesome-react",
        "golang": "https://github.com/avelino/awesome-go",
        "rust": "https://github.com/rust-unofficial/awesome-rust",
        "aws": "https://github.com/donnemartin/awesome-aws",
        "tensorflow": "https://github.com/jtoy/awesome-tensorflow",
        "pytorch": "https://github.com/bharathgs/Awesome-pytorch-list",
        "large language models": "https://github.com/Hannibal046/Awesome-LLM",
        "mlops": "https://github.com/visenger/awesome-mlops",
        "algorithms": "https://github.com/tayllan/awesome-algorithms",
        "sql": "https://github.com/danhuss/awesome-sql",
    }

    def find_resources(self, missing_skills: list[str]) -> dict[str, dict]:
        """For each missing skill, return a dict of resource links."""
        resources: dict[str, dict] = {}
        for skill in missing_skills:
            skill_lower = skill.lower()
            encoded = urllib.parse.quote_plus(skill)
            resources[skill.title()] = {
                "YouTube": f"https://www.youtube.com/results?search_query={encoded}+tutorial+for+beginners",
                "freeCodeCamp": f"https://www.freecodecamp.org/news/search/?query={encoded}",
                "Official Docs": self._OFFICIAL_DOCS.get(
                    skill_lower,
                    f"https://devdocs.io/search?q={encoded}"
                ),
                "GitHub": self._GITHUB_REPOS.get(
                    skill_lower,
                    f"https://github.com/search?q=awesome+{encoded}&type=repositories"
                ),
                "Roadmap.sh": f"https://roadmap.sh/search?q={encoded}",
            }
        return resources
