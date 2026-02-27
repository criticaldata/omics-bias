"""
Centralized mappings and utilities for figure generation.

All normalization maps (subcategory, Chinese keywords, semantic merging,
short display names) live here to ensure cross-figure consistency.
"""
import pandas as pd
import numpy as np
from pathlib import Path

# Define consistent color scheme for all figures
CATEGORY_COLORS = {
    'Genomics': '#3498db',  # Blue
    'Transcriptomics': '#2ecc71',  # Green
    'Metabolomics': '#e67e22',  # Orange
    'Proteomics': '#9b59b6',  # Purple
    'Multi-omics': '#e74c3c',  # Red
    'General Omics': '#f39c12',  # Yellow/Gold (Q11: display name for General_omics)
    'General_omics': '#f39c12',  # Legacy alias — CSV uses underscore form
    'Chinese Literature': '#1abc9c'  # Teal
}

# Mapping of curator-specific subcategory names → 5 canonical pipeline stages
SUBCATEGORY_MAP = {
    # Data Production
    "Data production bias": "Data Production Biases",
    "Data Production/Pre Analysis Bias": "Data Production Biases",
    # Q8: "Prediction" aspect also touches Computational/Analytical, but team
    # agreed to keep 1:1 mapping here and note the dual nature in paper text.
    "Data / Prediction Biases": "Data Production Biases",
    "Data Production / Pre-Analytical Biases": "Data Production Biases",
    "Data Production Biases": "Data Production Biases",
    # Technical / Instrumental
    "Technical/Instrumental biases": "Technical / Instrumental Biases",
    "Instrumental / Technical / Hardware Bias": "Technical / Instrumental Biases",
    "Instrumental / Technical / Hardware Biases": "Technical / Instrumental Biases",
    "Technical / Instrumental Biases": "Technical / Instrumental Biases",
    # Computational / Analytical
    "Computational/Analytical Bias": "Computational / Analytical Biases",
    "Analytical / Software / Computational Bias": "Computational / Analytical Biases",
    "Analytical / Software Biases": "Computational / Analytical Biases",
    "Computational / Analytical Biases": "Computational / Analytical Biases",
    # Reporting / Interpretation
    "Bias in Interpretation / Post-Analysis": "Reporting / Interpretation Biases",
    "Reporting / Interpretation / Post-Analysis Bias": "Reporting / Interpretation Biases",
    "Reporting / Interpretation / Post-Analysis Biases": "Reporting / Interpretation Biases",
    # Other
    "Other Biases / Challenges": "Other Biases / Challenges",
    "Other Biases / Challenges / Limitations": "Other Biases / Challenges",
}

SUBCATEGORY_ORDER = [
    "Data Production Biases",
    "Technical / Instrumental Biases",
    "Computational / Analytical Biases",
    "Reporting / Interpretation Biases",
    "Other Biases / Challenges",
]


# Canonical subcategory → short pipeline stage label (for lifecycle diagrams, Sankey, etc.)
STAGE_MAP = {
    'Data Production Biases': 'Data Production',
    'Technical / Instrumental Biases': 'Technical/Instrumental',
    'Computational / Analytical Biases': 'Computational/Analytical',
    'Reporting / Interpretation Biases': 'Reporting/Interpretation',
    'Other Biases / Challenges': 'Other Challenges',
}

STAGE_COLORS = {
    'Data Production': '#5DADE2',
    'Technical/Instrumental': '#F39C12',
    'Computational/Analytical': '#9B59B6',
    'Reporting/Interpretation': '#48C9B0',
    'Other Challenges': '#EC7063',
}

