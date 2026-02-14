# Contributing Guide

This guide contains detailed information for developers and contributors working on the omics-bias project.

## System Requirements

- **Python:** 3.11 or higher (tested with Python 3.12)
- **Operating System:** macOS, Linux, or Windows
- **Memory:** At least 2GB RAM recommended
- **UV:** Latest version (for dependency management)

## Development Setup

### Using UV (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone <repository-url>
cd omics-bias

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

### Traditional Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Testing

### Running Tests

The project includes comprehensive tests to ensure reproducibility and correctness.

```bash
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/test_dependencies.py -v       # Test dependencies and data
pytest tests/test_data_validation.py -v    # Test data integrity
pytest tests/test_figure_generation.py -v  # Test figure generation (smoke tests)
```

### Test Coverage

The test suite includes:

1. **Dependency Tests** ([tests/test_dependencies.py](tests/test_dependencies.py))
   - Verifies `data/bias.csv` exists
   - Tests Kaleido PNG export functionality

2. **Data Validation Tests** ([tests/test_data_validation.py](tests/test_data_validation.py))
   - Checks CSV structure and required columns
   - Validates data integrity (no duplicates, numeric counts)
   - Ensures 7 categories are present

3. **Figure Generation Tests** ([tests/test_figure_generation.py](tests/test_figure_generation.py))
   - Verifies all 11 figure scripts exist
   - Smoke tests for main figures (fig1_heatmap.py, fig1_1_lifecycle.py)
   - Smoke tests for supplementary figures (figS1_bubble_chart.py)
   - Validates output directory structure

Expected: **11 tests passing** in ~20-70 seconds

### Adding New Tests

When adding new figure scripts or modifying existing ones:

1. Add the script name to `MAIN_FIGURES` or `SUPPLEMENTARY_FIGURES` in [tests/test_figure_generation.py](tests/test_figure_generation.py)
2. Consider adding a smoke test if the figure has unique requirements
3. Run the full test suite to ensure nothing breaks

## Project Structure

```
omics-bias/
├── data/
│   └── bias.csv              # Source data (145 biases, 2,041 citations)
├── scripts/
│   └── figures/
│       ├── mapper.py         # Centralized mappings, utilities, and color schemes
│       ├── generate_all_figures.py  # Master generation script
│       ├── fig*.py           # Individual figure scripts (main)
│       └── figS*.py          # Individual figure scripts (supplementary)
├── figures/
│   ├── main/
│   │   ├── png/              # Main figures (PNG, 300 DPI)
│   │   └── pdf/              # Main figures (PDF)
│   └── supplementary/
│       ├── png/              # Supplementary figures (PNG, 300 DPI)
│       └── pdf/              # Supplementary figures (PDF)
├── tests/
│   ├── test_dependencies.py  # Dependency and environment tests
│   ├── test_data_validation.py  # Data integrity tests
│   └── test_figure_generation.py  # Figure generation smoke tests
├── pyproject.toml            # Project configuration and dependencies
├── README.md                 # Quick start guide
├── CONTRIBUTING.md           # This file
└── figures.md                # Figure descriptions and captions
```

## Reproducibility

### Guaranteed Reproducibility

All figures use `np.random.seed(42)` for reproducible layouts and jittering. To ensure identical output across different machines:

1. **Same Python version:** Use Python 3.11 or 3.12
2. **Same dependencies:** Install using `uv` or the exact versions in [pyproject.toml](pyproject.toml)
3. **Same data:** Use the provided [data/bias.csv](data/bias.csv) (145 biases, 2,041 citations)
4. **Run from repository root:** Always run scripts from the repository root directory

### Verification Steps

Complete verification workflow:

