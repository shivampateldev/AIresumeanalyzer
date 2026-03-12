"""
test_v4.py - Final verification for all 14 fixes. ASCII output only.
Tests: Groq model fix, PDF parser fix, skill extraction, pipeline validation.
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

RESUME = """
John Doe - Software Engineer

Skills: Python, Java, C++, MySQL, HTML, CSS, JavaScript, Git, Linux

Experience:
- Developed web application using HTML, CSS, JavaScript, and Flask
- Built CRUD system with MySQL database integration
- Backend API development using Python and REST APIs
- Database schema design and query optimization
- Version control with Git and GitHub
- Deployed applications on Linux servers
- Object Oriented Programming, Data Structures

Education: B.Tech Computer Science, 2020
2 years experience as Software Engineer
"""

all_passed = True

def check(label, cond, detail=""):
    global all_passed
    status = "PASS" if cond else "FAIL"
    if not cond:
        all_passed = False
    print(f"  [{status}] {label}")
    if detail:
        print(f"         {detail}")
    return cond

print("=" * 62)
print("AI RESUME ANALYZER v3.1 - FINAL VERIFICATION")
print("=" * 62)

# ── Fix 1: Groq model name (decommissioned -> current) ──────────────────────
print("\n[1] Groq Model & API Key")
from modules.groq_ai_client import GroqAIClient, _MODELS
check("primary model is llama-3.3-70b-versatile",
    _MODELS[0] == "llama-3.3-70b-versatile", f"got: {_MODELS[0]}")
check("fallback model is llama-3.1-8b-instant",
    _MODELS[1] == "llama-3.1-8b-instant", f"got: {_MODELS[1]}")
groq = GroqAIClient()
check(f"Groq client ready (available={groq.available})",
    True)  # init must not crash

if groq.available:
    print("       Testing live Groq API call...")
    role_skills = groq.get_role_skills("AI Engineer")
    check(f"Groq API works: {len(role_skills)} role skills returned",
        len(role_skills) >= 5,
        str(role_skills[:6]))
    resume_skills_ai = groq.extract_resume_skills(RESUME)
    count_py = sum(1 for s in resume_skills_ai if "python" in s)
    check(f"Groq resume extraction: {len(resume_skills_ai)} skills, Python found={count_py>0}",
        len(resume_skills_ai) >= 3,
        str(resume_skills_ai[:8]))
else:
    print("       GROQ_API_KEY not configured — skipping live API tests")

# ── Fix 2: PDF parser — pdfminer first ─────────────────────────────────────
print("\n[2] PDF Parser (pdfminer.six first)")
from modules.resume_parser import ResumeParser
import inspect
src = inspect.getsource(ResumeParser.extract_text)
pdfminer_pos = src.find("_read_pdf_pdfminer")
pypdf2_pos = src.find("_read_pdf_pypdf2")
check("pdfminer called BEFORE PyPDF2 in extract_text",
    pdfminer_pos < pypdf2_pos and pdfminer_pos != -1,
    f"pdfminer at char {pdfminer_pos}, pypdf2 at {pypdf2_pos}")

# Test pasted text parsing
text = ResumeParser.extract_text(RESUME, is_file=False)
wc = len(text.split())
check(f"Pasted text: {wc} words extracted (expect >= 50)",
    wc >= 50, f"word count = {wc}")

# ── Fix 3: Skill extraction ─────────────────────────────────────────────────
print("\n[3] Skill Extraction (Hybrid)")
from modules.skill_extractor import SkillExtractor
extractor = SkillExtractor(groq_client=groq)
skills = extractor.extract_skills(RESUME)
skill_set = {s.lower() for s in skills}
print(f"       Found: {sorted(skill_set)}")
check("C++ detected (not bare 'c')",
    "c++" in skill_set and skill_set != {"c"})
check("Python detected",
    "python" in skill_set)
check("MySQL detected",
    "mysql" in skill_set)
check("JavaScript detected",
    "javascript" in skill_set)
check("Git detected",
    "git" in skill_set)
check("Linux detected",
    "linux" in skill_set)
check("HTML detected",
    "html" in skill_set)
check("Total >= 8 skills found",
    len(skill_set) >= 8, f"found {len(skill_set)}")

# ── Fix 4: Skill gap analysis ───────────────────────────────────────────────
print("\n[4] Skill Gap Analysis")
from modules.skill_gap_analyzer import SkillGapAnalyzer
from modules.skill_normalizer import SkillNormalizer
normalizer = SkillNormalizer()
resume_norm = normalizer.normalize_list(list(skill_set))
role = ["python", "machine learning", "deep learning", "tensorflow", "pytorch",
        "sql", "docker", "git", "linux", "algorithms"]
gap = SkillGapAnalyzer().analyze(resume_norm, role)
check(f"Coverage {gap['coverage_percentage']}% (between 0 and 100, not 100)",
    0 < gap["coverage_percentage"] < 100)
check(f"Missing AI skills identified: {gap['missing_skills'][:4]}",
    any(s in ["machine learning", "deep learning", "pytorch", "tensorflow"]
        for s in gap["missing_skills"]))
check("Matching: git, python, linux found",
    all(s in gap["matching_skills"] for s in ["python", "git", "linux"]))

# ── Fix 5: Validation checkpoints ──────────────────────────────────────────
print("\n[5] Pipeline Validation Checkpoints")
from main import _validate_resume_skills, _validate_role_skills, _validate_score_inputs
check("Rule 1: empty list rejected",
    _validate_resume_skills([]) == False)
check("Rule 1: 1 skill rejected",
    _validate_resume_skills(["python"]) == False)
check("Rule 1: 2 skills pass",
    _validate_resume_skills(["python", "git"]) == True)
check("Rule 2: 2 role skills rejected",
    _validate_role_skills(["python", "ml"]) == False)
check("Rule 2: 3 role skills pass",
    _validate_role_skills(["python", "ml", "docker"]) == True)
check("Rule 3: empty role_skills -> skip scoring",
    _validate_score_inputs(["python"], []) == False)

# ── Fix 6: Scoring ─────────────────────────────────────────────────────────
print("\n[6] Regression Model Scoring")
from modules.regression_model import RegressionScoringModel
model = RegressionScoringModel()
s_none = model.predict(0.3, 0.7, 5, 0.1, 0.2, resume_skills=[])
s_low  = model.predict(0.2, 0.8, 4, 0.05, 0.1, resume_skills=["python"])
s_mid  = model.predict(0.5, 0.5, 12, 0.15, 0.4, resume_skills=["python","git","sql"])
s_high = model.predict(0.85, 0.15, 20, 0.25, 0.8, resume_skills=["python","ml","docker"])
check("Score=None for empty skills",
    s_none is None)
check(f"Low score < 0.5: got {s_low}",
    s_low is not None and s_low < 0.5)
check(f"Mid score 0.3-0.8: got {s_mid}",
    s_mid is not None and 0.3 <= s_mid <= 0.8)
check(f"High score > 0.5: got {s_high}",
    s_high is not None and s_high > 0.5)

# ── Fix 7: Probability estimation ─────────────────────────────────────────
print("\n[7] Probability Estimation")
from modules.probability_estimator import ProbabilityEstimator
p = ProbabilityEstimator().estimate(0.6, 0.5, 0.4, "AI Engineer")
check(f"Probability {p['probability']}% in [0,100]",
    0 <= p["probability"] <= 100)
check(f"Tier classification: '{p['tier']}'",
    isinstance(p["tier"], str) and len(p["tier"]) > 3)
check("Confidence band returned",
    "confidence_band" in p and "%" in p["confidence_band"])

# ── Fix 8: Radar chart ─────────────────────────────────────────────────────
print("\n[8] Radar Chart (2 polygons)")
from modules.radar_chart_generator import RadarChartGenerator
os.makedirs("d:/temp/airesumeprt/outputs", exist_ok=True)
rp = RadarChartGenerator.generate(
    {"Programming Languages": 5, "Web Frameworks": 2, "Databases": 2, "Software Engineering": 1},
    {"Programming Languages": 4, "Machine Learning": 5, "Deployment & DevOps": 3, "Databases": 2},
    "d:/temp/airesumeprt/outputs/skill_radar_chart.png"
)
check("Radar chart file created",
    os.path.exists(rp) and os.path.getsize(rp) > 5000)

# ── Fix 9: Personality analyzer ────────────────────────────────────────────
print("\n[9] Personality Analyzer")
from modules.personality_analyzer import PersonalityAnalyzer
pers = PersonalityAnalyzer().analyze(RESUME)
avg = sum(pers.values()) / len(pers)
nonzero = sum(1 for v in pers.values() if v > 0)
print(f"       Scores: {', '.join(f'{k[:6]}={v}' for k, v in pers.items())}")
check(f"Average {avg:.1f}/10 (expect > 2.5)",
    avg > 2.5)
check(f"{nonzero}/8 axes non-zero (expect >= 3)",
    nonzero >= 3)

# ── Fix 10: Learning roadmap ────────────────────────────────────────────────
print("\n[10] Learning Roadmap")
from modules.learning_roadmap_generator import LearningRoadmapGenerator
roadmap = LearningRoadmapGenerator().generate(
    ["machine learning", "pytorch", "docker"],
    {"machine learning": 0.9, "pytorch": 0.85, "docker": 0.8}
)
roadmap_skills = [v["skill"].lower() for v in roadmap.values()]
check(f"{len(roadmap)} roadmap weeks generated",
    len(roadmap) >= 1)
check("Python (already in resume) NOT in roadmap",
    "python" not in roadmap_skills)
check("Machine learning IS in roadmap",
    "machine learning" in roadmap_skills)

# ── Fix 11: Resume improvement advisor (category-specific) ─────────────────
print("\n[11] Resume Improvement Advisor")
from modules.resume_improvement_advisor import ResumeImprovementAdvisor
bullets = ResumeImprovementAdvisor().generate_suggestions(["git", "docker", "postgresql"])
check("git -> branching/version control bullet",
    any(w in bullets[0].lower() for w in ["branch", "version control", "merge", "open-source"]))
check("docker -> containerization bullet",
    "container" in bullets[1].lower())
check("postgresql -> schema/index bullet",
    any(w in bullets[2].lower() for w in ["schema", "index", "relational", "query"]))

# ── Fix 12: Interview questions (difficulty adaptive) ───────────────────────
print("\n[12] Interview Questions")
from modules.interview_question_generator import InterviewQuestionGenerator
qs_j = InterviewQuestionGenerator().generate(
    ["python", "sql"], ["docker"], "software engineer", "", 0.25, 0.1)
qs_s = InterviewQuestionGenerator().generate(
    ["python", "machine learning"], ["kubernetes"], "ai engineer", "openai", 0.82, 0.72)
check(f"Junior: {len(qs_j)} questions",
    len(qs_j) >= 3)
check(f"Senior: {len(qs_s)} questions",
    len(qs_s) >= 3)

# ── Fix 13: main.py imports cleanly ─────────────────────────────────────────
print("\n[13] main.py syntax check")
import subprocess
r = subprocess.run(["python", "-m", "py_compile", "main.py"],
                   capture_output=True, text=True, cwd="d:/temp/airesumeprt")
check("main.py compiles without syntax errors",
    r.returncode == 0, r.stderr.strip() if r.returncode != 0 else "")

print()
print("=" * 62)
if all_passed:
    print("ALL TESTS PASSED - System v3.1 READY")
else:
    print("SOME TESTS FAILED - see FAIL lines above")
print("=" * 62)
