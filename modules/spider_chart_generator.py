import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from modules.logger import logger


class SpiderChartGenerator:
    """Generates the professional competency spider chart from personality scores."""

    @staticmethod
    def generate(
        scores: dict[str, float],
        output_path: str = "outputs/personality_spider_chart.png",
    ) -> str:
        import os
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

        axes = list(scores.keys())
        values = list(scores.values())
        N = len(axes)

        # Close polygon
        values_closed = values + [values[0]]
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles_closed = angles + [angles[0]]

        fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
        fig.patch.set_facecolor("#0d1117")
        ax.set_facecolor("#0d1117")

        # Color gradient based on overall score
        avg_score = np.mean(values)
        fill_color = "#ff6b35" if avg_score < 5 else "#a855f7" if avg_score < 7 else "#00d4ff"

        ax.plot(angles_closed, values_closed, color=fill_color, linewidth=2.5)
        ax.fill(angles_closed, values_closed, color=fill_color, alpha=0.25)

        # Reference circles at 2.5, 5, 7.5, 10
        for r in [2.5, 5.0, 7.5, 10.0]:
            circle_vals = [r] * N + [r]
            ax.plot(angles_closed, circle_vals, color="#333333", linewidth=0.6, linestyle="--")

        # Axis labels
        ax.set_thetagrids(np.degrees(angles), axes, color="white", size=8.5)
        ax.set_ylim(0, 10)
        ax.set_rlabel_position(22)
        plt.yticks([2.5, 5, 7.5, 10], ["2.5", "5", "7.5", "10"], color="#888888", size=7)
        ax.tick_params(colors="#888888")
        ax.grid(color="#222222", linestyle="-", linewidth=0.4)

        # Score dots on each axis
        for angle, value in zip(angles, values):
            ax.plot(angle, value, "o", color=fill_color, markersize=5)

        plt.title("Professional Competency Profile", size=13, color="white", pad=20, fontweight="bold")

        # Subtitle: overall average
        fig.text(0.5, 0.02, f"Overall Average: {avg_score:.1f} / 10",
                 ha="center", fontsize=9, color="#aaaaaa")

        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close(fig)
        logger.info(f"Spider chart saved to {output_path}")
        return output_path
