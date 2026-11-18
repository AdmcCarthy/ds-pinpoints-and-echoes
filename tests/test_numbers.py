"""Every number quoted in the prose is checked against the extracts it comes from.

The story is built once with SubScout; each test recomputes a metric independently from story/data/ and compares it with
the value in the build's numbers ledger. Run from the repo root with the SubScout environment:

    uv run --project ../core-subscout pytest tests
"""

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from subscout.build import build

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "story" / "data"


@pytest.fixture(scope="module")
def ledger(tmp_path_factory):
    out = tmp_path_factory.mktemp("site")
    rep = build(ROOT / "story", out)
    assert rep.errors == [] and rep.warnings == [], (rep.errors, rep.warnings)
    report = json.loads((out / "build-report.json").read_text(encoding="utf-8"))
    return {r["name"]: r for r in report["ledger"]}


def value(ledger, name):
    v = ledger[name]["value"]  # the ledger writes integers with thousands separators
    try:
        return float(str(v).replace(",", ""))
    except ValueError:
        return v


def notes(name):
    return json.loads((DATA / f"{name}_notes.json").read_text(encoding="utf-8"))


def close(a, b, rel=1e-4):
    return math.isclose(float(a), float(b), rel_tol=rel, abs_tol=1e-9)


def test_every_quoted_metric_is_finite(ledger):
    for name, row in ledger.items():
        v = row["value"]
        try:
            assert math.isfinite(float(str(v).replace(",", ""))), name
        except ValueError:
            assert v, name  # names and years are strings


def test_plugs(ledger):
    p = pd.read_csv(DATA / "plugs.csv")
    k, phi = p.k_md, p.phi_pct
    assert value(ledger, "n_plugs") == len(p)
    assert close(value(ledger, "k_min"), k.min()) and close(value(ledger, "k_max"), k.max())
    band = p[(phi >= 19) & (phi <= 21) & (k > 0)]
    assert value(ledger, "band_n") == len(band)
    assert close(value(ledger, "band_x"), band.k_md.max() / band.k_md.min())
    ok = p[(k > 0) & (phi > 0)]
    assert close(value(ledger, "r2_phi"), np.corrcoef(ok.phi_pct, np.log10(ok.k_md))[0, 1] ** 2)


def test_mercury_injection(ledger):
    m = pd.read_csv(DATA / "micp.csv")
    s = pd.read_csv(DATA / "micp_samples.csv")
    assert value(ledger, "micp_n") == m.depth_m.nunique() == len(s)
    assert close(value(ledger, "micp_r_min"), m.pore_radius_um.min(), 1e-3)
    assert close(value(ledger, "micp_r_max"), m.pore_radius_um.max(), 1e-3)
    assert close(value(ledger, "r35_min"), s.r35_um.min(), 1e-3) and close(value(ledger, "r35_max"), s.r35_um.max(), 1e-3)
    # R35 really is where each curve reaches 35 %: the curve's saturation at that radius, interpolated in log radius
    for d, g in m.groupby("depth_m"):
        r35 = float(s.loc[s.depth_m == d, "r35_um"].iloc[0])
        g = g.sort_values("pore_radius_um")
        sat = np.interp(np.log10(r35), np.log10(g.pore_radius_um), g.hg_sat_frac)
        assert abs(sat - 0.35) < 0.03, d


def test_plug_volume(ledger):
    inch = 0.0254
    n = notes("core")["plug_volume"]
    litres = (n["n_horizontal"] * math.pi * (inch / 2) ** 2 * inch + n["n_vertical"] * math.pi * (1.5 * inch / 2) ** 2 * 1.5 * inch) * 1000
    assert close(value(ledger, "plug_litres"), litres)


def test_wells_and_scale(ledger):
    w = pd.read_csv(DATA / "wells.csv")
    g = pd.read_csv(DATA / "geometry.csv").set_index("key").value
    assert value(ledger, "n_wellbores") == len(w) == g["n_wellbores"]
    hole = g["reservoir_hole_mm"] / 1000
    assert close(value(ledger, "one_in"), g["hull_area_km2"] * 1e6 / (len(w) * math.pi * (hole / 2) ** 2))
    assert close(value(ledger, "coin_m"), g["nn_median_km"] * 1000 / hole * 0.01)
    r35 = notes("core")["plugs"]["r35_p50"] * 1e-6
    assert close(value(ledger, "orders"), math.log10(math.sqrt(g["hull_area_km2"]) * 1000 / r35))


