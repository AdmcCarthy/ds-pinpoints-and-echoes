# Outline: the remake

*Drafted 2026-11-18 for review at the Phase 1 gate (`docs/plan.md`). Each step lists its figure, the one number it carries and
where that number comes from. A value marked *found* was read from the mid-layer or the current extracts on 2026-11-18. A
value marked *to compute* or *to source* does not exist yet. None of these numbers will be typed into the prose: each
becomes a `story.py` metric.*

*Kept as the record of the Phase 1 gate. The published story (merged 2026-11-18) supersedes it: its numbers are computed in
`story/story.py` and checked by `tests/test_numbers.py`, the value of information (10.4) was replaced by break-even prices, and
the rulings below replaced the review-status wording. The markers above show what existed at the gate.*

## Spine

The page climbs about twelve orders of magnitude, from the pore throat (about 10⁻⁶ m) to the North Sea (about 10⁶ m). Two
devices run beside the figure:

- **Ladder:** a log ruler from 1 µm to 1,000 km, with a marker on the current rung.
- **Ledger:** one bar per rung for the spread that rung adds. The bars stack into the spread on the decision.

Arc: `zoom` (moment, context, moment). The page opens on the decision, descends to the pore, climbs to the basin and
returns to the decision.

Headline: **Pinpoints and Echoes** is kept. Proposed dek: "How a measurement smaller than a hair becomes a decision about a
sea." The wording will be checked against the voice checkers in Phase 4.

## Steps

### 1. The decision (moment)

| Step | Figure | Number | Source, confidence |
|---|---|---|---|
| 1.1 | `money` (Volve capex by year) | Volve's capex, NOK 4,689 million nominal 2005 to 2016; about USD 1,169 million in 2025 money | `field_investment_real`, `field_economics`; Observed (NOK), Derived (USD) *found* |
| 1.2 | `money` with production | 71.6 million boe recovered (11.38 million Sm³ o.e.) | `field_economics.ultimate_mmboe`, `volve_reserves.csv`; Observed *found* |
| 1.3 | `ladder` introduced | One board decision rests on a few cubic metres of measured rock | the plug volume from step 3.3; Derived *to compute* |

### 2. Down to the pore (10⁻⁶ m)

| Step | Figure | Number | Source, confidence |
|---|---|---|---|
| 2.1 | `pore` (diagram: grains, throats, flow) | Flow through a tube scales with the fourth power of its radius, so halving a throat cuts the flow sixteenfold | Poiseuille's law, textbook; diagram Interpreted. To source: a reviewed text in the private knowledge store |
| 2.2 | `pore` with mercury curve | 11 samples from 15/9-19 A; the throats a mercury curve reaches run from about 0.03 to 263 µm | `well_core_mercury_injection` (report pages 213 to 224); *candidate, not yet reviewed* *found* |
| 2.3 | `pore`, R35 marked | Throat radius at 35 % mercury saturation, read from each curve | Derived from the candidates *to compute* |

### 3. The plug (10⁻² m)

| Step | Figure | Number | Source, confidence |
|---|---|---|---|
| 3.1 | `plugs` (k against φ, log axis) | 860 plugs from 15/9-19 A (728) and BT2 (132); horizontal Klinkenberg permeability from 0.01 to 20,500 mD | `well_core_plug`; Observed *found* |
| 3.2 | `plugs`, band at 19 to 21 % porosity | 91 plugs at about the same porosity span 12 to 3,490 mD, a factor of about 290 | Derived *found* |
| 3.3 | `plugs` with R35 colour | Throat size explains what porosity does not; the relation is fitted on the 11 mercury samples and applied to all plugs | Derived *to compute*. Winland's published coefficients are not in the library (open item 2) |
| 3.4 | `plugs`, conditions | Measured at 20 bar net confining pressure, not reservoir stress; Klinkenberg applied by the laboratory's formula | `docs/core_analysis.md` of ep, report pages *found* |

### 4. The log (10⁻¹ m)

| Step | Figure | Number | Source, confidence |
|---|---|---|---|
| 4.1 | `log` (F-11 T2, four tracks) | One sample every 0.1 m over 2,060 m of hole; Hugin 101 m thick | `beats_notes.json`; Observed *found* |
| 4.2 | `corelog` (core against log permeability) | The interpreted permeability is 0.55 to 0.60 of the core median | `well_core_vs_log_summary`; Derived *found* |

### 5. The pinpoint (10⁻¹ to 10³ m)

| Step | Figure | Number | Source, confidence |
|---|---|---|---|
| 5.1 | `ruler` | A 22 cm hole; median 2.3 km to the nearest well | `geometry.csv`; Derived *found* |
| 5.2 | `errstack` | Position, datum, time-to-depth and pick errors stack | `chain.csv`; Derived *found* |

