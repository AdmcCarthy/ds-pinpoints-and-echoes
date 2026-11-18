"""The echo: one inline of the Volve ST10010 full stack through 15/9-F-11 T2, the trace at the well, the published horizons
along the line, a synthetic seismogram against the trace, a synthetic wedge and one two-way time read through every
check-shot table.

Inputs (never copied): the SEG-Y full stack, the Volve interpretation zip, the well-log zip and the ep mid-layer.
Writes section.json, trace.csv, horizons.csv, tie.csv, wedge.json, timedepth.csv and seismic_notes.json.

Choices (also in data/README.md):
- Domain is two-way time in ms (the file name says _T, the text header PSDM in time). Amplitudes are relative and the
  polarity is not stated, so the synthetic is drawn with whichever sign matches better and that sign is reported.
- The wavelet is a zero-phase Ricker at the centroid frequency of the real data around the reservoir. No stretch or
  squeeze; one bulk shift is reported.
- The wedge is synthetic: two interfaces of equal and opposite reflectivity at the log's reservoir velocity.
- The depth fan reads every Volve check-shot table at one two-way time that all of them cover.
"""

from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import segyio

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I drops the script folder from sys.path
from common import HUGIN_TVDSS, WELL, args, well_log, write_notes  # noqa: E402

SEGY = "Seismic/ST10010ZC11_PZ_PSDM_KIRCH_FULL_T.MIG_FIN.POST_STACK.3D.JS-017536.segy"
WELL_XY = (436123.2, 6479126.0)  # 15/9-F-11 T2 at the Hugin top pick, ED50 / UTM 31N
T0, T1 = 1800.0, 3300.0
KEEP_EVERY = 2
SPEC_WIN = (2300.0, 3100.0)
FAN_TWT = 2650.0
HORIZONS = {"Ty Fm top": "Ty_Fm_Top+ST10010_Full+STAT+TIME.dat", "Shetland Gp top": "SHETLAND_GP_Top+ST10010ZC11_Full+STAT+TIME.dat",
            "Base Cretaceous": "BCU+ST10010ZC11_Full+STAT+TIME.dat", "Hugin Fm top": "Hugin_Fm_Top+ST10010ZC11_Near_190314+STAT+TIME.dat",
            "Hugin Fm base": "Hugin_Fm_Base+ST10010ZC11_Near_190314+STAT+TIME.dat"}


def ricker(f_hz: float, dt_ms: float, half_ms: float = 100.0) -> np.ndarray:
    t = np.arange(-half_ms, half_ms + dt_ms, dt_ms) / 1000.0
    q = (np.pi * f_hz * t) ** 2
    return (1 - 2 * q) * np.exp(-q)


def section(segy: Path):
    with segyio.open(str(segy), ignore_geometry=True) as f:
        il = np.asarray(f.attributes(segyio.TraceField.INLINE_3D)[:])
        xl = np.asarray(f.attributes(segyio.TraceField.CROSSLINE_3D)[:])
        sc = np.asarray(f.attributes(segyio.TraceField.SourceGroupScalar)[:]).astype(float)
        k = np.where(sc < 0, -1.0 / sc, np.where(sc > 0, sc, 1.0))
        x = np.asarray(f.attributes(segyio.TraceField.CDP_X)[:]) * k
        y = np.asarray(f.attributes(segyio.TraceField.CDP_Y)[:]) * k
        t = np.asarray(f.samples, dtype=float)
        i_well = int(np.argmin((x - WELL_XY[0]) ** 2 + (y - WELL_XY[1]) ** 2))
        line = int(il[i_well])
        sel = np.where(il == line)[0]
        sel = sel[np.argsort(xl[sel])]
        w = (t >= T0) & (t <= T1)
        data = np.stack([f.trace[int(i)][w] for i in sel])
        trace_well = np.asarray(f.trace[i_well])
    dist = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(x[sel]), np.diff(y[sel])))])
    j = int(np.where(sel == i_well)[0][0])
    dt = float(t[1] - t[0])
    s0, s1 = np.searchsorted(t[w], SPEC_WIN[0]), np.searchsorted(t[w], SPEC_WIN[1])
    block = data[max(0, j - 20): j + 21, s0:s1] * np.hanning(s1 - s0)
    spec = np.abs(np.fft.rfft(block, axis=1)).mean(axis=0)
    freqs = np.fft.rfftfreq(s1 - s0, d=dt / 1000.0)
    kept = data[::KEEP_EVERY]
    scale = float(np.percentile(np.abs(kept), 99.5))
    sec = {"well": WELL, "inline": line, "domain": "two-way time, ms (PSDM stack in time)", "polarity": "not stated in the headers; unknown",
           "quantity": "relative amplitude, int8 on the scale below", "scale_abs": scale, "t0_ms": float(t[w][0]), "dt_ms": dt,
           "n_samples": int(kept.shape[1]), "crosslines": [int(v) for v in xl[sel][::KEEP_EVERY]], "dist_m": [round(float(v), 1) for v in dist[::KEEP_EVERY]],
           "well_dist_m": round(float(dist[j]), 1), "well_trace_offset_m": round(float(np.hypot(x[i_well] - WELL_XY[0], y[i_well] - WELL_XY[1])), 1),
           "bin_m": round(float(np.median(np.diff(dist))), 2), "dominant_hz": round(float(freqs[np.argmax(spec[1:]) + 1]), 1),
           "centroid_hz": round(float((freqs * spec).sum() / spec.sum()), 1), "spectrum_window_ms": list(SPEC_WIN), "crs": "ED50 / UTM 31N (text header)",
           "amp": np.clip(np.round(kept / scale * 127), -127, 127).astype(np.int8).tolist(),
           "source": "Volve data village, ST10010ZC11 PZ PSDM Kirchhoff full stack, time, 2011 processing"}
    keep_t = (t >= T0 - 400) & (t <= T1 + 200)
    trace = pd.DataFrame({"t_ms": t[keep_t].round(0).astype(int), "amp": np.round(trace_well[keep_t] / scale, 4)})
    return sec, trace


