"""
Figure 7: Cross-Omics Bias Landscape Heatmap
Shows frequency of bias categories across omics domains
Based on bias.csv data
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from utils import load_data, save_figure, get_category_color, normalize_subcategories, SUBCATEGORY_ORDER

def create_cross_omics_heatmap():
    """Create heatmap showing bias distribution across omics categories"""
    # Set random seed for reproducibility
    np.random.seed(42)

    # Load data and normalize subcategory names
    df = load_data()
    df = normalize_subcategories(df)

    # Create frequency matrix using CITATION COUNTS, not just counts of biases
    freq_matrix = df.groupby(['Subcategory', 'Category'])['Final count'].sum().unstack(fill_value=0)

    # Order categories for better visualization
    category_order = ['Genomics', 'Transcriptomics', 'Proteomics', 'Metabolomics',
                      'Multi-omics', 'General_omics', 'Chinese Literature']

    # Reorder columns
    freq_matrix = freq_matrix[[col for col in category_order if col in freq_matrix.columns]]

    # Reorder rows by pipeline stage
    freq_matrix = freq_matrix.reindex([s for s in SUBCATEGORY_ORDER if s in freq_matrix.index])

    # Create figure
    fig, ax = plt.subplots(figsize=(14, 10))

    # Create heatmap
    sns.heatmap(freq_matrix, annot=True, fmt='d', cmap='YlOrRd',
                cbar_kws={'label': 'Number of Biases'},
                linewidths=0.5, linecolor='white',
                ax=ax, square=False, vmin=0)

    # Customize
    ax.set_xlabel('Omics Category', fontsize=13, fontweight='bold', labelpad=10)
    ax.set_ylabel('Bias Subcategory', fontsize=13, fontweight='bold', labelpad=10)
    ax.set_title('Cross-Omics Bias Landscape\nFrequency of Bias Types Across Omics Domains',
                 fontsize=16, fontweight='bold', pad=20)

    # Rotate labels
    plt.xticks(rotation=45, ha='right', fontsize=11)
    plt.yticks(rotation=0, fontsize=11)

    plt.tight_layout()

    # Save figure
    save_figure(fig, 'fig7_cross_omics_heatmap.png')

    # Print summary statistics
    print("\n=== Cross-Omics Heatmap Summary ===")
    print(f"Categories analyzed: {freq_matrix.shape[1]}")
    print(f"Subcategories analyzed: {freq_matrix.shape[0]}")
    print(f"\nTotal biases per category:")
    for col in freq_matrix.columns:
        total = freq_matrix[col].sum()
        print(f"  {col}: {total}")
    print(f"\nTotal biases per subcategory:")
    for idx in freq_matrix.index:
        total = freq_matrix.loc[idx].sum()
        print(f"  {idx}: {total}")

    # Find most common bias types
    print(f"\nMost common bias subcategory-category combinations:")
    flat_data = []
    for subcat in freq_matrix.index:
        for cat in freq_matrix.columns:
            val = freq_matrix.loc[subcat, cat]
            if val > 0:
                flat_data.append((subcat, cat, val))

    flat_data.sort(key=lambda x: x[2], reverse=True)
    for subcat, cat, count in flat_data[:10]:
        print(f"  {subcat} × {cat}: {count} biases")

    return fig

if __name__ == '__main__':
    create_cross_omics_heatmap()
    plt.show()
