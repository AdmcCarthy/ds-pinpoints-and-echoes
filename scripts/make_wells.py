"""The pinpoint and the basin: every North Sea petroleum wellbore, the spacing between exploration sites, the hole size and the
chain of vertical errors at one well.

Inputs (ep mid-layer): canonical/well_header, marts/bit_size_interval, well_survey_check, seis_horizon_well_summary and
well_timedepth_pick_summary. Writes wells.csv, geometry.csv, chain.csv and wells_notes.json.

Choices (also in data/README.md):
- Positions are wellhead (surface) positions; deviated wells reach other places.
- "Petroleum wellbores" are Sodir well types DEVELOPMENT and EXPLORATION less soil drilling, shallow gas and scientific
  purposes; sidetracks count.
- The area is the convex hull of those wellheads, not the sea.
- One millisecond of two-way time is converted to depth with the Volve average velocity, a stated parameter.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull, cKDTree

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I drops the script folder from sys.path
from common import args, canonical, marts, write_notes  # noqa: E402

R_EARTH_KM = 6371.0088
EXCLUDE_PURPOSE = {"SOIL DRILLING", "SHALLOW GAS", "SCIENTIFIC"}
V_AVG_M_S = 2345.0  # Volve upper average velocity in the check-shot summary (rounded)


def xy_km(lat, lon, lat0):
    """Equirectangular kilometres about lat0; fine at this extent for an area to about 1 %."""
    y = np.radians(lat) * R_EARTH_KM
    x = np.radians(lon) * R_EARTH_KM * np.cos(np.radians(lat0))
    return np.column_stack([x, y])


def wells(ep: Path) -> pd.DataFrame:
    w = pd.read_parquet(canonical(ep) / "well_header.parquet")
    w = w[(w.main_area == "NORTH SEA") & w.lat_etrs89.notna()]
    w = w[w.well_type.isin(["DEVELOPMENT", "EXPLORATION"]) & ~w.purpose.isin(EXCLUDE_PURPOSE)]
    return pd.DataFrame({
        "wellbore": w.well_name.astype(str),
        "lat": w.lat_etrs89.astype(float).round(5),
        "lon": w.lon_etrs89.astype(float).round(5),
        "year": pd.to_datetime(w.entry_date).dt.year.astype("Int64"),
        "type": w.well_type.astype(str).str.lower(),
        "kind": w.wellbore_kind.astype(str),
    }).reset_index(drop=True)


def geometry(w: pd.DataFrame, ep: Path) -> pd.DataFrame:
    p = xy_km(w.lat.to_numpy(), w.lon.to_numpy(), w.lat.mean())
    hull = ConvexHull(p)
    first = w[(w.type == "exploration") & (w.kind == "initial")]
    pe = np.unique(np.round(xy_km(first.lat.to_numpy(), first.lon.to_numpy(), w.lat.mean()), 1), axis=0)  # one point per 100 m site
    nn = cKDTree(pe).query(pe, k=2)[0][:, 1]
    bits = pd.read_parquet(marts(ep) / "bit_size_interval.parquet")
    hole = bits[(bits.hole_state == "open_hole") & (bits.bottom_md_m >= 3000)].bit_size_mm  # Volve runs at reservoir depth
    rows = [
        ("reservoir_hole_mm", float(hole.median()), "mm", f"Volve open-hole runs reaching 3,000 m MD or deeper, {len(hole)} runs"),
        ("n_wellbores", len(w), "count", "wells.csv"),
        ("n_exploration_sites", len(pe), "count", "exploration wellbores (initial), 100 m cells"),
        ("hull_area_km2", hull.volume, "km2", "convex hull of wellhead positions"),
        ("nn_median_km", float(np.median(nn)), "km", "exploration sites, nearest neighbour"),
        ("nn_p10_km", float(np.percentile(nn, 10)), "km", "exploration sites, nearest neighbour"),
        ("nn_p90_km", float(np.percentile(nn, 90)), "km", "exploration sites, nearest neighbour"),
    ]
    return pd.DataFrame(rows, columns=["key", "value", "unit", "basis"])


def chain(ep: Path) -> pd.DataFrame:
    """The Volve error links, each in metres at the target, plus the horizontal one."""
    m = marts(ep)
    s = pd.read_parquet(m / "well_survey_check.parquet")
    h = pd.read_parquet(m / "seis_horizon_well_summary.parquet")
    k = pd.read_parquet(m / "well_timedepth_pick_summary.parquet").dropna(subset=["residual_abs_max_ms"])
    ms_to_m = V_AVG_M_S / 2 / 1000
    d = h[(h.domain == "DEPTH") & h.surface_name.str.contains("Hugin")]
    rows = [
        ("Well position (horizontal)", "horizontal", s.sigma_lateral_end_m.median(), s.sigma_lateral_end_m.max(),
         "Volve survey covariance at the end of 26 surveys; unit and confidence level not stated in the export", "Observed"),
        ("Well depth (vertical position)", "vertical", s.sigma_vertical_end_m.median(), s.sigma_vertical_end_m.max(), "the same surveys, vertical", "Observed"),
        ("Depth reference (rotary table to sea level)", "vertical", 0.0, s.rt_used_m.dropna().median(),
         "a mixed-up reference shifts every depth by the rotary-table elevation", "Observed"),
        ("Time to depth (check-shot residual)", "vertical", (k.residual_median_ms.abs() * ms_to_m).median(), k.residual_abs_max_ms.max() * ms_to_m,
         f"pick residuals against check shots, ms converted at {V_AVG_M_S:.0f} m/s", "Derived"),
        ("Horizon against well picks (reservoir)", "vertical", d.mistie_median.abs().median(), d.mistie_abs_max.max(),
         "Volve Hugin top and base, depth horizons already adjusted to wells", "Derived"),
    ]
    out = pd.DataFrame(rows, columns=["link", "axis", "typical", "worst", "basis", "confidence"])
    out[["typical", "worst"]] = out[["typical", "worst"]].astype(float).round(2)
    out.insert(4, "unit", "m")
    return out


def main() -> None:
    a = args()
    w = wells(a.ep)
    w.to_csv(a.out / "wells.csv", index=False)
    g = geometry(w, a.ep)
    g.to_csv(a.out / "geometry.csv", index=False)
    c = chain(a.ep)
    c.to_csv(a.out / "chain.csv", index=False)
    write_notes(a.out, "wells", {"geometry": dict(zip(g.key, g.value)), "chain": c.drop(columns="basis").to_dict("records")})


if __name__ == "__main__":
    main()
