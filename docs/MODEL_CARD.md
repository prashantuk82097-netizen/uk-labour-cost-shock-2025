# Analytical model card

## Intended use

Assess whether UK broad industries with greater pre-April-2025 structural labour-cost exposure exhibit different monthly PAYE employment trajectories after April 2025.

## Not intended for

- Forecasting individual firm employment.
- Estimating a firm's exact employer-NIC bill.
- Separately identifying the causal effect of the NLW and NIC reforms.
- Making employee-level or occupation-level claims.

## Exposure

2024 sector LCEI combining wage-floor proximity, lower-tail wage exposure and part-time intensity.

## Outcome

Natural log of seasonally adjusted monthly PAYE payrolled employees.

## Estimator

Sector fixed effects + calendar-month fixed effects + continuous exposure-by-post interaction.

## Primary uncertainty

Sector-clustered standard errors. Wild-cluster bootstrap is included because the primary sample has 16 clusters.

## Key validation / stress tests

- 19-sector sample.
- Exposure components separately.
- ASHE part-time alternative index.
- Delayed post windows.
- Shorter panel.
- Employment-size weighting.
- Sector-specific linear trends.
- Monthly log-growth outcome.
- Leave-one-sector-out.
- Alternative covariance estimators.
- Quarterly frequency sensitivity.

## Main caveats

See `LIMITATIONS.md`. The most important are the combined policy episode, broad-sector aggregation, significant joint pre-policy diagnostics and covariance-estimator sensitivity.
