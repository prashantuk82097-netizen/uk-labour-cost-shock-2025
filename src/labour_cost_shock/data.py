from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
from .config import START_MONTH, END_MONTH, POLICY_MONTH, EVENT_REFERENCE_MONTH


def extract_paye_monthly(raw_xlsx: str | Path) -> pd.DataFrame:
    """Extract SIC A-S monthly seasonally adjusted PAYE employees from ONS sheet 23."""
    raw_xlsx = Path(raw_xlsx)
    raw = pd.read_excel(raw_xlsx, sheet_name="23. Employees (Industry)", header=None)
    sic = raw.iloc[5, 1:20].astype(str).tolist()
    sectors = raw.iloc[6, 1:20].astype(str).tolist()
    data = raw.iloc[7:, :20].copy()
    data.columns = ["date_label"] + sic
    data = data[data["date_label"].notna()].copy()
    data["date"] = pd.to_datetime(data["date_label"], format="%B %Y", errors="coerce")
    data = data[data["date"].between(pd.Timestamp(START_MONTH), pd.Timestamp(END_MONTH))]
    long = data.melt(id_vars=["date"], value_vars=sic, var_name="sic_section", value_name="payrolled_employees")
    sector_map = dict(zip(sic, sectors))
    long["sector"] = long["sic_section"].map(sector_map)
    long["payrolled_employees"] = pd.to_numeric(long["payrolled_employees"], errors="raise")
    return long[["date", "sic_section", "sector", "payrolled_employees"]].sort_values(["date", "sic_section"]).reset_index(drop=True)


def load_paye_inputs(input_dir: str | Path) -> pd.DataFrame:
    """Load the versioned annual PAYE extracts and return one monthly panel."""
    input_dir = Path(input_dir)
    files = sorted(input_dir.glob("paye_rti_monthly_A-S_*.csv"))
    if not files:
        raise FileNotFoundError(f"No PAYE input extracts found in {input_dir}")
    parts = [pd.read_csv(f, parse_dates=["date"]) for f in files]
    df = pd.concat(parts, ignore_index=True)
    return df.sort_values(["date", "sic_section"]).reset_index(drop=True)


def build_monthly_panel(paye: pd.DataFrame, lcei: pd.DataFrame) -> pd.DataFrame:
    panel = paye.merge(lcei, on=["sic_section", "sector"], how="inner", validate="many_to_one")
    panel["log_employment"] = np.log(panel["payrolled_employees"])
    policy = pd.Timestamp(POLICY_MONTH)
    ref = pd.Timestamp(EVENT_REFERENCE_MONTH)
    panel["post_apr2025"] = (panel["date"] >= policy).astype(int)
    panel["event_month"] = ((panel["date"].dt.year - policy.year) * 12 + panel["date"].dt.month - policy.month).astype(int)
    ref_emp = panel.loc[panel["date"].eq(ref), ["sector", "payrolled_employees"]].set_index("sector")["payrolled_employees"]
    panel["employment_index_mar2025_100"] = panel["payrolled_employees"] / panel["sector"].map(ref_emp) * 100.0
    panel["period"] = panel["date"].dt.strftime("%Y-%m")
    return panel.sort_values(["date", "sic_section"]).reset_index(drop=True)
