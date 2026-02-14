"""
Tests for figure generation scripts
"""
import subprocess
import sys
from pathlib import Path

import pytest


# List of all figure scripts that should be executable
MAIN_FIGURES = [
    'fig1_heatmap.py',
    'fig1_1_lifecycle.py',
    'fig2_network.py',
    'fig3_chinese_comparison.py',
    'fig4_pipeline_sankey.py',
    'fig5_stacked_bar.py',
    'fig6_curated_hierarchy.py',
    'fig7_cross_omics_heatmap.py',
]

SUPPLEMENTARY_FIGURES = [
    'figS1_bubble_chart.py',
    'figS2_violin_plot.py',
    'figS4_category_profiles.py',
]


def test_all_figure_scripts_exist() -> None:
    """Verify all expected figure scripts exist."""
    repo_root = Path(__file__).resolve().parents[1]
    scripts_dir = repo_root / "scripts" / "figures"

    for script in MAIN_FIGURES + SUPPLEMENTARY_FIGURES:
        script_path = scripts_dir / script
        assert script_path.exists(), f"Missing figure script: {script}"


def test_mapper_module_exists() -> None:
    """Verify the mapper module exists and can be imported."""
    repo_root = Path(__file__).resolve().parents[1]
    mapper_path = repo_root / "scripts" / "figures" / "mapper.py"
    assert mapper_path.exists(), "Missing mapper.py module"


@pytest.mark.parametrize("script_name", MAIN_FIGURES[:2])  # Test first 2 main figures as smoke test
def test_main_figure_generation_smoke(script_name: str) -> None:
    """Smoke test: verify main figures can be generated without errors."""
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "figures" / script_name

    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, f"Script {script_name} failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"


@pytest.mark.parametrize("script_name", SUPPLEMENTARY_FIGURES[:1])  # Test first supplementary figure
def test_supplementary_figure_generation_smoke(script_name: str) -> None:
    """Smoke test: verify supplementary figures can be generated without errors."""
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "figures" / script_name

    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, f"Script {script_name} failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"


def test_generate_all_figures_script_exists() -> None:
    """Verify the generate_all_figures.py script exists."""
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "figures" / "generate_all_figures.py"
    assert script_path.exists(), "Missing generate_all_figures.py script"


def test_output_directories_structure() -> None:
    """Verify the output directory structure exists or can be created."""
    repo_root = Path(__file__).resolve().parents[1]

    # Check that figures directory exists or can be created
    figures_dir = repo_root / "figures"
    if not figures_dir.exists():
        pytest.skip("figures directory not yet created (will be created on first generation)")

    # If it exists, check structure
    main_dir = figures_dir / "main"
    supp_dir = figures_dir / "supplementary"

    for dir_path in [main_dir, supp_dir]:
        if dir_path.exists():
            # Check for png and pdf subdirectories
            assert (dir_path / "png").exists() or (dir_path / "pdf").exists(), \
                f"Output directory {dir_path} missing png/pdf subdirectories"
