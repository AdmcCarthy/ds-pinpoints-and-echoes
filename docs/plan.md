# Plan: the remake

*Approved 2026-11-18. The first story (31 steps, built 2026-11-09) is tagged `v1-final` and stays live until this remake is
merged. Work happens on the branch `remake`. The step-by-step outline and its number ledger are in
[`outline.md`](outline.md).*

## Thesis

A decision worth more than a billion dollars rests on a few cubic metres of measured rock. The measurements start at the pore
throat, a few micrometres across. They are carried up through the plug, the log, the well, the echo and the field to claims
about a sea, about eleven orders of magnitude. Each rung adds its own uncertainty, the uncertainties widen together, and the
decision is still reached, owned and tested against what the field later gave.

## Decisions (2026-11-18)

- **Rebuild everything in place:** same repo and URL; every script, figure and step is new.
- **Money from both** Volve's real record (Sodir investment and production, Observed and Derived) and a synthetic prospect for
  the drill-or-drop decision (Interpreted, with stated assumptions).
- **Plain text, deep appendix:** each step is written for a reader new to the subject. The specialist detail goes in Basis of
  analysis (`::: appendix`).
- **Pore throat from both** the mercury-injection curves of 15/9-19 A and a relation fitted on them and applied to all 860 plugs.

## Phases and gates

| Phase | Work | Gate |
|---|---|---|
| 0 | Branch `remake`, local tag `v1-final` | done 2026-11-18 |
| 1 | `outline.md` with every number and its source; open items | done 2026-11-18 (Adam's rulings in `outline.md`) |
| 2 | Scripts, one per section (`make_core`, `make_log`, `make_wells`, `make_seismic`, `make_field`, `make_cascade`, `make_money`, `make_test`); `story.py`; `tests/test_numbers.py` | done: 9 tests pass |
| 3 | Figures: `ladder` (and the ladder strip in every figure), `ledger`, `pore`, `plugs`, `corelog`, `cascade`, `money`, `volve`, and rewritten wells, log, section, wedge, tie, fan, transect, closure | done: looked at on 360 px and 1440 px |
| 4 | `story.md` and the appendix; Idiom checkers | done: checkers clean, build 0 warnings |
| 5 | Readability gate, snapshots, README | done: gate passes on five viewports; merged to main and pushed 2026-11-18 |

The story is one arc (`arc: zoom`). That needed a SubScout change (2026-11-18, Adam's choice), released as SubScout v0.16.0:
present mode runs every sequence as one deck, and the arc check accepts zoom's returning moment.

## Data in use

| Source | Tables or files | Terms |
|---|---|---|
| ep mid-layer (Volve) | `well_core_plug`, `well_core_mercury_injection`, `well_core_vs_log_summary`, logs, check shots, horizons | Volve Terms and Conditions |
| ep mid-layer (Sodir) | `well_header`, `reserves_snapshot`, `field_investment_real`, `field_economics` | NLOD 2.0, "Source: Sodir" |
| ep economics inputs | IMF prices, Norges Bank USDNOK, BLS CPI-U | IMF terms unverified: derived values only |
| kit-surfaces | `data/out/closures.json`, `contacts.json` | Volve Terms and Conditions |
| SEG-Y | ST10010ZC11 full stack, one inline | Volve Terms and Conditions |

Raw data never enters the repo; `story/data/` holds small derived extracts only.
