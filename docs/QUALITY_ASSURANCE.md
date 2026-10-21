# Quality assurance

The repository is designed to support transparent postgraduate Business Analytics research rather than only display final charts.

## Reproducibility controls

- Raw-source extraction is separated from analysis.
- Pre-policy exposure construction is deterministic and tested.
- Processed panel dimensions are tested.
- The headline monthly coefficient and p-value are regression-tested.
- Continuous integration reruns tests and the analysis pipeline on each push/pull request.
- Quarterly sampling is retained as a frequency sensitivity derived from the same monthly panel.

## Analytical controls

- Exposure is fixed from 2024 data before outcome interpretation.
- Null and contradictory results are retained.
- Pre-policy diagnostics are reported alongside post-policy estimates.
- Multiple covariance estimators are documented rather than selectively reported.
- Public/non-market-heavy sectors are excluded only from the primary business-facing sample and restored in robustness.
- The Business Analytics interpretation distinguishes statistical significance, practical magnitude and uncertainty.

## Data-governance controls

- No personal data are processed.
- Only aggregated official statistics are used.
- Source vintages, geographies and roles are recorded in a machine-readable register.
