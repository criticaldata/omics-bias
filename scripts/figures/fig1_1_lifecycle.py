"""
Figure 1.1: Omics Research Pipeline - Lifecycle Bias Distribution
Circular diagram showing biases at each stage of the research pipeline
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Wedge, Circle, FancyBboxPatch
from utils import load_data, save_figure

def categorize_to_pipeline_stage(subcategory):
    """Map subcategory to research pipeline stage"""
    subcat_lower = subcategory.lower()

    if 'data production' in subcat_lower or 'pre-analysis' in subcat_lower or 'pre analysis' in subcat_lower or 'prediction' in subcat_lower:
        return 'Data Production'
    elif 'technical' in subcat_lower or 'instrumental' in subcat_lower or 'hardware' in subcat_lower:
        return 'Technical/Instrumental'
    elif 'computational' in subcat_lower or 'analytical' in subcat_lower or 'software' in subcat_lower:
        return 'Computational/Analytical'
    elif 'reporting' in subcat_lower or 'interpretation' in subcat_lower or 'post-analysis' in subcat_lower:
        return 'Reporting/Interpretation'
    else:
        return 'Other Challenges'

def create_lifecycle_diagram():
    """Create circular lifecycle diagram with real bias data"""
    # Load data
    df = load_data()

    # Add pipeline stage
    df['Pipeline_Stage'] = df['Subcategory'].apply(categorize_to_pipeline_stage)

    # Get top biases for each stage
    stages_data = {}
    stages = ['Data Production', 'Technical/Instrumental', 'Computational/Analytical',
              'Reporting/Interpretation', 'Other Challenges']

    for stage in stages:
        stage_df = df[df['Pipeline_Stage'] == stage].nlargest(5, 'Final count')
        biases = []
        for _, row in stage_df.iterrows():
            keyword = row['Final_Keyword']
            count = row['Final count']
            # Shorten long bias names
            if len(keyword) > 35:
                keyword = keyword[:32] + '...'
            biases.append(f"{keyword}")
        stages_data[stage] = biases

    # Define colors for each stage
    stage_colors = {
        'Data Production': '#5DADE2',  # Light blue
        'Technical/Instrumental': '#F39C12',  # Orange
        'Computational/Analytical': '#9B59B6',  # Purple
        'Reporting/Interpretation': '#48C9B0',  # Teal
        'Other Challenges': '#EC7063'  # Red/pink
    }

    # Create figure
    fig = plt.figure(figsize=(16, 16))
    ax = fig.add_subplot(111, aspect='equal')

    # Parameters for the circle
    center = (0.5, 0.5)
    outer_radius = 0.45
    inner_radius = 0.18

    # Number of stages
    n_stages = len(stages)
    angle_per_stage = 360 / n_stages

    # Draw each stage as a wedge
    for i, stage in enumerate(stages):
        # Calculate angles (start from top, go clockwise)
        start_angle = 90 - (i * angle_per_stage)
        end_angle = start_angle - angle_per_stage

        # Create wedge
        wedge = Wedge(center, outer_radius, end_angle, start_angle,
                     width=outer_radius-inner_radius,
                     facecolor=stage_colors[stage],
                     edgecolor='white',
                     linewidth=3,
                     alpha=0.85)
        ax.add_patch(wedge)

        # Calculate position for stage label (just outside the wedge)
        label_angle = np.radians(start_angle - angle_per_stage/2)
        label_radius = outer_radius + 0.08
        label_x = center[0] + label_radius * np.cos(label_angle)
        label_y = center[1] + label_radius * np.sin(label_angle)

        # Add stage number only (name in legend)
        stage_num = i + 1

        ax.text(label_x, label_y, f"{stage_num}",
               ha='center', va='center',
               fontsize=16, fontweight='bold',
               color='white',
               bbox=dict(boxstyle='circle,pad=0.3', facecolor=stage_colors[stage],
                        edgecolor='white', linewidth=3))

        # Add only top 3 biases with SHORT names inside the wedge
        text_radius = (outer_radius + inner_radius) / 2
        text_angle_rad = np.radians(start_angle - angle_per_stage/2)
        text_x = center[0] + text_radius * np.cos(text_angle_rad)
        text_y = center[1] + text_radius * np.sin(text_angle_rad)

        # Format bias list - SHORTENED to first 2-3 words only
        short_biases = []
        for bias in stages_data[stage][:3]:  # Only top 3
            # Take first 2-3 words or first 25 chars max
            words = bias.split()
            if len(words) <= 3:
                short_biases.append(' '.join(words[:3]))
            else:
                short_biases.append(' '.join(words[:2]))

        bias_text = '\n'.join([f"• {b}" for b in short_biases])

        # Calculate rotation - ALWAYS keep text readable (never upside down)
        rotation = (start_angle - angle_per_stage/2) - 90
        # Keep text horizontal or nearly horizontal
        if rotation < -90:
            rotation += 180
        if rotation > 90:
            rotation -= 180
        # Avoid steep angles
        if rotation < -45:
            rotation = 0
        if rotation > 45:
            rotation = 0

        ax.text(text_x, text_y, bias_text,
               ha='center', va='center',
               fontsize=9,
               rotation=rotation,
               color='white',
               fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.6',
                        facecolor=stage_colors[stage],
                        alpha=0.9, edgecolor='white', linewidth=1.5))

    # Draw center circle with title
    center_circle = Circle(center, inner_radius,
                          facecolor='white',
                          edgecolor='#34495E',
                          linewidth=4)
    ax.add_patch(center_circle)

    # Add center text - concise
    ax.text(center[0], center[1], 'Research\nPipeline',
           ha='center', va='center',
           fontsize=16, fontweight='bold',
           color='#2C3E50')

    # Set axis limits and remove axes
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Add title
    fig.suptitle('Omics Research Pipeline - Top Biases by Stage',
                fontsize=18, fontweight='bold', y=0.96, color='#2C3E50')

    # Add compact legend on the right side
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=stage_colors[stage], label=f"{i+1}. {stage}")
                      for i, stage in enumerate(stages)]

    ax.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1.05, 0.5),
             fontsize=10, frameon=True, title='Pipeline Stages', title_fontsize=11)

    plt.tight_layout()

    # Save figure
    save_figure(fig, 'fig1_1_lifecycle.png', output_dir='figures/main')

    # Print summary
    print("\n=== Lifecycle Diagram Summary ===")
    print("\nTop biases by research stage:")
    for stage in stages:
        print(f"\n{stage}:")
        stage_df = df[df['Pipeline_Stage'] == stage].nlargest(5, 'Final count')
        for idx, row in stage_df.iterrows():
            print(f"  • {row['Final_Keyword']} ({int(row['Final count'])} citations)")

    # Print total counts per stage
    print("\n\nTotal citations by stage:")
    for stage in stages:
        total = df[df['Pipeline_Stage'] == stage]['Final count'].sum()
        count = len(df[df['Pipeline_Stage'] == stage])
        print(f"  {stage}: {int(total)} citations ({count} biases)")

    return fig

if __name__ == '__main__':
    create_lifecycle_diagram()
    plt.show()
