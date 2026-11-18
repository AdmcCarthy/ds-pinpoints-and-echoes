"""The field: two published versions of the same Volve horizons, closure area against depth on the Hugin top, and the 2005
plan's distribution of the oil-water contact.

Inputs (never copied): the Volve interpretation zip, the ep mid-layer pick check, and kit-surfaces data/out/closures.json
and contacts.json. Writes spread.csv, transect.csv, picks.csv, closure.csv, contact.csv and field_notes.json.

Choices (also in data/README.md):
- Each pair is the same surface from the base survey (ST0202R08, PSDM) and the reprocessed survey (ST10010). They differ
  in processing and in picking, so they are two published answers, not blind interpretations. Two-way time only.
  Differences are taken at nodes that coincide within 8 m; distance is to the nearest well pick of any surface.
- Closure area is the Volve high on kit-surfaces' smoothed Hugin top depth surface (interpreted). The contact
  distribution is the 2005 plan for development as digitised in kit-surfaces.
"""

from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I drops the script folder from sys.path
from common import args, marts, write_notes  # noqa: E402

PAIRS = {
    "Ty Fm top": ("Ty_Fm_Top+ST0202R08_PS_PSDM_FULL_PP+STAT+TIME.dat", "Ty_Fm_Top+ST10010_Full+STAT+TIME.dat"),
    "Shetland Gp top": ("SHETLAND_GP+ST0202R08_PS_PSDM_FULL_PP+STAT+TIME.dat", "SHETLAND_GP_Top+ST10010ZC11_Full+STAT+TIME.dat"),
    "Base Cretaceous": ("BCU+ST0202R08_PS_PSDM_FULL_PP+STAT+TIME.dat", "BCU+ST10010ZC11_Full+STAT+TIME.dat"),
    "Hod Fm top": ("Hod_Fm+ST0202R08_PS_PSDM_FULL_PP+STAT+TIME.dat", "Hod+ST10010_Pz-PSDM-Full+STAT+TIME.dat"),
}
BINS = [0, 250, 500, 1000, 2000, np.inf]
LABELS = ["0-250 m", "250-500 m", "0.5-1 km", "1-2 km", "over 2 km"]
MIN_N = 1000  # nodes per distance band, below which the band is not drawn
MATCH_M = 8.0
STEP_M = 50.0


