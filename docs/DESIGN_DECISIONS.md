# Design decisions and analytical audit trail

| Decision | Final implementation | Rationale |
|---|---|---|
| Unit of analysis | SIC sector-month | Matches the approved research design and preserves all monthly PAYE information. |
| Exposure timing | 2024 only | Avoids using post-policy information to define exposure. |
| Outcome | log monthly PAYE employment | Official administrative sector-level employment series. |
| Primary sample | 16 business-facing sectors | Reduces structural public-sector confounding; O/P/Q retained in robustness. |
| Primary reference month | March 2025 | Last full pre-policy month before April 2025. |
| Primary covariance | Sector-clustered SE | Allows arbitrary within-sector dependence over time. |
| Small-cluster check | Wild-cluster bootstrap | Baseline has only 16 sector clusters. |
| Quarterly analysis | Robustness only | Jan/Apr/Jul/Oct sampling is used only to test frequency sensitivity against the full monthly design. |
| Causal language | Restricted | Joint pre-policy diagnostics do not support strong parallel-trends claims. |
| Null results | Retained | No specification was chosen solely because it produced significance. |
