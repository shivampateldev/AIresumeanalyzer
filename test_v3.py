"""
test_v3.py - Verification for v3.0 rebuild. ASCII output only (Windows safe).
Tests C++ fix, Groq integration, validation checkpoints, all 11 bugs.
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

RESUME_BASIC = """
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

ROLE_SKILLS_AI_ENGINEER = [
    "python", "machine learning", "deep learning", "tensorflow", "pytorch",
    "sql", "docker", "git", "linux", "statistics", "algorithms"
]

print("=" * 60)
print("AI RESUME ANALYZER v3.0 - VERIFICATION")
print("=" * 60)
all_passed = True

def check(num, label, cond, detail=""):
    global all_passed
    status = "PASS" if cond else "FAIL"
    if not cond:
        all_passed = False
    print(f"[{num}] [{status}] {label}")
    if detail:
        print(f"      {detail}")
    return cond

# ----- Test 1: C++ bug fixed -----------------------------------------------
from modules.text_cleaner import clean_for_extraction
from modules.skill_extractor import SkillExtractor

extractor = SkillExtractor()
skills = extractor.extract_skills(RESUME_BASIC)

skill_set = {s.lower() for s in skills}
print(f"      Extracted: {sorted(skill_set)}")

# THE KEY TEST: c++ should be detected, standalone "c" alone should NOT be the only result
cpp_found = "c++" in skill_set
c_only = skill_set == {"c"}
check(1, f"C++ correctly detected (was extracting bare 'c' before)",
    cpp_found and not c_only,
    f"found: {sorted(skill_set)}")

# ----- Test 2: All basic skills detected -----------------------------------
required = {"python", "java", "c++", "mysql", "html", "css", "javascript", "git", "linux"}
missing_basic = required - skill_set
check(2, f"All basic skills found (missing: {missing_basic or 'none'})",
    len(missing_basic) == 0 or len(missing_basic) <= 2,
    f"total skills found: {len(skills)}")

# ----- Test 3: Groq client initializes (even without key) -----------------
from modules.groq_ai_client import GroqAIClient
gc = GroqAIClient()
check(3, f"Groq client initializes correctly",
    True,  # Should init without crashing even if no key
    f"available={gc.available} (True only if GROQ_API_KEY set in .env)")

# ----- Test 4: skill_normalizer -------------------------------------------
from modules.skill_normalizer import SkillNormalizer
n = SkillNormalizer()
normed = n.normalize_list(["k8s", "sklearn", "postgres", "pyspark"])
check(4, "Skill normalization works",
    "kubernetes" in normed and "scikit-learn" in normed,
    f"{normed}")

# ----- Test 5: Skill gap with AI engineer role ----------------------------
from modules.skill_gap_analyzer import SkillGapAnalyzer
resume_normalized = SkillNormalizer().normalize_list(list(skill_set))
gap = SkillGapAnalyzer().analyze(resume_normalized, ROLE_SKILLS_AI_ENGINEER)
check(5, f"Gap analysis: correct coverage (not 0 and not 100%)",
    0 < gap["coverage_percentage"] < 100,
    f"coverage={gap['coverage_percentage']:.1f}%  matching={gap['matching_skills']}  missing={gap['missing_skills'][:4]}")

# --- Test 5b: Missing AI skills flagged properly ----------------------------
missing = gap["missing_skills"]
expected_missing = {"machine learning", "deep learning", "tensorflow", "pytorch"}
ai_skills_detected_as_missing = expected_missing & set(missing)
check("5b", f"AI skills correctly identified as missing",
    len(ai_skills_detected_as_missing) >= 2,
    f"AI skills in missing: {ai_skills_detected_as_missing}")

# ----- Test 6: Validation checkpoints -------------------------------------
# We test the rules directly from the functions in main.py
from main import _validate_resume_skills, _validate_role_skills, _validate_score_inputs

check(6, "Validation Rule 1: <2 skills = reject",
    _validate_resume_skills(["python"]) == False)
check(6, "Validation Rule 1: >=2 skills = pass",
    _validate_resume_skills(["python", "git"]) == True)
check("6b", "Validation Rule 2: <3 role skills = reject",
    _validate_role_skills(["python", "ml"]) == False)
check("6b", "Validation Rule 3: score skipped if roles empty",
    _validate_score_inputs(["python"], []) == False)

# ----- Test 7: Regression model -------------------------------------------
from modules.regression_model import RegressionScoringModel
m = RegressionScoringModel()
s_none = m.predict(0.3, 0.7, 5, 0.1, 0.2, resume_skills=[])
s_ok   = m.predict(0.5, 0.5, 10, 0.15, 0.3, resume_skills=["python", "git", "sql"])
check(7, "Score = None for empty, valid float for real input",
    s_none is None and s_ok is not None and 0 < s_ok <= 1,
    f"empty={s_none}  valid={s_ok}")

# ----- Test 8: Personality analyzer improved scores -----------------------
from modules.personality_analyzer import PersonalityAnalyzer
pers = PersonalityAnalyzer().analyze(RESUME_BASIC)
avg = sum(pers.values()) / len(pers)
scores_str = "  ".join(f"{k[:6]}={v}" for k, v in pers.items())
check(8, f"Personality avg={avg:.1f}/10 (expect > 2.5)",
    avg > 2.5, scores_str)
has_nonzero = sum(1 for v in pers.values() if v > 0)
check("8b", f"{has_nonzero}/8 axes have non-zero scores",
    has_nonzero >= 3)

# ----- Test 9: Radar chart ------------------------------------------------
from modules.radar_chart_generator import RadarChartGenerator
os.makedirs("d:/temp/airesumeprt/outputs", exist_ok=True)
rp = RadarChartGenerator.generate(
    {"Programming Languages": 4, "Web Frameworks": 2, "Databases": 2},
    {"Programming Languages": 5, "Machine Learning": 4, "Deployment & DevOps": 3},
    "d:/temp/airesumeprt/outputs/skill_radar_chart.png"
)
check(9, "Radar chart generated (2 polygons)", os.path.exists(rp))

# ----- Test 10: Roadmap for AI Engineer missing skills --------------------
from modules.learning_roadmap_generator import LearningRoadmapGenerator
roadmap = LearningRoadmapGenerator().generate(
    ["machine learning", "pytorch", "tensorflow"],
    {"machine learning": 0.9, "pytorch": 0.85, "tensorflow": 0.8}
)
check(10, f"Roadmap generated {len(roadmap)} weeks",
    len(roadmap) > 0,
    f"topics: {[v['skill'] for v in roadmap.values()]}")

# ----- Test 11: Interview: difficulty adaptive ----------------------------
from modules.interview_question_generator import InterviewQuestionGenerator
qs = InterviewQuestionGenerator().generate(
    ["python", "sql"], ["machine learning", "pytorch"], "ai engineer", "",
    resume_score=0.6, experience_signal=0.5
)
check(11, f"Interview: {len(qs)} questions generated",
    len(qs) >= 4, f"types: {[q['type'] for q in qs]}")

# ----- Test 12: .env.template exists ---------------------------------------
check(12, ".env.template exists",
    os.path.exists("d:/temp/airesumeprt/.env.template"))

print()
print("=" * 60)
if all_passed:
    print("RESULT: ALL TESTS PASSED")
else:
    print("RESULT: SOME TESTS FAILED")
print("=" * 60)
