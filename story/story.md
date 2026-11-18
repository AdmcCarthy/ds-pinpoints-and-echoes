---
title: Pinpoints and Echoes
short_title: Pinpoints and Echoes
dek: How a measurement smaller than a hair becomes a decision about a sea. From the pore throat to the North Sea, each step up the scale adds its own uncertainty, and the decision is still made.
kicker: FROM THE PORE TO THE NORTH SEA · VOLVE AS THE WORKED CASE
byline: Adam McCarthy
date: 2026-11-18
arc: zoom
register: section
palette: tide
surface: nordic-cool
units: sm3
horizon: { data: header, height: 80, label: false, palette: shale }
kpis:
  - { metric: orders, label: "orders of magnitude from a pore throat to the North Sea", filter: round:0 }
  - { metric: plug_litres, label: "litres of rock measured in the laboratory for one field", filter: round:0 }
  - { metric: cas_cor_x, label: "× between the low and high case of one field's oil", filter: round:1 }
  - { metric: volve_capex_usd, label: "billion USD invested on that basis", filter: round:1 }
sources:
  sodir:
    name: Sodir FactPages, wellbore, discovery, field, reserves, production and investment tables (Norwegian Offshore Directorate)
    url: "https://factpages.sodir.no"
    accessed: 2026-11-18
    note: "Source: Sodir. Contains data under the Norwegian licence for Open Government data (NLOD 2.0) distributed by Sodir. Filtered, summarised and converted by the author's data engine; screening economics (opex, tariffs, abandonment, tax) are the engine's stated assumptions, not Sodir data."
  volve:
    name: Volve data village, Equinor ASA and the former Volve licence partners
    url: "https://www.equinor.com/energy/volve-data-sharing"
    note: "Contains data from the Volve data village, © Equinor ASA and the former Volve licence partners (ExxonMobil E&P Norway, Bayerngas Norge). Used under the Volve Terms and Conditions. Generalised for display. Core analysis and mercury injection from the 15/9-19 A and BT2 core reports (mercury injection: 15-9-19_A_0035.pdf, pages 213 to 224); horizons, closure curve and contact distribution via kit-surfaces; surveys, check shots and picks via the author's data engine."
  macro:
    name: IMF Primary Commodity Prices (Brent), Norges Bank USD/NOK, US Bureau of Labor Statistics CPI-U
    url: "https://www.imf.org/en/Research/commodity-prices"
    accessed: 2026-11-18
    note: "Used only to convert Sodir's NOK to real 2025 USD and to set the range of prices; only derived values are shown, the series are not reproduced."
  story:
    name: Stated assumptions of this story
    url: "https://github.com/AdmcCarthy/ds-pinpoints-and-echoes/blob/main/data/assumptions.yaml"
    note: "Ranges for the volumetric factors, the rock-quality link, the daily cost of a well and the windows used for base rates, chosen for the illustration and listed in Basis of analysis. They are not Volve's own estimates."
data:
  wells: data/wells.csv
  geometry: data/geometry.csv
  chain: data/chain.csv
  transect: data/transect.csv
  picks: data/picks.csv
  spread: data/spread.csv
  log: data/log.csv
  core_log_pairs: data/core_log_pairs.csv
  plugs: data/plugs.csv
  micp: data/micp.csv
  micp_samples: data/micp_samples.csv
  section: data/section.json
  header: data/header.json
  horizons: data/horizons.csv
  wedge: data/wedge.json
  tie: data/tie.csv
  timedepth: data/timedepth.csv
  closure: data/closure.csv
  contact: data/contact.csv
  cascade: data/cascade.csv
  cascade_hist: data/cascade_hist.csv
  volve_money: data/volve_money.csv
  prospect_price: data/prospect_price.csv
  prospect_npv: data/prospect_npv.csv
  prospect_curve: data/prospect_curve.csv
  volve_reserves: data/volve_reserves.csv
  revisions: data/revisions.csv
  core_notes: data/core_notes.json
  log_notes: data/log_notes.json
  wells_notes: data/wells_notes.json
  seismic_notes: data/seismic_notes.json
  field_notes: data/field_notes.json
  cascade_notes: data/cascade_notes.json
  money_notes: data/money_notes.json
  test_notes: data/test_notes.json
