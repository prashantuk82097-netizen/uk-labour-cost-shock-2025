from __future__ import annotations
import numpy as np
import pandas as pd
from scipy.stats import zscore
from .config import NLW_2025


def build_lcei(ashe: pd.DataFrame, bres: pd.DataFrame) -> pd.DataFrame:
    """Construct the locked 2024 Labour-Cost Exposure Index at SIC-section level.

    LCEI_s = mean[
        z(NLW_2025 / median hourly pay_s),
        z(NLW_2025 / p10 hourly pay_s),
        z(part-time intensity_s)
    ]

    Equal weights and 2024 pre-policy inputs are intentional and transparent.
    """
    cols = [
        "sic_section", "sector", "median_hourly_pay_excl_overtime",
        "p10_hourly_pay_excl_overtime", "part_time_intensity_ashe",
    ]
    df = ashe[cols].merge(
        bres[["sic_section", "part_time_intensity"]], on="sic_section", how="inner"
    )
    df = df.rename(columns={"part_time_intensity": "bres_part_time_intensity"})
    df["wage_floor_proximity"] = NLW_2025 / df["median_hourly_pay_excl_overtime"]
    df["lower_tail_exposure"] = NLW_2025 / df["p10_hourly_pay_excl_overtime"]
    df["z_wage_floor_proximity"] = zscore(df["wage_floor_proximity"], ddof=0)
    df["z_lower_tail_exposure"] = zscore(df["lower_tail_exposure"], ddof=0)
    df["z_bres_part_time_intensity"] = zscore(df["bres_part_time_intensity"], ddof=0)
    df["final_LCEI"] = df[[
        "z_wage_floor_proximity", "z_lower_tail_exposure", "z_bres_part_time_intensity"
    ]].mean(axis=1)

    sens = df[df["part_time_intensity_ashe"].notna()].copy()
    sens["z_wage_floor_sens"] = zscore(sens["wage_floor_proximity"], ddof=0)
    sens["z_lower_tail_sens"] = zscore(sens["lower_tail_exposure"], ddof=0)
    sens["z_ashe_part_time"] = zscore(sens["part_time_intensity_ashe"], ddof=0)
    sens["LCEI_ASHE_part_time_sensitivity"] = sens[[
        "z_wage_floor_sens", "z_lower_tail_sens", "z_ashe_part_time"
    ]].mean(axis=1)
    df = df.merge(
        sens[["sic_section", "LCEI_ASHE_part_time_sensitivity"]],
        on="sic_section", how="left"
    )
    return df.sort_values("sic_section").reset_index(drop=True)
