#!/usr/bin/env python3
from pathlib import Path
import sys
from labour_cost_shock.data import extract_paye_monthly

if len(sys.argv) != 2:
    raise SystemExit("Usage: python scripts/01_extract_paye_from_ons_xlsx.py data/raw/rtisasep2026.xlsx")
source=Path(sys.argv[1]); out_dir=Path("data/inputs"); out_dir.mkdir(parents=True,exist_ok=True)
df=extract_paye_monthly(source)
for year, part in df.groupby(df["date"].dt.year):
    suffix = f"{year}" if year < 2026 else "2026-01_to_2026-07"
    out = out_dir / f"paye_rti_monthly_A-S_{suffix}.csv"; part.to_csv(out,index=False); print(f"Wrote {len(part)} rows to {out}")
