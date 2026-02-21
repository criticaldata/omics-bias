"""
Figure 2: Network Graph - Cross-Omics Bias Relationships
Shows which specific biases appear across multiple omics fields
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from mapper import (load_data, get_category_color, save_figure,
                    shorten_bias, normalize_subcategories, STAGE_MAP, STAGE_COLORS,
                    merge_semantic_keywords)

def create_network_graph():
    """Create network graph showing cross-omics bias relationships"""
    # Set random seed for reproducibility
    np.random.seed(42)

    # Load data, normalize subcategories, and merge semantic keywords
    df = load_data()
    df = normalize_subcategories(df)
    df['Stage'] = df['Subcategory'].map(STAGE_MAP).fillna('Other Challenges')
    df = merge_semantic_keywords(df)

    # Create a bipartite network: Categories <-> Bias Keywords
    G = nx.Graph()

    # Track bias keywords that appear in multiple categories
    keyword_categories = {}
    # Track primary stage for each keyword (from highest-count row)
    keyword_stage = {}
    for _, row in df.iterrows():
        keyword = row['Final_Keyword']
        category = row['Category']
        count = row['Final count']
        stage = row['Stage']

        if keyword not in keyword_categories:
            keyword_categories[keyword] = []
        keyword_categories[keyword].append((category, count))

        # Assign stage from highest-count occurrence
        if keyword not in keyword_stage or count > keyword_stage[keyword][1]:
            keyword_stage[keyword] = (stage, count)

    # Add nodes and edges
    # Category nodes
    categories = df['Category'].unique()
    for cat in categories:
        G.add_node(cat, node_type='category', color=get_category_color(cat))

    # Bias keyword nodes - only add keywords that appear in multiple categories
    # or have high citation counts (>=10)
    for keyword, cat_list in keyword_categories.items():
        # Add keyword if it appears in multiple categories OR has high count
        max_count = max([count for _, count in cat_list])
        if len(cat_list) >= 2 or max_count >= 15:
            G.add_node(keyword, node_type='bias', color='#95a5a6')  # Gray

            # Add edges from keyword to categories
            for category, count in cat_list:
                if category in G.nodes():
                    G.add_edge(category, keyword, weight=count)

    # Layout
    # Use bipartite layout with categories on left, biases on right
    category_nodes = [n for n, attr in G.nodes(data=True) if attr.get('node_type') == 'category']
    bias_nodes = [n for n, attr in G.nodes(data=True) if attr.get('node_type') == 'bias']

    # Create circular layout for categories, then position biases
    pos = {}

    # Categories spread vertically on the left
    cat_y = np.linspace(-6, 6, len(category_nodes))
    for i, cat in enumerate(category_nodes):
        pos[cat] = (-4, cat_y[i])

    # Use spring layout for bias nodes - tighter clustering
    bias_subgraph = G.subgraph(bias_nodes + category_nodes)
    spring_pos = nx.spring_layout(bias_subgraph, k=3.5, iterations=150, seed=42, scale=7)

    # Position biases on the right - closer to center
    for bias in bias_nodes:
        if bias in spring_pos:
            # Reduced scaling for better distribution
            pos[bias] = (spring_pos[bias][0] * 1.8 + 3.5, spring_pos[bias][1] * 2.0)

    # Create figure - slightly smaller since nodes are closer
    fig, ax = plt.subplots(figsize=(20, 16))

    # Draw edges with varying thickness
    edges = G.edges()
    weights = [G[u][v]['weight'] for u, v in edges]
    max_weight = max(weights) if weights else 1

    # Normalize widths
    edge_widths = [0.5 + (w / max_weight) * 3 for w in weights]

    nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.3, edge_color='gray', ax=ax)

    # Draw category nodes (larger)
    cat_colors = [G.nodes[n]['color'] for n in category_nodes]
    nx.draw_networkx_nodes(G, pos, nodelist=category_nodes,
                          node_color=cat_colors, node_size=2000,
                          alpha=0.9, ax=ax, edgecolors='white', linewidths=2)

    # Draw bias nodes - color by subcategory (pipeline stage), size by universality
    bias_colors = []
    bias_sizes = []
    for bias in bias_nodes:
        # Color by pipeline stage
        stage = keyword_stage.get(bias, ('Other Challenges', 0))[0]
        bias_colors.append(STAGE_COLORS.get(stage, '#95a5a6'))
        # Size by number of connected categories (universality)
        num_connections = len([n for n in G.neighbors(bias) if n in category_nodes])
        bias_sizes.append(300 + num_connections * 150)  # 450 (1 field) to 900+ (4+ fields)

    nx.draw_networkx_nodes(G, pos, nodelist=bias_nodes,
                          node_color=bias_colors, node_size=bias_sizes,
                          alpha=0.8, ax=ax, edgecolors='white', linewidths=1)

    # Draw labels
    # Category labels
    cat_labels = {n: n for n in category_nodes}
    nx.draw_networkx_labels(G, pos, cat_labels, font_size=10,
                           font_weight='bold', ax=ax)

    # Bias labels - for biases in multiple categories or high citation counts
    bias_labels = {}
    for bias in bias_nodes:
        num_connections = len([n for n in G.neighbors(bias) if n in category_nodes])
        max_count = max([G[bias][cat]['weight'] for cat in G.neighbors(bias) if cat in category_nodes])

        # Show label for biases in 2+ categories OR high citation count
        if num_connections >= 2 or max_count >= 15:
            bias_labels[bias] = shorten_bias(bias)

    # Render bias labels with bbox backgrounds for readability
    for node, label in bias_labels.items():
        x, y = pos[node]
        ax.text(
            x, y + 0.35, label,
            fontsize=7, ha='center', va='bottom',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                      alpha=0.85, edgecolor='#cccccc', linewidth=0.5),
        )

    # Title and legend
    ax.set_title('Cross-Omics Bias Relationship Network\n'
                 '(Node color: Pipeline stage | Node size: Cross-field universality | Edge width: Citation count)',
                 fontsize=16, fontweight='bold', pad=20)

    # Create custom legend for pipeline stage colors
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    legend_elements = [
        Patch(facecolor=color, label=stage, alpha=0.8)
        for stage, color in STAGE_COLORS.items()
    ]
    # Add node size legend entries
    legend_elements.append(Line2D([0], [0], marker='o', color='w', markerfacecolor='gray',
                                  markersize=8, label='1 field (specific)'))
    legend_elements.append(Line2D([0], [0], marker='o', color='w', markerfacecolor='gray',
                                  markersize=14, label='4+ fields (universal)'))
    ax.legend(
        handles=legend_elements,
        loc='upper left',
        fontsize=9,
        bbox_to_anchor=(0, 0.98),
        frameon=True,
        fancybox=True,
        borderaxespad=0,
    )

    ax.axis('off')
    plt.tight_layout()

    # Save figure
    save_figure(fig, 'fig2_network.png')

    # Print summary statistics
    print("\n=== Network Graph Summary ===")
    print(f"Total nodes: {G.number_of_nodes()}")
    print(f"Category nodes: {len(category_nodes)}")
    print(f"Bias nodes: {len(bias_nodes)}")
    print(f"Total edges: {G.number_of_edges()}")

    # Universal biases (appear in 4+ categories)
    universal_biases = []
    for bias in bias_nodes:
        num_connections = len([n for n in G.neighbors(bias) if n in category_nodes])
        if num_connections >= 4:
            universal_biases.append((bias, num_connections))

    print(f"\nUniversal biases (appearing in 4+ categories):")
    for bias, count in sorted(universal_biases, key=lambda x: x[1], reverse=True):
        print(f"  {bias}: {count} categories")

    return fig

if __name__ == '__main__':
    create_network_graph()