# Chinese Literature keyword → equivalent keyword in another category.
# Chinese curators used different phrasing for the same bias concepts.
# This mapping is applied at figure generation time (CSV is not modified).
# Keywords NOT listed here are truly unique to Chinese Literature.
CHINESE_KEYWORD_MAP = {
    # Data Production
    "Participation–power limitation": "Sample size/underpowered",
    "Handling-related variability bias": "Sample Handling, Quality & Degradation",
    # "Context-driven missingness bias" → UNIQUE (systemic exclusion of 80% of
    #   uncultured microbial life ≠ stochastic RNA dropout in Transcriptomics
    #   — confirmed by Yichun, 2026-02-16)
    "Small Sample Size & Recruitment Barriers": "Sample size/underpowered",
    "Population Underrepresentation": "Ancestry/Population Bias",
    # Technical / Instrumental
    "Short-read sequencing limitations": "Sequencing Technology Limitations",
    "Allelic dropout & coverage bias": (
        "Detection/capture limitations (low RNA capture, dropout in scRNA-seq, "
        "incomplete coverage in WES/WGS, low-abundance molecules)"
    ),
    "Batch effects & platform variability": "Platform Variability & Batch Effects",
    "Metabolomics technical limits": (
        "Platform differences & Sensitivity, Specificity & Coverage Limitations"
    ),
    "Database-driven coverage gaps": "Reference Database Gaps & Errors",
    # Computational / Analytical
    "Database dependence & annotation bias": "Database/Annotation Gaps & Standardization",
    "Subjectivity in analysis thresholds": "Lack of Standardization",
    "Reference Genome & Database Bias": "Reference Database Gaps & Errors",
    "Data Integration Challenges": "Data Integration & Pipeline Issues",
    # "Haplotype phasing & complex admixture errors" → UNIQUE (Ancestral Lineage
    #   Masking: inability of standard pipelines to handle deep evolutionary
    #   histories unique to Asian high-altitude/isolated populations, e.g. EPAS1
    #   — confirmed by Yichun, 2026-02-16)
    # Reporting / Interpretation
    "Clinical translation barriers": "Misaligned translation paradigm",
    # Other
    "Reproducibility & validation gaps": "Reproducibility, Validation & Cost",
    # "Taxonomic & naming conflicts" → UNIQUE (TCM-Specific Compound Deficit:
    #   standard libraries HMDB/METLIN biased toward Western diets/synthetic drugs,
    #   creating blind spot for Traditional Chinese Medicine
    #   — confirmed by Yichun, 2026-02-16)
    # "Ethical, Consent & Cultural Barriers" → UNIQUE (sociological mistrust in
    #   Indigenous/rural communities ≠ legal/technical GDPR/HIPAA data restriction
    #   — confirmed by Yichun, 2026-02-16)
    "Resource Inequality & Economic Barriers": "High cost / resource barriers",
}

# Chinese Literature keyword → target omics category for redistribution.
# Used by figures that show per-category breakdowns (Sankey, category profiles)
# so Chinese Literature data flows into the owning omics category instead of
# appearing as a separate meta-review category.
CHINESE_CATEGORY_REASSIGN = {
    # → Genomics (5)
    "Participation–power limitation": "Genomics",
    "Small Sample Size & Recruitment Barriers": "Genomics",
    "Population Underrepresentation": "Genomics",
    "Short-read sequencing limitations": "Genomics",
    "Haplotype phasing & complex admixture errors": "Genomics",
    # → Multi-omics (4)
    "Handling-related variability bias": "Multi-omics",
    "Allelic dropout & coverage bias": "Multi-omics",
    "Data Integration Challenges": "Multi-omics",
    "Clinical translation barriers": "Multi-omics",
    # → Metabolomics (2)
    "Metabolomics technical limits": "Metabolomics",
    "Taxonomic & naming conflicts": "Metabolomics",
    # → Proteomics (1)
    "Database dependence & annotation bias": "Proteomics",
    # → General Omics (8) — shared across categories or truly unique
    "Batch effects & platform variability": "General Omics",
    "Database-driven coverage gaps": "General Omics",
    "Subjectivity in analysis thresholds": "General Omics",
    "Reference Genome & Database Bias": "General Omics",
    "Reproducibility & validation gaps": "General Omics",
    "Resource Inequality & Economic Barriers": "General Omics",
    "Context-driven missingness bias": "General Omics",
    "Ethical, Consent & Cultural Barriers": "General Omics",
}

