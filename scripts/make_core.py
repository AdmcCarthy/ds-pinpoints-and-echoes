"""The pore and the plug: mercury-injection curves, routine core plugs, a fitted throat relation and how much rock was measured.

Inputs (ep mid-layer, Volve core analysis of 15/9-19 A and 15/9-19 BT2, and Sodir cores):
- marts/well_core_mercury_injection: 11 mercury-injection curves of 15/9-19 A, report 15-9-19_A_0035.pdf pages 213 to 224.
- marts/well_core_plug: 860 routine plugs (Klinkenberg-corrected horizontal permeability, helium porosity).
- marts/well_core_vs_log_summary: core against the petrophysical interpretation.
- canonical/well_core and well_header: Sodir cored lengths per wellbore.

Choices, stated here and in data/README.md:
- R35 is the pore-throat radius at which the cumulative mercury saturation first reaches 35 % and stays above it,
  interpolated in log radius. The radii are the report's own conversion of pressure to radius.
- The throat relation log10(R35) = a + b log10(k) + c log10(phi) is fitted by least squares on the mercury samples
  (Winland's idea; his coefficients are not used). Porosity missing on a mercury sample is taken from the routine plug at
  the same depth (within 0.05 m).
- Plug volume: 1 inch horizontal plugs (report page 12) and 1.5 inch vertical plugs (page 9); the length is not stated,
  so a plug is taken as long as it is wide (an assumption).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I drops the script folder from sys.path
from common import args, canonical, marts, write_notes  # noqa: E402

INCH = 0.0254
R35_LEVEL = 0.35


def r35(curve: pd.DataFrame) -> float:
    """Radius at which the cumulative saturation crosses R35_LEVEL for the last time from below (skips the noisy first points)."""
    c = curve.sort_values("pc_bar")
    s, r = c.hg_sat_frac.to_numpy(), c.pore_radius_um.to_numpy()
    below = np.flatnonzero(s < R35_LEVEL)
    if len(below) == 0 or below[-1] == len(s) - 1:
        return math.nan
    i = below[-1]
    f = (R35_LEVEL - s[i]) / (s[i + 1] - s[i])
    return float(10 ** (np.log10(r[i]) + f * (np.log10(r[i + 1]) - np.log10(r[i]))))


def main() -> None:
    a = args()
    m, c = marts(a.ep), canonical(a.ep)
    notes = {}

    # ---- mercury injection
    mi = pd.read_parquet(m / "well_core_mercury_injection.parquet")
    mi = mi[~mi.flag_radius.astype(bool)]
    plugs = pd.read_parquet(m / "well_core_plug.parquet")
    p19a = plugs[plugs.well_name == "15/9-19 A"]
    samples = []
    for depth, g in mi.groupby("depth_m"):
        phi = g.porosity_frac.iloc[0]
        phi_basis = "report"
        if pd.isna(phi):
            near = p19a.iloc[(p19a.depth_md_m - depth).abs().argsort()[:1]]
            if len(near) and abs(float(near.depth_md_m.iloc[0]) - depth) <= 0.05 and pd.notna(near.por_h_pct.iloc[0]):
                phi, phi_basis = float(near.por_h_pct.iloc[0]) / 100, "routine plug at the same depth"
        samples.append({"depth_m": depth, "page": int(g.report_page.iloc[0]), "k_md": float(g.kl_md.iloc[0]), "phi": phi, "phi_basis": phi_basis,
                        "r35_um": r35(g), "entry_um": float(g.sort_values("pc_bar").pore_radius_um.iloc[np.argmax(g.sort_values("pc_bar").hg_sat_frac.to_numpy() >= 0.05)])})
    s = pd.DataFrame(samples)
    curves = mi[["depth_m", "pc_bar", "hg_sat_frac", "pore_radius_um"]].round({"hg_sat_frac": 3, "pore_radius_um": 4})
    curves.to_csv(a.out / "micp.csv", index=False)

    fit = s.dropna(subset=["phi", "r35_um"])
    X = np.column_stack([np.ones(len(fit)), np.log10(fit.k_md), np.log10(fit.phi * 100)])
    y = np.log10(fit.r35_um)
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ coef
    s["r35_fit_um"] = 10 ** (coef[0] + coef[1] * np.log10(s.k_md) + coef[2] * np.log10(s.phi * 100))
    s.round(4).to_csv(a.out / "micp_samples.csv", index=False)
    # the simpler relation on permeability alone, to show what porosity adds
    Xk = X[:, :2]
    ck, *_ = np.linalg.lstsq(Xk, y, rcond=None)
    rk = y - Xk @ ck
    notes["micp"] = {"n_samples": int(len(s)), "n_fit": int(len(fit)), "pages": [int(s.page.min()), int(s.page.max())], "report": "15-9-19_A_0035.pdf",
                     "r35_min_um": float(s.r35_um.min()), "r35_max_um": float(s.r35_um.max()), "radius_min_um": float(mi.pore_radius_um.min()),
                     "radius_max_um": float(mi.pore_radius_um.max()), "coef": [float(x) for x in coef], "rms_log10": float(np.sqrt(np.mean(resid**2))),
                     "rms_log10_k_only": float(np.sqrt(np.mean(rk**2))), "coef_k_only": [float(x) for x in ck],
                     "phi_from_plug": int((s.phi_basis != "report").sum())}

    # ---- routine plugs, with the fitted throat
    k = plugs.kl_h_md.astype(float)
    phi = plugs.por_h_pct.astype(float)
    ok = (k > 0) & (phi > 0)
    out = pd.DataFrame({"well": plugs.well_name, "depth_m": plugs.depth_shifted_md_m.astype(float).round(2), "k_md": k.round(3), "phi_pct": phi.round(1)})
    out["r35_um"] = np.where(ok, 10 ** (coef[0] + coef[1] * np.log10(k.where(ok)) + coef[2] * np.log10(phi.where(ok))), np.nan)
    out["r35_um"] = out.r35_um.round(3)
    out.to_csv(a.out / "plugs.csv", index=False)
    both = out[ok]
    band = both[(both.phi_pct >= 19) & (both.phi_pct <= 21)]
    lk, lp = np.log10(both.k_md), both.phi_pct
    notes["plugs"] = {"n_plugs": int(len(plugs)), "by_well": plugs.groupby("well_name").size().to_dict(), "n_k": int(k.notna().sum()), "n_both": int(len(both)),
                      "k_min": float(k.min()), "k_max": float(k.max()), "k_p10": float(k.quantile(0.1)), "k_p50": float(k.quantile(0.5)), "k_p90": float(k.quantile(0.9)),
                      "phi_p50": float(phi.median()), "band": [19, 21], "band_n": int(len(band)), "band_k_min": float(band.k_md.min()), "band_k_max": float(band.k_md.max()),
                      "r2_logk_phi": float(np.corrcoef(lp, lk)[0, 1] ** 2), "r35_p10": float(both.r35_um.quantile(0.1)), "r35_p50": float(both.r35_um.quantile(0.5)),
                      "r35_p90": float(both.r35_um.quantile(0.9))}

    # ---- how much rock the plugs are: horizontal 1 inch, vertical 1.5 inch, length = diameter (assumption)
    n_h = int((plugs.kl_h_md.notna() | plugs.por_h_pct.notna()).sum())
    n_v = int((plugs.kl_v_md.notna() | plugs.por_v_pct.notna()).sum())
    vol = lambda d_in: math.pi * (d_in * INCH / 2) ** 2 * (d_in * INCH)  # noqa: E731
    v_total = n_h * vol(1.0) + n_v * vol(1.5)
    notes["plug_volume"] = {"n_horizontal": n_h, "n_vertical": n_v, "m3_horizontal": vol(1.0), "m3_vertical": vol(1.5), "m3_total": v_total,
                            "pages": {"horizontal_1in": 12, "vertical_1_5in": 9}, "length_assumption": "length equals diameter"}

    # ---- every metre of core Sodir lists for the Norwegian North Sea
    wc = pd.read_parquet(c / "well_core.parquet")
    wh = pd.read_parquet(c / "well_header.parquet")[["wellbore_id", "main_area"]]
    wc = wc.merge(wh, on="wellbore_id", how="left")
    ns = wc[wc.main_area == "NORTH SEA"]
    length = (ns.base_md_m - ns.top_md_m).clip(lower=0)
    notes["sodir_core"] = {"n_cores": int(len(ns)), "n_wellbores": int(ns.wellbore_id.nunique()), "core_km": float(length.sum() / 1000)}

    write_notes(a.out, "core", notes)


if __name__ == "__main__":
    main()