def main() -> None:
    a = args(("--volve", {"required": True, "type": Path}))
    out, notes = a.out, {}
    sec, trace = section(a.volve / SEGY)
    (out / "section.json").write_text(json.dumps(sec, separators=(",", ":")))
    trace.to_csv(out / "trace.csv", index=False)
    notes["section"] = {k: v for k, v in sec.items() if k not in ("amp", "crosslines", "dist_m")} | {"n_traces": len(sec["crosslines"]) * KEEP_EVERY}

    # ---- the published horizons along the inline
    from ep_seismic.reader_seismic_interp import parse_horizons

    zi = zipfile.ZipFile(a.volve / "Volve_Geophysical_Interpretations.zip")
    names = {n.split("/")[-1]: n for n in zi.namelist()}
    rows = []
    for label, fn in HORIZONS.items():
        d = parse_horizons(zi.read(names[fn]).decode("latin-1"))[0][0]
        d = d[d.inline == sec["inline"]].set_index("crossline").z
        rows += [(label, xl, round(float(d.loc[xl]), 1)) for xl in sec["crosslines"] if xl in d.index]
    hz = pd.DataFrame(rows, columns=["horizon", "crossline", "twt_ms"])
    hz.to_csv(out / "horizons.csv", index=False)
    i_well = int(np.argmin(np.abs(np.array(sec["dist_m"]) - sec["well_dist_m"])))
    at = hz[(hz.horizon == "Hugin Fm top") & (hz.crossline == sec["crosslines"][i_well])]
    notes["horizons"] = {"counts": hz.horizon.value_counts().to_dict(), "hugin_twt_ms_at_well": float(at.twt_ms.iloc[0]) if len(at) else None}

    # ---- synthetic seismogram from the log against the real trace
    L, _, td_all = well_log(a.ep, a.volve)
    f_hz = float(sec["centroid_hz"])
    ai = (304800.0 / L.DT * L.RHOB).to_numpy()
    rc = np.zeros(len(L))
    ok = np.isfinite(ai[1:]) & np.isfinite(ai[:-1])
    rc[1:][ok] = (ai[1:][ok] - ai[:-1][ok]) / (ai[1:][ok] + ai[:-1][ok])
    twt = L.twt_ms.to_numpy()
    grid = np.arange(np.floor(twt.min()), np.ceil(twt.max()) + 1.0, 1.0)
    rc_t = np.zeros(len(grid))
    np.add.at(rc_t, np.clip(np.round(twt - grid[0]).astype(int), 0, len(grid) - 1), rc)
    syn = np.interp(trace.t_ms, grid, np.convolve(rc_t, ricker(f_hz, 1.0), mode="same"), left=0.0, right=0.0)
    win = ((trace.t_ms >= SPEC_WIN[0]) & (trace.t_ms <= SPEC_WIN[1])).to_numpy()
    syn = syn / (np.sqrt(np.mean(syn[win] ** 2)) or 1.0) * np.sqrt(np.mean(trace.amp[win] ** 2))
    cc = {lag * 4: float(np.corrcoef(np.roll(syn, lag)[win], trace.amp[win])[0, 1]) for lag in range(-10, 11)}
    best, worst = max(cc, key=cc.get), min(cc, key=cc.get)
    sign = -1 if -cc[worst] > cc[best] else 1
    best = worst if sign < 0 else best
    syn = sign * syn
    pd.DataFrame({"t_ms": trace.t_ms, "real": trace.amp, "synthetic": np.round(syn, 4), "synthetic_shifted": np.round(np.roll(syn, best // 4), 4)}).to_csv(out / "tie.csv", index=False)
    notes["tie"] = {"wavelet_hz": f_hz, "corr_zero_lag": round(sign * cc[0], 3), "best_shift_ms": best, "corr_best": round(abs(cc[best]), 3), "sign": sign,
                    "impedance_coverage": float(np.mean(np.isfinite(ai))), "window_ms": list(SPEC_WIN)}

    # ---- the wedge
    hug = L[(L.tvdss_m >= HUGIN_TVDSS[0]) & (L.tvdss_m <= HUGIN_TVDSS[1])]
    v_res = float(np.nanmedian(304800.0 / hug.DT))
    thick, tgrid = np.arange(0, 81, 1.0), np.arange(0, 200.0, 1.0)
    wav = ricker(f_hz, 1.0, half_ms=99.0)
    amp, appar = np.zeros((len(thick), len(tgrid))), np.zeros(len(thick))

    def refine(s, k):  # parabolic peak position between samples
        den = s[k - 1] - 2 * s[k] + s[k + 1] if 0 < k < len(s) - 1 else 0
        return k + 0.5 * (s[k - 1] - s[k + 1]) / den if den else float(k)

    for i, h in enumerate(thick):
        r = np.zeros(len(tgrid))
        r[60] += 1.0
        tb = int(round(60.0 + 2 * h / v_res * 1000))
        if tb < len(tgrid):
            r[tb] -= 1.0
        s = np.convolve(r, wav, mode="same")
        amp[i] = s
        it = int(np.argmax(s[:100]))
        ib = int(np.argmin(s[it:])) + it
        appar[i] = (refine(s, ib) - refine(s, it)) / 1000 * v_res / 2
    peak = amp.max(axis=1)
    sc = float(np.abs(amp).max())
    wedge = {"f_hz": f_hz, "v_m_s": round(v_res), "thickness_m": thick.tolist(), "t_ms": tgrid.tolist(), "top_ms": 60.0, "amp": np.round(amp / sc, 3).tolist(),
             "peak_amp": np.round(peak / sc, 3).tolist(), "apparent_m": np.round(appar, 1).tolist(), "tuning_m": float(thick[np.argmax(peak)]),
             "quarter_wavelength_m": round(v_res / (4 * f_hz), 1), "note": "synthetic: two interfaces of equal and opposite reflectivity"}
    (out / "wedge.json").write_text(json.dumps(wedge, separators=(",", ":")))
    notes["wedge"] = {k: wedge[k] for k in ("f_hz", "v_m_s", "tuning_m", "quarter_wavelength_m")}

    # ---- one time, every check-shot table
    rows = []
    for mem, g in td_all.groupby("member"):
        well = g.wellbore_name.iloc[0] or mem.split("/")[1].replace("_", "/", 1)
        short = mem.split("/")[-1].replace(".ASC", "").replace(".LIST", "").replace("TZV_TIME_", "").replace("STATOIL_", "")
        g = g.sort_values("twt_ms")
        rows += [(f"{well} {short}", round(r.twt_ms, 1), round(r.tvdss_m, 1)) for r in g.iloc[:: max(1, len(g) // 60)].itertuples()]
        if g.twt_ms.min() <= FAN_TWT <= g.twt_ms.max():
            rows.append((f"{well} {short}", FAN_TWT, round(float(np.interp(FAN_TWT, g.twt_ms, g.tvdss_m)), 1)))
    tdf = pd.DataFrame(rows, columns=["table", "twt_ms", "tvdss_m"]).drop_duplicates().sort_values(["table", "twt_ms"])
    tdf.to_csv(out / "timedepth.csv", index=False)
    at = tdf[tdf.twt_ms == FAN_TWT]
    notes["fan"] = {"twt_ms": FAN_TWT, "n_tables": int(len(at)), "depth_min": float(at.tvdss_m.min()), "depth_max": float(at.tvdss_m.max()),
                    "wells": sorted({" ".join(t.split(" ")[:2]) for t in at.table})}
    write_notes(out, "seismic", notes)


if __name__ == "__main__":
    main()