# Short display names for long bias keywords (used in labels, legends, etc.)
SHORT_NAMES = {
    "Sample & Cohort Heterogeneity": "Sample Heterogeneity",
    "Cohort Heterogeneity & Confounders": "Cohort Confounders",
    "Sample Heterogeneity & Variability": "Sample Variability",
    "Pre-analytical Variability": "Pre-analytical Variability",
    "Dropout Events / Sparsity": "Dropout / Sparsity",
    "Batch effects &  Instrument Differences": "Batch Effects",
    "Platform Variability & Batch Effects": "Platform Variability",
    "Short-read sequencing limitations": "Short-read Limitations",
    "RNA Degradation & Quality": "RNA Degradation",
    "Sample Prep & Extraction Bias": "Sample Prep Bias",
    "batch correction / effects & Metabolite Annotation": "Batch Correction",
    "Pipeline Heterogeneity & Lack of Standardization": "Pipeline Heterogeneity",
    "Data Integration & Pipeline Issues": "Data Integration",
    "Normalization & Batch Correction": "Normalization Issues",
    "Reference Database Gaps & Errors": "Database Gaps",
    "lack of transparency in methods & Reproducibility": "Methods Transparency",
    "Interpretability & Black-Box Models": "Black-Box Models",
    "Publication bias": "Publication Bias",
    "Reproducibility & Correlation/Causation": "Reproducibility Issues",
    "Incomplete Metadata/Methods Reporting": "Incomplete Metadata",
    "Lack of Standardization & Interoperability": "Standardization Gaps",
    "Data Sharing, Privacy & Regulatory Barriers": "Privacy & Regulation",
    "Lack of Standardization & Benchmarks": "Benchmark Gaps",
    "Ethical, Consent & Cultural Barriers": "Ethical Barriers",
    "Loss of spatial context / resolution trade-offs in ST": "Spatial Resolution",
    # Additional keywords for network graph and other figures
    "Algorithmic/Model Bias": "Algorithmic Bias",
    "Allelic dropout & coverage bias": "Allelic Dropout",
    "Amplification & PCR bias (GC-content, primer bias, copy number skew)": "PCR / Amplification Bias",
    "Amplification Bias": "Amplification Bias",
    "Ancestry/Population Bias": "Ancestry Bias",
    "Biased/Incomplete Reference Data": "Reference Data Gaps",
    "Capture & Selection Bias": "Capture Bias",
    "Clustering, imputation, dimensionality reduction model biases": "Clustering / Dim. Reduction",
    "Collection & processing biases (dissociation stress, inconsistent protocols, contamination, low microbial biomass)": "Collection Bias",
    "Detection bias for low-expression or low-abundance RNAs": "Low-Expression Bias",
    "Ethics\u2013data restriction bias": "Ethics Restriction",
    "Feature detection": "Feature Detection",
    "Filtering strategy & Variant Interpretation Challenges (incl. VUS)": "Variant Filtering",
    "Governance-limited generalizability": "Governance Limits",
    "Haplotype phasing & complex admixture errors": "Haplotype Phasing",
    "Hardware & Reagent Variability": "Reagent Variability",
    "High Dimensionality & Overfitting": "High-Dim / Overfitting",
    "High cost, input requirements, and scalability limits": "Cost & Scalability",
    "Instrument Drift & Batch Effects": "Instrument Drift",
    "Integration & Batch Correction": "Integration Correction",
    "Integration challenges (multi-omics, cross-study, EHR)": "Integration Challenges",
    "Interpreting VUS & Context": "VUS Interpretation",
    "Metadata quality bias": "Metadata Quality",
    "Model Overfitting & Feature Selection Bias": "Feature Selection Bias",
    "Model\u2013assay mismatch bias": "Model-Assay Mismatch",
    "Participation\u2013power limitation": "Participation Limits",
    "Pipeline-driven annotation bias": "Annotation Bias",
    "Platform-Specific Limits & Biases": "Platform Limits",
    "Population Underrepresentation": "Underrepresentation",
    "Processing\u2013power interaction bias": "Processing Interaction",
    "Reference Genome & Database Bias": "Reference Genome Bias",
    "Reproducibility & validation gaps": "Reproducibility Gaps",
    "Reproducibility, Validation & Cost": "Validation & Cost",
    "Resource Inequality & Economic Barriers": "Resource Inequality",
    "Sample Handling, Quality & Degradation": "Sample Degradation",
    "Sample Selection Bias & Heterogeneity": "Selection Heterogeneity",
    "Sample processing artifacts (fixation, slicing, dissociation stress-response)": "Processing Artifacts",
    "Sampling Issues (Missing Data, Small N)": "Small N / Missing Data",
    "Selection Bias & Underpowered Cohorts": "Underpowered Cohorts",
    "Sensitivity & Detection Limits": "Detection Limits",
    "Sensitivity limitations & Matrix Effects": "Matrix Effects",
    "Siloed integration bias": "Siloed Integration",
    "Small Sample Size & Recruitment Barriers": "Small Sample Size",
    "Temporal-driven data gaps": "Temporal Data Gaps",
    "Validation\u2013infrastructure mismatch": "Validation Mismatch",
    # Canonical names for merged keyword clusters
    "Batch Effects & Instrument Differences": "Batch Effects",
    "Sample Heterogeneity": "Sample Heterogeneity",
    "Lack of Standardization": "Standardization Gaps",
    "Reference Database Gaps": "Database Gaps",
    "High Cost / Resource Barriers": "Cost / Resources",
    "Reproducibility & Validation": "Reproducibility",
    "Algorithmic / Model Bias": "Algorithmic Bias",
    "Amplification / PCR Bias": "Amplification Bias",
    "Algorithm & Model Bias (especially AI/ML)": "Algorithmic Bias",
    "High Cost/Resource Barriers": "Cost / Resources",
    "High cost / resource barriers": "Cost / Resources",
    "Cost, scalability & infrastructure burden (high-throughput expense, specialized equipment)": "Cost / Resources",
    "Lack of Standardization & Reproducibility": "Standardization Gaps",
    "Lack of Standardization/Harmonization": "Standardization Gaps",
    "Lack of Standardization/Validation": "Standardization Gaps",
    "Lack of standarization": "Standardization Gaps",
}