---

In {{ volve_first_capex }} a group of companies began to spend money on a small oil field in the North Sea. By the
time it closed they had invested about {{ volve_capex_usd | round:1 }} billion US dollars in today's money. Every
dollar rested on rock nobody had seen. This story follows that rock up the scale, from the gaps between sand grains to
the whole of the Norwegian North Sea. At each step it keeps a tally of what was measured, what was calculated and what
was judged, and of how much each step leaves open.

## What one field cost, and what it rested on

::: step {beat=moment}
Volve lies in block 15/9 of the Norwegian North Sea. Investment began in {{ volve_first_capex }}, oil flowed from
{{ volve_first_oil }} to {{ volve_last_oil }}, and the field sold {{ volve_produced | volume }} before it shut down.
The bars are what the licensees spent each year, converted to 2025 dollars.

```chart
id: volve
type: custom
module: figures/volve.js
data: [volve_money, ladder]
state: { both: false }
title: About a billion dollars went into Volve before it closed
subtitle: Investment by year, Sodir's nominal NOK converted to 2025 USD
source: sodir
confidence: derived
unit: USD million (2025)
notes: Sodir's investment figures in nominal NOK, converted with the year's USD/NOK (Norges Bank) and US CPI-U (BLS). The negative bar in 2016 is Sodir's own figure. The strip along the top is the scale ladder; nothing is lit yet.
```
:::

::: step {beat=moment}
The money came back as oil. How much would come back was decided by the rock: how much of it there was, how much
oil its pores held and how easily the oil could flow out.

```chart
use: volve
both: true
title: The spending came first; the oil followed for nine years
subtitle: Investment by year in 2025 USD, and net sold production by year in million Sm³ o.e.
```
:::

::: step {beat=moment}
### A few litres of rock behind a billion dollars

In the laboratory, the rock measured from Volve's two cored wells comes to about {{ plug_litres | round:0 }} litres:
{{ n_plug_h | int }} small horizontal plugs and {{ n_plug_v | int }} larger vertical ones.

Across the whole Norwegian North Sea, Sodir lists {{ sodir_core_km | round:0 }} km of core from
{{ sodir_core_wells | int }} wellbores. The ladder runs from the smallest thing measured to the largest thing decided:
about {{ orders | round:0 }} orders of magnitude.

```chart
id: ladder
type: custom
module: figures/ladder.js
data: ladder
state: { upto: all }
title: From a pore throat to a sea, about eleven powers of ten
subtitle: Every scale this story visits, on one logarithmic ruler
source: volve
confidence: derived
unit: m
notes: Each length is computed from the data where it is a measurement (throat, log sample, hole, resolvable bed, well spacing, closure, area) and stated as a parameter where it is a class (sand grain, plug). Widths of areas are the side of a square of equal area.
exception: { rule: linear axes, reason: the lengths span about eleven orders of magnitude }
```
:::

## Down to the throats between the grains

::: step {beat=context}
Sandstone is grains with space between them. The space holds the oil. The narrow necks that join one pore to the
next, the pore throats, decide how fast it can move.

Flow through a tube grows with the fourth power of its width, so a throat half as wide passes about one
{{ poise_half | int }}th of the flow.

```chart
id: pore
type: custom
module: figures/pore.js
data: [micp, micp_samples, ladder]
state: { view: tubes }
title: Halve the throat and the flow falls sixteenfold
subtitle: A sketch of sand grains and the space between them, and two tubes whose radii differ by two
source: story
confidence: interpreted
notes: A diagram, not data. The fourth-power rule is Hagen–Poiseuille flow in a straight tube; real throats are irregular, so the rule sets the steepness, not the number.
```
:::

