"""
Figure 1.1: Omics Research Pipeline - Lifecycle Bias Distribution
Circular diagram showing biases at each stage of the research pipeline
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Circle, Patch
from mapper import (load_data, save_figure, normalize_subcategories,
                    STAGE_MAP, STAGE_COLORS, shorten_bias)

def create_lifecycle_diagram():
    """Create circular lifecycle diagram with real bias data suitable for publication"""
    
    # Configure Matplotlib for Nature-style publication standards
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
        'pdf.fonttype': 42,  # Ensures text is editable in PDF/EPS (Nature requirement)
        'ps.fonttype': 42,
        'svg.fonttype': 'none'
    })

    # Load data with normalized subcategories
    df = load_data()
    df = normalize_subcategories(df)

    # Map to pipeline stages
    df['Pipeline_Stage'] = df['Subcategory'].map(STAGE_MAP)

    # Get top biases for each stage
    stages_data = {}
    stages = ['Data Production', 'Technical/Instrumental', 'Computational/Analytical',
              'Reporting/Interpretation', 'Other Challenges']

    for stage in stages:
        stage_df = df[df['Pipeline_Stage'] == stage].nlargest(3, 'Final count')
        biases = [shorten_bias(row['Final_Keyword']) for _, row in stage_df.iterrows()]
        stages_data[stage] = biases

    # Colors from shared STAGE_COLORS in mapper.py
    stage_colors = STAGE_COLORS

    # Create figure
    fig = plt.figure(figsize=(20, 18))
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
                     linewidth=4, # Slightly thicker borders for high-res clarity
                     alpha=0.9)   # Slightly increased opacity for better contrast
        ax.add_patch(wedge)

        # Calculate position for stage number (just outside the wedge)
        label_angle = np.radians(start_angle - angle_per_stage/2)
        label_radius = outer_radius + 0.08
        label_x = center[0] + label_radius * np.cos(label_angle)
        label_y = center[1] + label_radius * np.sin(label_angle)

        # Add stage number (Increased size from 20 to 36)
        ax.text(label_x, label_y, f"{i + 1}",
               ha='center', va='center',
               fontsize=36, fontweight='bold',
               color='white',
               bbox=dict(boxstyle='circle,pad=0.3', facecolor=stage_colors[stage],
                        edgecolor='white', linewidth=3))

        # Position for bias text inside wedge — always horizontal
        text_radius = (outer_radius + inner_radius) / 2
        text_angle_rad = np.radians(start_angle - angle_per_stage/2)
        text_x = center[0] + text_radius * np.cos(text_angle_rad)
        text_y = center[1] + text_radius * np.sin(text_angle_rad)

        bias_text = '\n'.join([f"• {b}" for b in stages_data[stage]])

        # Add bias text (Increased size from 15 to 26)
        ax.text(text_x, text_y, bias_text,
               ha='center', va='center',
               fontsize=26,
               rotation=0,
               color='white',
               fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.6',
                        facecolor=stage_colors[stage],
                        alpha=0.9, edgecolor='white', linewidth=2))

    # Draw center circle with title
    center_circle = Circle(center, inner_radius,
                          facecolor='white',
                          edgecolor='#34495E',
                          linewidth=5)
    ax.add_patch(center_circle)

    # Center text (Increased size from 20 to 40)
    ax.text(center[0], center[1], 'Research\nPipeline',
           ha='center', va='center',
           fontsize=40, fontweight='bold',
           color='#2C3E50')

    # Set axis limits and remove axes
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Add legend (Increased sizes, pushed slightly further right to avoid overlapping larger text)
    legend_elements = [Patch(facecolor=stage_colors[stage], label=f"{i+1}. {stage}")
                      for i, stage in enumerate(stages)]

    ax.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1.08, 0.5),
             fontsize=22, frameon=True, title='Pipeline Stages', title_fontsize=26)

    plt.tight_layout()

    # Save figure (Recommended to save as PDF or EPS for Nature)
    save_figure(fig, 'fig1_1_lifecycle.pdf', output_dir='figures/main')
    save_figure(fig, 'fig1_1_lifecycle.png', output_dir='figures/main') # Keep PNG for quick viewing

    # Print summary
    print("\n=== Lifecycle Diagram Summary ===")
    print("\nTop biases by research stage:")
    for stage in stages:
        print(f"\n{stage}:")
        stage_df = df[df['Pipeline_Stage'] == stage].nlargest(5, 'Final count')
        for idx, row in stage_df.iterrows():
            print(f"  • {row['Final_Keyword']} ({int(row['Final count'])} citations)")

    return fig

if __name__ == '__main__':
    create_lifecycle_diagram()