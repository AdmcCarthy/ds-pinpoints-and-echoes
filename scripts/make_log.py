"""The log: the composite log of 15/9-F-11 T2 over the reservoir window, and the core against the log in the cored wells.

Inputs: the Volve well-log zip (one LAS file, never copied) and the ep mid-layer (the well's check shot for depth and time,
marts/well_core_vs_log for the paired core and interpreted values). Writes log.csv, core_log_pairs.csv and log_notes.json.

Choices: the check shot of the well converts measured depth to depth below sea level and to two-way time. The log is kept
at every fifth sample for the page. The core-to-log pairs are the engine's own pairing (shifted plug depth, nearest log
sample); the interpretation is calibrated to the core, so the comparison is a consistency check, not an independent test.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I drops the script folder from sys.path
from common import HUGIN_TVDSS, LAS_MEMBER, WELL, args, marts, well_log, write_notes  # noqa: E402

COLUMNS = {"DEPTH": "md_m", "GR": "gr_api", "RHOB": "rhob_g_cm3", "NPHI": "nphi_v_v", "RT": "rt_ohm_m", "DT": "dt_us_ft"}


def main() -> None:
    a = args(("--volve", {"required": True, "type": Path}))
    log, _, _ = well_log(a.ep, a.volve)
    out = log.iloc[::5][list(COLUMNS) + ["tvdss_m", "twt_ms"]].rename(columns=COLUMNS)
    out.round({"md_m": 2, "tvdss_m": 2, "twt_ms": 2, "gr_api": 1, "rhob_g_cm3": 3, "nphi_v_v": 3, "rt_ohm_m": 2, "dt_us_ft": 1}).to_csv(a.out / "log.csv", index=False)
    notes = {"log": {"well": WELL, "las": LAS_MEMBER.split("/")[-1], "sample_m": float(np.median(np.diff(log.DEPTH))), "md_range": [float(log.DEPTH.min()), float(log.DEPTH.max())],
                     "hugin_tvdss": list(HUGIN_TVDSS), "hugin_thickness_m": round(HUGIN_TVDSS[1] - HUGIN_TVDSS[0], 1),
                     "coverage": {c: float(log[c].notna().mean()) for c in ["GR", "RHOB", "NPHI", "RT", "DT"]}}}

    pairs = pd.read_parquet(marts(a.ep) / "well_core_vs_log.parquet")
    keep = ["well_name", "depth_shifted_md_m", "phi_core", "phi_log", "k_core_md", "k_log_md", "k_log_at_floor"]
    pairs[keep].round({"depth_shifted_md_m": 2, "phi_core": 4, "phi_log": 4, "k_core_md": 3, "k_log_md": 3}).to_csv(a.out / "core_log_pairs.csv", index=False)
    summ = pd.read_parquet(marts(a.ep) / "well_core_vs_log_summary.parquet")
    notes["core_vs_log"] = summ.to_dict("records")
    write_notes(a.out, "log", notes)


if __name__ == "__main__":
    main()
