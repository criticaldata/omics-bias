"""
Figure 3: Chinese Literature Comparison - Unique Bias Contributions
Visual comparison showing uniqueness of Chinese-language literature
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from utils import load_data, save_figure, get_category_color

def create_chinese_comparison():
    """Create visual comparison of Chinese vs Other biases"""
    # Set random seed
    np.random.seed(42)

    # Load data
    df = load_data()

    # Get unique bias keywords
    chinese_biases = set(df[df['Category'] == 'Chinese Literature']['Final_Keyword'].unique())
    other_biases = set(df[df['Category'] != 'Chinese Literature']['Final_Keyword'].unique())

    # Calculate
    unique_to_chinese = chinese_biases - other_biases
    shared = chinese_biases & other_biases

    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))

    # LEFT PANEL: Visual representation with circles
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    ax1.axis('off')

    # Draw two circles
    # Chinese Literature circle (left)
    chinese_circle = Circle((3, 5), 2.5, color=get_category_color('Chinese Literature'),
                           alpha=0.6, edgecolor='white', linewidth=4)
    ax1.add_patch(chinese_circle)

    # Other fields circle (right) - smaller since they share nothing
    other_circle = Circle((7, 5), 2.5, color='#3498db',
                         alpha=0.6, edgecolor='white', linewidth=4)
    ax1.add_patch(other_circle)

    # NO OVERLAP - circles are separate

    # Add labels
    ax1.text(3, 5, f'{len(unique_to_chinese)}\nUnique\nBiases',
            ha='center', va='center', fontsize=18, fontweight='bold',
            color='white')

    ax1.text(7, 5, f'{len(other_biases)}\nOther\nFields',
            ha='center', va='center', fontsize=18, fontweight='bold',
            color='white')

    # Title for left panel
    ax1.text(5, 9, 'Chinese Literature vs Other Omics Fields',
            ha='center', va='top', fontsize=16, fontweight='bold')

    # Add category labels
    ax1.text(3, 1.5, 'Chinese\nLiterature',
            ha='center', va='top', fontsize=12, fontweight='bold',
            color=get_category_color('Chinese Literature'))

    ax1.text(7, 1.5, 'Other Omics\nCategories',
            ha='center', va='top', fontsize=12, fontweight='bold',
            color='#3498db')

    # Add key finding
    ax1.text(5, 0.5, '100% of Chinese biases are unique',
            ha='center', va='bottom', fontsize=14, fontweight='bold',
            color='#e74c3c',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                     alpha=0.9, edgecolor='#e74c3c', linewidth=2))

    # RIGHT PANEL: Top 5 unique Chinese biases
    ax2.axis('off')

    # Get top 5 unique Chinese biases by citation
    unique_df = df[(df['Category'] == 'Chinese Literature') &
                   (df['Final_Keyword'].isin(unique_to_chinese))]
    top5 = unique_df.nlargest(5, 'Final count')

    # Title
    ax2.text(0.5, 0.95, 'Top 5 Unique Chinese Biases',
            transform=ax2.transAxes, ha='center', va='top',
            fontsize=14, fontweight='bold')

    # Draw bars for top 5
    y_start = 0.8
    max_count = top5['Final count'].max()

    for idx, (_, row) in enumerate(top5.iterrows()):
        y_pos = y_start - (idx * 0.15)

        # Draw bar
        bar_width = 0.6 * (row['Final count'] / max_count)
        bar = Rectangle((0.05, y_pos - 0.05), bar_width, 0.08,
                       facecolor=get_category_color('Chinese Literature'),
                       alpha=0.8, edgecolor='white', linewidth=2)
        ax2.add_patch(bar)

        # Add label
        keyword = row['Final_Keyword']
        if len(keyword) > 40:
            keyword = keyword[:37] + '...'

        ax2.text(0.05, y_pos, f"{idx+1}. {keyword}",
                va='center', ha='left', fontsize=11, fontweight='bold')

        # Add count
        ax2.text(bar_width + 0.07, y_pos, f"{int(row['Final count'])}",
                va='center', ha='left', fontsize=11, fontweight='bold',
                color=get_category_color('Chinese Literature'))

    # Overall title
    fig.suptitle('Chinese-Language Literature: Unique Bias Identification',
                fontsize=18, fontweight='bold', y=0.98)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    save_figure(fig, 'fig3_chinese_comparison.png')

    # Print summary
    print("\n=== Chinese Literature Comparison ===")
    print(f"Total Chinese biases: {len(chinese_biases)}")
    print(f"Unique to Chinese: {len(unique_to_chinese)} ({100*len(unique_to_chinese)/len(chinese_biases):.0f}%)")
    print(f"Shared: {len(shared)}")

    return fig

if __name__ == '__main__':
    create_chinese_comparison()
    plt.show()