def test_echo_and_field(ledger):
    s = notes("seismic")
    assert close(value(ledger, "fan_range"), s["fan"]["depth_max"] - s["fan"]["depth_min"])
    assert close(value(ledger, "tuning_m"), s["wedge"]["tuning_m"]) and close(value(ledger, "tie_corr"), s["tie"]["corr_best"])
    c = pd.read_csv(DATA / "closure.csv").sort_values("depth_m")
    f = notes("field")["closure"]
    assert close(value(ledger, "area_p90"), np.interp(f["P90"], c.depth_m, c.area_km2))
    assert close(value(ledger, "area_p50"), np.interp(f["P50"], c.depth_m, c.area_km2))
    t = pd.read_csv(DATA / "transect.csv")
    assert close(value(ledger, "gap_max_ms"), (t.twt_reprocessed_ms - t.twt_base_ms).abs().max())


def test_cascade_widens_and_links_widen_further(ledger):
    c = pd.read_csv(DATA / "cascade.csv")
    assert (np.diff(c.sd_log10) > 0).all(), "each step must widen the spread"
    by = c.set_index("key")
    assert close(value(ledger, "cas_rock_x"), by.loc["rock_volume", "p10"] / by.loc["rock_volume", "p90"], 1e-3)
    assert close(value(ledger, "cas_cor_x"), by.loc["correlated", "p10"] / by.loc["correlated", "p90"], 1e-3)
    assert value(ledger, "cas_cor_x") > value(ledger, "cas_ind_x")
    oil = pd.read_csv(DATA / "volve_money.csv").oil_sm3.sum() / 1e6
    assert close(value(ledger, "volve_oil"), oil)


def test_money(ledger):
    m = notes("money")
    v = pd.read_csv(DATA / "volve_money.csv")
    assert close(value(ledger, "volve_capex_usd"), v.investment_usd_mn_real.sum() / 1000)
    assert close(value(ledger, "volve_produced"), v.oe_sm3.sum())
    p = m["prospect"]
    assert close(value(ledger, "npv_x"), p["npv_p10"] / p["npv_p90"])
    # the break-even prices sit where the price lines cross zero
    grid = pd.read_csv(DATA / "prospect_price.csv")
    for case in ("P90", "P10"):
        g = grid[grid.volume_case == case].sort_values("price")
        assert close(np.interp(0, g.npv, g.price), p["break_even_price"][case.lower()], 1e-2)
    b = m["base_rate"]
    assert close(value(ledger, "dry_cost"), b["drilling_days_median"] * 1.0)
    pg = b["pg_commercial"]
    assert close(value(ledger, "emv"), (pg * p["npv_mean"] - (1 - pg) * b["dry_hole_usd_mn"]) / 1000)
    assert close(value(ledger, "be_pg"), b["dry_hole_usd_mn"] / (p["npv_mean"] + b["dry_hole_usd_mn"]))
    assert value(ledger, "price_min") >= value(ledger, "be_p90"), "the prose says the low case broke even at every annual price"


def test_test_section(ledger):
    vr = pd.read_csv(DATA / "volve_reserves.csv").sort_values("snapshot_year")
    assert close(value(ledger, "volve_first"), vr.recoverable_oe_sm3.iloc[0] / 1e6)
    assert close(value(ledger, "volve_peak"), vr.recoverable_oe_sm3.max() / 1e6)
    assert close(value(ledger, "volve_low"), vr.recoverable_oe_sm3.min() / 1e6)
    assert close(value(ledger, "volve_latest"), vr.recoverable_oe_sm3.iloc[-1] / 1e6)
    rv = pd.read_csv(DATA / "revisions.csv")
    assert value(ledger, "rev_n") == len(rv)
    assert close(value(ledger, "rev_up"), (rv.ratio > 1.05).mean(), 1e-3)
    assert close(value(ledger, "rev_halved"), (rv.ratio < 0.5).mean(), 1e-3)
