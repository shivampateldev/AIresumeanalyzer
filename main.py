"""
main.py — AI Resume Intelligence Analyzer v3.0
================================================
Hybrid pipeline: Regex + Vocabulary + Groq AI + Internet scraping
All validation checkpoints implemented per spec.

Usage:
    python main.py
"""

import sys
import os

_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from modules.logger import logger
from modules.resume_parser import ResumeParser
from modules.text_cleaner import clean_for_extraction
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

OUTPUT_DIR  = os.path.join(_ROOT, "outputs")
RADAR_PATH  = os.path.join(OUTPUT_DIR, "skill_radar_chart.png")
SPIDER_PATH = os.path.join(OUTPUT_DIR, "personality_spider_chart.png")


# ────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────

def _banner(groq_available: bool):
    print("\n" + "=" * 64)
    print("      AI RESUME INTELLIGENCE ANALYZER  v3.0")
    print("      Hybrid: Regex + Vocabulary + Groq AI + Internet")
    print("=" * 64)
    groq_status = "ACTIVE" if groq_available else "NOT CONFIGURED"
    print(f"  Groq AI ({groq_status}) | Type 'exit' to quit\n")


def _prompt(msg: str) -> str:
    val = input(msg).strip()
    if val.lower() == "exit":
        print("\n  Exiting. Goodbye!")
        sys.exit(0)
    return val


def _abort(reason: str):
    print(f"\n  *** PIPELINE ABORTED ***")
    print(f"  Reason: {reason}")
    print()


# ────────────────────────────────────────────────────────────────────────────
# Pipeline validation checkpoints
# ────────────────────────────────────────────────────────────────────────────

def _validate_resume_skills(skills: list[str]) -> bool:
    """Rule 1: resume must have at least 2 detected skills."""
    if len(skills) < 2:
        _abort("Resume skills < 2. Check resume text contains explicit skill names.")
        print("  Example: Python, SQL, Docker, React, Machine Learning")
        return False
    return True


def _validate_role_skills(skills: list[str]) -> bool:
    """Rule 2: role skills must have at least 3 items."""
    if len(skills) < 3:
        _abort("Role skills < 3. Internet unavailable and Groq AI not configured.")
        print("  To enable Groq AI: add GROQ_API_KEY=your_key to .env file")
        return False
    return True


def _validate_score_inputs(resume_skills: list[str], role_skills: list[str]) -> bool:
    """Rule 3: both skill lists must be non-empty before scoring."""
    if not role_skills:
        print("  [!] Score skipped: role_skills is empty (scoring would be meaningless).")
        return False
    if not resume_skills:
        print("  [!] Score skipped: resume_skills is empty.")
        return False
    return True


# ────────────────────────────────────────────────────────────────────────────
# Main analysis pipeline
# ────────────────────────────────────────────────────────────────────────────

