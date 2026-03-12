"""Functional E2E test for AI Resume Intelligence Analyzer."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")

RESUME = (
    "Software Engineer with 4 years of experience. "
    "Proficient in Python, pandas, numpy, SQL, scikit-learn, and machine learning. "
    "Built REST APIs using FastAPI and Flask. Used Git and Linux daily. "
    "Deployed applications using Docker. Familiar with AWS basics. "
    "Worked in agile scrum teams on data analysis projects."
)

ROLE_SKILLS = [
    "python", "tensorflow", "pytorch", "docker", "kubernetes",
    "machine learning", "deep learning", "sql", "mlops", "airflow", "spark",
]

print("=" * 50)
print("AI RESUME ANALYZER — FUNCTIONAL TEST")
print("=" * 50)

from modules.skill_extractor import SkillExtractor
from modules.skill_normalizer import SkillNormalizer
from modules.skill_gap_analyzer import SkillGapAnalyzer
from modules.skill_vectorizer import SkillVectorizer
from modules.regression_model import RegressionScoringModel
from modules.probability_estimator import ProbabilityEstimator
from modules.personality_analyzer import PersonalityAnalyzer
from modules.radar_chart_generator import RadarChartGenerator
from modules.spider_chart_generator import SpiderChartGenerator
from modules.learning_roadmap_generator import LearningRoadmapGenerator
from modules.resource_finder import ResourceFinder
from modules.resume_improvement_advisor import ResumeImprovementAdvisor
from modules.interview_question_generator import InterviewQuestionGenerator

extractor = SkillExtractor()
normalizer = SkillNormalizer()

# Step 1: Extract skills
resume_skills = normalizer.normalize_list(extractor.extract_skills(RESUME))
print(f"[1] Resume skills ({len(resume_skills)}): {resume_skills}")

# Step 2: Gap analysis
gap = SkillGapAnalyzer().analyze(resume_skills, ROLE_SKILLS)
print(f"[2] Coverage: {gap['coverage_percentage']}%")
print(f"    Missing ({len(gap['missing_skills'])}): {gap['missing_skills']}")

# Step 3: Vectorize
universe, rv, jv = SkillVectorizer().build_vectors(resume_skills, ROLE_SKILLS)
print(f"[3] Skill universe size: {len(universe)}")

# Step 4: Score
kd = extractor.keyword_density(RESUME)
exp = extractor.experience_signal(RESUME)
score = RegressionScoringModel().predict(
    skill_match_ratio=gap["coverage_percentage"] / 100,
    missing_skill_ratio=len(gap["missing_skills"]) / len(ROLE_SKILLS),
    skill_count=len(resume_skills),
    keyword_density=kd,
    experience_signal=exp,
)
print(f"[4] Score: {score:.3f}  kw_density={kd}  exp_signal={exp}")

# Step 5: Probability
prob = ProbabilityEstimator().estimate(
    score, gap["coverage_percentage"] / 100, exp, "machine learning engineer"
)
print(f"[5] Probability: {prob['probability']}%  Tier: {prob['tier']}")

# Step 6: Personality
pers = PersonalityAnalyzer().analyze(RESUME)
print(f"[6] Personality axes: {list(pers.keys())}")
for k, v in pers.items():
    print(f"    {k}: {v}")

# Step 7: Charts
os.makedirs("d:/temp/airesumeprt/outputs", exist_ok=True)
role_cat = extractor.get_skill_categories(ROLE_SKILLS)
res_cat = extractor.get_skill_categories(resume_skills)
rc = RadarChartGenerator.generate(
    {k: len(v) for k, v in res_cat.items()},
    {k: len(v) for k, v in role_cat.items()},
    "d:/temp/airesumeprt/outputs/skill_radar_chart.png"
)
sc = SpiderChartGenerator.generate(pers, "d:/temp/airesumeprt/outputs/personality_spider_chart.png")
print(f"[7] Charts exist: radar={os.path.exists(rc)}, spider={os.path.exists(sc)}")

# Step 8: Roadmap
roadmap = LearningRoadmapGenerator().generate(gap["missing_skills"][:3], gap["priority_scores"])
print(f"[8] Roadmap weeks: {list(roadmap.keys())}")

# Step 9: Resources
resources = ResourceFinder().find_resources(gap["missing_skills"][:3])
print(f"[9] Resources: {list(resources.keys())}")

# Step 10: Improvements
improvements = ResumeImprovementAdvisor().generate_suggestions(gap["missing_skills"][:3])
print(f"[10] Improvement suggestions: {len(improvements)}")
for imp in improvements:
    print(f"     - {imp[:80]}...")

# Step 11: Questions
questions = InterviewQuestionGenerator().generate(
    resume_skills, gap["missing_skills"][:3], "Machine Learning Engineer", "Google"
)
print(f"[11] Interview questions: {len(questions)}")
for q in questions[:4]:
    print(f"     [{q['type']}] {q['question'][:75]}...")

print()
print("=" * 50)
print("ALL TESTS PASSED")
print("=" * 50)
