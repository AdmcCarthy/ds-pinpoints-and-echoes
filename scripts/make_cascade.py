"""Compounding: recoverable oil from the volumetric chain, with one uncertain factor added at a time.

    recoverable = GRV x net-to-gross x porosity x oil saturation / Bo x recovery factor

GRV (gross rock volume) is the rock between the Hugin top and the oil-water contact, for a reservoir of a given gross
thickness: GRV = integral of A(z) dz from max(crest, contact - thickness) to the contact, where A(z) is the area of the
Volve high above depth z (story/data/closure.csv, kit-surfaces). The contact is drawn from the 2005 plan's distribution
(story/data/contact.csv); a contact deeper than the mapped surface takes its deepest area, and the share of such draws
is reported. The other factors are the stated ranges in data/assumptions.yaml, fitted with the prospect library's families (ep_prospect)
(lognormal, logit-normal) and sampled with one fixed seed, so every step uses the same draws.

Step 0 frees the contact and the thickness (together they are the rock volume) and holds the rest at their P50; each later
step frees one more factor. The last step is repeated with the
rock properties (net-to-gross, porosity, oil saturation, recovery) linked through one shared rock-quality factor.

Run after make_field.py. Writes cascade.csv, cascade_hist.csv and cascade_notes.json.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from ep_prospect import distributions as dist

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I drops the script folder from sys.path
from common import ROOT, args, write_notes  # noqa: E402

ORDER = ["thickness_m", "ntg", "porosity", "hc_saturation", "bo", "recovery"]
ROCK = ["ntg", "porosity", "hc_saturation", "recovery"]
BINS = np.linspace(-0.5, 2.5, 61)  # log10 of Mn Sm3, 0.3 to 300


def main() -> None:
    a = args()
    cfg = yaml.safe_load((ROOT / "data" / "assumptions.yaml").read_text())
    rng = np.random.default_rng(cfg["seed"])
    n = int(cfg["draws"])
    curve = pd.read_csv(a.out / "closure.csv").sort_values("depth_m")
    contact = pd.read_csv(a.out / "contact.csv")
    crest, deepest = float(curve.depth_m.min()), float(curve.depth_m.max())

    # cumulative volume above depth z: V(z) = integral of A from the crest to z, m3
    z = curve.depth_m.to_numpy()
    area_m2 = curve.area_km2.to_numpy() * 1e6
    cum = np.concatenate([[0.0], np.cumsum(np.diff(z) * (area_m2[1:] + area_m2[:-1]) / 2)])
    vol_above = lambda d: np.interp(np.clip(d, crest, deepest), z, cum)  # noqa: E731

    def grv(c, h):
        return vol_above(c) - vol_above(np.maximum(crest, c - h))

    # one set of draws for everything
    c = rng.choice(contact.depth_m.to_numpy(), size=n, p=contact.probability_pct.to_numpy() / contact.probability_pct.sum())
    z_ind = {k: rng.standard_normal(n) for k in ORDER}
    shared = rng.standard_normal(n)
    rho = float(cfg["rock_quality_correlation"])
    z_cor = {k: (rho * shared + np.sqrt(1 - rho**2) * z_ind[k]) if k in ROCK else z_ind[k] for k in ORDER}
    fits = {}
    for k in ORDER:
        f = cfg["factors"][k]
        d, ev = dist.fit(f["kind"], f["p90"], f["p50"], f["p10"])
        if d is None:
            raise SystemExit(f"{k}: {ev}")
        fits[k] = d

    def run(free: set[str], zz: dict) -> np.ndarray:
        v = {k: dist.sample(fits[k], zz[k]) if k in free else np.full(n, fits[k].quantile(0.5)) for k in ORDER}
        return grv(c, v["thickness_m"]) * v["ntg"] * v["porosity"] * v["hc_saturation"] / v["bo"] * v["recovery"] / 1e6

    # the contact and the thickness together make the rock volume, so they are freed together; every later factor multiplies
    steps = [("rock_volume", "how much rock lies above the contact", {"thickness_m"}, z_ind)]
    for i, k in enumerate(ORDER[1:], start=2):
        steps.append((k, cfg["factors"][k]["label"], set(ORDER[:i]), z_ind))
    steps.append(("correlated", "rock properties that move together", set(ORDER), z_cor))

    rows, hist = [], []
    for i, (key, label, free, zz) in enumerate(steps):
        r = run(free, zz)
        p90, p50, p10 = np.percentile(r, [10, 50, 90])
        rows.append({"step": i, "key": key, "label": label, "p90": p90, "p50": p50, "p10": p10, "mean": r.mean(), "ratio": p10 / p90,
                     "sd_log10": float(np.std(np.log10(r[r > 0])))})
        h, _ = np.histogram(np.log10(np.clip(r, 10 ** BINS[0], 10 ** BINS[-1])), bins=BINS)
        hist += [{"step": i, "log10_lo": BINS[j], "log10_hi": BINS[j + 1], "share": h[j] / n} for j in range(len(h))]
    cas = pd.DataFrame(rows)
    cas.round(4).to_csv(a.out / "cascade.csv", index=False)
    pd.DataFrame(hist).round(5).to_csv(a.out / "cascade_hist.csv", index=False)
    notes ={"n": n, "seed": cfg["seed"], "crest_m": crest, "deepest_mapped_m": deepest, "contact_beyond_map_share": float(np.mean(c > deepest)),
             "rho": rho, "steps": cas.round(4).to_dict("records"), "factors": {k: cfg["factors"][k] for k in ORDER},
             "independent_final_ratio": float(cas.ratio.iloc[-2]), "correlated_final_ratio": float(cas.ratio.iloc[-1])}
    write_notes(a.out, "cascade", notes)


if __name__ == "__main__":
    main()