# Semantic merge map: keywords that describe the same bias concept.
# Used across all figures to merge/sum counts before visualization.
KEYWORD_MERGE_MAP = {
    # 1. Batch effects cluster
    "Batch effects &  Instrument Differences": "Batch Effects & Instrument Differences",
    "Platform Variability & Batch Effects": "Batch Effects & Instrument Differences",
    "Instrument Drift & Batch Effects": "Batch Effects & Instrument Differences",
    # 2. Sample heterogeneity cluster
    "Sample & Cohort Heterogeneity": "Sample Heterogeneity",
    "Sample Heterogeneity & Variability": "Sample Heterogeneity",
    "Sample Selection Bias & Heterogeneity": "Sample Heterogeneity",
    # 3. Standardization cluster (includes typo fix)
    # Q4 resolved: all 7 kept here. "& Reproducibility" and "/Validation" stay because
    # standardization is the primary concept (the qualifier describes *what* lacks standards).
    # Explicit reproducibility/validation keywords live in cluster 6 (Q10). No overlap.
    "Lack of Standardization & Benchmarks": "Lack of Standardization",
    "Lack of Standardization & Interoperability": "Lack of Standardization",
    "Lack of Standardization & Reproducibility": "Lack of Standardization",
    "Lack of Standardization/Harmonization": "Lack of Standardization",
    "Lack of Standardization/Validation": "Lack of Standardization",
    "Lack of standarization": "Lack of Standardization",
    # 4. Reference database cluster
    "Reference Database Gaps & Errors": "Reference Database Gaps",
    "Reference Genome & Database Bias": "Reference Database Gaps",
    "Biased/Incomplete Reference Data": "Reference Database Gaps",
    # 5. Cost/resource cluster (includes former reproducibility-cost overlap)
    "High Cost/Resource Barriers": "High Cost / Resource Barriers",
    "High cost / resource barriers": "High Cost / Resource Barriers",
    "High cost, input requirements, and scalability limits": "High Cost / Resource Barriers",
    "Cost, scalability & infrastructure burden (high-throughput expense, specialized equipment)": "High Cost / Resource Barriers",
    "Reproducibility, Validation & Cost": "High Cost / Resource Barriers",
    # 6. Reproducibility & validation cluster (cost removed per Osama)
    "Reproducibility & Correlation/Causation": "Reproducibility & Validation",
    "Reproducibility & validation gaps": "Reproducibility & Validation",
    # Q10 additions (Marianna confirmed all 6 belong here, 2026-02-27):
    # Each keyword touches reproducibility/validation but was phrased differently
    # by different curators. Merging prevents double-counting across categories.
    "lack of transparency in methods & Reproducibility": "Reproducibility & Validation",  # Metabolomics, 18 cit
    "Lack of Validation & Replication": "Reproducibility & Validation",  # Multi-omics, 13 cit
    "Validation\u2013infrastructure mismatch": "Reproducibility & Validation",  # General_omics, 18 cit
    "Need for Experimental Validation": "Reproducibility & Validation",  # Proteomics, 2 cit
    "Lack of Benchmarks/Validation": "Reproducibility & Validation",  # Transcriptomics, 12 cit
    "Reproducibility & Over-interpretation": "Reproducibility & Validation",  # Proteomics, 6 cit
    # 7. Algorithmic/model bias cluster
    "Algorithm & Model Bias (especially AI/ML)": "Algorithmic / Model Bias",
    "Algorithmic/Model Bias": "Algorithmic / Model Bias",
    # 8. Amplification bias cluster
    "Amplification & PCR bias (GC-content, primer bias, copy number skew)": "Amplification / PCR Bias",
    "Amplification Bias": "Amplification / PCR Bias",
}


