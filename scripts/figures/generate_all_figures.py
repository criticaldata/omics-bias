"""
Master script to generate all figures for the omics bias paper
Run this script to regenerate all main and supplementary figures
"""
import sys
import time
from pathlib import Path

print("=" * 70)
print("OMICS BIAS PAPER - FIGURE GENERATION")
print("=" * 70)
print()

# Track generation times
start_time = time.time()
figure_times = {}

# List of figure scripts to run
main_figures = [
    ('fig1_heatmap.py', 'Figure 1: Overview Heatmap'),
    ('fig1_1_lifecycle.py', 'Figure 1.1: Lifecycle Diagram'),
    ('fig1_2_pipeline_bars.py', 'Figure 1.2: Pipeline Bars'),
    ('fig2_network.py', 'Figure 2: Network Graph'),
    ('fig3_chinese_comparison.py', 'Figure 3: Chinese Literature Comparison'),
    ('fig4_pipeline_sankey.py', 'Figure 4: Pipeline Sankey'),
    ('fig5_stacked_bar.py', 'Figure 5: Stacked Bar Chart'),
    ('fig6_curated_hierarchy.py', 'Figure 6: Curated Bias Hierarchy'),
    ('fig7_cross_omics_heatmap.py', 'Figure 7: Cross-Omics Heatmap'),
]

supplementary_figures = [
    ('figS1_bubble_chart.py', 'Supplementary Figure S1: Bubble Chart'),
    ('figS2_violin_plot.py', 'Supplementary Figure S2: Violin Plot'),
    ('figS3_aggregated_violins.py', 'Supplementary Figure S3: Aggregated Category Violins'),
    ('figS4_category_profiles.py', 'Supplementary Figure S4: Category Profiles'),
]

def run_figure_script(script_name, description):
    """Run a figure generation script"""
    print(f"\n{'='*70}")
    print(f"Generating: {description}")
    print(f"Script: {script_name}")
    print(f"{'='*70}")

    fig_start = time.time()

    try:
        # Run the script using subprocess
        import subprocess
        script_path = Path(__file__).parent / script_name
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            check=True
        )

        fig_end = time.time()
        elapsed = fig_end - fig_start
        figure_times[description] = elapsed

        print(f"\n✓ Successfully generated in {elapsed:.2f} seconds")
        return True

    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error generating figure: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False
    except Exception as e:
        print(f"\n✗ Error generating figure: {e}")
        import traceback
        traceback.print_exc()
        return False

# Generate main figures
print("\n" + "="*70)
print("GENERATING MAIN FIGURES")
print("="*70)

main_success = 0
for script, desc in main_figures:
    if run_figure_script(script, desc):
        main_success += 1

# Generate supplementary figures
print("\n" + "="*70)
print("GENERATING SUPPLEMENTARY FIGURES")
print("="*70)

supp_success = 0
for script, desc in supplementary_figures:
    if run_figure_script(script, desc):
        supp_success += 1

# Print summary
end_time = time.time()
total_time = end_time - start_time

print("\n" + "="*70)
print("GENERATION SUMMARY")
print("="*70)
print(f"\nMain figures: {main_success}/{len(main_figures)} successful")
print(f"Supplementary figures: {supp_success}/{len(supplementary_figures)} successful")
print(f"\nTotal time: {total_time:.2f} seconds")

print("\nGeneration times by figure:")
for desc, elapsed in sorted(figure_times.items(), key=lambda x: x[1], reverse=True):
    print(f"  {desc}: {elapsed:.2f}s")

# List output files
print("\n" + "="*70)
print("OUTPUT FILES")
print("="*70)

project_root = Path(__file__).parent.parent.parent
main_dir = project_root / 'figures' / 'main'
supp_dir = project_root / 'figures' / 'supplementary'

print(f"\nMain figures ({main_dir}):")
if main_dir.exists():
    for file in sorted(main_dir.glob('*')):
        size_kb = file.stat().st_size / 1024
        print(f"  {file.name} ({size_kb:.1f} KB)")

print(f"\nSupplementary figures ({supp_dir}):")
if supp_dir.exists():
    for file in sorted(supp_dir.glob('*')):
        size_kb = file.stat().st_size / 1024
        print(f"  {file.name} ({size_kb:.1f} KB)")

print("\n" + "="*70)
print("ALL FIGURES GENERATED SUCCESSFULLY!")
print("="*70)
