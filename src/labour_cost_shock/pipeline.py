from __future__ import annotations
import json, math
import pandas as pd
from .config import DATA_INPUTS, DATA_PROCESSED, RESULT_TABLES, RESULT_FIGURES
from .exposure import build_lcei
from .data import build_monthly_panel, load_paye_inputs
from .models import baseline_sample, fit_main, fit_event_study, wild_cluster_pvalue, two_way_cluster
from .diagnostics import linear_pretrend, joint_binned_pretrend, residual_diagnostics, alternative_covariances
from .robustness import run_robustness, leave_one_sector_out
from .plots import lcei_ranking, quartile_trends, event_plot


def main():
    for d in [DATA_PROCESSED, RESULT_TABLES, RESULT_FIGURES]: d.mkdir(parents=True,exist_ok=True)
    ashe=pd.read_csv(DATA_INPUTS/"ashe_2024_revised_section_extract.csv")
    bres=pd.read_csv(DATA_INPUTS/"bres_2024_gb_section_extract.csv")
    lcei=build_lcei(ashe,bres)
    lcei.to_csv(DATA_PROCESSED/"lcei_2024.csv",index=False)
    paye=load_paye_inputs(DATA_INPUTS)
    panel=build_monthly_panel(paye,lcei)
    panel.to_csv(DATA_PROCESSED/"monthly_paye_lcei_panel.csv",index=False)
    baseline=baseline_sample(panel)
    mainres=fit_main(baseline); wild=wild_cluster_pvalue(mainres); tw=two_way_cluster(mainres)
    main_table=pd.DataFrame([{"specification":"Monthly baseline final LCEI","coefficient":mainres["coefficient"],"clustered_se":mainres["se"],"p_value":mainres["p_value"],"ci_low":mainres["ci_low"],"ci_high":mainres["ci_high"],"wild_cluster_bootstrap_p":wild,"two_way_cluster_p":tw["p_value"],"n":mainres["n"],"clusters":mainres["clusters"],"exact_percent_effect":100*(math.exp(mainres["coefficient"])-1),"exact_percent_ci_low":100*(math.exp(mainres["ci_low"])-1),"exact_percent_ci_high":100*(math.exp(mainres["ci_high"])-1)}])
    main_table.to_csv(RESULT_TABLES/"main_fixed_effects_monthly.csv",index=False)
    event=fit_event_study(baseline); event.to_csv(RESULT_TABLES/"event_study_monthly.csv",index=False)
    pre_full=linear_pretrend(baseline); pre_recent=linear_pretrend(baseline,"2024-04-01"); joint=joint_binned_pretrend(baseline)
    resid=residual_diagnostics(mainres); cov=alternative_covariances(baseline)
    diagnostics={"linear_pretrend_full":pre_full,"linear_pretrend_recent":pre_recent,"joint_binned_pretrend":joint,"residual_diagnostics":resid,"alternative_covariances":cov}
    (RESULT_TABLES/"diagnostics.json").write_text(json.dumps(diagnostics,indent=2),encoding="utf-8")
    inference=pd.DataFrame([["Sector-clustered",mainres["coefficient"],mainres["se"],mainres["p_value"],"Primary inference"],["Wild-cluster bootstrap",mainres["coefficient"],float("nan"),wild,"999 Rademacher cluster bootstrap; p-value only"],["Two-way cluster: sector + month",tw["coefficient"],tw["se"],tw["p_value"],"Cross-sectional time clustering sensitivity"],["Panel-HAC (maxlag 3)",cov["panel_hac"]["coefficient"],cov["panel_hac"]["se"],cov["panel_hac"]["p_value"],"Alternative covariance"],["Driscoll-Kraay-style (maxlag 3)",cov["driscoll_kraay_style"]["coefficient"],cov["driscoll_kraay_style"]["se"],cov["driscoll_kraay_style"]["p_value"],"Contradictory significant covariance sensitivity"]],columns=["method","coefficient","se","p_value","note"])
    inference.to_csv(RESULT_TABLES/"inference_sensitivity.csv",index=False)
    run_robustness(panel).to_csv(RESULT_TABLES/"robustness_monthly.csv",index=False)
    leave_one_sector_out(panel).to_csv(RESULT_TABLES/"leave_one_sector_out_monthly.csv",index=False)
    quarterly=baseline[baseline["date"].dt.month.isin([1,4,7,10])].copy(); qres=fit_main(quarterly)
    pd.DataFrame([["Monthly primary","Monthly",mainres["n"],mainres["coefficient"],mainres["se"],mainres["p_value"],mainres["ci_low"],mainres["ci_high"]],["Quarterly sampling from same monthly panel","Quarterly",qres["n"],qres["coefficient"],qres["se"],qres["p_value"],qres["ci_low"],qres["ci_high"]]],columns=["specification","frequency","n","coefficient","se","p_value","ci_low","ci_high"]).to_csv(RESULT_TABLES/"monthly_vs_quarterly.csv",index=False)
    ref=panel.loc[panel["date"].eq(pd.Timestamp("2025-03-01")),["sector","payrolled_employees"]].set_index("sector")["payrolled_employees"]
    end=panel.loc[panel["date"].eq(pd.Timestamp("2026-07-01")),["sector","payrolled_employees"]].set_index("sector")["payrolled_employees"]
    sector_summary=lcei[["sic_section","sector","final_LCEI"]].copy(); sector_summary["mar2025_to_jul2026_pct"]=[100*(end[s]/ref[s]-1) for s in sector_summary["sector"]]; sector_summary["baseline_included"]=~sector_summary["sector"].isin({"Public administration and defence; social security","Education","Health and social work"}); sector_summary.sort_values("final_LCEI",ascending=False).to_csv(RESULT_TABLES/"sector_summary.csv",index=False)
    lcei_ranking(lcei,RESULT_FIGURES/"01_lcei_ranking.svg"); quartile_trends(baseline,RESULT_FIGURES/"02_monthly_employment_by_lcei_quartile.svg"); event_plot(event,RESULT_FIGURES/"03_monthly_event_study.svg")
    summary={"panel_rows_all_19":int(len(panel)),"panel_rows_baseline_16":int(len(baseline)),"months":int(panel["date"].nunique()),"main_beta":mainres["coefficient"],"clustered_p":mainres["p_value"],"wild_cluster_p":wild,"two_way_cluster_p":tw["p_value"],"exact_percent_effect":100*(math.exp(mainres["coefficient"])-1),"ci_percent":[100*(math.exp(mainres["ci_low"])-1),100*(math.exp(mainres["ci_high"])-1)],"joint_pretrend_full_p":joint["full_p"],"joint_pretrend_recent_p":joint["recent_p"],"driscoll_kraay_style_p":cov["driscoll_kraay_style"]["p_value"],"interpretation":"No statistically detectable exposure-related PAYE employment divergence under primary clustered inference; causal interpretation remains limited by pre-policy diagnostics and covariance sensitivity."}
    (RESULT_TABLES/"headline_results.json").write_text(json.dumps(summary,indent=2),encoding="utf-8"); print(json.dumps(summary,indent=2))

if __name__ == "__main__": main()