def versions(ep: Path, zpath: Path, out: Path) -> dict:
    from ep_seismic.reader_seismic_interp import parse_horizons

    z = zipfile.ZipFile(zpath)
    names = {n.split("/")[-1]: n for n in z.namelist()}
    load = lambda fn: parse_horizons(z.read(names[fn]).decode("latin-1"))[0][0]  # noqa: E731
    wc = pd.read_parquet(marts(ep) / "seis_horizon_well_check.parquet")
    tree = cKDTree(wc[["easting", "northing"]].dropna().drop_duplicates().to_numpy())
    rows, cache = [], {}
    for surf, (fa, fb) in PAIRS.items():
        A, B = load(fa), load(fb)
        cache[surf] = (A, B)
        d, i = cKDTree(A[["x", "y"]].to_numpy()).query(B[["x", "y"]].to_numpy())
        m = d < MATCH_M
        diff = B.z.to_numpy()[m] - A.z.to_numpy()[i[m]]
        band = pd.cut(tree.query(np.column_stack([B.x.to_numpy()[m], B.y.to_numpy()[m]]))[0], BINS, labels=LABELS, right=False)
        for lab in LABELS:
            s = np.asarray(band == lab)
            if s.sum() >= MIN_N:
                ad = np.abs(diff[s])
                rows.append((surf, lab, int(s.sum()), round(float(np.median(ad)), 2), round(float(np.percentile(ad, 90)), 2), round(float(np.median(diff[s])), 2)))
    spread = pd.DataFrame(rows, columns=["surface", "band", "nodes", "abs_median_ms", "abs_p90_ms", "signed_median_ms"])
    spread.to_csv(out / "spread.csv", index=False)

    # the longest straight line between two Ty Fm top picks that both versions cover
    A, B = cache["Ty Fm top"]
    picks = wc[wc.surface_name == "Ty Fm. Top"][["well", "easting", "northing", "pick_twt_ms"]].dropna()
    ta, tb = cKDTree(A[["x", "y"]].to_numpy()), cKDTree(B[["x", "y"]].to_numpy())
    pts = picks[["easting", "northing"]].to_numpy()
    best = None
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            L = float(np.hypot(*(pts[j] - pts[i])))
            if best is not None and L <= best[0]:
                continue
            line = pts[i] + np.linspace(0, 1, int(L // STEP_M) + 1)[:, None] * (pts[j] - pts[i])
            if (ta.query(line)[0] < MATCH_M * 2).all() and (tb.query(line)[0] < MATCH_M * 2).all():
                best = (L, i, j)
    L, i, j = best
    n = int(L // STEP_M) + 1
    line = pts[i] + np.linspace(0, 1, n)[:, None] * (pts[j] - pts[i])
    pd.DataFrame({"dist_m": np.round(np.linspace(0, L, n), 1), "twt_base_ms": np.round(A.z.to_numpy()[ta.query(line)[1]], 2),
                  "twt_reprocessed_ms": np.round(B.z.to_numpy()[tb.query(line)[1]], 2)}).to_csv(out / "transect.csv", index=False)
    u = (pts[j] - pts[i]) / L
    rel = pts - pts[i]
    along, across = rel @ u, rel @ np.array([-u[1], u[0]])
    near = (np.abs(across) <= 150) & (along >= -50) & (along <= L + 50)
    picks[near].assign(dist_m=np.round(along[near], 1), offset_m=np.round(across[near], 1))[["well", "dist_m", "offset_m", "pick_twt_ms"]].round(2).to_csv(out / "picks.csv", index=False)
    return {"line_m": L, "n_samples": n, "n_picks": int(near.sum()), "surfaces": sorted(spread.surface.unique())}


def closure(surfaces: Path, out: Path) -> dict:
    cl = json.loads((surfaces / "data/out/closures.json").read_text())["horizons"]["hugin_top_depth"]["highs"]
    high = max((h for h in cl if h.get("curve")), key=lambda h: h["relief"])
    curve = pd.DataFrame({"depth_m": high["curve"]["depth"], "area_km2": high["curve"]["area_km2"]})
    curve.to_csv(out / "closure.csv", index=False)
    txt = json.dumps(json.loads((surfaces / "data/out/contacts.json").read_text()))
    q = json.loads(re.search(r'"quantiles":\s*(\{[^}]*"exceedance":\s*\{[^}]*\}[^}]*\})', txt).group(1))
    exc = {float(k): v for k, v in q["exceedance"].items()}
    depths = sorted(exc)
    probs = [exc[d] - (exc[depths[i + 1]] if i + 1 < len(depths) else 0) for i, d in enumerate(depths)]
    pd.DataFrame({"depth_m": depths, "exceedance_pct": [exc[d] for d in depths], "probability_pct": probs}).to_csv(out / "contact.csv", index=False)
    area_at = lambda d: float(np.interp(d, curve.depth_m, curve.area_km2, right=np.nan))  # noqa: E731
    return {"high": high["id"], "crest_m": high["z"], "spill_m": high["spill"]["z"], "spill_kind": high["spill"]["kind"], "curve_max_depth": float(curve.depth_m.max()),
            "P90": q["P90"], "P50": q["P50"], "P10": q["P10"], "area_P90": area_at(q["P90"]), "area_P50": area_at(q["P50"])}


def main() -> None:
    a = args(("--volve", {"required": True, "type": Path}), ("--surfaces", {"required": True, "type": Path}))
    notes = {"versions": versions(a.ep, a.volve / "Volve_Geophysical_Interpretations.zip", a.out), "closure": closure(a.surfaces, a.out)}
    write_notes(a.out, "field", notes)


if __name__ == "__main__":
    main()
