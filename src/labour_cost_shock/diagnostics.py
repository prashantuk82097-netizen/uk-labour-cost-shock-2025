from __future__ import annotations
import math
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm
from statsmodels.stats.diagnostic import het_breuschpagan
from .config import POLICY_MONTH
from .models import _design


def linear_pretrend(records: pd.DataFrame, start: str | None = None) -> dict:
    policy = pd.Timestamp(POLICY_MONTH)
    pre = records.loc[records["date"] < policy].copy()
    if start:
        pre = pre.loc[pre["date"] >= pd.Timestamp(start)].copy()
    dates = sorted(pre["date"].unique()); sectors = sorted(pre["sector"].unique())
    sec_d, date_d = sectors[1:], dates[1:]
    tmap = {pd.Timestamp(d): i for i,d in enumerate(dates)}
    names = ["Intercept"] + [f"sector[{s}]" for s in sec_d] + [f"month[{pd.Timestamp(d):%Y-%m}]" for d in date_d] + ["Exposure_x_linear_time"]
    X=[]; y=[]; groups=[]
    for r in pre.itertuples(index=False):
        dt = pd.Timestamp(r.date)
        row=[1.0] + [1.0 if r.sector==s else 0.0 for s in sec_d] + [1.0 if dt==pd.Timestamp(d) else 0.0 for d in date_d]
        row += [float(r.final_LCEI) * float(tmap[dt])]
        X.append(row); y.append(float(r.log_employment)); groups.append(r.sector)
    fit=sm.OLS(np.asarray(y),np.asarray(X)).fit(cov_type="cluster",cov_kwds={"groups":np.asarray(groups)})
    j=names.index("Exposure_x_linear_time")
    return {"coefficient": float(fit.params[j]), "se":float(fit.bse[j]), "p_value":float(fit.pvalues[j]), "n":len(pre), "months":len(dates)}


def joint_binned_pretrend(records: pd.DataFrame, recent_start: str = "2024-04-01") -> dict:
    policy=pd.Timestamp(POLICY_MONTH); reference=pd.Timestamp("2025-03-01")
    pre=records.loc[records["date"]<policy].copy()
    def label(dt):
        dt=pd.Timestamp(dt)
        if dt==reference: return "REF"
        qstart=((dt.month-1)//3)*3+1
        return f"{dt.year}-{qstart:02d}"
    pre["pre_bin"]=pre["date"].map(label)
    bins=sorted([b for b in pre["pre_bin"].unique() if b!="REF"])
    sectors=sorted(pre["sector"].unique()); dates=sorted(pre["date"].unique())
    sec_d, date_d=sectors[1:], dates[1:]
    names=["Intercept"]+[f"sector[{s}]" for s in sec_d]+[f"month[{pd.Timestamp(d):%Y-%m}]" for d in date_d]+[f"Exposure_x_prebin[{b}]" for b in bins]
    X=[]; y=[]; groups=[]
    for r in pre.itertuples(index=False):
        dt=pd.Timestamp(r.date)
        row=[1.0]+[1.0 if r.sector==s else 0.0 for s in sec_d]+[1.0 if dt==pd.Timestamp(d) else 0.0 for d in date_d]
        row += [float(r.final_LCEI)*(1.0 if r.pre_bin==b else 0.0) for b in bins]
        X.append(row); y.append(float(r.log_employment)); groups.append(r.sector)
    fit=sm.OLS(np.asarray(y),np.asarray(X)).fit(cov_type="cluster",cov_kwds={"groups":np.asarray(groups)})
    R=np.zeros((len(bins),len(names)))
    for i,b in enumerate(bins): R[i,names.index(f"Exposure_x_prebin[{b}]")]=1.0
    full=fit.wald_test(R,use_f=True,scalar=True)
    recent_label=pd.Timestamp(recent_start).strftime("%Y-%m")
    recent_bins=[b for b in bins if b>=recent_label]
    R2=np.zeros((len(recent_bins),len(names)))
    for i,b in enumerate(recent_bins): R2[i,names.index(f"Exposure_x_prebin[{b}]")]=1.0
    recent=fit.wald_test(R2,use_f=True,scalar=True)
    return {"full_stat":float(full.statistic),"full_p":float(full.pvalue),"full_restrictions":len(bins),
            "recent_stat":float(recent.statistic),"recent_p":float(recent.pvalue),"recent_restrictions":len(recent_bins)}


def residual_diagnostics(main: dict) -> dict:
    fit = sm.OLS(main["y"], main["X"]).fit()
    bp=het_breuschpagan(fit.resid, main["X"])
    df=main["df"].copy(); df["resid"]=fit.resid
    sectors=sorted(df["sector"].unique()); dates=sorted(df["date"].unique())
    matrix=np.asarray([[df.loc[(df["sector"]==s)&(df["date"]==d),"resid"].iloc[0] for d in dates] for s in sectors])
    cors=[]
    for i in range(len(sectors)):
        for j in range(i+1,len(sectors)):
            cors.append(np.corrcoef(matrix[i],matrix[j])[0,1])
    N,T=len(sectors),len(dates)
    cd=math.sqrt(2*T/(N*(N-1)))*sum(cors)
    cd_p=2*(1-norm.cdf(abs(cd)))
    ar1=[np.corrcoef(row[1:],row[:-1])[0,1] for row in matrix]
    return {"breusch_pagan_lm":float(bp[0]),"breusch_pagan_p":float(bp[1]),
            "pesaran_style_cd":float(cd),"pesaran_style_cd_p":float(cd_p),
            "mean_residual_ar1":float(np.mean(ar1))}


def alternative_covariances(records: pd.DataFrame) -> dict:
    y,X,names,groups,df=_design(records)
    j=names.index("Exposure_x_Post")
    df=df.sort_values(["sector","date"]).reset_index(drop=True)
    y,X,names,groups,df=_design(df)
    g_codes=pd.Categorical(df["sector"]).codes
    t_codes=pd.Categorical(df["date"]).codes
    hac=sm.OLS(y,X).fit(cov_type="hac-panel",cov_kwds={"groups":g_codes,"time":t_codes,"maxlags":3})
    dk=sm.OLS(y,X).fit(cov_type="hac-groupsum",cov_kwds={"time":t_codes,"maxlags":3})
    return {
        "panel_hac": {"coefficient":float(hac.params[j]),"se":float(hac.bse[j]),"p_value":float(hac.pvalues[j])},
        "driscoll_kraay_style": {"coefficient":float(dk.params[j]),"se":float(dk.bse[j]),"p_value":float(dk.pvalues[j])},
    }