::: step {beat=context}
Throats are measured by forcing mercury into a plug. At low pressure it enters only the widest throats; at high
pressure it finds the narrowest. {{ micp_n | int }} plugs of {{ well_a }} were tested this way, and their throats run
from about {{ micp_r_min | round:2 }} µm to about {{ micp_r_max | round:0 }} µm.

```chart
id: micp
type: custom
module: figures/pore.js
data: [micp, micp_samples, ladder]
state: { view: curves }
title: Mercury finds the wide throats first and the narrow ones last
subtitle: Mercury saturation against the throat radius it has entered, mercury-injection plugs of 15/9-19 A
source: volve
confidence: observed
unit: µm, % of pore volume
notes: Read from the special core analysis report 15-9-19_A_0035.pdf, pages 213 to 224; radii are the report's own conversion of injection pressure. The first points of some curves carry a small conformance artefact.
exception: { rule: linear axes, reason: throat radii span four orders of magnitude }
```
:::

::: step {beat=context}
One number summarises each curve: R35, the throat radius at which mercury fills {{ 35 | param }} % of the pore space.
In these plugs it runs from {{ r35_min | round:1 }} to {{ r35_max | round:0 }} µm, inside sand grains about
{{ grain_mm | round:2 }} mm across.

```chart
use: micp
view: r35
title: The throat that matters is a few micrometres across
subtitle: The same curves, with the radius at 35 % mercury saturation marked on each
```
:::

## Eight hundred plugs from two wells

::: step {beat=context}
The routine core analysis of {{ well_a }} and {{ well_b }} holds {{ n_plugs | int }} plugs. Their permeability, the
ease with which fluid flows through them, runs from {{ k_min | round:2 }} to {{ k_max | int }} millidarcies: about
{{ k_span | round:0 }} orders of magnitude within one reservoir.

```chart
id: plugs
type: custom
module: figures/plugs.js
data: [plugs, micp_samples, ladder]
state: { band: false }
title: One reservoir holds rock a million times more permeable than other rock in it
subtitle: Horizontal Klinkenberg permeability against helium porosity, routine plugs of 15/9-19 A and BT2
source: volve
confidence: observed
unit: mD, %
notes: Every plug with both measurements is drawn; none is removed. Permeability on a logarithmic axis, as is conventional. Where the plugs are coloured by throat size, the colour is Derived from the relation fitted on the mercury samples.
exception: { rule: linear axes, reason: permeability spans six orders of magnitude }
```
:::

::: step {beat=context}
### At one porosity, a three-hundredfold range

Porosity, the share of the rock that is pore space, predicts some of that range but not most of it. The
{{ band_n | int }} plugs with about the same porosity, {{ 19 | param }} to {{ 21 | param }} %, still differ in
permeability by a factor of {{ band_x | round:0 }}.

```chart
use: plugs
band: true
title: At one porosity, permeability still varies almost three-hundredfold
```
:::

::: step {beat=context}
The throats explain much of the rest. A relation fitted to the mercury plugs gives every routine plug a throat size
from its permeability and porosity, with an error of about {{ fit_err_pct | round:0 }} %.

The idea is Winland's; the coefficients are fitted on this field's own data. Coloured by throat, the cloud sorts
itself into bands.

```chart
use: plugs
band: false
throat: true
mercury: true
title: Coloured by throat size, the scatter turns into order
subtitle: The same plugs, coloured by the throat radius the fitted relation gives them; rings are the mercury samples
```
:::

::: step {beat=context}
Each plug was measured at {{ plug_bar | int }} bar of confining pressure, far less than the rock felt underground,
after it had been cleaned and dried.

```chart
use: plugs
throat: false
mercury: false
title: Every plug is a measurement under laboratory conditions
```
:::

## A log is continuous along one line only

::: step {beat=context}
A well log is drawn by tools pulled up the hole. The composite log of {{ well_log }} samples the rock every
{{ log_sample_cm | int }} cm over {{ log_span_m | round:0 }} m: natural radioactivity, density, electrical resistivity
and the speed of sound. The reservoir, the Hugin Formation, is {{ hugin_m | round:0 }} m thick here.

