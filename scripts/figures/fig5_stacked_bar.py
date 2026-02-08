"""
Figure 5: Stacked Bar Chart - Bias Distribution by Omics Category
Shows both absolute and normalized distributions
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from utils import load_data, get_category_color, save_figure

def create_stacked_bar():
    # Set random seed for reproducibility
    np.random.seed(42)

    """Create stacked bar chart showing bias distribution"""
    # Load data
    df = load_data()

    # Simplify subcategory names for better visualization
    # Extract the general type from subcategory
    def categorize_subcategory(subcat):
        subcat_lower = subcat.lower()
        if 'data production' in subcat_lower or 'pre-analysis' in subcat_lower or 'pre analysis' in subcat_lower or 'prediction' in subcat_lower:
            return 'Data Production'
        elif 'technical' in subcat_lower or 'instrumental' in subcat_lower or 'hardware' in subcat_lower:
            return 'Technical/Instrumental'
        elif 'computational' in subcat_lower or 'analytical' in subcat_lower or 'software' in subcat_lower:
            return 'Computational/Analytical'
        elif 'reporting' in subcat_lower or 'interpretation' in subcat_lower or 'post-analysis' in subcat_lower:
            return 'Reporting/Interpretation'
        else:
            return 'Other'

    df['Subcategory_Type'] = df['Subcategory'].apply(categorize_subcategory)

    # Aggregate by Category and Subcategory Type
    grouped = df.groupby(['Category', 'Subcategory_Type'])['Final count'].sum().reset_index()

    # Pivot for stacking
    pivot = grouped.pivot(index='Category', columns='Subcategory_Type', values='Final count').fillna(0)

    # Reorder columns for consistent stacking
    subcat_order = ['Data Production', 'Technical/Instrumental',
                    'Computational/Analytical', 'Reporting/Interpretation', 'Other']
    pivot = pivot[[col for col in subcat_order if col in pivot.columns]]

    # Calculate totals for sorting
    pivot['Total'] = pivot.sum(axis=1)
    pivot = pivot.sort_values('Total', ascending=True)
    pivot = pivot.drop('Total', axis=1)

    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

    # Define colors for subcategory types
    subcat_colors = {
        'Data Production': '#3498db',
        'Technical/Instrumental': '#e67e22',
        'Computational/Analytical': '#9b59b6',
        'Reporting/Interpretation': '#2ecc71',
        'Other': '#95a5a6'
    }

    # Plot 1: Absolute counts
    pivot.plot(kind='barh', stacked=True, ax=ax1,
               color=[subcat_colors.get(col, '#95a5a6') for col in pivot.columns],
               width=0.7, edgecolor='white', linewidth=0.5)

    ax1.set_title('Absolute Citation Counts by Omics Category', fontsize=14, fontweight='bold', pad=15)
    ax1.set_xlabel('Total Citation Count', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Omics Category', fontsize=12, fontweight='bold')
    ax1.legend(title='Bias Type', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    ax1.grid(axis='x', alpha=0.3, linestyle='--')

    # Add percentage labels in white on each segment (left panel - absolute counts)
    for i, (idx, row) in enumerate(pivot.iterrows()):
        total = row.sum()
        cumulative = 0
        for col in pivot.columns:
            value = row[col]
            if value > 0:
                percentage = (value / total) * 100
                # Only show label if segment is large enough (>3% to avoid clutter)
                if percentage > 3:
                    segment_center = cumulative + (value / 2)
                    ax1.text(segment_center, i, f'{percentage:.1f}%',
                            ha='center', va='center',
                            fontsize=9, fontweight='bold',
                            color='white')
                cumulative += value

        # Add total value at the end of bar
        ax1.text(total + 1, i, f'{int(total)}', va='center', fontsize=9, fontweight='bold')

    # Plot 2: Normalized (percentage)
    pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100

    pivot_pct.plot(kind='barh', stacked=True, ax=ax2,
                   color=[subcat_colors.get(col, '#95a5a6') for col in pivot_pct.columns],
                   width=0.7, edgecolor='white', linewidth=0.5)

    ax2.set_title('Relative Distribution (%) by Omics Category', fontsize=14, fontweight='bold', pad=15)
    ax2.set_xlabel('Percentage (%)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('')  # Remove y-label for second plot
    ax2.legend(title='Bias Type', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    ax2.set_xlim(0, 100)
    ax2.grid(axis='x', alpha=0.3, linestyle='--')
    ax2.set_yticklabels([])  # Remove y-tick labels for second plot

    # Add percentage labels in white on each segment (right panel - percentages)
    for i, (idx, row) in enumerate(pivot_pct.iterrows()):
        cumulative = 0
        for col in pivot_pct.columns:
            value = row[col]
            if value > 0:
                # Only show label if segment is large enough (>3% to avoid clutter)
                if value > 3:
                    segment_center = cumulative + (value / 2)
                    ax2.text(segment_center, i, f'{value:.1f}%',
                            ha='center', va='center',
                            fontsize=9, fontweight='bold',
                            color='white')
                cumulative += value

    plt.tight_layout()

    # Save figure
    save_figure(fig, 'fig5_stacked_bar.png')

    # Print summary statistics
    print("\n=== Stacked Bar Chart Summary ===")
    print(f"\nTotal counts by category:")
    totals = pivot.sum(axis=1).sort_values(ascending=False)
    for cat, total in totals.items():
        print(f"  {cat}: {int(total)}")

    print(f"\nDominant bias type by category:")
    for cat in pivot.index:
        dominant = pivot.loc[cat].idxmax()
        pct = pivot_pct.loc[cat, dominant]
        print(f"  {cat}: {dominant} ({pct:.1f}%)")

    return fig

if __name__ == '__main__':
    create_stacked_bar()
    plt.show()