def run_analysis(
    skill_extractor, skill_normalizer, scraper, gap_analyzer,
    priority_ranker, vectorizer, scoring_model, prob_estimator,
    personality_analyzer, roadmap_gen, resource_finder,
    improvement_advisor, question_gen,
) -> None:

    print()
    print("─" * 64)
    print("  STEP 1 — Resume Input")
    print("  Options:")
    print("  • Paste resume text directly (press Enter twice when done)")
    print("  • Enter path to a .pdf or .txt file")
    print("─" * 64)

    first_line = _prompt("  > ")
    is_file = first_line.lower().endswith((".pdf", ".txt"))

    if is_file:
        resume_raw = first_line
    else:
        lines = [first_line]
        print("  (Keep pasting, blank line to finish)")
        while True:
            line = input()
            if not line.strip():
                break
            lines.append(line)
        resume_raw = "\n".join(lines)

    # ── Parse ──────────────────────────────────────────────────────────────
    resume_text = ResumeParser.extract_text(resume_raw, is_file=is_file)
    if not resume_text or len(resume_text.strip()) < 10:
        print("  [!] Could not extract text. Please try again.")
        return

    print(f"\n  [Parsed] {len(resume_text.split())} words extracted from resume.")

    # ── Role & Company ─────────────────────────────────────────────────────
    target_role = _prompt("\n  Target job role (e.g. 'AI Engineer'):\n  > ")
    company     = _prompt("\n  Company name (optional, Enter to skip):\n  > ")

    print("\n  [Analyzing]  Please wait...\n")
    logger.info(f"Analysis start: role='{target_role}', company='{company}'")

    # ── STAGE 1: Skill Extraction ──────────────────────────────────────────
    print("  [1/9] Extracting skills from resume (Hybrid: Regex + Vocab + AI)...")
    raw_skills    = skill_extractor.extract_skills(resume_text)
    resume_skills = skill_normalizer.normalize_list(raw_skills)
    print(f"        Found {len(resume_skills)} skills: {resume_skills[:10]}{'...' if len(resume_skills)>10 else ''}")

    # ── VALIDATION CHECKPOINT 1 ────────────────────────────────────────────
    if not _validate_resume_skills(resume_skills):
        return

    # ── STAGE 2: Role Skill Discovery ──────────────────────────────────────
    print("  [2/9] Discovering role requirements (Web + AI fallback)...")
    role_skills_raw, internet_used = scraper.fetch_skills(target_role, company)
    role_skills = skill_normalizer.normalize_list(role_skills_raw)

    # Expand extractor vocabulary and re-extract if we gained new role skills
    if role_skills:
        added = skill_extractor.expand_vocabulary(role_skills)
        if added > 0:
            expanded_raw  = skill_extractor.extract_skills(resume_text, extra_vocab=role_skills)
            resume_skills  = skill_normalizer.normalize_list(expanded_raw)
        print(f"        Role requires {len(role_skills)} skills.")
    else:
        print(f"        [!] No role skills obtained.")

    # ── VALIDATION CHECKPOINT 2 ────────────────────────────────────────────
    if not _validate_role_skills(role_skills):
        return

    # ── STAGE 3: Skill Gap Analysis ────────────────────────────────────────
    print("  [3/9] Computing skill gap...")
    gap      = gap_analyzer.analyze(resume_skills, role_skills)
    matching = gap["matching_skills"]
    missing  = gap["missing_skills"]
    extra    = gap["extra_skills"]
    coverage = gap["coverage_percentage"]
    print(f"        Coverage: {coverage:.1f}%  Matching: {len(matching)}  Missing: {len(missing)}")

    ranked_missing = priority_ranker.rank(missing, role_skills)

    # ── STAGE 4: Vectorization ─────────────────────────────────────────────
    print("  [4/9] Building skill vectors...")
    universe, resume_vec, role_vec = vectorizer.build_vectors(resume_skills, role_skills)

    # ── VALIDATION CHECKPOINT 3 + STAGE 5: Scoring ────────────────────────
    print("  [5/9] Running ML scoring model...")
    score = None
    probability = None

    if _validate_score_inputs(resume_skills, role_skills):
        kw_density = skill_extractor.keyword_density(resume_text)
        exp_signal = skill_extractor.experience_signal(resume_text)
        match_ratio   = coverage / 100.0
        missing_ratio = len(missing) / max(len(role_skills), 1)

        score = scoring_model.predict(
            skill_match_ratio   = match_ratio,
            missing_skill_ratio = missing_ratio,
            skill_count         = len(resume_skills),
            keyword_density     = kw_density,
            experience_signal   = exp_signal,
            resume_skills       = resume_skills,
        )
        if score is not None:
            print(f"        Score: {score:.3f} / 1.000")
    else:
        kw_density = 0.0
        exp_signal = 0.0

    # ── STAGE 6: Probability ───────────────────────────────────────────────
    print("  [6/9] Estimating interview probability...")
    if score is not None:
        probability = prob_estimator.estimate(score, coverage/100.0, exp_signal, target_role)
        print(f"        Probability: {probability['probability']}%  {probability['tier']}")

    # ── STAGE 7: Personality ───────────────────────────────────────────────
    print("  [7/9] Analyzing professional competency...")
    personality_scores = personality_analyzer.analyze(resume_text)
    avg_pers = sum(personality_scores.values()) / len(personality_scores)
    print(f"        Avg competency: {avg_pers:.1f}/10")

    # ── STAGE 8: Charts ────────────────────────────────────────────────────
    print("  [8/9] Generating visual charts...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    role_cat   = skill_extractor.get_skill_categories(role_skills)
    resume_cat = skill_extractor.get_skill_categories(resume_skills)
    role_cat_counts   = {k: len(v) for k, v in role_cat.items()}
    resume_cat_counts = {k: len(v) for k, v in resume_cat.items()}

    radar_path  = RadarChartGenerator.generate(resume_cat_counts, role_cat_counts, RADAR_PATH)
    spider_path = SpiderChartGenerator.generate(personality_scores, SPIDER_PATH)

    # ── STAGE 9: Report content ────────────────────────────────────────────
    print("  [9/9] Generating learning plan and report...")
    ordered_missing = [item["skill"] for item in ranked_missing]
    roadmap      = roadmap_gen.generate(ordered_missing[:8],
                                        {item["skill"]: item["priority_score"] for item in ranked_missing})
    resources    = resource_finder.find_resources(ordered_missing[:6])
    improvements = improvement_advisor.generate_suggestions(ordered_missing[:6])
    questions    = question_gen.generate(
        resume_skills     = resume_skills,
        missing_skills    = ordered_missing[:3],
        role              = target_role,
        company           = company,
        resume_score      = score or 0.3,
        experience_signal = exp_signal if score else 0.2,
    )

    ReportGenerator.print_report(
        target_role         = target_role,
        company             = company,
        resume_skills       = resume_skills,
        role_skills         = role_skills,
        matching_skills     = matching,
        missing_skills      = ordered_missing,
        extra_skills        = extra,
        coverage            = coverage,
        score               = score,
        probability         = probability,
        personality_scores  = personality_scores,
        radar_chart_path    = radar_path,
        spider_chart_path   = spider_path,
        roadmap             = roadmap,
        resources           = resources,
        improvements        = improvements,
        questions           = questions,
        internet_used       = internet_used,
        ranked_missing      = ranked_missing,
        output_dir          = OUTPUT_DIR,
    )


def main():
    # Initialize Groq first
    print("\n  [Init] Initializing AI components...")
    groq_client = GroqAIClient()
    if groq_client.available:
        print("  [Init] Groq AI: ACTIVE (llama3-70b-8192)")
    else:
        print("  [Init] Groq AI: Not configured  (add GROQ_API_KEY to .env)")

    print("  [Init] Loading skill vocabulary and ML models...")
    skill_extractor  = SkillExtractor(groq_client=groq_client)
    skill_normalizer = SkillNormalizer()
    scraper          = InternetJobScraper(skill_extractor=skill_extractor, groq_client=groq_client)
    gap_analyzer     = SkillGapAnalyzer()
    priority_ranker  = SkillPriorityRanker()
    vectorizer       = SkillVectorizer()
    scoring_model    = RegressionScoringModel()
    prob_estimator   = ProbabilityEstimator()
    personality_analyzer = PersonalityAnalyzer()
    roadmap_gen          = LearningRoadmapGenerator()
    resource_finder      = ResourceFinder()
    improvement_advisor  = ResumeImprovementAdvisor()
    question_gen         = InterviewQuestionGenerator()
    print("  [Init] Ready.\n")

    _banner(groq_client.available)

    while True:
        try:
            run_analysis(
                skill_extractor, skill_normalizer, scraper,
                gap_analyzer, priority_ranker, vectorizer,
                scoring_model, prob_estimator, personality_analyzer,
                roadmap_gen, resource_finder, improvement_advisor, question_gen,
            )
        except KeyboardInterrupt:
            print("\n\n  Interrupted.")
            break

        print("─" * 64)
        again = _prompt("\n  Analyze another resume? Enter to continue or type 'exit':\n  > ")
        if again.strip():
            print()


if __name__ == "__main__":
    main()
