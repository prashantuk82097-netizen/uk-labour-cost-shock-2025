import pandas as pd
from labour_cost_shock.config import DATA_INPUTS
from labour_cost_shock.exposure import build_lcei
from labour_cost_shock.data import build_monthly_panel, load_paye_inputs
from labour_cost_shock.models import baseline_sample, fit_main


def test_primary_monthly_result_is_reproduced():
    paye=load_paye_inputs(DATA_INPUTS); ashe=pd.read_csv(DATA_INPUTS/"ashe_2024_revised_section_extract.csv"); bres=pd.read_csv(DATA_INPUTS/"bres_2024_gb_section_extract.csv")
    res=fit_main(baseline_sample(build_monthly_panel(paye,build_lcei(ashe,bres))))
    assert abs(res["coefficient"] - (-0.0025680774)) < 1e-8
    assert abs(res["p_value"] - 0.8112548405) < 1e-7
    assert res["n"]==688 and res["clusters"]==16