```chart
id: log
type: custom
module: figures/log.js
data: [log, ladder]
state: { zoom: false }
title: Rich along one line, blind a metre away
subtitle: Composite log of 15/9-F-11 T2 against depth below mean sea level; the Hugin Fm shaded
source: volve
confidence: observed
unit: API, g/cm³, ohm·m, µs/ft
notes: Four of the composite's curves. Depth is converted from measured depth with the well's near-offset check shot. Resistivity on a logarithmic axis, as is conventional. The reservoir band is the interpreters' top and base picks.
```
:::

::: step {beat=context}
Inside the reservoir the log resolves layers a few tens of centimetres thick. It does not measure permeability. That
is calculated from the other curves, with a model calibrated to the plugs.

```chart
use: log
zoom: true
title: In the reservoir, the log resolves layers the echo cannot
```
:::

::: step {beat=context}
### The log against the plugs it was calibrated to

Set the calculated permeability beside the plugs at the same depths and the two disagree in a steady way. In the two
cored wells the log gives {{ cl_lo | pct }} to {{ cl_hi | pct }} of the plugs' median.

Neither is wrong. They measure different volumes of rock under different conditions, and the model is fitted to the
plugs.

```chart
id: corelog
type: custom
module: figures/corelog.js
data: [core_log_pairs, ladder]
title: The log reads lower than the plugs it was calibrated to
subtitle: Interpreted log permeability against plug permeability at the same depth, 15/9-19 A and BT2
source: volve
confidence: derived
unit: mD
notes: The interpretation is calibrated to the core, so this is a consistency check, not an independent test. Hollow points sit at the interpretation's 0.1 mD floor. Plug depths are shifted to the log by the core shift table.
exception: { rule: linear axes, reason: both quantities span six orders of magnitude }
```
:::

## The well as a pinpoint

::: step {beat=context}
At reservoir depth a wellbore is about {{ hole_cm | round:0 }} cm across. The typical exploration well is
{{ nn_km | round:1 }} km from the nearest other one. Everything the log and the plugs know lies inside that hole.

```chart
id: ruler
type: custom
module: figures/ruler.js
data: [geometry, ladder]
state: { coin: false }
title: From a hole a hand fits into, to an area hundreds of kilometres wide
subtitle: Lengths on a logarithmic scale
source: sodir
confidence: derived
unit: m, km
notes: Distances use wellhead positions of exploration wellbores (first bores, 100 m cells). Hole diameter is the Volve reservoir-depth median.
exception: { rule: linear axes, reason: the lengths span seven orders of magnitude }
```
:::

::: step {beat=context}
Shrink the wellbore to a coin a centimetre across and the next well is about {{ coin_m | round:0 }} m away.

```chart
use: ruler
coin: true
title: As a coin, the next well is a long walk away
```
:::

::: step {beat=context}
### Even a well's position is a measurement

The surveys of Volve's wells carry a typical sideways uncertainty of {{ pos_h | round:0 }} m at their end. Depth adds
links of its own: the reference the depths are measured from, the conversion from time, the pick of a surface.
Combined, the typical vertical error is about {{ stack_typical | round:0 }} m; the largest values on file combine to
about {{ stack_worst | round:0 }} m.

```chart
id: errstack
type: custom
module: figures/errstack.js
data: [stack, ladder]
state: { upto: 6 }
title: Small errors at each link add up at the target
subtitle: Vertical errors at the reservoir by link, typical (solid) and largest on file (light), and their combination
source: volve
confidence: interpreted
unit: m
notes: Links combined in quadrature, which assumes they are independent. The depth reference is a systematic offset, not a random error, so the combined largest value is a bound, not a forecast.
```
:::

## Between the wells, only echoes

::: step {beat=context}
Between the wells the rock is seen only by sound. A survey ship fires air guns and listens for echoes from the
layers below. The panel is inline {{ inline | int }} of the Volve survey, {{ n_traces | int }} traces
{{ bin_m | round:1 }} m apart. The vertical axis is time: the echo from the top of the reservoir returns after
{{ hugin_twt_s | round:2 }} seconds.

