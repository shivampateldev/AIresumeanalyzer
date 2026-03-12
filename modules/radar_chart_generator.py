"""
radar_chart_generator.py — Skill coverage radar chart.

FIXED: Correctly plots TWO polygons (role requirements + resume skills).
Categories derived dynamically from skill_categories.json via SkillExtractor.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
from modules.logger import logger


class RadarChartGenerator:

    @staticmethod
    def generate(
        resume_cat_counts: dict[str, int],
        role_cat_counts: dict[str, int],
        output_path: str = "outputs/skill_radar_chart.png",
    ) -> str:
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

        # Union of categories, exclude 'Other' to keep chart clean
        all_cats = sorted(
            (set(resume_cat_counts) | set(role_cat_counts)) - {"Other", "Uncategorized"}
        )
        # Need at least 3 axes for a radar
        while len(all_cats) < 3:
            all_cats.append(f"Area{len(all_cats)+1}")
        N = len(all_cats)

        role_vals   = np.array([role_cat_counts.get(c, 0)   for c in all_cats], dtype=float)
        resume_vals = np.array([resume_cat_counts.get(c, 0) for c in all_cats], dtype=float)

        # Normalize to 0–100 scale relative to the max value
        max_val = max(role_vals.max(), resume_vals.max(), 1)
        role_pct   = (role_vals   / max_val) * 100
        resume_pct = (resume_vals / max_val) * 100

        # Close polygons
        angles     = [n / N * 2 * np.pi for n in range(N)] + [0]
        role_pct   = np.append(role_pct,   role_pct[0])
        resume_pct = np.append(resume_pct, resume_pct[0])

        # ── Plot ──────────────────────────────────────────────────────────
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        fig.patch.set_facecolor("#0d1117")
        ax.set_facecolor("#0d1117")

        # Role polygon
        ax.plot(angles, role_pct,   color="#00d4ff", linewidth=2.5, label="Role Required", zorder=3)
        ax.fill(angles, role_pct,   color="#00d4ff", alpha=0.18,  zorder=2)

        # Resume polygon
        ax.plot(angles, resume_pct, color="#39ff14", linewidth=2.5, label="Your Resume",   zorder=3)
        ax.fill(angles, resume_pct, color="#39ff14", alpha=0.20,  zorder=2)

        # Gridlines and labels
        ax.set_thetagrids(np.degrees(angles[:-1]), all_cats, color="white", size=8)
        ax.set_rlabel_position(30)
        ax.yaxis.set_tick_params(labelcolor="#aaaaaa", labelsize=7)
        ax.set_ylim(0, 100)
        plt.yticks([25, 50, 75, 100], ["25%", "50%", "75%", "100%"], color="#aaaaaa", size=7)
        ax.grid(color="#333333", linestyle="--", linewidth=0.6)
        for spine in ax.spines.values():
            spine.set_edgecolor("#333333")

        plt.title("Skill Coverage Radar", size=13, color="white", pad=22, fontweight="bold")
        plt.legend(
            loc="upper right", bbox_to_anchor=(1.35, 1.12),
            facecolor="#161b22", edgecolor="#444444", labelcolor="white",
        )
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close(fig)
        logger.info(f"Radar chart saved: {output_path}")
        return output_path
