"""
Shared utilities for figure generation
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
    'General_omics': '#f39c12',  # Yellow/Gold
    'Chinese Literature': '#1abc9c'  # Teal
}

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
