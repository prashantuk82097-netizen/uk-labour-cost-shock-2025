from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_INPUTS = ROOT / "data" / "inputs"
DATA_PROCESSED = ROOT / "data" / "processed"
RESULT_TABLES = ROOT / "results" / "tables"
RESULT_FIGURES = ROOT / "results" / "figures"

NLW_2025 = 12.21
POLICY_MONTH = "2025-04-01"
EVENT_REFERENCE_MONTH = "2025-03-01"
START_MONTH = "2023-01-01"
END_MONTH = "2026-07-01"
WILD_BOOTSTRAP_REPS = 999
RANDOM_SEED = 2026

BASELINE_EXCLUSIONS = {
    "Public administration and defence; social security",
    "Education",
    "Health and social work",
}
