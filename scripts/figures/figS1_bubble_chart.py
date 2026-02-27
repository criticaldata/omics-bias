"""
Supplementary Figure S1: Bubble Chart - Top Biases by Citation Count
Highlights the most frequently cited biases across categories
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mapper import (load_data, get_category_color, save_figure,
                    normalize_subcategories, STAGE_MAP, shorten_bias, merge_semantic_keywords)

def create_bubble_chart():
    """Create bubble chart showing top biases"""
    # Set random seed for reproducibility
    np.random.seed(42)

    # Load data with canonical stage mapping and semantic merging
    df = load_data()
    df = normalize_subcategories(df)
    df['Subcategory_Type'] = df['Subcategory'].map(STAGE_MAP).fillna('Other Challenges')
    df = merge_semantic_keywords(df)

    # Filter top biases (count >= 10) to avoid overcrowding
    df_top = df[df['Final count'] >= 10].copy()

    # Create figure with larger size to reduce crowding
    fig, ax = plt.subplots(figsize=(18, 12))

    # Define category order for y-axis
    category_order = ['Chinese Literature', 'General Omics', 'Multi-omics', 'Proteomics',
                      'Metabolomics', 'Transcriptomics', 'Genomics']

    # Define subcategory order for x-axis
    subcat_order = ['Data Production', 'Technical/Instrumental',
                    'Computational/Analytical', 'Reporting/Interpretation', 'Other Challenges']

    # Create position mappings
    y_positions = {cat: i for i, cat in enumerate(category_order)}
    x_positions = {subcat: i for i, subcat in enumerate(subcat_order)}

    # Plot bubbles
    for _, row in df_top.iterrows():
        cat = row['Category']
        subcat_type = row['Subcategory_Type']
        count = row['Final count']
        keyword = row['Final_Keyword']

        if cat in y_positions and subcat_type in x_positions:
            # Add reduced jitter to avoid overlap
            x = x_positions[subcat_type] + np.random.uniform(-0.1, 0.1)
            y = y_positions[cat] + np.random.uniform(-0.1, 0.1)

            # Bubble size proportional to count
            size = count * 30

            # Color by category
            color = get_category_color(cat)

            # Plot bubble
            bubble = ax.scatter(x, y, s=size, c=color, alpha=0.6,
                              edgecolors='white', linewidth=1.5)

            # Don't add individual labels here - we'll add cluster labels later

    # Customize axes
    ax.set_xticks(range(len(subcat_order)))
    ax.set_xticklabels(subcat_order, rotation=45, ha='right', fontsize=11)
    ax.set_yticks(range(len(category_order)))
    ax.set_yticklabels(category_order, fontsize=11)

    ax.set_xlabel('Bias Type (Subcategory)', fontsize=13, fontweight='bold', labelpad=10)
    ax.set_ylabel('Omics Category', fontsize=13, fontweight='bold', labelpad=10)

    ax.set_title('Top Biases by Citation Count\n(Bubble size proportional to citation count, showing biases with count ≥ 10)',
                 fontsize=15, fontweight='bold', pad=20)

    # Add grid
    ax.grid(True, alpha=0.2, linestyle='--')

    # Set axis limits with padding
    ax.set_xlim(-0.5, len(subcat_order) - 0.5)
    ax.set_ylim(-0.5, len(category_order) - 0.5)

    # Add top 2 keywords per category-subcategory cluster
    for cat_idx, cat in enumerate(category_order):
        for subcat_idx, subcat_type in enumerate(subcat_order):
            # Get top 2 biases for this cluster
            cluster_biases = df_top[(df_top['Category'] == cat) &
                                    (df_top['Subcategory_Type'] == subcat_type)]
            if len(cluster_biases) > 0:
                top2 = cluster_biases.nlargest(2, 'Final count')

                # Position labels slightly above cluster center
                label_y = cat_idx + 0.3
                for i, (_, row) in enumerate(top2.iterrows()):
                    keyword = row['Final_Keyword']
                    display = shorten_bias(keyword)

                    # Offset second label
                    offset = 0 if i == 0 else 0.15
                    ax.text(subcat_idx, label_y + offset, display,
                           fontsize=8, ha='center', va='center',
                           fontweight='bold', style='italic',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                                    alpha=0.8, edgecolor='gray', linewidth=0.5))

    # Add legend for bubble sizes - positioned in upper right with high transparency
    legend_sizes = [10, 15, 20, 25, 30]
    legend_bubbles = [ax.scatter([], [], s=size*30, c='gray', alpha=0.6,
                                edgecolors='white', linewidth=1.5)
                     for size in legend_sizes]

    legend1 = ax.legend(legend_bubbles, legend_sizes, scatterpoints=1,
                       loc='upper right',
                       title='Citation Count',
                       frameon=True, fontsize=9, title_fontsize=10,
                       fancybox=True, framealpha=0.95,
                       edgecolor='black', facecolor='white')
    ax.add_artist(legend1)

    plt.tight_layout()

    # Save figure
    save_figure(fig, 'figS1_bubble_chart.png', output_dir='figures/supplementary')

    # Print summary
    print("\n=== Bubble Chart Summary ===")
    print(f"Total biases shown: {len(df_top)}")
    print(f"Citation count range: {df_top['Final count'].min():.0f} - {df_top['Final count'].max():.0f}")
    print(f"\nTop 10 biases by citation count:")
    top10 = df_top.nlargest(10, 'Final count')[['Category', 'Final_Keyword', 'Final count']]
    for idx, row in top10.iterrows():
        print(f"  {row['Category']}: {row['Final_Keyword']} ({int(row['Final count'])})")

    return fig

if __name__ == '__main__':
    create_bubble_chart()
