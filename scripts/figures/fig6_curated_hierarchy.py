"""
Figure 6: Curated Bias Hierarchy - Sunburst Visualization
Clearer hierarchical view using sunburst chart instead of treemap
"""
import pandas as pd
import plotly.graph_objects as go
from mapper import load_data, get_category_color, save_plotly_figure, normalize_subcategories
import numpy as np

def create_curated_hierarchy():
    """Create sunburst visualization of curated biases - easier to understand"""
    # Set random seed for reproducibility
    np.random.seed(42)

    # Load data
    df = load_data()

    # Focus on the specified columns
    df_curated = df[['Category', 'Subcategory', 'Final_Keyword', 'Final count']].copy()
    df_curated = df_curated.dropna(subset=['Final_Keyword', 'Final count'])
    df_curated = normalize_subcategories(df_curated)

    # Create data for sunburst
    labels = []
    parents = []
    values = []
    colors = []

    # Root
    labels.append("All Omics Biases")
    parents.append("")
    values.append(df_curated['Final count'].sum())
    colors.append("#ecf0f1")

    # Add categories
    for cat in df_curated['Category'].unique():
        cat_df = df_curated[df_curated['Category'] == cat]
        labels.append(cat)
        parents.append("All Omics Biases")
        values.append(cat_df['Final count'].sum())
        colors.append(get_category_color(cat))

    # Add subcategories
    for cat in df_curated['Category'].unique():
        cat_df = df_curated[df_curated['Category'] == cat]
        for subcat in cat_df['Subcategory'].unique():
            subcat_df = cat_df[cat_df['Subcategory'] == subcat]

            # Shorten subcategory name
            short_subcat = subcat if len(subcat) < 30 else subcat[:27] + '...'

            labels.append(short_subcat)
            parents.append(cat)
            values.append(subcat_df['Final count'].sum())
            colors.append(get_category_color(cat))

    # Create sunburst
    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",
        marker=dict(
            colors=colors,
            line=dict(color='white', width=2)
        ),
        hovertemplate='<b>%{label}</b><br>Citations: %{value}<br><extra></extra>',
        textfont=dict(size=13, family='Arial, sans-serif', color='white')
    ))

    fig.update_layout(
        title=dict(
            text='Curated Bias Hierarchy<br><sub>Center → Categories → Subcategories (by citation count)</sub>',
            x=0.5,
            xanchor='center',
            font=dict(size=20)
        ),
        width=1400,
        height=1400,
        font=dict(size=14)
    )

    # Save figure
    save_plotly_figure(fig, 'fig6_curated_hierarchy.png')

    # Print summary
    print("\n=== Curated Bias Hierarchy Summary ===")
    print(f"Total biases: {len(df_curated)}")
    print(f"Total categories: {df_curated['Category'].nunique()}")
    print(f"Total subcategories: {df_curated['Subcategory'].nunique()}")
    print(f"Total citations: {df_curated['Final count'].sum():.0f}")

    print("\nTop 5 categories by citations:")
    cat_totals = df_curated.groupby('Category')['Final count'].sum().sort_values(ascending=False)
    for cat, total in cat_totals.head(5).items():
        print(f"  {cat}: {int(total)} citations")

    return fig

if __name__ == '__main__':
    create_curated_hierarchy()
