"""Shared paths and helpers for the extract scripts.

Every script reads the ep_geoscience_analytics mid-layer (Parquet) or the local Volve archive and writes small files to
story/data/. Run them with the ep interpreter in isolated mode, for example:

    ..\\ep_geoscience_analytics\\.venv\\Scripts\\python.exe -I scripts\\make_core.py --ep ..\\ep_geoscience_analytics
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "story" / "data"


def args(*extra: tuple[str, dict]) -> argparse.Namespace:
    """--ep (the engine checkout) and --out, plus any extra options as (flag, kwargs) pairs."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--ep", required=True, type=Path)
    ap.add_argument("--out", type=Path, default=OUT)
    for flag, kw in extra:
        ap.add_argument(flag, **kw)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    return a


def marts(ep: Path) -> Path:
    return ep / "data" / "midlayer" / "marts"


def canonical(ep: Path) -> Path:
    return ep / "data" / "midlayer" / "canonical"


WELL = "15/9-F-11 T2"
LAS_MEMBER = "Well_logs_pr_WELL/15_9-F-11 T2/05.PETROPHYSICAL INTERPRETATION/WLC_PETRO_COMPUTED_INPUT_1.LAS"
CHECKSHOT = "TZV_TIME_CHECKSHOT_1"  # the near-offset check shot of the well
HUGIN_TVDSS = (3181.5, 3282.84)  # the interpreters' Hugin top and base picks in this well, m below MSL
LOG_TVDSS = (2300.0, 3320.0)  # window kept for the composite log


def read_las(text: str):
    """The ~A block of a LAS 2 file as a DataFrame named by the ~C mnemonics; -999.25 is null."""
    import io
    import re

    import pandas as pd

    head, _, body = text.partition("~A")
    cur = head.split("~C")[1].split("~")[0]
    pat = r"\s*([A-Za-z0-9_\-]+)\s*\."
    names = [re.match(pat, line).group(1) for line in cur.splitlines() if re.match(pat, line)]
    body = body.split("\n", 1)[1]
    return pd.read_csv(io.StringIO(body), sep=r"\s+", header=None, names=names, na_values=[-999.25, "-999.25"], engine="c")


def well_log(ep: Path, volve: Path):
    """The composite log of the story's well inside LOG_TVDSS, with TVDSS and two-way time from its check shot.
    Returns (log at full sample rate, time-depth table of the well, all time-depth tables)."""
    import zipfile

    import numpy as np
    import pandas as pd

    td_all = pd.read_parquet(marts(ep) / "well_timedepth.parquet")
    td = td_all[td_all.member.str.contains(WELL.replace("/", "_")) & td_all.member.str.contains(CHECKSHOT)].sort_values("md_m")
    las = read_las(zipfile.ZipFile(volve / "Volve_Well_logs_pr_WELL.zip").read(LAS_MEMBER).decode("latin-1"))
    las["tvdss_m"] = np.interp(las.DEPTH, td.md_m, td.tvdss_m)
    las["twt_ms"] = np.interp(las.DEPTH, td.md_m, td.twt_ms)
    keep = (las.tvdss_m >= LOG_TVDSS[0]) & (las.tvdss_m <= LOG_TVDSS[1]) & las.DEPTH.between(td.md_m.min(), td.md_m.max())
    return las[keep].copy(), td, td_all


def write_notes(out: Path, name: str, notes: dict) -> None:
    """One JSON of summary numbers per script (`<name>_notes.json`), read by story/story.py."""
    (out / f"{name}_notes.json").write_text(json.dumps(notes, indent=1, default=float))
    print(json.dumps(notes, indent=1, default=float))
