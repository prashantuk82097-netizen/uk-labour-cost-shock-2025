# Model and data limitations

1. **Combined policy episode.** The National Living Wage and employer NIC changes occurred within days of each other. The model measures exposure to the combined labour-cost episode and cannot separately identify their causal effects.
2. **Exposure is approximate.** The LCEI combines wage distribution and part-time structure; it does not calculate employer-level NIC liabilities or Employment Allowance offsets.
3. **Broad sector aggregation.** SIC sections average over heterogeneous firms, contracts, occupations and demand conditions.
4. **Geography mismatch.** The BRES component is Great Britain while ASHE/PAYE are UK-wide. An ASHE part-time sensitivity is retained.
5. **Few clusters.** The baseline has 16 sector clusters; wild-cluster bootstrap and alternative covariance estimators are therefore reported.
6. **Pre-policy differences.** Joint event-bin tests reject equality of some pre-policy exposure coefficients, limiting causal interpretation.
7. **Inference sensitivity.** A Driscoll-Kraay-style covariance sensitivity is statistically significant while the primary clustered/wild/two-way/HAC specifications are not.
8. **Outcome scope.** PAYE headcount does not directly measure hours, vacancies, job quality, productivity, wages within the model, price pass-through or margins.
9. **Post-policy horizon.** The endpoint is July 2026; longer-run adjustment may differ.
