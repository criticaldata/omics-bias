"""
Figure 4: Enhanced Pipeline Sankey - Bias Flow Through Research Stages
Shows how biases flow through the research pipeline stages
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from mapper import (load_data, get_category_color, normalize_subcategories,
                   STAGE_MAP, merge_semantic_keywords, shorten_bias,
                   reassign_chinese_categories)

def create_pipeline_sankey():
    # Set random seed for reproducibility
    np.random.seed(42)

    """Create enhanced Sankey diagram organized by research pipeline"""
    # Load data
    df = load_data()
    df = normalize_subcategories(df)
    df = reassign_chinese_categories(df)
    df['Pipeline_Stage'] = df['Subcategory'].map(STAGE_MAP).fillna('Other Challenges')
    df = merge_semantic_keywords(df)

    # For top biases, aggregate by category, pipeline stage, and keyword
    # Focus on biases with count >= 5 to avoid clutter
    df_filtered = df[df['Final count'] >= 10].copy()

    # Create nodes
    nodes = []
    node_colors = []
    node_dict = {}
    node_index = 0

    # Stage 1: Categories (left)
    categories = sorted(df_filtered['Category'].unique())
    for cat in categories:
        node_dict[('category', cat)] = node_index
        nodes.append(cat)
        node_colors.append(get_category_color(cat))
        node_index += 1

    # Stage 2: Pipeline stages (middle)
    stages = ['Data Production', 'Technical/Instrumental', 'Computational/Analytical',
              'Reporting/Interpretation', 'Other Challenges']
    stage_colors = {
        'Data Production': '#3498db',
        'Technical/Instrumental': '#e67e22',
        'Computational/Analytical': '#9b59b6',
        'Reporting/Interpretation': '#2ecc71',
        'Other Challenges': '#95a5a6'
    }

    for stage in stages:
        node_dict[('stage', stage)] = node_index
        nodes.append(stage)
        node_colors.append(stage_colors[stage])
        node_index += 1

    # Stage 3: Top bias keywords (right) - limit to top 30 by count
    top_biases = df_filtered.nlargest(30, 'Final count')
    for _, row in top_biases.iterrows():
        keyword = row['Final_Keyword']
        if ('bias', keyword) not in node_dict:
            node_dict[('bias', keyword)] = node_index
            # Truncate long keywords
            display_name = shorten_bias(keyword)
            nodes.append(display_name)
            node_colors.append('#95a5a6')  # Gray for keywords
            node_index += 1

    # Create links
    sources = []
    targets = []
    values = []
    link_colors = []

    # Helper function to convert hex to rgba
    def hex_to_rgba(hex_color, alpha=0.3):
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f'rgba({r}, {g}, {b}, {alpha})'

    # Link 1: Category -> Pipeline Stage
    cat_stage = df_filtered.groupby(['Category', 'Pipeline_Stage'])['Final count'].sum().reset_index()
    for _, row in cat_stage.iterrows():
        cat = row['Category']
        stage = row['Pipeline_Stage']
        count = row['Final count']

        if ('category', cat) in node_dict and ('stage', stage) in node_dict:
            sources.append(node_dict[('category', cat)])
            targets.append(node_dict[('stage', stage)])
            values.append(count)
            # Color by category
            color = get_category_color(cat)
            link_colors.append(hex_to_rgba(color))

    # Link 2: Pipeline Stage -> Bias Keyword (for top biases only)
    for _, row in top_biases.iterrows():
        stage = row['Pipeline_Stage']
        keyword = row['Final_Keyword']
        count = row['Final count']

        if ('stage', stage) in node_dict and ('bias', keyword) in node_dict:
            sources.append(node_dict[('stage', stage)])
            targets.append(node_dict[('bias', keyword)])
            values.append(count)
            # Color by stage
            color = stage_colors.get(stage, '#95a5a6')
            link_colors.append(hex_to_rgba(color))

    # Create Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color='white', width=2),
            label=nodes,
            color=node_colors,
            customdata=[f"Citations: {sum([values[i] for i in range(len(sources)) if sources[i] == idx or targets[i] == idx])}"
                       for idx in range(len(nodes))],
            hovertemplate='%{label}<br>%{customdata}<extra></extra>'
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors,
            hovertemplate='%{source.label} → %{target.label}<br>Citations: %{value}<extra></extra>'
        )
    )])

    fig.update_layout(
        title=dict(
            text="Bias Flow Through Research Pipeline Stages<br><sub>Category → Pipeline Stage → Top Bias Keywords (count ≥ 10)</sub>",
            font=dict(size=20, family='Arial, sans-serif', color='#2c3e50'),
            x=0.5,
            xanchor='center'
        ),
        font=dict(size=11, family='Arial, sans-serif'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=1000,
        width=1800,
        margin=dict(l=20, r=20, t=100, b=20)
    )

    # Save figure using utility function
    from mapper import save_plotly_figure
    save_plotly_figure(fig, 'fig4_pipeline_sankey.png')

    # Print summary
    print("\n=== Pipeline Sankey Summary ===")
    print(f"Total nodes: {len(nodes)}")
    print(f"Total links: {len(sources)}")
    print(f"Total citation flow: {sum(values)}")

    # Top stages by total flow
    stage_flows = {}
    for i, (src, tgt, val) in enumerate(zip(sources, targets, values)):
        if tgt < len(categories) + len(stages) and tgt >= len(categories):
            stage_name = nodes[tgt]
            stage_flows[stage_name] = stage_flows.get(stage_name, 0) + val

    print(f"\nTotal citations by pipeline stage:")
    for stage, flow in sorted(stage_flows.items(), key=lambda x: x[1], reverse=True):
        print(f"  {stage}: {int(flow)}")

    return fig

if __name__ == '__main__':
    try:
        import plotly.graph_objects as go
        import kaleido
        create_pipeline_sankey()
    except ImportError as e:
        print(f"Missing library: {e}")
        print("Installing required libraries...")
        import subprocess
        subprocess.run(['pip', 'install', 'plotly', 'kaleido'], check=True)
        create_pipeline_sankey()
