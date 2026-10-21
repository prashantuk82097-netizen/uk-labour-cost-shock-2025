# Robustness and sensitivity programme

The final pipeline retains null and contradictory results rather than selecting specifications after seeing significance.

Checks include:

1. All 19 SIC A-S sectors.
2. Each LCEI component separately.
3. Top-exposure quartile indicator.
4. July 2025 delayed post start.
5. October 2025 delayed post start.
6. Shorter January 2024-July 2026 window.
7. ASHE part-time alternative LCEI.
8. Employment-size weighting.
9. Sector-specific linear trends.
10. Month-to-month log-employment growth outcome.
11. Leave-one-sector-out analysis.
12. Wild-cluster bootstrap for the small number of sector clusters.
13. Two-way sector/month clustering.
14. Panel-HAC and Driscoll-Kraay-style covariance sensitivities.
15. Quarterly sampling from the same monthly panel as a frequency robustness check.

The purpose is not to search for a preferred p-value. The purpose is to assess whether the substantive conclusion depends on one exposure definition, one sample, one timing choice, one sector or one covariance estimator.