```bash
# 1. Verify Python version
python --version  # Should be 3.11+ or 3.12+

# 2. Verify all dependencies are installed
pytest tests/test_dependencies.py -v

# 3. Verify data integrity
pytest tests/test_data_validation.py -v

# 4. Verify figure generation works
pytest tests/test_figure_generation.py -v

# 5. Generate all figures
python scripts/figures/generate_all_figures.py

# 6. Verify outputs exist
ls -lh figures/main/png/  # Should contain 8 PNG files
ls -lh figures/main/pdf/  # Should contain 8 PDF files
ls -lh figures/supplementary/png/  # Should contain 3 PNG files
ls -lh figures/supplementary/pdf/  # Should contain 3 PDF files
```

## Troubleshooting

### Common Issues

**Issue:** `ModuleNotFoundError` when running scripts
- **Solution:** Ensure you've activated your virtual environment and installed dependencies:
  ```bash
  source .venv/bin/activate
  uv pip install -e ".[dev]"
  ```

**Issue:** `kaleido` installation fails
- **Solution:** Try installing with:
  ```bash
  uv pip install kaleido==0.2.1 --force-reinstall
  ```
  Or use pip directly:
  ```bash
  pip install kaleido==0.2.1 --force-reinstall
  ```

**Issue:** Permission errors when creating output directories
- **Solution:** Ensure you have write permissions in the repository directory
  ```bash
  chmod -R u+w figures/
  ```

**Issue:** Figures look different from paper
- **Solution:** Verify you're using the correct Python version (3.11+) and have installed exact dependency versions:
  ```bash
  python --version
  uv pip list | grep -E "(pandas|numpy|matplotlib|seaborn|scipy|networkx|plotly|kaleido)"
  ```

**Issue:** Tests fail with import errors
- **Solution:** Install the package in editable mode:
  ```bash
  uv pip install -e ".[dev]"
  ```

**Issue:** UV not found
- **Solution:** Install uv:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # Then restart your shell or run:
  source $HOME/.cargo/env
  ```

### Getting Help

If you encounter issues not covered here:

1. **Check dependencies:**
   ```bash
   uv pip list | grep -E "(pandas|numpy|matplotlib|seaborn|scipy|networkx|plotly|kaleido)"
   ```

2. **Verify Python version:**
   ```bash
   python --version
   ```

3. **Run tests to identify the problem:**
   ```bash
   pytest tests/ -v
   ```

4. **Check for existing issues:**
   - Review closed/open issues in the repository
   - Search for error messages

## Dependencies

All dependencies are managed in [pyproject.toml](pyproject.toml):

### Core Dependencies
- `pandas>=2.2.0` - Data manipulation
- `numpy>=1.26.0` - Numerical computing
- `matplotlib>=3.8.0` - Plotting
- `seaborn>=0.13.0` - Statistical visualization
- `scipy>=1.11.0` - Scientific computing
- `networkx>=3.2.0` - Network analysis
- `plotly>=5.20.0` - Interactive plots
- `kaleido>=0.2.1` - Static image export

### Development Dependencies
- `pytest>=8.0.0` - Testing framework

## Code Style

- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and small
- Use the shared `mapper.py` for common functionality
- Follow existing color schemes in `CATEGORY_COLORS`

## Making Changes

1. Create a new branch for your changes
2. Make your modifications
3. Run the test suite: `pytest tests/ -v`
4. Generate all figures to verify: `python scripts/figures/generate_all_figures.py`
5. Commit your changes with clear messages
6. Submit a pull request

## Data

- **Source:** `data/bias.csv` (145 curated biases, 2,041 citations)
- **Categories:** 7 omics fields (Genomics, Transcriptomics, Proteomics, Metabolomics, Multi-omics, General_omics, Chinese Literature)
- **Format:** CSV with columns: Category, Subcategory, Final_Keyword, Final count, etc.

### Data Validation

The data is validated by tests to ensure:
- All required columns are present
- No duplicate keywords
- All counts are numeric and positive
- Exactly 7 categories exist

## Figure Documentation

See [figures.md](figures.md) for detailed descriptions and captions of all 11 figures.
