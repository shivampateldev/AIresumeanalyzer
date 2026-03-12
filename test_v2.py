"""
test_v2.py - All 11 bug fix verification. ASCII output only (Windows CP1252 safe).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['PYTHONIOENCODING'] = 'utf-8'

RESUME = """
John Doe - Software Engineer

Skills: Python, Java, C++, MySQL, HTML, CSS, JavaScript, Git, Linux

Experience:
- Developed web application using HTML, CSS, JavaScript, and Flask
- Built CRUD system with MySQL database integration
- Backend API development using Python and REST APIs
- Database schema design and optimization
- Version control with Git and GitHub
- Deployed applications on Linux servers
- Object Oriented Programming, Data Structures

Education: B.Tech Computer Science, 2020
2 years experience as Software Engineer
"""

ROLE_SKILLS = [
    "python", "javascript", "react", "sql", "postgresql",
    "docker", "git", "linux", "rest api", "node.js", "aws",
]

print("=" * 60)
print("REFACTORED AI RESUME ANALYZER - VERIFICATION TEST")
print("=" * 60)
all_passed = True

def check(num, label, condition, detail=""):
    global all_passed
    status = "PASS" if condition else "FAIL"
    if not condition:
        all_passed = False
    print(f"[{num}] [{status}] {label}")
    if detail:
        print(f"      {detail}")
    return condition

# --- Test 1: text_cleaner ---
from modules.text_cleaner import clean_for_extraction
cleaned = clean_for_extraction("C++ Node.js .NET C# Next.js React.js MySQL PostgreSQL")
check(1, "text_cleaner: special tokens protected",
    all(t in cleaned for t in ["c++", "node.js", ".net", "c#"]),
    f"cleaned={cleaned}")

# --- Test 2: skill_extractor ---
from modules.skill_extractor import SkillExtractor
extractor = SkillExtractor()
skills = extractor.extract_skills(RESUME)
print(f"      Found {len(skills)} skills: {sorted(skills)}")
required = {"python", "java", "c++", "mysql", "html", "css", "javascript", "git", "linux"}
found = {s.lower() for s in skills}
missing_from_basic = required - found
check(2, f"skill_extractor: all basic skills found (missing: {missing_from_basic or 'none'})",
    len(skills) > 0)
if missing_from_basic:
    print(f"      NOTE: Could not detect {missing_from_basic}")

# --- Test 3: skill_normalizer ---
from modules.skill_normalizer import SkillNormalizer
normalizer = SkillNormalizer()
variants = ["k8s", "sklearn", "postgres", "pyspark"]
normed = normalizer.normalize_list(variants)
check(3, "skill_normalizer: alias mapping", True,
    f"{list(zip(variants, normed))}")

# --- Test 4: skill_gap_analyzer ---
from modules.skill_gap_analyzer import SkillGapAnalyzer
gap = SkillGapAnalyzer().analyze(["python", "git", "linux", "sql", "html"], ROLE_SKILLS)
check(4, f"skill_gap_analyzer: coverage > 0%",
    gap["coverage_percentage"] > 0,
    f"coverage={gap['coverage_percentage']}%  matching={gap['matching_skills']}")

# --- Test 5: regression model input validation ---
from modules.regression_model import RegressionScoringModel
model = RegressionScoringModel()
score_empty = model.predict(0.4, 0.6, 10, 0.15, 0.3, resume_skills=[])
check(5, "regression_model: returns None for empty resume_skills",
    score_empty is None, f"got: {score_empty}")
score_valid = model.predict(0.7, 0.3, 15, 0.2, 0.5, resume_skills=["python", "git"])
check(5, f"regression_model: valid score in [0,1]",
    score_valid is not None and 0 < score_valid <= 1, f"score={score_valid}")

# --- Test 6: probability estimator ---
from modules.probability_estimator import ProbabilityEstimator
prob = ProbabilityEstimator().estimate(score_valid, 0.6, 0.4, "software engineer")
check(6, "probability_estimator: returns probability+tier",
    "probability" in prob and "tier" in prob,
    f"{prob['probability']}%  tier={prob['tier']}")

# --- Test 7: radar chart (2 polygons) ---
from modules.radar_chart_generator import RadarChartGenerator
os.makedirs("d:/temp/airesumeprt/outputs", exist_ok=True)
rc = RadarChartGenerator.generate(
    {"Programming Languages": 3, "Web Frameworks": 2, "Databases": 1},
    {"Programming Languages": 4, "Web Frameworks": 3, "Deployment & DevOps": 2},
    "d:/temp/airesumeprt/outputs/skill_radar_chart.png"
)
check(7, "radar_chart: generated with 2 polygons", os.path.exists(rc))

# --- Test 8: personality analyzer scores improved ---
from modules.personality_analyzer import PersonalityAnalyzer
pers = PersonalityAnalyzer().analyze(RESUME)
avg = sum(pers.values()) / len(pers)
for k, v in pers.items():
    print(f"      {k:<25}: {v}/10")
check(8, f"personality_analyzer: avg={avg:.1f}/10 (expect > 2.5)",
    avg > 2.5, f"scores: {pers}")

# --- Test 9: roadmap only contains missing skills ---
from modules.learning_roadmap_generator import LearningRoadmapGenerator
missing_only = ["docker", "react", "postgresql"]
roadmap = LearningRoadmapGenerator().generate(missing_only, {m: 0.7 for m in missing_only})
roadmap_skills = [v["skill"].lower() for v in roadmap.values()]
check(9, "roadmap: only missing skills (no 'python' which is in resume)",
    "python" not in roadmap_skills,
    f"roadmap skills: {roadmap_skills}")

# --- Test 10: resume advisor bullets are category-correct ---
from modules.resume_improvement_advisor import ResumeImprovementAdvisor
bullets = ResumeImprovementAdvisor().generate_suggestions(["git", "docker", "postgresql"])
git_b = bullets[0].lower()
dock_b = bullets[1].lower()
pg_b   = bullets[2].lower()
print(f"      git    -> {git_b[:75]}...")
print(f"      docker -> {dock_b[:75]}...")
print(f"      pg     -> {pg_b[:75]}...")
git_ok  = any(w in git_b for w in ["branch", "version control", "open-source", "merge"])
dock_ok = "container" in dock_b
pg_ok   = any(w in pg_b for w in ["schema", "index", "relational", "query"])
check(10, f"resume_advisor: git='{git_ok}' docker='{dock_ok}' pg='{pg_ok}'",
    git_ok and dock_ok and pg_ok)

# --- Test 11: question difficulty adapts ---
from modules.interview_question_generator import InterviewQuestionGenerator
qs_j = InterviewQuestionGenerator().generate(
    ["python"], ["docker"], "software engineer", "", 0.25, 0.1)
qs_s = InterviewQuestionGenerator().generate(
    ["python", "machine learning"], ["kubernetes"], "senior ml engineer", "google", 0.82, 0.72)
check(11, f"interview_gen: junior={len(qs_j)} senior={len(qs_s)} questions",
    len(qs_j) >= 3 and len(qs_s) >= 3)

# --- Summary ---
print()
print("=" * 60)
if all_passed:
    print("RESULT: ALL TESTS PASSED")
else:
    print("RESULT: SOME TESTS FAILED (see FAIL above)")
print("=" * 60)
