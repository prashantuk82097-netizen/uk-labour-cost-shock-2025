# Methodology

## Design

The empirical design is a secondary quantitative **sector-month panel**. Exposure is fixed using 2024 pre-policy information and linked to monthly PAYE RTI employment from January 2023 to July 2026.

### Primary sample

- 19 SIC A-S sectors in the complete panel.
- 16 business-facing sectors in the primary model.
- O: Public administration and defence; social security, P: Education, and Q: Health and social work are excluded from the baseline because their employment is materially shaped by public/non-market funding mechanisms. They remain in the 19-sector robustness model.
- 43 months in the final panel.
- 688 sector-month observations in the baseline; 817 in the 19-sector panel.

## Labour-Cost Exposure Index (LCEI)

The 2024 pre-policy index is:

```text
LCEI_s = [ z(12.21 / MedianPay_s)
         + z(12.21 / P10Pay_s)
         + z(PartTimeShare_s) ] / 3
```

The three components represent typical wage-floor proximity, lower-tail wage exposure, and workforce structure. Each is standardised across common sectors and equally weighted. Equal weights are deliberately transparent and were not selected to maximise the employment result.

The LCEI is a **structural labour-cost exposure measure**, not a direct employer-NIC liability calculator. Exact NIC liabilities depend on earnings, hours, employer characteristics and Employment Allowance eligibility.

## Primary model

```text
ln(Employment_st) = alpha_s + lambda_t + beta(LCEI_s x Post_t) + epsilon_st
```

- `alpha_s`: sector fixed effects.
- `lambda_t`: calendar-month fixed effects.
- `Post_t`: 1 from April 2025 onward.
- Primary uncertainty: standard errors clustered by sector.

The coefficient tests whether more-exposed sectors experienced different post-April-2025 monthly employment trajectories after controlling for stable sector differences and common calendar-month shocks.

## Dynamic specification

The event study uses monthly exposure-by-event-time interactions, with **March 2025** as the reference month and April 2025 as event month 0.

## Identification discipline

The analysis is not presented as a clean causal difference-in-differences design. Linear pre-trend tests are benign, but joint binned pre-policy tests show exposure-related pre-period differences. The findings are therefore interpreted as adjusted exposure-related longitudinal associations.
