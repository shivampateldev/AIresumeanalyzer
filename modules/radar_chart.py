import matplotlib.pyplot as plt
import numpy as np

class RadarChartGenerator:
    """Generates a skill radar chart using matplotlib."""
    
    @staticmethod
    def generate(resume_categories: dict, role_categories: dict, output_path: str = "skill_radar_chart.png"):
        """
        resume_categories and role_categories are dictionaries mapping a category to a count of skills.
        """
        # Ensure categories match
        categories = list(role_categories.keys())
        # Remove empty categories or Uncategorized to keep chart neat if needed
        categories = [c for c in categories if c != "Uncategorized"]
        
        N = len(categories)
        if N < 3:
            # Need at least 3 axes for a radar chart
            categories.extend([f"Pad_{i}" for i in range(3 - N)])
            N = max(N, 3)
            
        role_values = [role_categories.get(cat, 0) for cat in categories]
        resume_values = [resume_categories.get(cat, 0) for cat in categories]
        
        # Max scaling
        max_val = max(max(role_values) if role_values else 1, max(resume_values) if resume_values else 1)
        role_values = [(v / max_val) * 100 for v in role_values]
        resume_values = [(v / max_val) * 100 for v in resume_values]
        
        # Close the plot path
        role_values += role_values[:1]
        resume_values += resume_values[:1]
        
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        
        # Draw one axe per variable + add labels
        plt.xticks(angles[:-1], categories, color='grey', size=8)
        
        # Draw ylabels
        ax.set_rlabel_position(0)
        plt.yticks([25, 50, 75], ["25", "50", "75"], color="grey", size=7)
        plt.ylim(0, 100)
        
        # Plot data
        ax.plot(angles, role_values, linewidth=1, linestyle='solid', label='Role Required')
        ax.fill(angles, role_values, 'b', alpha=0.1)
        
        ax.plot(angles, resume_values, linewidth=1, linestyle='solid', label='Resume Skills')
        ax.fill(angles, resume_values, 'r', alpha=0.1)
        
        plt.title('Skill Coverage Radar Chart', size=11, color='black', y=1.1)
        plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        
        plt.savefig(output_path, bbox_inches='tight')
        plt.close(fig)
