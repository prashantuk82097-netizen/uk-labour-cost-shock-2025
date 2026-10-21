# UK Labour-Cost Shock 2025 — Reproducible Business Analytics Study

**Prashant Kumawat | MSc Business Analytics**

This repository contains the reproducible analytical implementation for a Route 1 research dissertation examining whether UK industries with greater **pre-policy labour-cost exposure** experienced different monthly PAYE employment trajectories after the April 2025 increase in the National Living Wage and employer National Insurance costs.

## Research questions

1. Which UK industries had the highest pre-policy exposure to the April 2025 increase in employer labour costs?
2. Did industries with greater pre-policy labour-cost exposure experience different changes in payrolled employment following April 2025 compared with less-exposed industries?
3. How do the observed sectoral employment patterns compare with firms' reported adjustment responses to higher labour costs, including margin absorption, pricing and workforce changes?

## Analytical contribution

The implementation combines three official UK data streams at a common broad SIC level:

- **ASHE 2024 revised** — median and 10th-percentile hourly pay.
- **BRES 2024** — part-time workforce intensity.
- **PAYE RTI** — monthly seasonally adjusted payrolled employment.

A fixed pre-policy **Labour-Cost Exposure Index (LCEI)** is constructed as:

```text
LCEI_s = [ z(12.21 / MedianPay_s)
         + z(12.21 / P10Pay_s)
         + z(PartTimeShare_s) ] / 3
```

The primary panel uses every month from **January 2023 to July 2026**.

## Final design

| Item | Primary design |
|---|---:|
| Frequency | Monthly |
| Months | 43 |
| SIC A-S sectors | 19 |
| Baseline business-facing sectors | 16 |
| Baseline observations | 688 sector-months |
| First post-policy month | April 2025 |
| Event-study reference | March 2025 |
| Outcome | ln(monthly PAYE payrolled employment) |
| Primary uncertainty | Sector-clustered standard errors |

Public administration (O), education (P), and health/social work (Q) are excluded from the business-facing baseline and restored in the 19-sector robustness specification.

## Headline finding

The final monthly model produces a small negative exposure coefficient (approximately **-0.00257 log points per +1 SD LCEI**) that is **not statistically distinguishable from zero under the primary sector-clustered inference**. A wild-cluster bootstrap and several other sensitivity checks lead to the same substantive conclusion.

The result is interpreted carefully: the analysis finds **no statistically detectable exposure-related PAYE employment divergence** in the primary specification. It does **not** establish that the April 2025 policy package had no employment effect. Joint pre-policy diagnostics and covariance-estimator sensitivity limit strong causal claims.

Exact machine-readable values are regenerated into `results/tables/headline_results.json`.

## Repository structure

```text
.
├── data/
│   ├── inputs/                 # Small research extracts used by the pipeline
│   ├── processed/              # Generated locally by the pipeline (not versioned)
│   ├── README.md               # Raw-source reproduction instructions
│   ├── source_register.csv     # Provenance register
│   └── data_dictionary.csv
├── src/labour_cost_shock/      # Reusable analysis modules
├── scripts/                    # Command-line entry points
├── tests/                      # Data- and result-integrity tests
├── results/
│   ├── tables/                 # Machine-readable estimates/diagnostics
│   └── figures/                # Analytical figures
├── docs/                       # Methodology, limitations, decisions, reproducibility
└── .github/workflows/ci.yml    # Automated reproducibility checks
```

## Reproduce the analysis

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
pytest
python -m labour_cost_shock.pipeline
```

The pipeline reconstructs the LCEI, rebuilds the monthly panel and regenerates the main regression, event study, diagnostics, robustness tables and figures.

See [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md) for the full raw-source workflow.

## Evidence discipline

This repository deliberately separates:

- **Primary administrative outcome analysis:** ASHE/BRES exposure + PAYE RTI employment.
- **Secondary mechanism triangulation:** Decision Maker Panel and BICS evidence used in the dissertation discussion, not merged into the PAYE regression panel.

The repository also preserves contradictory evidence. In particular, a Driscoll-Kraay-style covariance sensitivity differs from the primary clustered inference. This is documented in [`docs/RESULTS_INTERPRETATION.md`](docs/RESULTS_INTERPRETATION.md) and [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md).

## Data provenance

Official source links, vintages, geographies, retrieval dates and analytical roles are recorded in [`data/source_register.csv`](data/source_register.csv). Large raw workbooks are intentionally excluded from Git history; instructions for recreating the PAYE extract are in [`data/README.md`](data/README.md).

## Research-quality controls

The repository is designed as an auditable research implementation, not a file dump. It includes automated tests, continuous integration, a model card, design-decision log, reproducibility guide, source register, data dictionary, explicit limitations and robustness documentation. See [`docs/QUALITY_ASSURANCE.md`](docs/QUALITY_ASSURANCE.md).

## License

Code is released under the MIT License. Data remain subject to the terms of their original official providers; source attribution is retained in the data register.
