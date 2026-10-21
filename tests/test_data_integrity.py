import pandas as pd
from labour_cost_shock.config import DATA_INPUTS
from labour_cost_shock.exposure import build_lcei
from labour_cost_shock.data import build_monthly_panel, load_paye_inputs
from labour_cost_shock.models import baseline_sample


def _inputs():
    return load_paye_inputs(DATA_INPUTS), pd.read_csv(DATA_INPUTS/"ashe_2024_revised_section_extract.csv"), pd.read_csv(DATA_INPUTS/"bres_2024_gb_section_extract.csv")


def test_lcei_structure_and_ranking():
    _,ashe,bres=_inputs(); lcei=build_lcei(ashe,bres)
    assert len(lcei)==19 and lcei["sic_section"].is_unique
    assert lcei.loc[lcei["final_LCEI"].idxmax(),"sic_section"]=="I"
    assert lcei.loc[lcei["final_LCEI"].idxmin(),"sic_section"]=="D"
    assert abs(float(lcei.loc[lcei["sic_section"]=="I","final_LCEI"].iloc[0])-2.354661) < 1e-6
    assert abs(float(lcei["final_LCEI"].mean())) < 1e-12


def test_monthly_panel_dimensions_and_keys():
    paye,ashe,bres=_inputs(); panel=build_monthly_panel(paye,build_lcei(ashe,bres)); baseline=baseline_sample(panel)
    assert panel["date"].nunique()==43 and panel["sector"].nunique()==19 and len(panel)==817
    assert baseline["sector"].nunique()==16 and len(baseline)==688
    assert baseline["date"].min()==pd.Timestamp("2023-01-01") and baseline["date"].max()==pd.Timestamp("2026-07-01")
    assert not panel[["date","sector"]].duplicated().any() and panel["payrolled_employees"].notna().all() and (panel["payrolled_employees"]>0).all()
    assert set(panel.loc[~panel["sector"].isin(baseline["sector"].unique()),"sic_section"])=={"O","P","Q"}
