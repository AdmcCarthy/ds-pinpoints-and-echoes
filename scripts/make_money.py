"""The money: what Volve cost and returned, and a drill-or-drop decision on a Volve-sized prospect.

Volve (Observed and Derived, from the ep mid-layer):
- marts/field_investment_real: Sodir investment by year in nominal NOK, and in real 2025 USD by ep's conventions (USD/NOK
  of the year from Norges Bank, US CPI-U from BLS).
- canonical/production_monthly: Volve's net sold production by year.
- marts/field_economics: ep's screening economics (pre-tax NPV at flat prices and at the historical price deck, break-even
  price). Opex, tariffs, abandonment and tax are ep's configured screening assumptions (economics.yaml), not Volve's books.
Only these derived values leave the machine; the price series themselves are not shipped.

The prospect (Interpreted, from data/assumptions.yaml and story/data/cascade.csv):
- Volume: a lognormal fitted to the P90, P50 and P10 of the last (correlated) cascade step, in Mn Sm3 of oil.
- Value if found: pre-tax NPV at 8 % real, from a straight line in volume fitted at each flat price to the subsea
  tie-back fields of field_economics (NPV is affine in volume, ep economics.md), interpolated in price.
- Price: the 10th, 50th and 90th percentile of the annual Brent average, real 2025 USD, over the stated years (ep macro,
  IMF); only the three numbers are kept.
- Chance of success, two ways (Sodir): technical, the share of North Sea wildcats since 2000 that made a registered
  discovery; commercial, the share of wildcats in an older window whose discovery is producing, shut down, approved for
  production or included in a field.
- Dry-hole cost: the median drilling days of North Sea wildcats since 2015 (Sodir) times an assumed daily spread cost.
- The drill decision: EMV and the break-even chance, from ep-prospect's decision module.
- The sanction decision: NPV against price for the P90, P50 and P10 volumes, and the break-even price of each.
Writes volve_money.csv, prospect_npv.csv, prospect_price.csv, prospect_curve.csv and money_notes.json.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from ep_prospect import decision
from ep_prospect import distributions as dist

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I drops the script folder from sys.path
from common import ROOT, args, canonical, marts, write_notes  # noqa: E402

PRICES = [40, 50, 60, 70, 80]
BBL_PER_SM3 = 6.29


def volve(ep: Path, out: Path) -> dict:
    inv = pd.read_parquet(marts(ep) / "field_investment_real.parquet")
    inv = inv[inv.field_name.str.upper() == "VOLVE"][["year", "investment_mnok", "investment_usd_mn_real"]]
    prod = pd.read_parquet(canonical(ep) / "production_monthly.parquet")
    prod = prod[prod.entity_name.astype(str).str.upper() == "VOLVE"].groupby("year")[["oil_sm3", "oe_sm3"]].sum().reset_index()
    t = inv.merge(prod, on="year", how="outer").sort_values("year").fillna(0.0)
    t = t[(t.investment_mnok != 0) | (t.oe_sm3 != 0)]
    t.round(2).to_csv(out / "volve_money.csv", index=False)
    fe = pd.read_parquet(marts(ep) / "field_economics.parquet")
    v = fe[fe.field_name.str.upper() == "VOLVE"].iloc[0]
    return {"capex_mnok_nominal": float(inv.investment_mnok.sum()), "capex_usd_mn_real": float(inv.investment_usd_mn_real.sum()),
            "first_capex_year": int(v.first_capex_year), "first_production_year": int(v.first_production_year), "last_production_year": int(v.last_production_year),
            "oil_sm3": float(prod.oil_sm3.sum()), "oe_sm3": float(prod.oe_sm3.sum()), "ultimate_mmboe": float(v.ultimate_mmboe),
            "npv_pre": {p: float(v[f"npv_pre_{p}"]) for p in PRICES}, "npv_pre_historical": float(v.npv_pre_historical),
            "be_pre_usd_bbl": float(v.be_pre_usd_bbl), "development_well_slots": int(v.development_well_slots), "concept": v.concept}


def npv_lines(ep: Path) -> pd.DataFrame:
    """NPV = a + b x volume at each flat price, over the subsea tie-back fields; volume in Mn Sm3 o.e."""
    fe = pd.read_parquet(marts(ep) / "field_economics.parquet")
    fe = fe[(fe.concept_group == "Subsea tie-back") & fe.excluded_reason.isna()].dropna(subset=["ultimate_mmboe"])
    vol = fe.ultimate_mmboe / BBL_PER_SM3
    rows = []
    for p in PRICES:
        y = fe[f"npv_pre_{p}"]
        b, a = np.polyfit(vol, y, 1)
        rows.append({"price": p, "a": a, "b": b, "r2": float(np.corrcoef(vol, y)[0, 1] ** 2), "n": int(len(fe))})
    return pd.DataFrame(rows)


def main() -> None:
    a = args()
    cfg = yaml.safe_load((ROOT / "data" / "assumptions.yaml").read_text())
    P = cfg["prospect"]
    notes = {"volve": volve(a.ep, a.out)}

    lines = npv_lines(a.ep)
    notes["npv_lines"] = lines.round(4).to_dict("records")
    wh = pd.read_parquet(canonical(a.ep) / "well_header.parquet")
    wc = wh[(wh.main_area == "NORTH SEA") & (wh.purpose == "WILDCAT") & (wh.wellbore_kind == "initial")].assign(yr=lambda d: pd.to_datetime(d.entry_date).dt.year)
    since = wc[wc.yr >= 2000]
    pg_tech = float(since.is_discovery_wellbore.astype(float).mean())
    disc = pd.read_parquet(canonical(a.ep) / "discovery.parquet")
    developed = disc[disc.field_id.notna() | disc.activity_status.isin(["Producing", "Shut down", "Approved for production"])].discovery_id
    w0, w1 = P["commercial_window"]
    old = wc[wc.yr.between(w0, w1)]
    commercial = old.is_discovery_wellbore.astype(bool) & old.discovery_id.isin(developed)
    pg = float(commercial.mean())
    days = float(wc[wc.yr >= 2015].drilling_days.astype(float).median())
    dry = days * float(P["spread_cost_usd_mn_per_day"])
    notes["base_rate"] = {"n_wildcats": int(len(since)), "n_discoveries": int(since.is_discovery_wellbore.sum()), "pg_technical": pg_tech, "from_year": 2000,
                          "commercial_window": [w0, w1], "n_wildcats_window": int(len(old)), "n_commercial": int(commercial.sum()), "pg_commercial": pg,
                          "drilling_days_median": days, "drilling_days_n": int(wc[wc.yr >= 2015].drilling_days.notna().sum()), "dry_hole_usd_mn": dry}

    # price spread from the record, volume from the cascade
    macro = pd.read_parquet(canonical(a.ep) / "econ_macro_annual.parquet")
    y0, y1 = P["price_years"]
    brent = macro[macro.year.between(y0, y1)].brent_usd_bbl_real.dropna()
    pr = {"kind": "lognormal", "p90": float(brent.quantile(0.1)), "p50": float(brent.quantile(0.5)), "p10": float(brent.quantile(0.9)),
          "years": [y0, y1], "n_years": int(len(brent)), "min": float(brent.min()), "max": float(brent.max())}
    pdist, _ = dist.fit("lognormal", pr["p90"], pr["p50"], pr["p10"])
    cas = pd.read_csv(a.out / "cascade.csv").set_index("key").loc["correlated"]
    vdist, _ = dist.fit("lognormal", cas.p90, cas.p50, cas.p10)
    rng = np.random.default_rng(cfg["seed"] + 1)
    n = int(cfg["draws"])
    vol = dist.sample(vdist, rng.standard_normal(n))
    price = dist.sample(pdist, rng.standard_normal(n))
    # NPV is affine in price as well as volume (ep economics.md), so the intercept and slope are straight lines in price
    a1, a0 = np.polyfit(lines.price, lines.a, 1)
    b1, b0 = np.polyfit(lines.price, lines.b, 1)
    npv_at = lambda p, v: (a0 + a1 * p) + (b0 + b1 * p) * v  # noqa: E731
    npv = npv_at(price, vol)
    be_price = {k: float(-(a0 + b0 * v) / (a1 + b1 * v)) for k, v in (("p90", cas.p90), ("p50", cas.p50), ("p10", cas.p10))}
    notes["npv_model"] = {"a0": a0, "a1": a1, "b0": b0, "b1": b1, "max_abs_residual": float(max(np.abs(lines.a - (a0 + a1 * lines.price)).max(),
                                                                                                    np.abs(lines.b - (b0 + b1 * lines.price)).max()))}
    grid = pd.DataFrame([(p, k, npv_at(p, v)) for p in range(20, 161, 5) for k, v in (("P90", cas.p90), ("P50", cas.p50), ("P10", cas.p10))],
                        columns=["price", "volume_case", "npv"])
    grid.round(1).to_csv(a.out / "prospect_price.csv", index=False)
    q = np.percentile(npv, [10, 50, 90])
    hist, edges = np.histogram(npv, bins=60)
    pd.DataFrame({"npv_lo": edges[:-1], "npv_hi": edges[1:], "share": hist / n}).round(4).to_csv(a.out / "prospect_npv.csv", index=False)
    e_npv = float(npv.mean())
    emv, _ = decision.emv_row(pg, e_npv, dry)
    # EMV against the chance of success, for the figure
    curve = pd.DataFrame({"pg": np.round(np.linspace(0, 1, 101), 2)})
    curve["emv"] = curve.pg * e_npv - (1 - curve.pg) * dry
    curve.round(3).to_csv(a.out / "prospect_curve.csv", index=False)
    notes["prospect"] = {"volume": {"p90": float(cas.p90), "p50": float(cas.p50), "p10": float(cas.p10)}, "price": pr,
                         "price_outside_fit_share": float(np.mean((price < PRICES[0]) | (price > PRICES[-1]))), "break_even_price": be_price,
                         "npv_p90": float(q[0]), "npv_p50": float(q[1]), "npv_p10": float(q[2]), "npv_mean": e_npv,
                         "share_npv_negative": float(np.mean(npv < 0)), "loss_p": float(np.percentile(npv, 2)), "emv": emv["emv"],
                         "break_even_pg": emv["break_even_pg"], "npv_p10_over_p90": float(q[2] / q[0]) if q[0] > 0 else None,
                         "discount_rate": 0.08, "basis": "pre-tax, real 2025 USD"}
    write_notes(a.out, "money", notes)


if __name__ == "__main__":
    main()
