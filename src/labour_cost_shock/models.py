from __future__ import annotations
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm
from statsmodels.stats.sandwich_covariance import cov_cluster_2groups
from .config import BASELINE_EXCLUSIONS, RANDOM_SEED, WILD_BOOTSTRAP_REPS


def baseline_sample(panel: pd.DataFrame) -> pd.DataFrame:
    return panel.loc[~panel["sector"].isin(BASELINE_EXCLUSIONS)].copy()


def _design(records: pd.DataFrame, exposure: str = "final_LCEI", post_start_event: int = 0,
            event_study: bool = False, sector_trends: bool = False):
    df = records.sort_values(["sector", "date"]).reset_index(drop=True)
    sectors = sorted(df["sector"].unique())
    dates = sorted(pd.to_datetime(df["date"].unique()))
    sec_d = sectors[1:]
    date_d = dates[1:]
    names = ["Intercept"] + [f"sector[{s}]" for s in sec_d] + [f"month[{pd.Timestamp(d):%Y-%m}]" for d in date_d]
    event_ks = sorted(df["event_month"].astype(int).unique())
    if event_study:
        ints = [k for k in event_ks if k != -1]
        names += [f"Exposure_x_event_{k}" for k in ints]
    else:
        names += ["Exposure_x_Post"]
    if sector_trends:
        names += [f"trend[{s}]" for s in sec_d]
    date_index = {pd.Timestamp(d): i for i, d in enumerate(dates)}
    X, y, groups = [], [], []
    for r in df.itertuples(index=False):
        dt = pd.Timestamp(r.date)
        row = [1.0]
        row += [1.0 if r.sector == s else 0.0 for s in sec_d]
        row += [1.0 if dt == pd.Timestamp(d) else 0.0 for d in date_d]
        ex = float(getattr(r, exposure))
        if event_study:
            row += [ex * (1.0 if int(r.event_month) == k else 0.0) for k in ints]
        else:
            row += [ex * (1.0 if int(r.event_month) >= post_start_event else 0.0)]
        if sector_trends:
            ti = float(date_index[dt])
            row += [ti if r.sector == s else 0.0 for s in sec_d]
        X.append(row); y.append(float(r.log_employment)); groups.append(r.sector)
    return np.asarray(y), np.asarray(X), names, np.asarray(groups), df


def fit_main(records: pd.DataFrame, exposure: str = "final_LCEI", post_start_event: int = 0,
             weights=None, sector_trends: bool = False) -> dict:
    y, X, names, groups, df = _design(records, exposure, post_start_event, False, sector_trends)
    model = sm.OLS(y, X) if weights is None else sm.WLS(y, X, weights=np.asarray(weights, dtype=float))
    fit = model.fit(cov_type="cluster", cov_kwds={"groups": groups})
    j = names.index("Exposure_x_Post")
    lo, hi = fit.conf_int()[j]
    return {
        "coefficient": float(fit.params[j]), "se": float(fit.bse[j]), "p_value": float(fit.pvalues[j]),
        "ci_low": float(lo), "ci_high": float(hi), "n": int(len(df)),
        "clusters": int(pd.Series(groups).nunique()), "fit": fit, "X": X, "y": y,
        "groups": groups, "names": names, "df": df,
    }


def fit_event_study(records: pd.DataFrame, exposure: str = "final_LCEI") -> pd.DataFrame:
    y, X, names, groups, df = _design(records, exposure, event_study=True)
    fit = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": groups})
    out = []
    for k in sorted(df["event_month"].astype(int).unique()):
        if k == -1:
            out.append([k, 0.0, 0.0, np.nan, 0.0, 0.0, "Reference (Mar 2025)"])
        else:
            j = names.index(f"Exposure_x_event_{k}")
            lo, hi = fit.conf_int()[j]
            out.append([k, fit.params[j], fit.bse[j], fit.pvalues[j], lo, hi, "Pre-policy" if k < 0 else "Post-policy"])
    return pd.DataFrame(out, columns=["event_month","coefficient","clustered_se","p_value","ci_low","ci_high","timing"])


def wild_cluster_pvalue(main: dict, reps: int = WILD_BOOTSTRAP_REPS, seed: int = RANDOM_SEED) -> float:
    """Wild-cluster bootstrap-t p-value for the exposure-by-post coefficient."""
    X, y, groups, names = main["X"], main["y"], main["groups"], main["names"]
    j = names.index("Exposure_x_Post")
    X0 = np.delete(X, j, axis=1)
    beta0 = np.linalg.solve(X0.T @ X0, X0.T @ y)
    yhat0 = X0 @ beta0
    u0 = y - yhat0
    xtx_inv = np.linalg.inv(X.T @ X)
    unique = sorted(set(groups))
    group_index = {g: i for i, g in enumerate(unique)}
    gids = np.asarray([group_index[g] for g in groups])
    n, k = X.shape
    g = len(unique)
    small_sample_scale = (g / (g - 1)) * ((n - 1) / (n - k))
    observed_t = float(main["fit"].tvalues[j])
    rng = np.random.default_rng(seed)
    draws = rng.choice([-1.0, 1.0], size=(reps, g))
    weights = draws[:, gids]
    y_boot = yhat0[None, :] + weights * u0[None, :]
    beta_boot = (xtx_inv @ X.T @ y_boot.T).T
    resid_boot = y_boot - beta_boot @ X.T
    projection = X @ xtx_inv[:, j]
    variance = np.zeros(reps)
    for group_id in range(g):
        mask = gids == group_id
        score = (resid_boot[:, mask] * projection[mask][None, :]).sum(axis=1)
        variance += score**2
    se_boot = np.sqrt(variance * small_sample_scale)
    t_boot = beta_boot[:, j] / se_boot
    exceed = np.count_nonzero(np.abs(t_boot) >= abs(observed_t))
    return float((exceed + 1) / (reps + 1))


def two_way_cluster(main: dict) -> dict:
    fit_plain = sm.OLS(main["y"], main["X"]).fit()
    df = main["df"]
    sec_codes = pd.Categorical(df["sector"]).codes
    time_codes = pd.Categorical(df["date"]).codes
    cov_both, _, _ = cov_cluster_2groups(fit_plain, sec_codes, time_codes)
    j = main["names"].index("Exposure_x_Post")
    se = float(np.sqrt(cov_both[j, j]))
    t = float(fit_plain.params[j] / se)
    p = float(2 * (1 - norm.cdf(abs(t))))
    return {"coefficient": float(fit_plain.params[j]), "se": se, "p_value": p,
            "ci_low": float(fit_plain.params[j]-1.96*se), "ci_high": float(fit_plain.params[j]+1.96*se)}
