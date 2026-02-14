"""
Figure 3: Chinese Literature Comparison - Bias Overlap After Harmonization
Venn-style diagram showing shared vs unique biases after keyword harmonization
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from mapper import load_data, save_figure, get_category_color, normalize_chinese_keywords, shorten_bias

def create_chinese_comparison():
    """Create visual comparison of Chinese vs Other biases after harmonization"""
    # Set random seed
    np.random.seed(42)

    # Load data and harmonize Chinese keywords
    df = load_data()
    df = normalize_chinese_keywords(df)

    # Get unique bias keywords
    chinese_biases = set(df[df['Category'] == 'Chinese Literature']['Final_Keyword'].unique())
    other_biases = set(df[df['Category'] != 'Chinese Literature']['Final_Keyword'].unique())

    # Calculate overlap
    unique_to_chinese = chinese_biases - other_biases
    shared = chinese_biases & other_biases
    unique_to_other = other_biases - chinese_biases

    n_unique = len(unique_to_chinese)
    n_shared = len(shared)
    n_total_chinese = len(chinese_biases)
    pct_shared = 100 * n_shared / n_total_chinese
    pct_unique = 100 * n_unique / n_total_chinese

    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))

    # LEFT PANEL: Venn-style overlapping circles
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    ax1.axis('off')

    # Overlapping circles (offset controls overlap amount)
    chinese_circle = Circle((3.8, 5), 2.5,
                           facecolor=get_category_color('Chinese Literature'),
                           alpha=0.5, edgecolor='white', linewidth=4)
    ax1.add_patch(chinese_circle)

    other_circle = Circle((6.2, 5), 2.5, facecolor='#3498db',
                         alpha=0.5, edgecolor='white', linewidth=4)
    ax1.add_patch(other_circle)

    # Labels: unique Chinese (left), shared (center), unique other (right)
    ax1.text(2.5, 5, f'{n_unique}\nUnique',
            ha='center', va='center', fontsize=18, fontweight='bold',
            color='white')

    ax1.text(5, 5, f'{n_shared}\nShared',
            ha='center', va='center', fontsize=18, fontweight='bold',
            color='#2C3E50')

    ax1.text(7.5, 5, f'{len(unique_to_other)}\nUnique',
            ha='center', va='center', fontsize=16, fontweight='bold',
            color='white')

    # Title for left panel
    ax1.text(5, 9, 'Chinese Literature vs Other Omics Fields\n(After Keyword Harmonization)',
            ha='center', va='top', fontsize=15, fontweight='bold')

    # Category labels below circles
    ax1.text(3.8, 1.5, 'Chinese\nLiterature',
            ha='center', va='top', fontsize=12, fontweight='bold',
            color=get_category_color('Chinese Literature'))

    ax1.text(6.2, 1.5, 'Other Omics\nCategories',
            ha='center', va='top', fontsize=12, fontweight='bold',
            color='#3498db')

    # Key finding
    ax1.text(5, 0.5,
            f'{pct_shared:.0f}% shared, {pct_unique:.0f}% unique ({n_unique} of {n_total_chinese})',
            ha='center', va='bottom', fontsize=14, fontweight='bold',
            color='#2C3E50',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#f0f0f0',
                     alpha=0.9, edgecolor='#2C3E50', linewidth=2))

    # RIGHT PANEL: Top unique Chinese biases (the truly unique ones)
    ax2.axis('off')

    # Get the truly unique Chinese biases (un-harmonized originals for display)
    df_raw = load_data()  # reload without harmonization for original names
    unique_df = df_raw[(df_raw['Category'] == 'Chinese Literature') &
                       (df_raw['Final_Keyword'].isin(unique_to_chinese))]
    top_unique = unique_df.nlargest(5, 'Final count')

    # Title
    ax2.text(0.5, 0.95, f'Truly Unique Chinese Biases ({n_unique})',
            transform=ax2.transAxes, ha='center', va='top',
            fontsize=14, fontweight='bold')

    if len(top_unique) > 0:
        y_start = 0.8
        max_count = top_unique['Final count'].max()

        for idx, (_, row) in enumerate(top_unique.iterrows()):
            y_pos = y_start - (idx * 0.15)

            # Draw bar
            bar_width = 0.6 * (row['Final count'] / max_count)
            bar = Rectangle((0.05, y_pos - 0.05), bar_width, 0.08,
                           facecolor=get_category_color('Chinese Literature'),
                           alpha=0.8, edgecolor='white', linewidth=2)
            ax2.add_patch(bar)

            # Add label
            keyword = shorten_bias(row['Final_Keyword'])

            ax2.text(0.05, y_pos, f"{idx+1}. {keyword}",
                    va='center', ha='left', fontsize=11, fontweight='bold')

            # Add count
            ax2.text(bar_width + 0.07, y_pos, f"{int(row['Final count'])}",
                    va='center', ha='left', fontsize=11, fontweight='bold',
                    color=get_category_color('Chinese Literature'))
    else:
        ax2.text(0.5, 0.5, 'No truly unique biases\nafter harmonization',
                transform=ax2.transAxes, ha='center', va='center',
                fontsize=14, color='gray')

    # Overall title
    fig.suptitle('Chinese-Language Literature: Bias Overlap After Harmonization',
                fontsize=18, fontweight='bold', y=0.98)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    save_figure(fig, 'fig3_chinese_comparison.png')

    # Print summary
    print("\n=== Chinese Literature Comparison (Harmonized) ===")
    print(f"Total Chinese biases: {n_total_chinese}")
    print(f"Shared with other fields: {n_shared} ({pct_shared:.0f}%)")
    print(f"Unique to Chinese: {n_unique} ({pct_unique:.0f}%)")
    print(f"\nShared keywords: {sorted(shared)}")
    print(f"Unique keywords: {sorted(unique_to_chinese)}")

    return fig

if __name__ == '__main__':
    create_chinese_comparison()
    plt.show()
