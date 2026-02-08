# Omics Bias Paper - Figure Generation

Generate all 11 figures (8 main + 3 supplementary) for the omics bias systematic review paper.

## Quick Start

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# Generate all figures
python scripts/figures/generate_all_figures.py
```

That's it! Your figures will be in:
- `figures/main/png/` and `figures/main/pdf/` (8 main figures)
- `figures/supplementary/png/` and `figures/supplementary/pdf/` (3 supplementary figures)

## Requirements

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager

## Generate Individual Figures

```bash
cd scripts/figures

# Main figures
python fig1_heatmap.py              # Figure 1: Overview Heatmap
python fig1_1_lifecycle.py          # Figure 1.1: Lifecycle Diagram
python fig2_network.py              # Figure 2: Network Graph
python fig3_chinese_comparison.py   # Figure 3: Chinese Literature Comparison
python fig4_pipeline_sankey.py      # Figure 4: Pipeline Sankey
python fig5_stacked_bar.py          # Figure 5: Stacked Bar Chart
python fig6_curated_hierarchy.py    # Figure 6: Curated Hierarchy (Sunburst)
python fig7_cross_omics_heatmap.py  # Figure 7: Cross-Omics Heatmap

# Supplementary figures
python figS1_bubble_chart.py        # Supplementary S1: Bubble Chart
python figS2_violin_plot.py         # Supplementary S2: Violin Plot
python figS4_category_profiles.py   # Supplementary S4: Category Profiles
```

## Verify Installation

```bash
pytest tests/ -v
```

All 11 tests should pass. If you encounter issues, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Data

Source data: `data/bias.csv` (145 curated biases, 2,041 citations across 7 omics fields)

## More Information

- **Figure descriptions:** See [figures.md](figures.md)
- **Development & testing:** See [CONTRIBUTING.md](CONTRIBUTING.md)
- **Dependencies:** See [pyproject.toml](pyproject.toml)
