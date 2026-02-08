"""
Supplementary Figure S2: Violin/Box Plot - Citation Count Distribution
Shows the statistical distribution of bias citation counts across categories
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from utils import load_data, get_category_color, save_figure

def create_violin_plot():
    # Set random seed for reproducibility
    np.random.seed(42)

    """Create violin plot showing citation count distributions"""
    # Load data
    df = load_data()

    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

    # Define category order
    category_order = ['Genomics', 'Transcriptomics', 'Metabolomics', 'Proteomics',
                      'Multi-omics', 'General_omics', 'Chinese Literature']

    # Get colors for categories
    palette = [get_category_color(cat) for cat in category_order]

    # Plot 1: Violin plot with box plot overlay
    parts = ax1.violinplot(
        [df[df['Category'] == cat]['Final count'].values for cat in category_order],
        positions=range(len(category_order)),
        showmeans=True,
        showmedians=True,
        widths=0.7
    )

    # Color the violins
    for i, pc in enumerate(parts['bodies']):
        pc.set_facecolor(palette[i])
        pc.set_alpha(0.6)
        pc.set_edgecolor('black')
        pc.set_linewidth(1)

    # Customize violin plot elements
    for partname in ('cbars', 'cmins', 'cmaxes', 'cmedians', 'cmeans'):
        if partname in parts:
            vp = parts[partname]
            vp.set_edgecolor('black')
            vp.set_linewidth(1.5)

    # Overlay box plot
    bp = ax1.boxplot(
        [df[df['Category'] == cat]['Final count'].values for cat in category_order],
        positions=range(len(category_order)),
        widths=0.3,
        patch_artist=True,
        showfliers=True,
        boxprops=dict(facecolor='white', alpha=0.7),
        medianprops=dict(color='red', linewidth=2),
        whiskerprops=dict(linewidth=1.5),
        capprops=dict(linewidth=1.5),
        flierprops=dict(marker='o', markerfacecolor='red', markersize=4, alpha=0.5)
    )

    ax1.set_xticks(range(len(category_order)))
    ax1.set_xticklabels(category_order, rotation=45, ha='right', fontsize=11)
    ax1.set_ylabel('Citation Count', fontsize=12, fontweight='bold')
    ax1.set_title('Distribution of Citation Counts by Category\n(Violin + Box Plot)',
                  fontsize=14, fontweight='bold', pad=15)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    ax1.set_ylim(bottom=0)

    # Plot 2: Swarm plot with individual points
    sns.violinplot(data=df, x='Category', y='Final count', order=category_order,
                   palette=palette, alpha=0.4, inner=None, ax=ax2)

    sns.swarmplot(data=df, x='Category', y='Final count', order=category_order,
                  color='black', alpha=0.5, size=3, ax=ax2)

    ax2.set_xticklabels(category_order, rotation=45, ha='right', fontsize=11)
    ax2.set_xlabel('Omics Category', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Citation Count', fontsize=12, fontweight='bold')
    ax2.set_title('Individual Bias Distribution\n(Violin + Swarm Plot)',
                  fontsize=14, fontweight='bold', pad=15)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')

    plt.tight_layout()

    # Save figure
    save_figure(fig, 'figS2_violin_plot.png', output_dir='figures/supplementary')

    # Print summary statistics
    print("\n=== Violin Plot Summary ===")
    print("\nDescriptive statistics by category:")
    for cat in category_order:
        cat_data = df[df['Category'] == cat]['Final count']
        print(f"\n{cat}:")
        print(f"  Count: {len(cat_data)}")
        print(f"  Mean: {cat_data.mean():.2f}")
        print(f"  Median: {cat_data.median():.2f}")
        print(f"  Std: {cat_data.std():.2f}")
        print(f"  Min: {cat_data.min():.0f}")
        print(f"  Max: {cat_data.max():.0f}")
        print(f"  Q1: {cat_data.quantile(0.25):.2f}")
        print(f"  Q3: {cat_data.quantile(0.75):.2f}")

    # Kruskal-Wallis test
    print("\n=== Statistical Test ===")
    groups = [df[df['Category'] == cat]['Final count'].values for cat in category_order]
    h_stat, p_value = stats.kruskal(*groups)
    print(f"Kruskal-Wallis H-test:")
    print(f"  H-statistic: {h_stat:.4f}")
    print(f"  p-value: {p_value:.6f}")

    if p_value < 0.05:
        print("  Result: Significant differences exist between categories (p < 0.05)")
    else:
        print("  Result: No significant differences between categories (p ≥ 0.05)")

    return fig

if __name__ == '__main__':
    create_violin_plot()
    plt.show()