```chart
id: section
type: custom
module: figures/section.js
data: [section, horizons, ladder]
state: { horizons: false }
title: Between the wells, the rock is known by its echo
subtitle: Inline of the ST10010 full stack through 15/9-F-11 T2, two-way time
source: volve
confidence: observed
unit: ms
notes: Relative amplitude; the polarity is not stated in the file. Every second trace is drawn.
```
:::

::: step {beat=context}
The interpreters' surfaces follow the echoes from well to well. At the well they are tied to the log; away from it
they are a judgement about which echo is the same layer.

```chart
use: section
horizons: true
title: The published surfaces follow the echoes away from the well
```
:::

::: step {beat=context}
### How thin a bed the echo can see

The sound that returns from Volve's reservoir has a typical frequency of {{ dom_hz | round:0 }} Hz. Through rock at
{{ v_res | int }} m/s that blurs any bed thinner than about {{ tuning_m | round:0 }} m into a single echo, a hundred
times thicker than the layers the log resolved.

```chart
id: wedge
type: custom
module: figures/wedge.js
data: [wedge, ladder]
title: Below a few tens of metres, top and base merge into one echo
subtitle: A synthetic bed thinning to nothing, seen through the data's own frequency
source: volve
confidence: derived
unit: m, ms
notes: Synthetic. Two interfaces of equal and opposite reflectivity at the reservoir's sonic velocity, with a zero-phase wavelet at the centroid frequency of the real data.
```
:::

::: step {beat=context}
A synthetic echo made from the log can be set beside the real one at the well, which ties the pinpoint to the echo.

```chart
id: tie
type: custom
module: figures/tie.js
data: [tie, ladder]
state: { shifted: false }
title: The log's echo and the real echo, side by side
subtitle: Synthetic seismogram from the log of 15/9-F-11 T2 beside the real trace at the well
source: volve
confidence: derived
unit: ms
notes: Zero-phase wavelet at the data's centroid frequency, no stretch or squeeze, one bulk shift. A full tie would extract the wavelet and adjust the time-depth relation.
```
:::

::: step {beat=context}
After one shift of {{ tie_shift | int }} ms the two correlate at {{ tie_corr | round:2 }}. The outline agrees; the
detail does not. That remainder is the honest measure of how well the two records fit.

```chart
use: tie
shifted: true
title: After one shift the outline agrees; the detail does not
```
:::

::: step {beat=context}
### One echo time, several depths

Time becomes depth through the speed of sound, measured in each well by a check shot. Read {{ fan_n | int }} of
Volve's check-shot tables at {{ fan_twt_s | round:2 }} seconds and they give depths spread over
{{ fan_range | round:0 }} m.

```chart
id: fan
type: custom
module: figures/fan.js
data: [timedepth, ladder]
state: { at: 2650, zoom: true }
title: One echo time, read through each well's table, lands at different depths
subtitle: Two-way time against depth below sea level for every Volve check-shot table covering that time
source: volve
confidence: observed
unit: m, ms
notes: Each table belongs to one wellbore and is valid along that well's path; the spread includes real lateral change in velocity as well as measurement error.
```
:::

## From surfaces to the area of oil

::: step {beat=context}
Volve's surfaces were picked twice, on two processings of the seismic. Along a line of {{ line_km | round:1 }} km
between wells, the two versions of the Ty Formation top differ by up to {{ gap_max_ms | round:0 }} ms, about
{{ gap_max_m | round:0 }} m. Both pass close to the {{ n_picks_line | int }} well picks near the line; between them
each is a judgement.

```chart
id: transect
type: custom
module: figures/transect.js
data: [transect, picks, ladder]
state: { stage: 3 }
title: Two versions of the same surface part company between the wells
subtitle: Ty Fm top along a line between two well picks, base survey and reprocessed survey, two-way time
source: volve
confidence: observed
unit: ms
notes: Both versions are published Volve interpretations; they differ in processing and in picking, so they are two answers, not a controlled experiment. Depth at 2,345 m/s, the field's average upper velocity.
```
:::