def merge_semantic_keywords(df):
    """Merge semantically equivalent keywords by summing their counts.

    Keywords in KEYWORD_MERGE_MAP are replaced with canonical names,
    then counts are summed within each group.
    """
    df = df.copy()
    df['Final_Keyword'] = df['Final_Keyword'].map(KEYWORD_MERGE_MAP).fillna(df['Final_Keyword'])
    group_cols = [c for c in ['Category', 'Subcategory', 'Subcategory_Type', 'Stage',
                               'Pipeline_Stage', 'Final_Keyword']
                  if c in df.columns]
    return df.groupby(group_cols, as_index=False).agg({'Final count': 'sum'})


def shorten_bias(keyword):
    """Get a short display name for a bias keyword."""
    if keyword in SHORT_NAMES:
        return SHORT_NAMES[keyword]
    words = keyword.split()
    short = ' '.join(words[:3])
    if len(short) > 25:
        short = short[:22] + '...'
    return short


def normalize_subcategories(df):
    """Normalize subcategory names to 5 canonical pipeline stages."""
    df = df.copy()
    df['Subcategory'] = df['Subcategory'].map(SUBCATEGORY_MAP).fillna(df['Subcategory'])
    return df


def normalize_chinese_keywords(df):
    """Harmonize Chinese Literature keywords with other categories.

    Replaces Chinese Literature Final_Keyword values with the equivalent
    keyword from another category so that overlap detection works correctly.
    Keywords not in CHINESE_KEYWORD_MAP are left unchanged (truly unique).
    """
    df = df.copy()
    mask = df['Category'] == 'Chinese Literature'
    df.loc[mask, 'Final_Keyword'] = (
        df.loc[mask, 'Final_Keyword'].map(CHINESE_KEYWORD_MAP).fillna(
            df.loc[mask, 'Final_Keyword']
        )
    )
    return df


