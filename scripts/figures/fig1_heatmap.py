"""
Figure 1: Overview Heatmap - Bias Landscape Across Omics Categories
Shows the complete bias landscape with hierarchical clustering
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.spatial.distance import pdist
from mapper import load_data, save_figure, normalize_subcategories, SUBCATEGORY_ORDER

def create_heatmap():
    # Set random seed for reproducibility
    np.random.seed(42)

    """Create overview heatmap of bias landscape"""
    # Load data and normalize subcategory names
    df = load_data()
    df = normalize_subcategories(df)

    # Aggregate data: Group by Category and Subcategory, sum Final count
    heatmap_data = df.groupby(['Category', 'Subcategory'])['Final count'].sum().reset_index()

    # Pivot to create matrix: rows=Subcategory, columns=Category
    pivot_data = heatmap_data.pivot(index='Subcategory', columns='Category', values='Final count')

    # Fill NaN with 0 (subcategories not present in some categories)
    pivot_data = pivot_data.fillna(0)

    # Reorder columns to match category order
    category_order = ['Genomics', 'Transcriptomics', 'Metabolomics', 'Proteomics',
                      'Multi-omics', 'General_omics', 'Chinese Literature']
    pivot_data = pivot_data[[col for col in category_order if col in pivot_data.columns]]

    # Apply hierarchical clustering to rows (subcategories)
    if len(pivot_data) > 1:
        # Compute linkage matrix
        row_linkage = linkage(pdist(pivot_data, metric='euclidean'), method='ward')
        # Get dendrogram order
        dendro = dendrogram(row_linkage, no_plot=True)
        row_order = dendro['leaves']
        pivot_data = pivot_data.iloc[row_order]

    # Create figure
    fig, ax = plt.subplots(figsize=(14, 10))

    # Create heatmap
    sns.heatmap(pivot_data, annot=True, fmt='.0f', cmap='YlOrRd',
                cbar_kws={'label': 'Citation Count'}, linewidths=0.5,
                linecolor='white', ax=ax, vmin=0, vmax=pivot_data.max().max())

    # Customize
    ax.set_title('Bias Landscape Across Omics Categories\n(Hierarchically Clustered by Subcategory)',
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Omics Category', fontsize=12, fontweight='bold')
    ax.set_ylabel('Bias Subcategory', fontsize=12, fontweight='bold')

    # Rotate x-axis labels
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    # Adjust y-axis labels
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=9)

    plt.tight_layout()

    # Save figure
    save_figure(fig, 'fig1_heatmap.png')

    # Print summary statistics
    print("\n=== Heatmap Summary ===")
    print(f"Total categories: {len(pivot_data.columns)}")
    print(f"Total subcategories: {len(pivot_data)}")
    print(f"Total citation count: {pivot_data.sum().sum():.0f}")
    print(f"Mean count per cell: {pivot_data.mean().mean():.2f}")
    print(f"\nTop 5 Category-Subcategory combinations:")
    # Get top combinations
    top_combos = []
    for cat in pivot_data.columns:
        for subcat in pivot_data.index:
            if pivot_data.loc[subcat, cat] > 0:
                top_combos.append((cat, subcat, pivot_data.loc[subcat, cat]))
    top_combos = sorted(top_combos, key=lambda x: x[2], reverse=True)[:5]
    for cat, subcat, count in top_combos:
        print(f"  {cat} - {subcat}: {count:.0f}")

    return fig

if __name__ == '__main__':
    create_heatmap()