::: step {beat=context}
The oil fills the trap down to its contact with water. The 2005 plan put that contact at {{ owc_p90 | int }} m below
sea level in the low case (P90) and {{ owc_p50 | int }} m in the middle case (P50).

Those {{ owc_step | int }} m take the area above the contact from {{ area_p90 | round:1 }} to {{ area_p50 | round:1 }}
km².

```chart
id: closure
type: custom
module: figures/closure.js
data: [closure, contact, field_notes, ladder]
state: { cases: true }
title: Thirty metres of contact depth more than doubles the area of oil
subtitle: Area inside the closing contour against depth, Volve high on the Hugin top, with the plan's contact cases
source: volve
confidence: interpreted
unit: km², m
notes: The surface is kit-surfaces' smoothed Hugin top in depth, an interpretation. P90 is the low case, P10 the high case (oilfield convention). The deepest case lies below the mapped surface.
```
:::

## Every well in the Norwegian North Sea

::: step {beat=context}
Step back to the whole shelf. The map shows {{ n_wellbores | int }} petroleum wellbores at their true size on the
{{ area_km2 | about }} km² they span. None is visible. Together they have pierced one part in {{ one_in | about }} of
that area.

```chart
id: shelf
type: custom
module: figures/scale.js
data: [wells, geometry, ladder]
state: { mag: 1 }
title: At true size, every well ever drilled vanishes
subtitle: Wellhead positions of petroleum wellbores, Norwegian North Sea, drawn at true diameter
source: sodir
confidence: derived
unit: km² (area), cm (hole)
notes: Wellhead positions, not bottom-hole. The dashed outline is the convex hull of the wellheads, not the sea. Every wellbore counts, sidetracks included.
```
:::

::: step {beat=context}
Enlarged twelve thousand times, the wells show where the drilling has been: clusters on the fields, lone points on old
ideas.

The ground between them is still almost all unsampled. Every claim about the North Sea is built outwards from these
points, and every new idea starts from them too.

```chart
use: shelf
mag: 12000
title: Enlarged to be seen, the wells still leave the sea empty
subtitle: The same wellheads, each enlarged by the factor stated below
```
:::

## How the uncertainties multiply

::: step {beat=context}
The oil a field will give is a product: rock volume, times the share that is reservoir, times porosity, times oil
saturation, divided by shrinkage at the surface, times the share that can be recovered.

Each factor comes from a different rung of the ladder. With only the rock volume uncertain, the high case is
{{ cas_rock_x | round:1 }} times the low.

```chart
id: cascade
type: custom
module: figures/cascade.js
data: [cascade, cascade_hist, test_notes, ladder]
state: { upto: 0 }
title: Rock volume alone leaves more than a threefold range
subtitle: Recoverable oil, one row per factor added; P90 to P10 bar, P50 dot, the factor between them at right
source: story
confidence: interpreted
unit: million Sm³
notes: A Monte Carlo of the volumetric equation with one fixed set of draws. The contact is the 2005 plan's distribution on the Hugin top area curve; the other ranges are the story's stated assumptions, not Volve's own estimates. Logarithmic axis.
exception: { rule: linear axes, reason: the products are lognormal; equal ratios read as equal distances }
```
:::

::: step {beat=context}
Add the factors one by one and the range widens at every step. With all six uncertain and independent, the high case
is {{ cas_ind_x | round:1 }} times the low.

```chart
use: cascade
upto: 5
title: Each factor widens the range
```
:::

::: step {beat=context}
### Good rock tends to be good in every way

The factors are not independent. In the plugs, porosity accounts for {{ r2_phi | pct }} of the variation in log
permeability. Link the rock properties and the low case falls from {{ cas_ind_p90 | round:1 }} to
{{ cas_cor_p90 | round:1 }} million Sm³; the high case becomes {{ cas_cor_x | round:1 }} times the low.

```chart
use: cascade
upto: 6
title: Linked rock properties widen the range again
```
:::

