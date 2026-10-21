from __future__ import annotations
import numpy as np
import pandas as pd
import statsmodels.api as sm
from .models import fit_main, baseline_sample


def log_growth_sample(panel: pd.DataFrame) -> pd.DataFrame:
    df=panel.sort_values(["sector","date"]).copy()
    df["log_growth"] = df.groupby("sector")["log_employment"].diff()
    return df.dropna(subset=["log_growth"]).copy()


def fit_growth(records: pd.DataFrame, exposure: str = "final_LCEI") -> dict:
    df=records.sort_values(["sector","date"]).reset_index(drop=True)
    sectors=sorted(df["sector"].unique()); dates=sorted(df["date"].unique())
    secd=sectors[1:]; dated=dates[1:]
    names=["Intercept"]+[f"sector[{s}]" for s in secd]+[f"month[{pd.Timestamp(d):%Y-%m}]" for d in dated]+["Exposure_x_Post"]
    X=[]; y=[]; groups=[]
    for r in df.itertuples(index=False):
        dt=pd.Timestamp(r.date)
        row=[1.0]+[1.0 if r.sector==s else 0.0 for s in secd]+[1.0 if dt==pd.Timestamp(d) else 0.0 for d in dated]
        row += [float(getattr(r, exposure)) * float(r.post_apr2025)]
        X.append(row); y.append(float(r.log_growth)); groups.append(r.sector)
    fit=sm.OLS(np.asarray(y),np.asarray(X)).fit(cov_type="cluster",cov_kwds={"groups":np.asarray(groups)})
    j=names.index("Exposure_x_Post"); lo,hi=fit.conf_int()[j]
    return {"coefficient":float(fit.params[j]),"se":float(fit.bse[j]),"p_value":float(fit.pvalues[j]),"ci_low":float(lo),"ci_high":float(hi),"n":len(df),"clusters":len(set(groups))}


def run_robustness(panel: pd.DataFrame) -> pd.DataFrame:
    baseline=baseline_sample(panel)
    rows=[]
    def add(label,res,note):
        rows.append([label,res["coefficient"],res["se"],res["p_value"],res["ci_low"],res["ci_high"],res["n"],res["clusters"],note])
    add("Monthly baseline: final LCEI, 16 business-facing sectors", fit_main(baseline), "Primary specification")
    add("Monthly all 19 A-S sectors", fit_main(panel), "Adds O, P and Q")
    for exposure,label in [
        ("z_wage_floor_proximity","Wage-floor proximity component only"),
        ("z_lower_tail_exposure","Lower-tail exposure component only"),
        ("z_bres_part_time_intensity","BRES part-time intensity component only"),
    ]:
        add(label,fit_main(baseline,exposure=exposure),"Single-component sensitivity")
    q75=baseline[["sector","final_LCEI"]].drop_duplicates()["final_LCEI"].quantile(.75)
    high=baseline.copy(); high["high_exposure_q4"]=(high["final_LCEI"]>=q75).astype(float)
    add("Top exposure quartile vs remaining sectors",fit_main(high,exposure="high_exposure_q4"),"Binary exposure sensitivity")
    add("Delayed post start: July 2025",fit_main(baseline,post_start_event=3),"Three-month adjustment lag")
    add("Delayed post start: October 2025",fit_main(baseline,post_start_event=6),"Six-month adjustment lag")
    short=baseline.loc[baseline["date"]>=pd.Timestamp("2024-01-01")].copy()
    add("Shorter window: Jan 2024-Jul 2026",fit_main(short),"Reduces influence of early 2023")
    alt=baseline.dropna(subset=["LCEI_ASHE_part_time_sensitivity"]).copy()
    add("ASHE part-time alternative LCEI",fit_main(alt,exposure="LCEI_ASHE_part_time_sensitivity"),"Mining omitted because ASHE PT count is suppressed")
    jan25=panel.loc[panel["date"].eq(pd.Timestamp("2025-01-01")),["sector","payrolled_employees"]].set_index("sector")["payrolled_employees"]
    weights=baseline["sector"].map(jan25).to_numpy()
    add("Employment-size weighted FE",fit_main(baseline,weights=weights),"Weights = Jan 2025 PAYE employment")
    add("Sector-specific linear trends",fit_main(baseline,sector_trends=True),"Controls for sector-specific linear trends")
    growth=log_growth_sample(baseline)
    add("Log-employment-growth outcome",fit_growth(growth),"Outcome is month-to-month delta ln(PAYE employment)")
    return pd.DataFrame(rows,columns=["specification","coefficient","se","p_value","ci_low","ci_high","n","clusters","note"])


def leave_one_sector_out(panel: pd.DataFrame) -> pd.DataFrame:
    baseline=baseline_sample(panel)
    rows=[]
    for sector in sorted(baseline["sector"].unique()):
        res=fit_main(baseline.loc[baseline["sector"]!=sector])
        rows.append([sector,res["coefficient"],res["se"],res["p_value"],res["ci_low"],res["ci_high"]])
    return pd.DataFrame(rows,columns=["dropped_sector","coefficient","se","p_value","ci_low","ci_high"])
