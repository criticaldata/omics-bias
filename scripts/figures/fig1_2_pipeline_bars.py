"""
Figure 1.2: Omics Research Pipeline - Top Biases by Stage (Bar Chart)
Horizontal bar chart showing top 3 most-cited biases per pipeline stage.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from mapper import (load_data, save_figure, normalize_subcategories,
                    STAGE_MAP, STAGE_COLORS, shorten_bias)


def create_pipeline_bars():
    """Create horizontal bar chart of top 3 biases per pipeline stage."""
    # Load data with normalized subcategories
    df = load_data()
    df = normalize_subcategories(df)
    df['Pipeline_Stage'] = df['Subcategory'].map(STAGE_MAP)

    stages = ['Data Production', 'Technical/Instrumental', 'Computational/Analytical',
              'Reporting/Interpretation', 'Other Challenges']

    # Collect top 3 per stage
    rows = []
    for stage in stages:
        stage_df = df[df['Pipeline_Stage'] == stage]
        total = int(stage_df['Final count'].sum())
        n_biases = len(stage_df)
        top3 = stage_df.nlargest(3, 'Final count')
        for rank, (_, row) in enumerate(top3.iterrows()):
            rows.append({
                'stage': stage,
                'keyword': shorten_bias(row['Final_Keyword']),
                'count': int(row['Final count']),
                'rank': rank,
                'stage_total': total,
                'stage_n': n_biases,
            })

    plot_df = pd.DataFrame(rows)

    # Figure layout
    fig, ax = plt.subplots(figsize=(16, 10))

    # Vertical positioning: stages are groups separated by gaps
    bar_height = 0.7
    group_gap = 1.4
    y_positions = []
    y_labels = []
    stage_label_y = []

    y = 0
    for i, stage in enumerate(stages):
        grp = plot_df[plot_df['stage'] == stage].sort_values('rank')
        color = STAGE_COLORS[stage]
        total = grp.iloc[0]['stage_total']
        pct = total / df['Final count'].sum() * 100

        # Stage label position (center of group)
        stage_label_y.append(y + bar_height)

        alphas = [1.0, 0.75, 0.55]
        for j, (_, row) in enumerate(grp.iterrows()):
            bar = ax.barh(y, row['count'], height=bar_height,
                          color=color, alpha=alphas[j], edgecolor='white',
                          linewidth=0.5)
            # Label inside bar
            label = f"{row['keyword']}  ({row['count']})"
            ax.text(row['count'] - 0.5, y, label,
                    ha='right', va='center', fontsize=11, fontweight='bold',
                    color='white')
            y -= (bar_height + 0.15)

        y -= group_gap  # gap between stages

    # Stage labels on the left
    y = 0
    for i, stage in enumerate(stages):
        grp = plot_df[plot_df['stage'] == stage]
        total = grp.iloc[0]['stage_total']
        pct = total / df['Final count'].sum() * 100
        mid_y = y - bar_height  # center of 3 bars
        color = STAGE_COLORS[stage]

        ax.text(-1.5, mid_y, f"{i+1}. {stage}",
                ha='right', va='center', fontsize=13, fontweight='bold',
                color=color)
        ax.text(-1.5, mid_y - 0.9, f"{total} citations ({pct:.1f}%)",
                ha='right', va='center', fontsize=10, color='#666666')

        y -= 3 * (bar_height + 0.15) + group_gap

    # Horizontal separator lines between stages
    y = 0
    for i, stage in enumerate(stages[:-1]):
        y -= 3 * (bar_height + 0.15)
        sep_y = y - group_gap / 2 + 0.1
        ax.axhline(y=sep_y, color='#DDDDDD', linewidth=1, linestyle='-',
                   xmin=0.0, xmax=1.0)
        y -= group_gap

    # Styling
    ax.set_xlim(0, plot_df['count'].max() * 1.05)
    ax.set_xlabel('Number of Citations', fontsize=12, labelpad=10)
    ax.yaxis.set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Title
    total_citations = int(df['Final count'].sum())
    total_biases = len(df)
    n_cats = df['Category'].nunique()
    fig.suptitle('Omics Research Pipeline: Top Biases by Stage',
                 fontsize=22, fontweight='bold', y=0.97, x=0.45)
    ax.set_title(f'Top 3 most-cited biases per pipeline stage  |  '
                 f'{total_citations:,} citations across {total_biases} biases '
                 f'in {n_cats} omics categories',
                 fontsize=11, color='#888888', pad=12, loc='center')

    # Legend for rank
    legend_elements = [
        Patch(facecolor='#999999', alpha=1.0, label='1st (most cited)'),
        Patch(facecolor='#999999', alpha=0.75, label='2nd'),
        Patch(facecolor='#999999', alpha=0.55, label='3rd'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=10,
              frameon=True, title='Rank within stage', title_fontsize=11)

    plt.subplots_adjust(left=0.30, right=0.95, top=0.90, bottom=0.08)

    # Save
    save_figure(fig, 'fig1_2_pipeline_bars.png', output_dir='figures/main')

    # Print summary
    print("\n=== Pipeline Bars Summary ===")
    for stage in stages:
        grp = plot_df[plot_df['stage'] == stage]
        total = grp.iloc[0]['stage_total']
        print(f"\n{stage} ({total} citations):")
        for _, row in grp.iterrows():
            print(f"  {row['rank']+1}. {row['keyword']} ({row['count']})")

    return fig


if __name__ == '__main__':
    create_pipeline_bars()
    plt.show()