::: step {beat=context}
Volve itself produced {{ volve_oil | round:1 }} million Sm³ of oil. On this illustration that sits below the middle
case, with about {{ volve_exceed | pct }} of the outcomes above it: inside the range, on the low side.

```chart
use: cascade
upto: 6
volve: true
title: The real field came in below the middle of the range
```
:::

## Price, chance and the drill-or-drop decision

::: step {beat=context}
Volume meets price. For a Volve-sized find developed as a subsea tie-back, value rises with price along a straight
line for each volume case. The low case needs about {{ be_p90 | int }} USD a barrel to break even, the high case about
{{ be_p10 | int }}. The annual Brent price since 2005 has not fallen below about {{ price_min | int }} USD in today's
money.

```chart
id: money
type: custom
module: figures/money.js
data: [prospect_price, prospect_npv, prospect_curve, money_notes, ladder]
state: { view: price }
title: The bigger the find, the lower the price it needs
subtitle: Pre-tax value of the prospect against a flat oil price, for its P90, P50 and P10 volumes
source: story
confidence: interpreted
unit: USD billion (2025), USD per barrel
notes: Value is pre-tax NPV at 8 % real from a straight line in volume fitted to the screening economics of the subsea tie-back fields, and in price as the economics are affine in it. The grey band is the 10th to 90th percentile of annual Brent, 2005 to 2024, in 2025 money.
```
:::

::: step {beat=context}
Draw volume and price together and the value of the find, if it is found, runs from {{ npv_p90 | round:1 }} to
{{ npv_p10 | round:1 }} billion USD between the low and high cases, a factor of {{ npv_x | round:1 }}. Two uncertain
things, multiplied, give a wider answer than either alone.

```chart
use: money
view: spread
title: "Volume times price: the value spans a factor of more than seven"
subtitle: Pre-tax NPV of the prospect if found, with volume and price both uncertain
```
:::

::: step {beat=context}
### The chance of finding it at all

Before any of that, the well has to find oil. Since 2000, {{ pg_tech | pct }} of North Sea wildcat wellbores made a registered
discovery. Of those drilled from 2000 to 2014, {{ pg_comm | pct }} found something that became, or joined, a producing
field.

A dry hole takes about {{ dry_days | int }} days of drilling, costed here at about {{ dry_cost | int }} million USD.

```chart
use: money
view: chance
title: For a prize this size, the dry hole is the smaller risk
subtitle: Expected value of drilling the prospect against its chance of success, with Sodir's base rates
```
:::

::: step {beat=context}
At the commercial rate the expected value of drilling is about {{ emv | round:1 }} billion USD, and the well breaks
even at a chance of about {{ be_pg | pct }}. The recommendation is to drill. The cost of being wrong is stated beside
it: the licence group loses the cost of the well about three times in four, and the volume, if found, may be a quarter
of the middle case. Volve itself, on the same screening economics, broke even at about {{ volve_be | int }} USD.

```chart
use: money
view: price
volve: true
title: Volve itself broke even at under thirty dollars
subtitle: The prospect's lines with Volve's own screening value against price (dashed)
```
:::

## What the regulator's own record shows

::: step {beat=moment}
Sodir publishes its estimate of every field every year. For Volve it began at {{ volve_first | round:1 }} million Sm³
o.e. in {{ volve_first_yr }}, rose to {{ volve_peak | round:1 }} in {{ volve_peak_yr }}, fell to
{{ volve_low | round:1 }} in {{ volve_low_yr }} and ended at {{ volve_latest | round:1 }}. The answer moved while the
oil was being produced.

```chart
id: volve_hist
type: line
data: volve_hist
x: snapshot_year
y: recoverable_mn_sm3
series: series
title: Twenty years of one field's number
subtitle: Sodir's recoverable estimate for Volve by year, million Sm³ o.e.
source: sodir
confidence: observed
unit: million Sm³ o.e.
```
:::

