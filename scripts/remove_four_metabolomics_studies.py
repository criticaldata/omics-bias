"""
Remove four metabolomics studies from the extraction sheet and subtract their contribution
from the metabolomics keyword counts in data/bias.csv.

The four rows (data.xlsx, Metabolomics tab: Bai 2021, Langdor 2024, Havelund 2023, Li 2022) were
dropped from the review in October 2026. Each keyword count in bias.csv is the number of coded
studies that mention that bias, so the correction is: for each of the 25 metabolomics keywords,
count how many of the four rows name that bias explicitly in their coded text, and subtract.
The per-keyword judgements are in data/removed_metabolomics_contribution.csv so they can be audited.

Run once from the repo root:  python3 scripts/remove_four_metabolomics_studies.py [repo_root]
"""
import csv
import sys
from pathlib import Path

import openpyxl

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
XLSX = ROOT / "data" / "data.xlsx"
BIAS = ROOT / "data" / "bias.csv"
AUDIT = ROOT / "data" / "removed_metabolomics_contribution.csv"

REMOVED_TITLES = [
    "Advances and challenges in clinical metabolomics for precision medicine",
    "The metabolome as a window on mechanisms underlying aging and age-related diseases: status, challenges, and opportunities",
    "Advancing Pediatric Metabolomics: Current Status and Future Perspectives",
    "Metabolomics profiling and its application in precision nutrition",
]
SHORT = ["Bai 2021", "Langdor 2024", "Havelund 2023", "Li 2022"]

# Final_Keyword (as in bias.csv, Category == Metabolomics, in file order) -> (Bai, Langdor, Havelund, Li)
# 1 = the row's coded text names this bias explicitly.
CONTRIBUTION = [
    ("Sample Selection Bias & Heterogeneity", (1, 1, 0, 0), "Bai: population bias in cohort selection; Langdor: survival/selection bias"),
    ("Cohort Heterogeneity & Confounders", (1, 1, 1, 0), "Bai: sample heterogeneity, biological confounders; Langdor: multifactorial confounding; Havelund: age/sex/nutritional confounding"),
    ("Lack of Standardized Protocols/SOPs", (0, 0, 1, 0), "Havelund: difficulties standardizing sample collection/storage"),
    ("Lack of Reference Materials/Standards", (0, 0, 1, 0), "Havelund: limited pediatric reference databases, lack of age-referenced data"),
    ("Batch effects &  Instrument Differences", (1, 1, 1, 1), "Bai: batch effects, hardware differences; Langdor: hardware differences across centers, batch correction; Havelund: batch effects; Li: LC/MS parameter differences among centers, batch normalization"),
    ("Platform differences & Sensitivity, Specificity & Coverage Limitations", (1, 1, 1, 0), "Bai: MS/NMR platforms, limited coverage; Langdor: platform-specific biases; Havelund: platform limitations"),
    ("Sensitivity limitations & Matrix Effects ", (0, 1, 1, 1), "Langdor: instrument sensitivity; Havelund: lower sensitivity in small volumes; Li: food matrix effects"),
    ("batch correction / effects & Metabolite Annotation", (0, 1, 1, 1), "Langdor: batch correction, imperfect annotation; Havelund: annotation, batch effects; Li: annotation/identification challenges"),
    ("Feature detection ", (0, 0, 0, 0), "none"),
    ("Lack of standarization", (1, 0, 0, 0), "Bai: discrepancies in computational workflows"),
    ("lack of transparency in methods & Reproducibility", (1, 0, 0, 0), "Bai: lack of transparency in analytic methods, reproducibility issues"),
    ("Overinterpretation of findings (esp. biomarkers)", (1, 0, 0, 0), "Bai: selective interpretation of positive results"),
    ("Cross-study / inter-laboratory comparability ", (1, 1, 1, 1), "Bai: inter-lab variation; Langdor: multi-site harmonization; Havelund: multi-center harmonization; Li: differences among centers"),
    ("High cost / resource barriers", (1, 0, 1, 0), "Bai: high cost and complexity; Havelund: cost challenges"),
    ("Large fraction of unannotated / unknown metabolites", (0, 0, 0, 1), "Li: novel/unknown food biomarkers"),
    ("Pre-analytical Variability", (1, 1, 1, 1), "all four name pre-analytical variability"),
    ("Instrument Drift & Batch Effects", (1, 1, 1, 0), "Bai: calibration and drift; Langdor: instrument drift; Havelund: instrument drift"),
    ("Calibration & Maintenance", (1, 0, 0, 1), "Bai: instrument calibration; Li: instrument calibration"),
    ("Data Processing & Annotation/Database Issues", (1, 1, 1, 1), "Bai: normalization, database gaps; Langdor: normalization, annotation; Havelund: normalization, reference databases; Li: limited databases"),
    ("Pipeline Variability & Database Gaps", (1, 1, 1, 1), "Bai: workflow discrepancies, database gaps; Langdor: evolving pipelines; Havelund: inconsistent pipelines; Li: limited databases"),
    ("Incomplete Metadata/Methods Reporting", (1, 1, 1, 1), "Bai: incomplete metadata; Langdor: variable description of QC; Havelund: missing annotation on datasets; Li: variable reporting of methodology"),
    ("Underreporting of Negative Results", (0, 1, 1, 1), "Langdor: underreporting of null findings; Havelund: lack of negative results; Li: selective reporting of successful biomarkers"),
    ("Lack of Standardized Reporting", (1, 0, 1, 1), "Bai: inconsistent reporting standards; Havelund: variable adherence to reporting guidelines; Li: lack of standardization in validation protocols"),
    ("Lack of Standardization/Harmonization", (1, 1, 1, 1), "Bai: integrating multi-omics; Langdor: harmonization/integration; Havelund: multi-center harmonization; Li: integration with heterogeneous data"),
    ("High Cost/Resource Barriers", (1, 0, 1, 0), "Bai: high cost; Havelund: cost challenges"),
]


