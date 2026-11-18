"""Metrics and derived datasets for Pinpoints and Echoes.

Inputs are the small extracts in story/data/, written by scripts/make_*.py (scripts/make_all.ps1 runs them in order). Every
number in the prose comes from here, with its method, source and confidence.
"""

import math

import numpy as np
import pandas as pd
from subscout import metric

SODIR = "sodir"
VOLVE = "volve"
MACRO = "macro"
STORY = "story"
V_AVG = 2345.0  # m/s, Volve upper average velocity in the check-shot summary (rounded); stated on the page
MS_TO_M = V_AVG / 2 / 1000  # metres of depth per ms of two-way time

# The rungs of the scale ladder, smallest first: (key, label, length in m, where it comes from). Lengths that are not a
# metric below are labelled as parameters on the page.
RUNGS = [
    ("throat", "pore throat", None, "R35 median of the plugs"),
    ("grain", "sand grain", 0.00035, "medium sand, the plugs' own description (M-gr)"),
    ("plug", "core plug", 0.0254, "1 inch plug"),
    ("log", "log sample", None, "composite log sampling"),
    ("hole", "wellbore", None, "hole at reservoir depth"),
    ("bed", "thinnest bed the echo resolves", None, "tuning thickness"),
    ("spacing", "next exploration well", None, "median distance"),
    ("field", "Volve high", None, "width of a square of the P50 closure area"),
    ("sea", "Norwegian North Sea", None, "width of a square of the area the wells span"),
]


def _g(d, key):
    return float(d["geometry"].set_index("key").value[key])


def _ladder(d):
    n = d["core_notes"]
    lengths = {
        "throat": n["plugs"]["r35_p50"] * 1e-6,
        "log": d["log_notes"]["log"]["sample_m"],
        "hole": _g(d, "reservoir_hole_mm") / 1000,
        "bed": d["seismic_notes"]["wedge"]["tuning_m"],
        "spacing": _g(d, "nn_median_km") * 1000,
        "field": math.sqrt(d["field_notes"]["closure"]["area_P50"]) * 1000,
        "sea": math.sqrt(_g(d, "hull_area_km2")) * 1000,
    }
    rows = [{"key": k, "label": lab, "m": lengths.get(k, m), "basis": b, "order": i} for i, (k, lab, m, b) in enumerate(RUNGS)]
    return pd.DataFrame(rows)


def _fan_area(d):
    """Area above the P50 contact over the area left when the reservoir top is moved down by the depth spread of the
    check-shot tables at one time (the same as raising the contact by it)."""
    c = d["closure"].sort_values("depth_m")
    fan = d["seismic_notes"]["fan"]
    owc = d["field_notes"]["closure"]["P50"]
    at = lambda z: float(np.interp(z, c.depth_m, c.area_km2))  # noqa: E731
    return at(owc) / at(owc - (fan["depth_max"] - fan["depth_min"]))


def _ledger(d):
    """One bar per rung: the factor between the low and the high value that rung leaves open."""
    cn, ln, sn, fn, cas, mn, tn = (d[k] for k in ("core_notes", "log_notes", "seismic_notes", "field_notes", "cascade", "money_notes", "test_notes"))
    p = cn["plugs"]
    cvl = pd.DataFrame(ln["core_vs_log"])
    fan = sn["fan"]
    cl = fn["closure"]
    c = cas.set_index("key")
    pr = mn["prospect"]
    rv = tn["revisions"]
    rows = [
        ("pore", "Permeability at one porosity", p["band_k_max"] / p["band_k_min"], "plugs at 19 to 21 % porosity, highest over lowest", "observed"),
        ("log", "Log against core permeability", 1 / cvl.k_median_ratio_log_over_core.min(), "core median over interpreted log, the wider of two wells", "derived"),
        ("echo", "Area if the top moves by one fan", _fan_area(d), "closure area at the P50 contact over the area with the top shifted down by the check-shot spread at one time", "derived"),
        ("field", "Area above the contact", cl["area_P50"] / cl["area_P90"], "closure area at the P50 contact over the P90", "interpreted"),
        ("volume", "Recoverable oil", float(c.loc["correlated", "ratio"]), "P10 over P90 of the cascade, rock properties linked", "interpreted"),
        ("money", "Value if found", pr["npv_p10_over_p90"], "P10 over P90 of the prospect's NPV", "interpreted"),
        ("test", "Later estimate over first", rv["p90"] / rv["p10"], "90th over 10th percentile of 59 fields' latest over first estimate", "derived"),
    ]
    return pd.DataFrame(rows, columns=["key", "label", "factor", "basis", "confidence"]).assign(order=lambda x: range(len(x)))


