# Reproducibility guide

## Fast path

The repository includes the small extracted PAYE industry file needed to reproduce all published analytical outputs.

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
pytest
python -m labour_cost_shock.pipeline
```

Expected source-of-truth checks:

- 43 months, January 2023-July 2026.
- 19 A-S sectors = 817 rows.
- 16-sector baseline = 688 rows.
- Primary beta approximately `-0.0025680774`.
- Primary sector-clustered p-value approximately `0.8112548405`.

## Full raw-source path

To recreate the small PAYE input extract from the official ONS workbook:

```bash
mkdir -p data/raw
# download rtisasep2026.xlsx to data/raw/
python scripts/01_extract_paye_from_ons_xlsx.py data/raw/rtisasep2026.xlsx
python -m labour_cost_shock.pipeline
```

The analysis pipeline then reconstructs the LCEI from the included ASHE/BRES sector extracts, merges it with monthly PAYE and regenerates all tables and figures.

## Why tests matter

The tests check both data shape and the numerical headline estimate. If source data or code changes unexpectedly, continuous integration should fail rather than silently changing the dissertation result.