def fix_bias_csv():
    with open(BIAS, newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)
    met = [r for r in rows if r["Category"].strip().lower().startswith("metab")]
    assert len(met) == len(CONTRIBUTION), (len(met), len(CONTRIBUTION))
    audit = []
    before = after = 0
    for r, (kw, flags, why) in zip(met, CONTRIBUTION):
        assert r["Final_Keyword"].strip().lower().startswith(kw.strip().lower()), (r["Final_Keyword"], kw)
        kw = r["Final_Keyword"]
        old = int(float(r["Final count"])) if r["Final count"].strip() else int(float(r["ChatGPT_Count"]))
        new = old - sum(flags)
        assert new >= 0
        r["Final count"] = str(new)
        before += old
        after += new
        audit.append({"Final_Keyword": kw.strip(), **dict(zip(SHORT, flags)),
                      "removed": sum(flags), "count_before": old, "count_after": new, "evidence": why})
    with open(BIAS, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    with open(AUDIT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(audit[0].keys()))
        w.writeheader()
        w.writerows(audit)
    print(f"metabolomics citations: {before} -> {after} (removed {before - after})")


def fix_xlsx():
    wb = openpyxl.load_workbook(XLSX)
    ws = wb["Metabolomics"]
    targets = []
    for row in ws.iter_rows(min_row=2):
        if row[0].value and str(row[0].value).strip() in REMOVED_TITLES:
            targets.append(row[0].row)
    assert len(targets) == 4, targets
    for r in sorted(targets, reverse=True):
        ws.delete_rows(r)
    wb.save(XLSX)
    print(f"data.xlsx: deleted Metabolomics rows {sorted(targets)}; {ws.max_row - 1} rows remain")


if __name__ == "__main__":
    fix_bias_csv()
    fix_xlsx()
