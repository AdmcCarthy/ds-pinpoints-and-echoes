# Data

Raw downloads go in `data/raw/` (git-ignored). Story-sized extracts are committed in `story/data/`, written by the scripts in
`scripts/` (one per section, run in order by `scripts/make_all.ps1`). Heavy ingestion stays in `ep-geoscience-analytics`.
Stated assumptions for the compounding and money sections are in [`assumptions.yaml`](assumptions.yaml).

## In use

| File | From | Section |
|---|---|---|
| `micp.csv`, `micp_samples.csv` | Eleven mercury-injection curves of 15/9-19 A (report pages 213 to 224), with R35 and the fitted throat relation | the pore |
| `plugs.csv` | 860 routine plugs of 15/9-19 A and BT2: Klinkenberg permeability, helium porosity, fitted R35 | the plug |
| `core_notes.json` | Plug counts and ranges, the fit, the plug volume, Sodir's North Sea core lengths | pore, plug, decision |
| `log.csv`, `core_log_pairs.csv`, `log_notes.json` | 15/9-F-11 T2 composite log; core against interpreted log permeability | the log |
| `wells.csv`, `geometry.csv`, `chain.csv` | Sodir North Sea wellheads, spacing, hole diameter; Volve error links | pinpoint, basin |
| `section.json`, `trace.csv`, `horizons.csv`, `tie.csv`, `wedge.json`, `timedepth.csv` | ST10010 inline 10215, the trace at the well, published horizons, the tie, a synthetic wedge, every check-shot table | the echo |
| `spread.csv`, `transect.csv`, `picks.csv`, `closure.csv`, `contact.csv` | Two published versions of four horizons; area against depth on the Hugin top; the 2005 plan's contacts | the field |
| `cascade.csv`, `cascade_hist.csv` | The volumetric Monte Carlo, one factor added per step, then the linked case | compounding |
| `volve_money.csv`, `prospect_*.csv`, `money_notes.json` | Volve's investment and production; the prospect's value against price, its spread and the value of drilling | the money |
| `volve_reserves.csv`, `revisions.csv` | Sodir's estimates of Volve by year; first-to-latest ratios of 59 fields | the test |

Licences and attribution lines: [`../DATA-LICENCE.md`](../DATA-LICENCE.md).

## Assumptions worth knowing

- Positions are wellhead positions; the study area is the convex hull of them, not the sea.
- R35 is read from each mercury curve; the throat relation is fitted on the eight samples with a porosity (Winland's form,
  this field's coefficients).
- Plug volume takes each plug as long as it is wide; the report gives the diameters only.
- The cascade's ranges are the story's stated assumptions, not Volve's estimates; the contact distribution and the area curve
  are Volve's.
- Money is pre-tax, real 2025 USD at 8 %; opex, tariffs, abandonment and tax are the data engine's screening assumptions.
- The dry-hole cost is median drilling days times an assumed 1 million USD a day.
- The seismic polarity is not stated by the data; the synthetic is drawn with the better-matching sign.
