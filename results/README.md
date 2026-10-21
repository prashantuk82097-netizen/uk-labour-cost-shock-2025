# Results outputs

## Tables

- `main_fixed_effects_monthly.csv` — primary coefficient, uncertainty and practical magnitude.
- `event_study_monthly.csv` — monthly dynamic exposure coefficients, March 2025 reference.
- `diagnostics.json` — linear/joint pre-trends, residual diagnostics and alternative covariance results.
- `inference_sensitivity.csv` — direct comparison of covariance/inference approaches.
- `robustness_monthly.csv` — alternative samples, exposures, timing, weights and outcomes.
- `leave_one_sector_out_monthly.csv` — influence check by omitted sector.
- `monthly_vs_quarterly.csv` — monthly-versus-quarterly frequency sensitivity using the same underlying panel.
- `sector_summary.csv` — final LCEI and descriptive March-2025-to-July-2026 employment change.
- `headline_results.json` — source-of-truth summary used for dissertation consistency checks.

## Figures

- `01_lcei_ranking.svg` — all 19 SIC A-S sectors ranked by pre-policy exposure.
- `02_monthly_employment_by_lcei_quartile.svg` — monthly PAYE trajectories, March 2025 = 100.
- `03_monthly_event_study.svg` — monthly exposure-intensity event study with 95% intervals.
