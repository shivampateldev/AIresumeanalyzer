"""
report_generator.py — Full terminal + file report.

Design:
  - All terminal output uses ASCII only (Windows CP1252 compatible)
  - The saved .txt file also uses ASCII for maximum portability
  - Unicode emoji/symbols replaced with ASCII equivalents
"""
import os
from datetime import datetime
from modules.logger import logger


class ReportGenerator:
    LINE_WIDE = "=" * 62
    LINE_THIN = "-" * 62

    @staticmethod
    def print_report(
        target_role: str,
        company: str,
        resume_skills: list[str],
        role_skills: list[str],
        matching_skills: list[str],
        missing_skills: list[str],
        extra_skills: list[str],
        coverage: float,
        score: float | None,
        probability: dict | None,
        personality_scores: dict[str, float],
        radar_chart_path: str,
        spider_chart_path: str,
        roadmap: dict,
        resources: dict,
        improvements: list[str],
        questions: list[dict],
        internet_used: bool,
        ranked_missing: list[dict] | None = None,
        output_dir: str = "outputs",
    ) -> None:
        R = ReportGenerator
        L = []

        data_src = "[LIVE] Internet + Groq AI" if internet_used else "[GROQ] Groq AI (offline mode)"

        L += [
            "", R.LINE_WIDE,
            "         AI RESUME INTELLIGENCE REPORT",
            R.LINE_WIDE,
            f"  Generated   : {datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}",
            f"  Data Source : {data_src}",
            R.LINE_WIDE,
            f"\n  Target Role : {target_role.title()}",
            f"  Company     : {company.title() if company else 'N/A (Generic Analysis)'}",
        ]

        # ── Extracted Resume Skills ──────────────────────────────────────
        L += ["", R.LINE_THIN, "  EXTRACTED RESUME SKILLS", R.LINE_THIN]
        if resume_skills:
            for i, s in enumerate(sorted(resume_skills), 1):
                L.append(f"  {i:>3}. {s.title()}")
        else:
            L += [
                "  *** NO SKILLS DETECTED ***",
                "  Tip: Resume must contain explicit skill names.",
                "  Example: Python, SQL, Docker, React, Machine Learning",
            ]

        # ── Role Requirements ────────────────────────────────────────────
        src_label = "internet" if internet_used else "groq ai"
        L += ["", R.LINE_THIN,
              f"  REQUIRED SKILLS FOR: {target_role.title()} (via {src_label})",
              R.LINE_THIN]
        if role_skills:
            match_set = {s.lower() for s in matching_skills}
            for i, s in enumerate(role_skills, 1):
                mark = "[HAVE]" if s.lower() in match_set else "[MISS]"
                L.append(f"  {i:>3}. {mark} {s.title()}")
        else:
            L.append("  No role skills available. Check internet or Groq API key.")

        # ── Skill Gap ────────────────────────────────────────────────────
        L += ["", R.LINE_THIN, "  SKILL GAP ANALYSIS", R.LINE_THIN]
        L.append(f"  Skill Coverage : {coverage:.1f}%  "
                 f"({len(matching_skills)} of {len(role_skills)} role skills matched)")

        L.append(f"\n  MATCHING Skills ({len(matching_skills)}) -- skills you already have:")
        if matching_skills:
            for s in sorted(matching_skills):
                L.append(f"      [+] {s.title()}")
        else:
            L.append("      (none matched)")

        L.append(f"\n  MISSING Skills ({len(missing_skills)}) -- skills you need to learn:")
        if missing_skills:
            for s in missing_skills:
                L.append(f"      [-] {s.title()}")
        else:
            L.append("      All role skills present -- full coverage!")

        L.append(f"\n  EXTRA Skills ({len(extra_skills)}) -- bonus skills not in role spec:")
        for s in sorted(extra_skills)[:12]:
            L.append(f"      [*] {s.title()}")

        # ── Suitability Score ────────────────────────────────────────────
        L += ["", R.LINE_THIN, "  RESUME SUITABILITY SCORE", R.LINE_THIN]
        if score is None:
            L.append("  SCORE NOT COMPUTED -- Resume skill extraction failed.")
            L.append("  Re-run with a resume containing explicit skill names.")
        else:
            score_pct = score * 100
            filled = int(score_pct / 5)
            bar = "#" * filled + "." * (20 - filled)
            L += [
                f"  Score  : {score:.3f} / 1.000   [{bar}] {score_pct:.1f}%",
                f"  Rating : {ReportGenerator._score_label(score)}",
            ]

        # ── Probability ──────────────────────────────────────────────────
        L += ["", R.LINE_THIN, "  INTERVIEW SHORTLISTING PROBABILITY", R.LINE_THIN]
        if probability is None:
            L.append("  Not computed (score unavailable).")
        else:
            L += [
                f"  Probability : {probability['probability']}%",
                f"  Range       : {probability['confidence_band']}",
                f"  Tier        : {probability['tier']}",
            ]

        # ── Competency Profile ───────────────────────────────────────────
        L += ["", R.LINE_THIN, "  PROFESSIONAL COMPETENCY PROFILE", R.LINE_THIN]
        for axis, val in personality_scores.items():
            filled = int(val)
            bar = "#" * filled + "." * (10 - filled)
            L.append(f"  {axis:<25} [{bar}] {val:.1f}/10")

        # ── Visual Outputs ───────────────────────────────────────────────
        L += [
            "", R.LINE_THIN, "  VISUAL OUTPUTS", R.LINE_THIN,
            f"  Skill Coverage Radar    : {radar_chart_path}",
            f"  Competency Spider Chart : {spider_chart_path}",
        ]

        # ── Priority Skill Ranking ───────────────────────────────────────
        L += ["", R.LINE_THIN, "  PRIORITY SKILLS TO LEARN", R.LINE_THIN]
        if ranked_missing:
            L.append("  Priority = job_importance*0.5 + learning_speed*0.3 + market_demand*0.2")
            L.append("")
            for i, item in enumerate(ranked_missing[:8], 1):
                L.append(
                    f"  #{i:<2} {item['skill'].title():<25} "
                    f"priority={item['priority_score']:.2f}  "
                    f"demand={item['market_demand']:.2f}"
                )
        elif missing_skills:
            for i, s in enumerate(missing_skills[:8], 1):
                L.append(f"  #{i:<2} {s.title()}")
        else:
            L.append("  No missing skills -- resume is fully aligned!")

        # ── Learning Roadmap ─────────────────────────────────────────────
        L += ["", R.LINE_THIN, "  LEARNING ROADMAP (missing skills only)", R.LINE_THIN]
        if roadmap:
            for week_label, plan in list(roadmap.items())[:6]:
                L += [
                    f"\n  >> {week_label}",
                    f"     Topics  : {plan['topics']}",
                    f"     Practice: {plan['practice']}",
                    f"     Project : {plan['project']}",
                ]
        else:
            L.append("  No gaps to fill -- resume is fully aligned!")

        # ── Free Resources ───────────────────────────────────────────────
        L += ["", R.LINE_THIN, "  FREE LEARNING RESOURCES", R.LINE_THIN]
        for skill_name, links in list(resources.items())[:6]:
            L.append(f"\n  [{skill_name.title()}]")
            for platform, url in links.items():
                L.append(f"     {platform:<16}: {url}")

        # ── Resume Improvements ──────────────────────────────────────────
        L += ["", R.LINE_THIN, "  RESUME IMPROVEMENT SUGGESTIONS", R.LINE_THIN]
        L.append("  Add these bullet points after gaining each skill:\n")
        for i, suggestion in enumerate(improvements[:6], 1):
            words = suggestion.split()
            wrapped, line = [], f"  {i}. "
            for word in words:
                if len(line) + len(word) + 1 < 78:
                    line += word + " "
                else:
                    wrapped.append(line.rstrip())
                    line = "     " + word + " "
            wrapped.append(line.rstrip())
            L.extend(wrapped)
            L.append("")

        # ── Interview Questions ──────────────────────────────────────────
        L += ["", R.LINE_THIN, "  PROBABLE INTERVIEW QUESTIONS", R.LINE_THIN]
        grouped: dict[str, list] = {
            "Behavioral": [], "Conceptual": [], "Coding": [], "Scenario": []
        }
        for q in questions:
            grouped.setdefault(q["type"], []).append(q["question"])
        for qtype, qs in grouped.items():
            if qs:
                L.append(f"\n  -- {qtype} " + "-" * 42)
                for i, q in enumerate(qs, 1):
                    wrapped_q, line = [], f"  Q{i}. "
                    for word in q.split():
                        if len(line) + len(word) + 1 < 78:
                            line += word + " "
                        else:
                            wrapped_q.append(line.rstrip())
                            line = "       " + word + " "
                    wrapped_q.append(line.rstrip())
                    L.extend(wrapped_q)

        # ── Footer ───────────────────────────────────────────────────────
        L += ["", R.LINE_WIDE, "  END OF REPORT", R.LINE_WIDE, ""]

        report_text = "\n".join(L)

        # Print with safe encoding (replace unrecognized chars with ?)
        try:
            print(report_text)
        except UnicodeEncodeError:
            safe_text = report_text.encode("ascii", errors="replace").decode("ascii")
            print(safe_text)

        # Save to file (UTF-8, full fidelity)
        os.makedirs(output_dir, exist_ok=True)
        report_file = os.path.join(output_dir, "analysis_report.txt")
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_text)

        logger.info(f"Report saved: {report_file}")
        print(f"\n  Report saved: {report_file}\n")

    @staticmethod
    def _score_label(score: float) -> str:
        if score >= 0.85: return "***** Excellent Match"
        if score >= 0.70: return "****  Strong Match"
        if score >= 0.55: return "***   Good Match"
        if score >= 0.40: return "**    Moderate Match"
        return "*     Weak Match -- Significant Skill Gap"