def datasets(d):
    c = d["chain"]
    v = c[c.axis == "vertical"].copy()
    v["cum_typical"] = (v.typical**2).cumsum() ** 0.5  # independent errors add in quadrature
    v["cum_worst"] = (v.worst**2).cumsum() ** 0.5
    vr = d["volve_reserves"].assign(series="Sodir estimate", recoverable_mn_sm3=lambda x: x.recoverable_oe_sm3 / 1e6)
    rev = d["revisions"].assign(
        decade=lambda x: (x.pdo_year // 10 * 10).astype(int).astype(str) + "s", field_label=lambda x: x.field.str.title(), ratio_pct=lambda x: x.ratio * 100
    )
    return {"stack": v.reset_index(drop=True), "volve_hist": vr, "revisions_dec": rev, "ladder": _ladder(d), "ledger": _ledger(d)}


def decision_metrics(d):
    v = d["money_notes"]["volve"]
    pv = d["core_notes"]["plug_volume"]
    sc = d["core_notes"]["sodir_core"]
    return {
        "volve_capex_usd": metric(v["capex_usd_mn_real"] / 1000, "Volve investment 2005 to 2016 (Sodir, nominal NOK) in real 2025 USD by the year's USD/NOK and US CPI-U, billion", SODIR, "derived", "USD bn"),
        "volve_first_capex": metric(str(v["first_capex_year"]), "First year with Volve investment", SODIR, "observed"),
        "volve_first_oil": metric(str(v["first_production_year"]), "First year of Volve production", SODIR, "observed"),
        "volve_last_oil": metric(str(v["last_production_year"]), "Last year of Volve production", SODIR, "observed"),
        "volve_produced": metric(v["oe_sm3"], "Volve net sold production, all years, Sm³ o.e.", SODIR, "observed", "Sm³"),
        "volve_oil": metric(v["oil_sm3"] / 1e6, "Volve net sold oil, all years, million Sm³", SODIR, "observed", "Mn Sm³"),
        "plug_litres": metric(pv["m3_total"] * 1000, "Rock in the routine plugs of 15/9-19 A and BT2: 1 inch horizontal and 1.5 inch vertical plugs (core report pages 12 and 9), each taken as long as it is wide, litres", VOLVE, "interpreted", "L"),
        "n_plug_h": metric(pv["n_horizontal"], "Horizontal plugs with a measurement", VOLVE, "observed"),
        "n_plug_v": metric(pv["n_vertical"], "Vertical plugs with a measurement", VOLVE, "observed"),
        "sodir_core_km": metric(sc["core_km"], "Length of every core Sodir lists for Norwegian North Sea wellbores, km", SODIR, "observed", "km"),
        "sodir_core_wells": metric(sc["n_wellbores"], "Norwegian North Sea wellbores with at least one core", SODIR, "observed"),
    }


def pore_metrics(d):
    m, p = d["core_notes"]["micp"], d["core_notes"]["plugs"]
    lad = _ladder(d).set_index("key").m
    return {
        "micp_n": metric(m["n_samples"], "Mercury-injection curves of 15/9-19 A, report 15-9-19_A_0035.pdf pages 213 to 224", VOLVE, "observed"),
        "micp_r_min": metric(m["radius_min_um"], "Smallest pore-throat radius any curve reaches, µm (the report's conversion of pressure to radius)", VOLVE, "observed", "µm"),
        "micp_r_max": metric(m["radius_max_um"], "Largest radius on any curve, µm", VOLVE, "observed", "µm"),
        "r35_min": metric(m["r35_min_um"], "Smallest R35 of the 11 samples, the radius at 35 % mercury saturation, µm", VOLVE, "derived", "µm"),
        "r35_max": metric(m["r35_max_um"], "Largest R35 of the 11 samples, µm", VOLVE, "derived", "µm"),
        "fit_n": metric(m["n_fit"], "Mercury samples with a porosity, used to fit the throat relation", VOLVE, "derived"),
        "fit_err_pct": metric((10 ** m["rms_log10"] - 1) * 100, "Root-mean-square error of log10 R35 = a + b log10 k + c log10 porosity on those samples, as a percentage", VOLVE, "derived", "%"),
        "fit_b": metric(m["coef"][1], "Exponent of permeability in the fitted throat relation", VOLVE, "derived"),
        "orders": metric(math.log10(lad["sea"] / lad["throat"]), "Orders of magnitude from the median pore throat to the width of the area the North Sea wells span", STORY, "derived"),
        "grain_mm": metric(0.35, "Medium sand, the middle of the Wentworth class 0.25 to 0.5 mm; the plugs are described as medium-grained (M-gr)", STORY, "interpreted", "mm"),
        "poise_half": metric(16, "Flow through a tube scales with the fourth power of its radius (Hagen–Poiseuille), so halving the radius divides the flow by 2⁴", STORY, "derived"),
    }


def name_metrics(d):
    """Well and report names used in the prose, read from the extracts so that none is typed."""
    wells = sorted(d["core_notes"]["plugs"]["by_well"])
    m = d["core_notes"]["micp"]
    return {
        "well_a": metric(wells[0], "First cored wellbore of the routine core analysis", VOLVE, "observed"),
        "well_b": metric(wells[1], "Second cored wellbore of the routine core analysis", VOLVE, "observed"),
        "well_log": metric(d["log_notes"]["log"]["well"], "Wellbore of the composite log, the section and the tie", VOLVE, "observed"),
        "micp_report": metric(m["report"], "Special core analysis report holding the mercury-injection curves", VOLVE, "observed"),
        "micp_page_lo": metric(m["pages"][0], "First report page with a mercury-injection curve", VOLVE, "observed"),
        "micp_page_hi": metric(m["pages"][1], "Last report page with a mercury-injection curve", VOLVE, "observed"),
    }


def plug_metrics(d):
    p = d["core_notes"]["plugs"]
    return {
        "n_plugs": metric(p["n_plugs"], "Routine plugs of 15/9-19 A and 15/9-19 BT2", VOLVE, "observed"),
        "k_min": metric(p["k_min"], "Lowest horizontal Klinkenberg permeability, mD", VOLVE, "observed", "mD"),
        "k_max": metric(p["k_max"], "Highest horizontal Klinkenberg permeability, mD", VOLVE, "observed", "mD"),
        "k_span": metric(math.log10(p["k_max"] / p["k_min"]), "Orders of magnitude between the lowest and highest plug permeability", VOLVE, "derived"),
        "band_n": metric(p["band_n"], "Plugs with porosity from 19 to 21 %", VOLVE, "observed"),
        "band_x": metric(p["band_k_max"] / p["band_k_min"], "Highest over lowest permeability at that porosity", VOLVE, "derived"),
        "r2_phi": metric(p["r2_logk_phi"], "Share of the variance of log permeability that porosity accounts for (r²)", VOLVE, "derived"),
        "plug_bar": metric(20, "Net confining pressure of the permeability measurements, bar (core report)", VOLVE, "observed", "bar"),
    }


def log_metrics(d):
    L = d["log_notes"]["log"]
    cvl = pd.DataFrame(d["log_notes"]["core_vs_log"]).set_index("well_name")
    return {
        "log_sample_cm": metric(round(L["sample_m"] * 100), "Depth sampling of the composite log, cm", VOLVE, "observed", "cm"),
        "log_span_m": metric(L["md_range"][1] - L["md_range"][0], "Measured depth covered by the log window shown, m", VOLVE, "observed", "m"),
        "hugin_m": metric(L["hugin_thickness_m"], "Vertical thickness of the Hugin Fm at 15/9-F-11 T2 from the interpreters' top and base picks, m", VOLVE, "observed", "m"),
        "cl_lo": metric(cvl.k_median_ratio_log_over_core.min(), "Median of interpreted over core permeability, the lower of the two cored wells", VOLVE, "derived"),
        "cl_hi": metric(cvl.k_median_ratio_log_over_core.max(), "The same, the higher of the two wells", VOLVE, "derived"),
    }


def well_metrics(d):
    n = _g(d, "n_wellbores")
    area = _g(d, "hull_area_km2")
    hole_m = _g(d, "reservoir_hole_mm") / 1000
    nn_m = _g(d, "nn_median_km") * 1000
    s = d["stack"]
    ch = d["chain"].set_index("link")
    row = lambda k: ch[ch.index.str.startswith(k)].iloc[0]  # noqa: E731
    return {
        "n_wellbores": metric(int(n), "Petroleum wellbores (development and exploration, sidetracks included) with a wellhead position in the Norwegian North Sea", SODIR, "observed"),
        "area_km2": metric(area, "Area spanned by those wellheads (convex hull), km²", SODIR, "derived", "km²"),
        "hole_cm": metric(hole_m * 100, "Median open-hole diameter of Volve runs reaching 3,000 m MD or deeper, cm", VOLVE, "derived", "cm"),
        "one_in": metric(area / (n * math.pi * (hole_m / 2) ** 2 / 1e6), "Area spanned by the wellheads divided by the summed cross-sections of the wellbores at that diameter", SODIR, "derived"),
        "nn_km": metric(nn_m / 1000, "Median distance from an exploration well to the nearest other exploration site (wellhead positions, 100 m cells), km", SODIR, "derived", "km"),
        "coin_m": metric(nn_m / hole_m * 0.01, "If the wellbore were a 1 cm coin, the median distance to the nearest exploration site, m", SODIR, "derived", "m"),
        "pos_h": metric(float(row("Well position").typical), "Median horizontal position uncertainty at the end of 26 Volve surveys, m (unit and confidence level not stated in the export)", VOLVE, "observed", "m"),
        "stack_typical": metric(float(s.cum_typical.iloc[-1]), "Typical vertical errors combined in quadrature, m (independence assumed)", VOLVE, "interpreted", "m"),
        "stack_worst": metric(float(s.cum_worst.iloc[-1]), "Largest vertical errors on file combined in quadrature, m; the depth reference is a systematic offset, so this is a bound, not a forecast", VOLVE, "interpreted", "m"),
    }


def echo_metrics(d):
    sn = d["seismic_notes"]
    S, T, W, F = sn["section"], sn["tie"], sn["wedge"], sn["fan"]
    return {
        "inline": metric(S["inline"], "ST10010 inline through the well", VOLVE, "observed"),
        "n_traces": metric(S["n_traces"], "Traces on the inline (every second one drawn)", VOLVE, "observed"),
        "bin_m": metric(S["bin_m"], "Distance between traces on the inline, m", VOLVE, "observed", "m"),
        "hugin_twt_s": metric(sn["horizons"]["hugin_twt_ms_at_well"] / 1000, "Two-way time of the published Hugin top horizon at the well, s", VOLVE, "observed", "s"),
        "dom_hz": metric(S["centroid_hz"], "Centroid frequency of the amplitude spectrum, 41 traces about the well, 2,300 to 3,100 ms", VOLVE, "derived", "Hz"),
        "v_res": metric(W["v_m_s"], "Median sonic velocity of the Hugin Fm at the well, m/s", VOLVE, "derived", "m/s"),
        "tuning_m": metric(W["tuning_m"], "Bed thickness at which the synthetic wedge's top and base echoes merge (peak amplitude), m", VOLVE, "derived", "m"),
        "tie_corr": metric(T["corr_best"], "Correlation of the synthetic and the real trace, 2,300 to 3,100 ms, after one bulk shift", VOLVE, "derived"),
        "tie_shift": metric(abs(T["best_shift_ms"]), "Bulk shift applied to the synthetic, ms", VOLVE, "derived", "ms"),
        "fan_twt_s": metric(F["twt_ms"] / 1000, "Two-way time at which every check-shot table is read, s", VOLVE, "derived", "s"),
        "fan_n": metric(F["n_tables"], "Check-shot tables in the Volve release that cover that time", VOLVE, "observed"),
        "fan_range": metric(F["depth_max"] - F["depth_min"], "Spread of depth for that time across the tables, m", VOLVE, "derived", "m"),
    }


def field_metrics(d):
    t, sp, pk = d["transect"], d["spread"], d["picks"]
    gap = (t.twt_reprocessed_ms - t.twt_base_ms).abs()
    C = d["field_notes"]["closure"]
    return {
        "gap_max_ms": metric(float(gap.max()), "Largest difference between the two published versions of the Ty Fm top along the line, ms TWT", VOLVE, "derived", "ms"),
        "gap_max_m": metric(float(gap.max() * MS_TO_M), f"The same in depth at {V_AVG:.0f} m/s, m", VOLVE, "interpreted", "m"),
        "line_km": metric(float(t.dist_m.max() / 1000), "Length of the line between two Ty Fm top picks, km", VOLVE, "derived", "km"),
        "n_picks_line": metric(int(len(pk)), "Well picks within 150 m of the line", VOLVE, "observed"),
        "owc_p90": metric(C["P90"], "Oil-water contact, P90 (low case), 2005 plan for development, m below MSL", VOLVE, "observed", "m"),
        "owc_p50": metric(C["P50"], "Oil-water contact, P50, 2005 plan for development, m below MSL", VOLVE, "observed", "m"),
        "owc_step": metric(C["P50"] - C["P90"], "Depth between the P90 and P50 contacts, m", VOLVE, "derived", "m"),
        "area_p90": metric(C["area_P90"], "Closure area at the P90 contact, km² (smoothed Hugin top surface)", VOLVE, "interpreted", "km²"),
        "area_p50": metric(C["area_P50"], "Closure area at the P50 contact, km²", VOLVE, "interpreted", "km²"),
    }


def cascade_metrics(d):
    c = d["cascade"].set_index("key")
    cn = d["cascade_notes"]
    tn = d["test_notes"]["volve"]
    return {
        "cas_n": metric(cn["n"], "Draws in the volume simulation (fixed seed)", STORY, "derived"),
        "cas_rock_x": metric(float(c.loc["rock_volume", "ratio"]), "P10 over P90 of recoverable oil with only the contact and the thickness uncertain", STORY, "interpreted"),
        "cas_ind_x": metric(float(c.loc["recovery", "ratio"]), "P10 over P90 with all six factors uncertain and independent", STORY, "interpreted"),
        "cas_cor_x": metric(float(c.loc["correlated", "ratio"]), "P10 over P90 with the rock properties linked", STORY, "interpreted"),
        "cas_ind_p90": metric(float(c.loc["recovery", "p90"]), "P90 (low case) recoverable oil, independent factors, million Sm³", STORY, "interpreted", "Mn Sm³"),
        "cas_cor_p90": metric(float(c.loc["correlated", "p90"]), "P90 (low case) recoverable oil, rock properties linked, million Sm³", STORY, "interpreted", "Mn Sm³"),
        "rho": metric(cn["rho"], "Loading of the shared rock-quality factor (an assumption; the plugs' log permeability and porosity have r about 0.83)", STORY, "interpreted"),
        "beyond_map": metric(cn["contact_beyond_map_share"], "Share of draws whose contact lies below the mapped surface and takes its deepest area", STORY, "derived"),
        "volve_exceed": metric(tn["oil_exceedance_on_cascade"], "Share of the linked cascade above Volve's produced oil (a lognormal fitted to its P90, P50 and P10)", STORY, "interpreted"),
    }


def money_metrics(d):
    mn = d["money_notes"]
    v, b, p = mn["volve"], mn["base_rate"], mn["prospect"]
    return {
        "volve_be": metric(v["be_pre_usd_bbl"], "Volve's pre-tax break-even oil price at 8 % real, ep screening economics (opex, tariffs and abandonment assumed), USD/bbl", SODIR, "interpreted", "USD/bbl"),
        "price_lo": metric(p["price"]["p90"], "10th percentile of the annual Brent average 2005 to 2024, real 2025 USD/bbl (IMF via ep)", MACRO, "derived", "USD/bbl"),
        "price_mid": metric(p["price"]["p50"], "Median of the same, USD/bbl", MACRO, "derived", "USD/bbl"),
        "price_hi": metric(p["price"]["p10"], "90th percentile of the same, USD/bbl", MACRO, "derived", "USD/bbl"),
        "price_min": metric(p["price"]["min"], "Lowest annual Brent average 2005 to 2024, real 2025 USD/bbl", MACRO, "derived", "USD/bbl"),
        "be_p90": metric(p["break_even_price"]["p90"], "Break-even oil price of the prospect at its P90 volume, subsea tie-back economics, USD/bbl", STORY, "interpreted", "USD/bbl"),
        "be_p10": metric(p["break_even_price"]["p10"], "The same at the P10 volume", STORY, "interpreted", "USD/bbl"),
        "npv_p90": metric(p["npv_p90"] / 1000, "P90 (low case) pre-tax NPV of the prospect if found, USD billion (2025)", STORY, "interpreted", "USD bn"),
        "npv_p10": metric(p["npv_p10"] / 1000, "P10 (high case) of the same, USD billion", STORY, "interpreted", "USD bn"),
        "npv_x": metric(p["npv_p10_over_p90"], "P10 over P90 of the prospect's NPV", STORY, "interpreted"),
        "npv_lines_n": metric(mn["npv_lines"][0]["n"], "Subsea tie-back fields whose screening NPV against volume sets the prospect's value", SODIR, "derived"),
        "pg_tech": metric(b["pg_technical"], "Share of Norwegian North Sea wildcats since 2000 that made a registered discovery", SODIR, "observed"),
        "pg_comm": metric(b["pg_commercial"], "Share of North Sea wildcats 2000 to 2014 whose discovery is producing, shut down, approved for production or part of a field", SODIR, "observed"),
        "dry_days": metric(b["drilling_days_median"], "Median drilling days of North Sea wildcats since 2015", SODIR, "observed", "days"),
        "spread_day": metric(1.0, "Assumed all-in daily cost of an exploration well, USD million", STORY, "interpreted", "USD mn"),
        "dry_cost": metric(b["dry_hole_usd_mn"], "Cost of a dry hole: median drilling days times the assumed daily cost, USD million", STORY, "interpreted", "USD mn"),
        "emv": metric(p["emv"] / 1000, "Expected value of drilling: commercial chance times mean NPV, less the chance of failure times the dry-hole cost, USD billion", STORY, "interpreted", "USD bn"),
        "be_pg": metric(p["break_even_pg"], "Chance of success at which drilling breaks even", STORY, "interpreted"),
    }


def test_metrics(d):
    tv, rv = d["test_notes"]["volve"], d["test_notes"]["revisions"]
    return {
        "volve_first_yr": metric(str(tv["first_year"]), "First Sodir snapshot year for Volve", SODIR, "observed"),
        "volve_first": metric(tv["first"] / 1e6, "Sodir's recoverable estimate for Volve in that year, million Sm³ o.e.", SODIR, "observed", "Mn Sm³"),
        "volve_peak_yr": metric(str(tv["peak_year"]), "Year of the highest estimate", SODIR, "observed"),
        "volve_peak": metric(tv["peak"] / 1e6, "Highest Sodir estimate for Volve, million Sm³ o.e.", SODIR, "observed", "Mn Sm³"),
        "volve_low_yr": metric(str(tv["low_year"]), "Year of the lowest estimate", SODIR, "observed"),
        "volve_low": metric(tv["low"] / 1e6, "Lowest Sodir estimate for Volve, million Sm³ o.e.", SODIR, "observed", "Mn Sm³"),
        "volve_latest": metric(tv["latest"] / 1e6, "Latest Sodir estimate for Volve, million Sm³ o.e. (the field is produced out)", SODIR, "observed", "Mn Sm³"),
        "rev_n": metric(rv["n_fields"], "Fields with a plan approved, a first snapshot within a year of approval and at least five snapshots", SODIR, "derived"),
        "rev_up": metric(rv["share_up"], "Share of those fields whose estimate grew by more than 5 %", SODIR, "derived"),
        "rev_down": metric(rv["share_down"], "Share whose estimate fell by more than 5 %", SODIR, "derived"),
        "rev_halved": metric(rv["share_halved"], "Share whose estimate at least halved", SODIR, "derived"),
        "rev_doubled": metric(rv["share_doubled"], "Share whose estimate at least doubled", SODIR, "derived"),
        "rev_p10": metric(rv["p10"], "10th percentile of latest over first estimate", SODIR, "derived"),
        "rev_p90": metric(rv["p90"], "90th percentile of latest over first estimate", SODIR, "derived"),
    }


def metrics(d):
    d = {**d, **datasets(d)}
    out = {}
    for f in (name_metrics, decision_metrics, pore_metrics, plug_metrics, log_metrics, well_metrics, echo_metrics, field_metrics, cascade_metrics, money_metrics, test_metrics):
        out.update(f(d))
    return out
