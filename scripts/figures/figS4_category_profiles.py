"""
Supplementary Figure S4: Category-Specific Bias Profiles
Small multiples showing top 10 biases for each omics category
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mapper import load_data, get_category_color, save_figure, shorten_bias, merge_semantic_keywords

def create_category_profiles():
    """Create small multiple bar charts for each category"""
    # Set random seed
    np.random.seed(42)

    # Load data and merge semantic keywords
    df = load_data()
    df = merge_semantic_keywords(df)

    # Get categories
    categories = sorted(df['Category'].unique())
    n_categories = len(categories)

    # Create figure with subplots
    fig, axes = plt.subplots(3, 3, figsize=(20, 16))
    axes = axes.flatten()

    # Plot each category
    for idx, cat in enumerate(categories):
        ax = axes[idx]
        cat_df = df[df['Category'] == cat]

        # Get top 10 biases
        top10 = cat_df.nlargest(10, 'Final count')

        # Shorten bias names using curated SHORT_NAMES
        labels = [shorten_bias(kw) for kw in top10['Final_Keyword']]

        counts = top10['Final count'].values

        # Create bars with category color
        color = get_category_color(cat)
        bars = ax.barh(range(len(labels)), counts, color=color, alpha=0.8,
                      edgecolor='white', linewidth=2)

        # Add value labels
        for i, (bar, count) in enumerate(zip(bars, counts)):
            ax.text(count + 0.5, i, f'{int(count)}',
                   va='center', fontsize=9, fontweight='bold')

        # Styling
        ax.set_yticks(range(len(labels)))
        ax.set_yticklabels(labels, fontsize=9)
        ax.set_xlabel('Citations', fontsize=10, fontweight='bold')
        ax.set_title(f'{cat}\n({len(cat_df)} biases, {int(cat_df["Final count"].sum())} citations)',
                    fontsize=12, fontweight='bold', color=color, pad=10)
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        ax.set_xlim(0, max(counts) * 1.15)

        # Invert y-axis so top bias is at top
        ax.invert_yaxis()

    # Hide unused subplots
    for idx in range(n_categories, len(axes)):
        axes[idx].axis('off')

    # Overall title
    fig.suptitle('Category-Specific Bias Profiles - Top 10 Biases per Omics Field',
                fontsize=18, fontweight='bold', y=0.995)

    plt.tight_layout(rect=[0, 0, 1, 0.99])

    # Save figure
    save_figure(fig, 'figS4_category_profiles.png', output_dir='figures/supplementary')

    # Print summary
    print("\n=== Category Profiles Summary ===")
    for cat in categories:
        cat_df = df[df['Category'] == cat]
        print(f"\n{cat}:")
        print(f"  Total biases: {len(cat_df)}")
        print(f"  Total citations: {int(cat_df['Final count'].sum())}")
        print(f"  Top bias: {cat_df.nlargest(1, 'Final count')['Final_Keyword'].values[0]} ({int(cat_df['Final count'].max())} citations)")

    return fig

if __name__ == '__main__':
    create_category_profiles()
    plt.show()
