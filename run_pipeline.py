"""
run_pipeline.py — Automated E2E pipeline runner (no user input required).
Simulates a complete analysis of a sample resume against "AI Engineer" role.
Writes fresh outputs to d:/temp/airesumeprt/outputs/
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Set Groq key if available in env ──────────────────────────────────────────
# (Already set via $env:GROQ_API_KEY in PowerShell)

SAMPLE_RESUME = """
John Doe
Software Engineer | john.doe@email.com | github.com/johndoe

SKILLS
Python, Java, C++, MySQL, HTML, CSS, JavaScript, Git, Linux, Flask

EXPERIENCE
Software Engineer — TechCorp (2022–Present)
- Developed web applications using HTML, CSS, JavaScript and Flask
- Built CRUD APIs with MySQL database integration and query optimization
- Backend API development using Python and REST APIs
- Version control with Git and GitHub across team of 5 engineers
- Deployed applications on Linux servers using Nginx
- Object Oriented Programming, Data Structures, Algorithms

Junior Developer — StartupXYZ (2020–2022)
- Implemented C++ modules for data processing pipeline
- Collaborated with 3-person team using Agile sprints
- Database schema design for customer management system

EDUCATION
B.Tech Computer Science — University of Engineering (2020)
GPA: 8.2/10

PROJECTS
- Resume Analyzer: Python web app using Flask and MySQL
- Sorting Visualizer: JavaScript + HTML canvas animation tool
"""

TARGET_ROLE = "AI Engineer"
COMPANY = ""  # No company → generic role analysis

print("=" * 64)
print("AI RESUME INTELLIGENCE ANALYZER v3.1")
print("Automated E2E Test — AI Engineer Role")
print("=" * 64)

# ── Init modules ──────────────────────────────────────────────────────────────
print("\n[Init] Loading modules...")
from modules.groq_ai_client import GroqAIClient
from modules.skill_extractor import SkillExtractor
from modules.skill_normalizer import SkillNormalizer
from modules.internet_job_scraper import InternetJobScraper
from modules.skill_gap_analyzer import SkillGapAnalyzer
from modules.skill_priority_ranker import SkillPriorityRanker
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
from modules.report_generator import ReportGenerator

groq = GroqAIClient()
print(f"  Groq AI: {'ACTIVE (' + groq.active_model + ')' if groq.available else 'Not configured'}")

extractor  = SkillExtractor(groq_client=groq)
normalizer = SkillNormalizer()
scraper    = InternetJobScraper(skill_extractor=extractor, groq_client=groq)

OUTPUT_DIR  = "d:/temp/airesumeprt/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── STEP 1: Resume parsing ─────────────────────────────────────────────────────
print("\n[1/11] Parsing resume...")
from modules.resume_parser import ResumeParser
resume_text = ResumeParser.extract_text(SAMPLE_RESUME, is_file=False)
word_count  = len(resume_text.split())
print(f"  Extracted {word_count} words")
assert word_count >= 50, f"Parser failure: only {word_count} words"

# ── STEP 2: Skill extraction (hybrid) ──────────────────────────────────────────
print("\n[2/11] Extracting skills (Regex + Vocab + Groq AI)...")
raw_skills    = extractor.extract_skills(resume_text)
resume_skills = normalizer.normalize_list(raw_skills)
print(f"  Found {len(resume_skills)} skills: {resume_skills[:12]}")
if len(resume_skills) < 2:
    print("  ABORT: fewer than 2 skills detected. Cannot analyze.")
    sys.exit(1)

# ── STEP 3: Role skill discovery ───────────────────────────────────────────────
print(f"\n[3/11] Discovering role skills for '{TARGET_ROLE}'...")
role_skills_raw, internet_ok = scraper.fetch_skills(TARGET_ROLE, COMPANY)
role_skills = normalizer.normalize_list(role_skills_raw)
data_source = "Groq AI" if groq.available else "Internet Scraping" if internet_ok else "UNAVAILABLE"
if internet_ok:
    data_source = "Groq AI (+ scraping fallback)" if not internet_ok else "Internet Scraping"
    if groq.available and not internet_ok:
        data_source = "Groq AI"
    elif groq.available:
        data_source = "Internet + Groq AI"
    else:
        data_source = "Internet Scraping"
print(f"  Source: {data_source}  |  {len(role_skills)} role skills found")
print(f"  Role skills: {role_skills[:10]}")

# Expand vocab with role skills, re-extract
if role_skills:
    extractor.expand_vocabulary(role_skills)
    expanded = normalizer.normalize_list(extractor.extract_skills(resume_text, extra_vocab=role_skills))
    if len(expanded) > len(resume_skills):
        resume_skills = expanded
        print(f"  Re-extracted: {len(resume_skills)} skills after vocab expansion")

if len(role_skills) < 3:
    print("  ABORT: fewer than 3 role skills discovered.")
    sys.exit(1)

# ── STEP 4: Skill gap analysis ─────────────────────────────────────────────────
print("\n[4/11] Computing skill gap...")
gap      = SkillGapAnalyzer().analyze(resume_skills, role_skills)
matching = gap["matching_skills"]
missing  = gap["missing_skills"]
extra    = gap["extra_skills"]
coverage = gap["coverage_percentage"]
print(f"  Coverage: {coverage:.1f}%  |  Matching: {len(matching)}  |  Missing: {len(missing)}")
print(f"  Matching: {matching[:6]}")
print(f"  Missing : {missing[:8]}")

ranked_missing = SkillPriorityRanker().rank(missing, role_skills)
ordered_missing = [item["skill"] for item in ranked_missing]

# ── STEP 5: Vectorization ──────────────────────────────────────────────────────
print("\n[5/11] Building skill vectors...")
universe, resume_vec, role_vec = SkillVectorizer().build_vectors(resume_skills, role_skills)

# ── STEP 6: Scoring ────────────────────────────────────────────────────────────
print("\n[6/11] Computing resume score...")
kw_density = extractor.keyword_density(resume_text)
exp_signal = extractor.experience_signal(resume_text)
match_ratio = coverage / 100.0
missing_ratio = len(missing) / max(len(role_skills), 1)

score = RegressionScoringModel().predict(
    skill_match_ratio   = match_ratio,
    missing_skill_ratio = missing_ratio,
    skill_count         = len(resume_skills),
    keyword_density     = kw_density,
    experience_signal   = exp_signal,
    resume_skills       = resume_skills,
)
print(f"  Score: {score:.3f} / 1.000  ({score*100:.1f}%)")

# ── STEP 7: Probability ────────────────────────────────────────────────────────
print("\n[7/11] Estimating interview probability...")
probability = ProbabilityEstimator().estimate(score, match_ratio, exp_signal, TARGET_ROLE)
print(f"  Probability: {probability['probability']}%  [{probability['confidence_band']}]  {probability['tier']}")

# ── STEP 8: Personality ────────────────────────────────────────────────────────
print("\n[8/11] Analyzing professional competencies...")
personality = PersonalityAnalyzer().analyze(resume_text)
for k, v in personality.items():
    bar = "#" * int(v) + "." * (10 - int(v))
    print(f"  {k:<25}: [{bar}] {v}/10")

# ── STEP 9: Charts ─────────────────────────────────────────────────────────────
print("\n[9/11] Generating charts...")
role_cat   = extractor.get_skill_categories(role_skills)
resume_cat = extractor.get_skill_categories(resume_skills)

radar_path = RadarChartGenerator.generate(
    {k: len(v) for k, v in resume_cat.items()},
    {k: len(v) for k, v in role_cat.items()},
    os.path.join(OUTPUT_DIR, "skill_radar_chart.png"),
)
spider_path = SpiderChartGenerator.generate(
    personality,
    os.path.join(OUTPUT_DIR, "personality_spider_chart.png"),
)
print(f"  Radar  -> {radar_path}")
print(f"  Spider -> {spider_path}")

# ── STEP 10: Roadmap + Resources + Improvements + Questions ───────────────────
print("\n[10/11] Generating learning plan and advice...")
roadmap      = LearningRoadmapGenerator().generate(
    ordered_missing[:8],
    {item["skill"]: item["priority_score"] for item in ranked_missing}
)
resources    = ResourceFinder().find_resources(ordered_missing[:6])
improvements = ResumeImprovementAdvisor().generate_suggestions(ordered_missing[:6])
questions    = InterviewQuestionGenerator().generate(
    resume_skills     = resume_skills,
    missing_skills    = ordered_missing[:3],
    role              = TARGET_ROLE,
    company           = COMPANY,
    resume_score      = score,
    experience_signal = exp_signal,
)
print(f"  Roadmap: {len(roadmap)} weeks  |  Questions: {len(questions)}")

# ── STEP 11: Report ────────────────────────────────────────────────────────────
print("\n[11/11] Writing report...")
ReportGenerator.print_report(
    target_role        = TARGET_ROLE,
    company            = COMPANY,
    resume_skills      = resume_skills,
    role_skills        = role_skills,
    matching_skills    = matching,
    missing_skills     = ordered_missing,
    extra_skills       = extra,
    coverage           = coverage,
    score              = score,
    probability        = probability,
    personality_scores = personality,
    radar_chart_path   = radar_path,
    spider_chart_path  = spider_path,
    roadmap            = roadmap,
    resources          = resources,
    improvements       = improvements,
    questions          = questions,
    internet_used      = internet_ok,
    ranked_missing     = ranked_missing,
    output_dir         = OUTPUT_DIR,
)

print("\n" + "=" * 64)
print("PIPELINE COMPLETE - Report saved to outputs/analysis_report.txt")
print("=" * 64)
