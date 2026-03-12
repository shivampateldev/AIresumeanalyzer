import os
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

def execute_pipeline(resume_text: str, target_role: str, company: str = ""):
    OUTPUT_DIR  = "outputs"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    groq = GroqAIClient()
    extractor  = SkillExtractor(groq_client=groq)
    normalizer = SkillNormalizer()
    scraper    = InternetJobScraper(skill_extractor=extractor, groq_client=groq)

    # 2. Extract Skills
    raw_skills    = extractor.extract_skills(resume_text)
    resume_skills = normalizer.normalize_list(raw_skills)

    if not resume_skills and not target_role:
        return {"error": "Could not extract skills and no role provided."}
    
    # 3. Role Skills
    role_skills = []
    internet_ok = False
    if target_role:
        role_skills_raw, internet_ok = scraper.fetch_skills(target_role, company)
        role_skills = normalizer.normalize_list(role_skills_raw)
        
        # Expand vocab
        if role_skills:
            extractor.expand_vocabulary(role_skills)
            expanded = normalizer.normalize_list(extractor.extract_skills(resume_text, extra_vocab=role_skills))
            if len(expanded) > len(resume_skills):
                resume_skills = expanded

    # Provide fallback empty if we still have no role skills
    if not role_skills:
        role_skills = resume_skills

    # 4. Gap Analysis
    gap      = SkillGapAnalyzer().analyze(resume_skills, role_skills)
    matching = gap["matching_skills"]
    missing  = gap["missing_skills"]
    extra    = gap["extra_skills"]
    coverage = gap["coverage_percentage"]

    ranked_missing = SkillPriorityRanker().rank(missing, role_skills)
    ordered_missing = [item["skill"] for item in ranked_missing]

    # 5. Vectors, 6. Scoring
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

    # 7. Probability
    probability = ProbabilityEstimator().estimate(score, match_ratio, exp_signal, target_role)

    # 8. Personality
    personality = PersonalityAnalyzer().analyze(resume_text)

    # 9. Charts
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

    # 10. Roadmap + Advice
    roadmap      = LearningRoadmapGenerator().generate(
        ordered_missing[:8],
        {item["skill"]: item["priority_score"] for item in ranked_missing}
    )
    resources    = ResourceFinder().find_resources(ordered_missing[:6])
    improvements = ResumeImprovementAdvisor().generate_suggestions(ordered_missing[:6])
    questions    = InterviewQuestionGenerator().generate(
        resume_skills     = resume_skills,
        missing_skills    = ordered_missing[:3],
        role              = target_role,
        company           = company,
        resume_score      = score,
        experience_signal = exp_signal,
    )

    # 11. Write Report
    ReportGenerator.print_report(
        target_role        = target_role,
        company            = company,
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

    with open(os.path.join(OUTPUT_DIR, "analysis_report.txt"), "r", encoding="utf-8") as f:
        report_text = f.read()

    return {
        "report": report_text,
        "score": score,
        "probability": probability.get("probability", 0) if isinstance(probability, dict) else 0,
        "probability_tier": probability.get("tier", "") if isinstance(probability, dict) else "",
        "skills": resume_skills,
        "role_skills": role_skills,
        "matching_skills": matching,
        "missing_skills": missing,
        "extra_skills": extra,
        "radar_chart": "/outputs/skill_radar_chart.png",
        "spider_chart": "/outputs/personality_spider_chart.png",
        "roadmap": roadmap,
        "improvements": improvements,
        "questions": questions,
        "personality": personality
    }
