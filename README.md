# Pinpoints and Echoes

[![Pages](https://github.com/AdmcCarthy/ds-pinpoints-and-echoes/actions/workflows/pages.yml/badge.svg)](https://github.com/AdmcCarthy/ds-pinpoints-and-echoes/actions/workflows/pages.yml)
[![Python](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/)
[![Licence](https://img.shields.io/badge/licence-MIT%20with%20acknowledgement-lightgrey)](LICENSE)

A data story about scale and compounding uncertainty: how a measurement made in a pore throat a few micrometres across is
carried up through the plug, the log, the well, the echo and the field to a decision about the North Sea, and how the
uncertainty of each step widens the range the decision rests on. Live page: <https://admccarthy.github.io/ds-pinpoints-and-echoes/>.
Built with [SubScout](https://github.com/AdmcCarthy/core-subscout); Volve is the worked case and Sodir's records cover the
shelf.

The remake (2026-11-18) replaced the first story, which is kept as the local tag `v1-final`. Plan: [`docs/plan.md`](docs/plan.md);
step-by-step outline with every number's source: [`docs/outline.md`](docs/outline.md).

## The story

About eleven orders of magnitude, climbed in order: pore throat, sand grain, plug, log sample, wellbore, the thinnest bed the
echo resolves, the spacing between wells, the field, the North Sea. A scale ladder along the top of every figure marks the rung.
Each rung leaves a range open, and the ranges meet in the volume of oil and its value: the story multiplies them in a Monte Carlo,
links the rock properties that move together, sets the result against price and the chance of success, and tests it against
Sodir's own revisions. The arc is SubScout's `zoom`: the decision, the context from pore to basin, the decision again.

Every claim carries one of three words: **Observed**, **Derived** or **Interpreted**. P90 is the low case.

## Build

Extracts are written from local data that is never committed: the `ep_geoscience_analytics` mid-layer, the Volve archive
(`C:\appl\Volve`) and `kit-surfaces`. One script per section; `scripts/make_all.ps1` runs them in order with the ep interpreter
in isolated mode. Stated assumptions for the compounding and money sections are in [`data/assumptions.yaml`](data/assumptions.yaml).

```powershell
.\scripts\make_all.ps1                     # all extracts into story/data/
# story/data/header.json is the synthetic header band, made once by the author's seismic-art tool and kept as it is
uv run --project ..\core-subscout subscout build story --out _site
uv run --project ..\core-subscout pytest tests                                   # every quoted number against the extracts
uv run --project ..\core-subscout python ..\core-subscout\scripts\readability.py _site   # five viewports
```

| Script | Section | Writes |
|---|---|---|
| `make_core.py` | the pore and the plug | `micp.csv`, `micp_samples.csv`, `plugs.csv`, `core_notes.json` |
| `make_log.py` | the log | `log.csv`, `core_log_pairs.csv`, `log_notes.json` |
| `make_wells.py` | the pinpoint and the basin | `wells.csv`, `geometry.csv`, `chain.csv`, `wells_notes.json` |
| `make_seismic.py` | the echo | `section.json`, `trace.csv`, `horizons.csv`, `tie.csv`, `wedge.json`, `timedepth.csv`, `seismic_notes.json` |
| `make_field.py` | the field | `spread.csv`, `transect.csv`, `picks.csv`, `closure.csv`, `contact.csv`, `field_notes.json` |
| `make_cascade.py` | compounding | `cascade.csv`, `cascade_hist.csv`, `cascade_notes.json` |
| `make_money.py` | the money | `volve_money.csv`, `prospect_*.csv`, `money_notes.json` |
| `make_test.py` | the test | `volve_reserves.csv`, `revisions.csv`, `test_notes.json` |

The page needs SubScout with the whole-story present deck and the returning-beat arc check (core-subscout branch
`whole-story-arc`, to be released as the next tag).

## Licence and acknowledgement

MIT License with Acknowledgement (see [LICENSE](LICENSE)): the MIT licence plus one condition, that anything built with this
work says so visibly and does not imply endorsement. It is custom wording and not OSI-approved. Use the line:
"Built with Pinpoints and Echoes by Adam McCarthy (https://github.com/AdmcCarthy/ds-pinpoints-and-echoes)".

The data extracts keep their own terms: Sodir (NLOD 2.0, "Source: Sodir"), the Volve data village (Volve Terms and
Conditions, CC BY 4.0 based with a no-sale condition) and the price and exchange-rate series used only as derived values.
Details and attribution lines: [DATA-LICENCE.md](DATA-LICENCE.md). Built with SubScout by Adam McCarthy
(https://github.com/AdmcCarthy/core-subscout).
