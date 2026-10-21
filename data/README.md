# Data provenance and reproduction

This repository contains **small research extracts and derived sector-level data only**. Large source workbooks are not versioned.

## Official sources

| Dataset | Vintage used | Role | Official source |
|---|---|---|---|
| Annual Survey of Hours and Earnings (ASHE), Table 4 | 2024 revised | Median hourly pay, P10 hourly pay, ASHE part-time sensitivity | https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/industry2digitsicashetable4 |
| Business Register and Employment Survey (BRES) | 2024 | Full-time and part-time employee structure | https://www.nomisweb.co.uk/datasets/newbres6pub |
| PAYE Real Time Information (RTI), seasonally adjusted | September 2026 publication vintage | Monthly payrolled employment by industry | https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/realtimeinformationstatisticsreferencetableseasonallyadjusted/current |

## PAYE raw-file reproduction

1. Download the September 2026 seasonally adjusted PAYE RTI workbook from ONS.
2. Save it as `data/raw/rtisasep2026.xlsx`.
3. Run:

```bash
python scripts/01_extract_paye_from_ons_xlsx.py data/raw/rtisasep2026.xlsx
```

The extractor uses worksheet **`23. Employees (Industry)`**, SIC sections A-S, and retains every month from January 2023 to July 2026.

## Why July 2026 is the endpoint

The study stops at July 2026 rather than using the earliest estimate for August 2026. This keeps the analysis on a more mature observation while preserving the predefined study window.

## Geography note

The BRES extract used in the final LCEI is Great Britain while ASHE/PAYE are UK-level. This is disclosed as a limitation and an ASHE part-time alternative index is retained as a sensitivity check.

## Generated processed data

Running `python -m labour_cost_shock.pipeline` creates `data/processed/lcei_2024.csv` and `data/processed/monthly_paye_lcei_panel.csv`. These derived files are not versioned because they are reproducible from the tracked input extracts.