### 6. The echo (10¹ m)

| Step | Figure | Number | Source, confidence |
|---|---|---|---|
| 6.1 | `section` | Inline 10215 in two-way time | SEG-Y ST10010; Observed *found* |
| 6.2 | `wedge` | 22 Hz, so beds thinner than about 36 m blur into one | `beats_notes.json` wedge; Derived *found* |
| 6.3 | `tie` | Correlation 0.32 after a 12 ms shift | `beats_notes.json` tie; Derived *found* |
| 6.4 | `fan` | One time (2.65 s) read as six depths over 68 m | `timedepth.csv`; Observed *found* |

### 7. The field (10³ m)

| Step | Figure | Number | Source, confidence |
|---|---|---|---|
| 7.1 | `transect` | Two published versions of one horizon and the gap between them | `spread.csv`, `transect.csv`; Observed *found* |
| 7.2 | `closure` | The area grows from 7.5 to 19.7 km² between the P90 and P50 contacts | `beats_notes.json` closure; Derived *found* |

### 8. The basin (10⁵ to 10⁶ m)

| Step | Figure | Number | Source, confidence |
|---|---|---|---|
| 8.1 | `scale` (7,033 wellbores at true size) | Together they cover one part in about 517 million of the area | `wells.csv`, `geometry.csv`; Derived *found* |
| 8.2 | `ladder` complete | Pore to basin is about twelve orders of magnitude | Derived *to compute* |

### 9. Compounding

| Step | Figure | Number | Source, confidence |
|---|---|---|---|
| 9.1 | `cascade` (one factor) | Area alone: P90 to P10 | Monte Carlo with the prospect library, fixed seed; Interpreted *to compute* |
| 9.2 | `cascade` (factors added one by one) | P10/P90 widens; the existing run gives 7.9 to 33.9 (a factor of about 4.3) with five factors | `beats_notes.json` volumes; Interpreted *found* (to be rerun) |
| 9.3 | `cascade`, correlated against independent | Porosity, permeability and saturation move together in the plugs; treating them as independent narrows the spread | the correlation from `well_core_plug`; Derived *to compute* |

### 10. The money

| Step | Figure | Number | Source, confidence |
|---|---|---|---|
| 10.1 | `money` (Volve NPV against price) | Pre-tax NPV USD 500 million at USD 40/bbl, USD 2,267 million at USD 80; break-even about USD 29/bbl | `field_economics`; Derived, with screening assumptions for opex, tax and abandonment *found* |
| 10.2 | `money` (the prospect) | Chance of success, NPV if found, cost of a dry hole, expected value | the prospect and economics libraries on a synthetic prospect with stated assumptions (`data/assumptions.yaml`); Interpreted *to compute* |
| 10.3 | `money`, the base rate | The share of North Sea exploration wells that made a discovery, as the prior on chance | Sodir wellbores; Observed *to compute* |
| 10.4 | `money`, value of information | What one more measurement is worth before the drill-or-drop vote | value of information from the prospect library; Interpreted *to compute* |

### 11. The test (return to the moment)

| Step | Figure | Number | Source, confidence |
|---|---|---|---|
| 11.1 | `revisions` (Volve estimate by year) | 13.68 million Sm³ o.e. in 2005, 9.91 in 2009, 11.38 today | `volve_reserves.csv`; Observed *found* |
| 11.2 | `revisions` (59 fields) | Half grew, half shrank; P10 to P90 of latest over first is 0.31 to 1.91 | `revisions.csv`; Derived *found* |
| 11.3 | `ledger` complete | The final step returns to the decision of step 1 with every bar in place | none |

## Decisions at the Phase 1 gate (Adam, 2026-11-18)

"This is a narrative story as such do not enforce such strict wording as not yet checked. Just quote the source. Fit you own
relation."

1. **Mercury injection.** The 11 samples are used and cited by report and page (`15-9-19_A_0035.pdf`, pages 213 to 224). Their
   review status stays in the data and the appendix, not in the prose.
2. **Throat relation.** The throat radius at 35 % mercury saturation is read from the 11 curves, and a k–φ–throat relation is
   fitted on them (Derived) and applied to all plugs. Winland is named as the origin of the idea; his coefficients are not used.
3. **Prices.** Only derived NPV values are shipped, never the IMF series (its redistribution terms are unverified). The
   attribution names IMF, Norges Bank and BLS.
4. **Plug size.** It is read from the core report and cited. If the report does not state it, the step gives the volume
   per plug as a stated assumption.
5. **Poiseuille.** The law is stated as standard physics (Hagen–Poiseuille), and the page shows the measured relation beside
   it.