def reassign_chinese_categories(df):
    """Redistribute Chinese Literature rows into their respective omics categories.

    Reassigns the Category column using CHINESE_CATEGORY_REASSIGN, then
    normalizes keyword text via CHINESE_KEYWORD_MAP. Both operations target
    the same row indices (identified before any changes).
    """
    df = df.copy()
    chinese_idx = df.index[df['Category'] == 'Chinese Literature']
    # Step 1: reassign category using original Chinese keywords
    df.loc[chinese_idx, 'Category'] = (
        df.loc[chinese_idx, 'Final_Keyword'].map(CHINESE_CATEGORY_REASSIGN)
        .fillna('General Omics')
    )
    # Step 2: normalize keywords (replace Chinese phrasing with equivalents)
    df.loc[chinese_idx, 'Final_Keyword'] = (
        df.loc[chinese_idx, 'Final_Keyword'].map(CHINESE_KEYWORD_MAP)
        .fillna(df.loc[chinese_idx, 'Final_Keyword'])
    )
    return df


def load_data(data_path='data/bias.csv'):
    """Load and preprocess the bias data"""
    # Get the project root directory (2 levels up from scripts/figures/)
    project_root = Path(__file__).parent.parent.parent
    full_path = project_root / data_path

    # Load data
    df = pd.read_csv(full_path)

    # Handle missing Final count values
    # Convert to numeric, replacing empty strings with NaN
    df['Final count'] = pd.to_numeric(df['Final count'], errors='coerce')

    # For rows with missing Final count, use ChatGPT_Count as fallback
    df['Final count'] = df['Final count'].fillna(df['ChatGPT_Count'])

    # Drop any rows that still have no count
    df = df.dropna(subset=['Final count'])

    # Convert to integer
    df['Final count'] = df['Final count'].astype(int)

    # Clean up category and subcategory names
    df['Category'] = df['Category'].str.strip()
    df['Subcategory'] = df['Subcategory'].str.strip()
    df['Final_Keyword'] = df['Final_Keyword'].str.strip()

    # Q11: display-friendly category name (CSV stores "General_omics")
    df['Category'] = df['Category'].replace('General_omics', 'General Omics')

    return df

def get_category_color(category):
    """Get the color for a specific category"""
    return CATEGORY_COLORS.get(category, '#95a5a6')  # Gray as default

def save_figure(fig, filename, output_dir='figures/main', dpi=300):
    """Save a matplotlib figure with consistent settings in both PNG and PDF"""
    project_root = Path(__file__).parent.parent.parent

    # Save PNG
    png_dir = project_root / output_dir / 'png'
    png_dir.mkdir(parents=True, exist_ok=True)
    png_path = png_dir / filename
    fig.savefig(png_path, dpi=dpi, bbox_inches='tight', facecolor='white')

    # Save PDF
    pdf_dir = project_root / output_dir / 'pdf'
    pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_filename = filename.replace('.png', '.pdf')
    pdf_path = pdf_dir / pdf_filename
    fig.savefig(pdf_path, format='pdf', bbox_inches='tight', facecolor='white')

    return png_path

def save_plotly_figure(fig, filename, output_dir='figures/main'):
    """Save a plotly figure in PNG and PDF formats"""
    project_root = Path(__file__).parent.parent.parent

    # Save PNG
    png_dir = project_root / output_dir / 'png'
    png_dir.mkdir(parents=True, exist_ok=True)
    png_path = png_dir / filename
    fig.write_image(str(png_path), width=2000, height=1200, scale=3)

    # Save PDF
    pdf_dir = project_root / output_dir / 'pdf'
    pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_filename = Path(filename).stem + '.pdf'
    pdf_path = pdf_dir / pdf_filename
    fig.write_image(str(pdf_path), width=2000, height=1200, format='pdf')

    return png_path, pdf_path
