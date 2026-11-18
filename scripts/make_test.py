"""The test: Sodir's own estimate of Volve over twenty years, every field's latest estimate against its first, and where
Volve's produced oil falls on the cascade's spread.

Inputs (ep mid-layer): canonical/reserves_snapshot, field_master, production_monthly; story/data/cascade.csv.
Writes volve_reserves.csv, revisions.csv and test_notes.json.

Choices: a field enters the revision set when its plan for development was approved, its first snapshot is within a year
of the approval and it has at least five snapshots. Snapshots are never summed. Volve's place on the cascade uses a
lognormal fitted to the last (correlated) step's P90, P50 and P10; the cascade is an illustration with stated ranges, not
Volve's own estimate, so the comparison is a check on the illustration, not on the field's planners.
"""

from __future__ import annotations

import sys
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pandas as pd
from ep_prospect import distributions as dist

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I drops the script folder from sys.path
from common import args, canonical, write_notes  # noqa: E402


def main() -> None:
    a = args()
    c = canonical(a.ep)
    rs = pd.read_parquet(c / "reserves_snapshot.parquet")
    rs = rs[(rs.entity_type == "field") & (rs.rc_group == "RC_ALL")]
    volve = rs[rs.entity_name.str.upper() == "VOLVE"].sort_values("snapshot_year")
    volve[["snapshot_year", "recoverable_oe_sm3", "recoverable_oil_sm3", "remaining_oe_sm3"]].to_csv(a.out / "volve_reserves.csv", index=False)

    fm = pd.read_parquet(c / "field_master.parquet")
    pdo = fm.dropna(subset=["pdo_approved_date"]).assign(pdo_year=lambda d: pd.to_datetime(d.pdo_approved_date).dt.year)
    pdo = pdo.assign(key=pdo.field_name.str.upper())[["key", "pdo_year"]].drop_duplicates("key")
    r = rs.assign(key=rs.entity_name.str.upper()).merge(pdo, on="key", how="inner")
    r = r[r.snapshot_year >= r.pdo_year - 1]
    g = r.sort_values("snapshot_year").groupby("key")
    rev = pd.DataFrame({"first_year": g.snapshot_year.first(), "first_oe": g.recoverable_oe_sm3.first(), "latest_year": g.snapshot_year.last(),
                        "latest_oe": g.recoverable_oe_sm3.last(), "n_years": g.size(), "pdo_year": g.pdo_year.first()})
    rev = rev[(rev.first_year <= rev.pdo_year + 1) & (rev.n_years >= 5) & (rev.first_oe > 0)]
    rev["ratio"] = rev.latest_oe / rev.first_oe
    rev = rev.reset_index().rename(columns={"key": "field"}).sort_values("ratio")
    rev.round({"ratio": 3}).to_csv(a.out / "revisions.csv", index=False)

    prod = pd.read_parquet(c / "production_monthly.parquet")
    oil = float(prod[prod.entity_name.astype(str).str.upper() == "VOLVE"].oil_sm3.sum()) / 1e6
    cas = pd.read_csv(a.out / "cascade.csv").set_index("key").loc["correlated"]
    d, _ = dist.fit("lognormal", cas.p90, cas.p50, cas.p10)
    exceed = 1 - NormalDist().cdf((np.log(oil) - d.mu) / d.sigma)
    peak = volve.loc[volve.recoverable_oe_sm3.idxmax()]
    low = volve.loc[volve.recoverable_oe_sm3.idxmin()]
    notes = {"volve": {"first_year": int(volve.snapshot_year.iloc[0]), "first": float(volve.recoverable_oe_sm3.iloc[0]), "peak_year": int(peak.snapshot_year),
                       "peak": float(peak.recoverable_oe_sm3), "low_year": int(low.snapshot_year), "low": float(low.recoverable_oe_sm3),
                       "latest_year": int(volve.snapshot_year.iloc[-1]), "latest": float(volve.recoverable_oe_sm3.iloc[-1]), "produced_oil_mn_sm3": oil,
                       "oil_exceedance_on_cascade": float(exceed)},
             "revisions": {"n_fields": int(len(rev)), "median_ratio": float(rev.ratio.median()), "p10": float(rev.ratio.quantile(0.1)), "p90": float(rev.ratio.quantile(0.9)),
                           "share_up": float((rev.ratio > 1.05).mean()), "share_down": float((rev.ratio < 0.95).mean()),
                           "share_halved": float((rev.ratio < 0.5).mean()), "share_doubled": float((rev.ratio > 2).mean())}}
    write_notes(a.out, "test", notes)


if __name__ == "__main__":
    main()