::: step {beat=moment}
Across {{ rev_n | int }} fields followed by Sodir from their plan for development, the latest estimate grew in
{{ rev_up | pct }} and shrank in {{ rev_down | pct }}. {{ rev_halved | pct }} at least halved; {{ rev_doubled | pct }}
at least doubled. For the middle eight in ten, the latest estimate is {{ rev_p10 | round:2 }} to
{{ rev_p90 | round:2 }} times the first.

```chart
id: revisions
type: dots
data: revisions_dec
row: decade
value: ratio_pct
label: field_label
scale: symlog
title: Half the fields grew and half shrank
subtitle: Latest Sodir estimate as a percentage of the first, by decade of the plan's approval
source: sodir
confidence: derived
unit: "%"
```
:::

::: step {beat=moment}
### Every rung leaves a range open

The ranges stack into the decision, and the decision is still made: on the evidence there is, with the cost of being
wrong stated beside it. Then the field is produced, the estimate is revised, and the next idea starts from
{{ sodir_core_km | round:0 }} km of core and every well already drilled.

```chart
id: ledger
type: custom
module: figures/ledger.js
data: [ledger, ladder]
title: Each rung of the ladder leaves its own range
subtitle: For each step of the story, the factor between its low and high values
source: story
confidence: interpreted
unit: factor (high over low)
notes: Each factor is measured in its own way (hover for the basis) and they are not multiplied together. Logarithmic axis.
exception: { rule: linear axes, reason: the factors run from under two to nearly three hundred }
```
:::

::: appendix
### Pore throats and plugs

Mercury-injection curves are read from the special core analysis of {{ well_a }} ({{ micp_report }}, pages
{{ micp_page_lo }} to {{ micp_page_hi }}), as cumulative mercury saturation against the report's own pore-throat
radius. R35 is the radius at which the cumulative saturation last crosses {{ 35 | param }} % from below, interpolated in
log radius; the first points of each curve carry a small conformance artefact and are passed over by that rule. The
throat relation, log₁₀ R35 = a + b log₁₀ k + c log₁₀ φ (k in mD, φ in %), follows Winland's idea and is fitted by least
squares on the {{ fit_n | int }} mercury samples that have a porosity; Winland's published coefficients are not used.
The fitted exponent of permeability is {{ fit_b | round:2 }}. Routine plugs: horizontal Klinkenberg permeability and
helium porosity at {{ plug_bar | int }} bar net confining pressure, cleaned and dried; the Klinkenberg correction is the
laboratory's empirical formula. Plug volume assumes each plug is as long as it is wide (one-inch horizontal and
inch-and-a-half vertical plugs).

### How the volume chain is computed

Recoverable oil = GRV × net-to-gross × φ × oil saturation ÷ Bo × recovery factor. GRV is the integral of the closure
area between the contact and the contact less the gross thickness, capped at the crest. Families: lognormal for the
thickness and Bo, logit-normal for the fractions, fitted to the stated P90, P50 and P10. The linked case draws the four
rock properties from one shared factor with a loading of {{ rho | round:1 }}. Seed and draws ({{ cas_n | int }}) are
fixed, so every step uses the same draws. {{ beyond_map | pct }} of the contacts lie below the mapped surface and take
its deepest area.

### Value, price and chance

NPV is pre-tax, real 2025 USD, at {{ 8 | param }} % a year, from the data engine's screening economics of the
{{ npv_lines_n | int }} subsea tie-back fields, fitted as a + b × volume at each flat price; both a and b are straight
lines in price within rounding, so prices outside the fitted range are extrapolated on those lines. Base rates count
first wellbores with purpose wildcat in the Norwegian North Sea; a commercial success is a discovery now producing, shut
down, approved for production or included in a field. The dry-hole cost is the median drilling days of North Sea
wildcat wellbores since 2015 times an assumed {{ spread_day | round:0 }} million USD a day. The range of prices is the 10th to
90th percentile of annual Brent from 2005 to 2024, real 2025 USD: {{ price_lo | int }} to {{ price_hi | int }} USD a
barrel, median {{ price_mid | int }}.
:::
