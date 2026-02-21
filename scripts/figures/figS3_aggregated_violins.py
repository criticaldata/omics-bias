"""
Supplementary Figure S3: Violin/Box Plot - Aggregated Category Distributions
Shows citation count distributions for Multi-omics, General_omics, and Chinese Literature,
which are excluded from S2 because they aggregate biases across multiple fields.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from itertools import combinations
from mapper import load_data, get_category_color, save_figure


def draw_significance_bar(ax, x1, x2, y, p_corrected, h=0.5, lw=1.2):
    """Draw a significance bracket between positions x1 and x2 at height y."""
    if p_corrected >= 0.05:
        return
    if p_corrected < 0.001:
        sig_text = '***'
    elif p_corrected < 0.01:
        sig_text = '**'
    else:
        sig_text = '*'
    ax.plot([x1, x1, x2, x2], [y, y + h, y + h, y], lw=lw, color='black')
    ax.text((x1 + x2) / 2, y + h, sig_text,
            ha='center', va='bottom', fontsize=11, fontweight='bold')


def create_aggregated_violin_plot():
    """Create violin plot for aggregated categories (Multi-omics, General_omics, Chinese Literature)."""
    np.random.seed(42)

    df = load_data()
    # Include ONLY the 3 aggregated categories (excluded from S2)
    included = {'Multi-omics', 'General_omics', 'Chinese Literature'}
    df = df[df['Category'].isin(included)].copy()

    category_order = ['Multi-omics', 'General_omics', 'Chinese Literature']
    palette = [get_category_color(cat) for cat in category_order]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 9))

    # --- Panel 1: Violin + Box plot with significance bars ---
    parts = ax1.violinplot(
        [df[df['Category'] == cat]['Final count'].values for cat in category_order],
        positions=range(len(category_order)),
        showmeans=True,
        showmedians=True,
        widths=0.7
    )

    for i, pc in enumerate(parts['bodies']):
        pc.set_facecolor(palette[i])
        pc.set_alpha(0.6)
        pc.set_edgecolor('black')
        pc.set_linewidth(1)

    for partname in ('cbars', 'cmins', 'cmaxes', 'cmedians', 'cmeans'):
        if partname in parts:
            vp = parts[partname]
            vp.set_edgecolor('black')
            vp.set_linewidth(1.5)

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
    ax1.set_title('Distribution of Citation Counts\n(Violin + Box Plot, Pairwise Mann-Whitney U)',
                  fontsize=14, fontweight='bold', pad=15)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    ax1.set_ylim(bottom=0)

    # Pairwise Mann-Whitney U tests with Bonferroni correction
    pairs = list(combinations(range(len(category_order)), 2))
    n_comparisons = len(pairs)  # C(3,2) = 3

    pairwise_results = []
    for i1, i2 in pairs:
        cat1, cat2 = category_order[i1], category_order[i2]
        data1 = df[df['Category'] == cat1]['Final count'].values
        data2 = df[df['Category'] == cat2]['Final count'].values
        u_stat, p_value = stats.mannwhitneyu(data1, data2, alternative='two-sided')
        p_corrected = min(p_value * n_comparisons, 1.0)
        pairwise_results.append((i1, i2, cat1, cat2, u_stat, p_value, p_corrected))

    max_y = max([df[df['Category'] == cat]['Final count'].max() for cat in category_order])
    bar_y_start = max_y * 1.08
    bar_y_step = max_y * 0.09

    sig_pairs = [(i1, i2, p_corr) for i1, i2, _, _, _, _, p_corr in pairwise_results if p_corr < 0.05]
    sig_pairs.sort(key=lambda x: abs(x[0] - x[1]))

    for bar_idx, (i1, i2, p_corr) in enumerate(sig_pairs):
        y = bar_y_start + bar_idx * bar_y_step
        draw_significance_bar(ax1, i1, i2, y, p_corr)

    if sig_pairs:
        ax1.set_ylim(top=bar_y_start + len(sig_pairs) * bar_y_step + max_y * 0.06)

    # --- Panel 2: Violin + Swarm plot ---
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

    save_figure(fig, 'figS3_aggregated_violins.png', output_dir='figures/supplementary')

    # Print summary
    print("\n=== Aggregated Category Violin Plot Summary ===")
    print("Categories: Multi-omics, General_omics, Chinese Literature")
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
    print("\n=== Statistical Tests ===")
    groups = [df[df['Category'] == cat]['Final count'].values for cat in category_order]
    h_stat, p_value = stats.kruskal(*groups)
    print(f"Kruskal-Wallis H-test:")
    print(f"  H-statistic: {h_stat:.4f}")
    print(f"  p-value: {p_value:.6f}")
    if p_value < 0.05:
        print("  Result: Significant differences exist between categories (p < 0.05)")
    else:
        print("  Result: No significant differences between categories (p >= 0.05)")

    print(f"\nPairwise Mann-Whitney U tests (Bonferroni-corrected, {n_comparisons} comparisons):")
    for i1, i2, cat1, cat2, u_stat, p_val, p_corr in pairwise_results:
        sig = '***' if p_corr < 0.001 else '**' if p_corr < 0.01 else '*' if p_corr < 0.05 else 'ns'
        print(f"  {cat1} vs {cat2}: U={u_stat:.1f}, p={p_val:.6f}, p_corrected={p_corr:.6f} ({sig})")

    return fig


if __name__ == '__main__':
    create_aggregated_violin_plot()
