"""
Figure 2: Network Graph - Cross-Omics Bias Relationships
Shows which specific biases appear across multiple omics fields
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from utils import load_data, get_category_color, save_figure

def create_network_graph():
    """Create network graph showing cross-omics bias relationships"""
    # Set random seed for reproducibility
    np.random.seed(42)

    # Load data
    df = load_data()

    # Create a bipartite network: Categories <-> Bias Keywords
    G = nx.Graph()

    # Track bias keywords that appear in multiple categories
    keyword_categories = {}
    for _, row in df.iterrows():
        keyword = row['Final_Keyword']
        category = row['Category']
        count = row['Final count']

        if keyword not in keyword_categories:
            keyword_categories[keyword] = []
        keyword_categories[keyword].append((category, count))

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
    spring_pos = nx.spring_layout(bias_subgraph, k=2.5, iterations=100, seed=42, scale=6)

    # Position biases on the right - closer to center
    for bias in bias_nodes:
        if bias in spring_pos:
            # Reduced scaling for better distribution
            pos[bias] = (spring_pos[bias][0] * 1.5 + 3, spring_pos[bias][1] * 1.8)

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

    # Draw bias nodes (smaller)
    # Color by number of connections (universal biases)
    bias_colors = []
    for bias in bias_nodes:
        num_connections = len([n for n in G.neighbors(bias) if n in category_nodes])
        if num_connections >= 4:  # Universal bias
            bias_colors.append('#e74c3c')  # Red for universal
        elif num_connections >= 3:
            bias_colors.append('#f39c12')  # Orange
        elif num_connections >= 2:
            bias_colors.append('#3498db')  # Blue
        else:
            bias_colors.append('#95a5a6')  # Gray

    nx.draw_networkx_nodes(G, pos, nodelist=bias_nodes,
                          node_color=bias_colors, node_size=500,
                          alpha=0.7, ax=ax, edgecolors='white', linewidths=1)

    # Draw labels
    # Category labels
    cat_labels = {n: n for n in category_nodes}
    nx.draw_networkx_labels(G, pos, cat_labels, font_size=10,
                           font_weight='bold', ax=ax)

    # Bias labels - for biases in multiple categories or high citation counts
    bias_labels = {}
    for bias in bias_nodes:
        num_connections = len([n for n in G.neighbors(bias) if n in category_nodes])
        # Get max count for this bias
        max_count = max([G[bias][cat]['weight'] for cat in G.neighbors(bias) if cat in category_nodes])

        # Show label for biases in 2+ categories OR high citation count
        if num_connections >= 2 or max_count >= 15:
            # Truncate long labels
            label = bias if len(bias) < 40 else bias[:37] + '...'
            bias_labels[bias] = label

    nx.draw_networkx_labels(G, pos, bias_labels, font_size=8, ax=ax)

    # Title and legend
    ax.set_title('Cross-Omics Bias Relationship Network\n(Node size: Category vs Bias | Edge width: Citation count)',
                 fontsize=16, fontweight='bold', pad=20)

    # Create custom legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#e74c3c', label='Universal bias (4+ fields)'),
        Patch(facecolor='#f39c12', label='Common bias (3 fields)'),
        Patch(facecolor='#3498db', label='Shared bias (2 fields)'),
        Patch(facecolor='#95a5a6', label='Field-specific bias')
    ]
    ax.legend(
        handles=legend_elements,
        loc='upper left',
        fontsize=10,
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
    plt.show()
