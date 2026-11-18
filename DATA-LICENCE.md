# Data licence

The licence in `LICENSE` (MIT License with Acknowledgement) covers the code, the story text and the figures made here. The
extracts in `story/data/` are derived from the sources below and keep their terms.

## Sodir (Norwegian Offshore Directorate)

`wells.csv`, `geometry.csv` (except the hole diameter), `volve_money.csv`, `volve_reserves.csv`, `revisions.csv`, the Sodir
core lengths in `core_notes.json`, the base rates in `money_notes.json` and the screening values derived from Sodir's
investment and production tables derive from the Sodir FactPages. Terms: Norwegian Licence for Open Government Data
(NLOD 2.0), as recorded in the author's dataset register. Credit "Source: Sodir". Reuse, change and redistribution are
permitted with that credit, a reference to the licence and a note that the data has been changed.

> Source: Sodir. Contains data under the Norwegian licence for Open Government data (NLOD 2.0) distributed by Sodir. Filtered, summarised and converted by the author.

## Volve

`plugs.csv`, `micp.csv`, `micp_samples.csv`, `core_log_pairs.csv`, `log.csv`, `chain.csv`, `spread.csv`, `transect.csv`,
`picks.csv`, `section.json`, `trace.csv`, `horizons.csv`, `wedge.json`, `tie.csv`, `timedepth.csv`, `closure.csv`,
`contact.csv`, the hole diameter in `geometry.csv` and the cascade, whose contact and area come from Volve, derive from the
Volve data village. The mercury-injection curves are read from the special core analysis report `15-9-19_A_0035.pdf`, pages
213 to 224. `header.json`, the band in the page's hero, is a synthetic section made by the author's seismic-art tool and
derives from no dataset; the page says so. Terms: "Terms and conditions for license to data, Volve", published by Equinor ASA
and the former Volve licence partners. The terms are based on CC BY 4.0 with two changes: the material may not be sold, and
the licence covers all the data whether or not copyright applies. Commercial and non-commercial use, adapted material and
sharing are permitted with credit, a link to the terms and a copyright notice; adapted material may not be shared under
terms that stop recipients complying; the data must not be presented in a misleading or distorted way; no endorsement is
implied.

> Contains data from the Volve data village, © Equinor ASA and the former Volve licence partners (ExxonMobil E&P Norway, Bayerngas Norge). Used under the Volve Terms and Conditions. Generalised for display.

The raw Volve data (seismic, logs, interpretations, reports) is not in this repository and is never committed; the scripts
read it from a local path. Everything here is a small, derived extract.

## Prices, exchange rates and inflation

The IMF Primary Commodity Prices (Brent), Norges Bank's USD/NOK and the US Bureau of Labor Statistics CPI-U are used by the
author's data engine to convert Sodir's NOK to real 2025 USD and to set the range of oil prices. Their redistribution terms
are not all verified (BLS data is US Government work), so only derived values appear here: converted investment, three
percentiles of the annual Brent price, and values computed from them. The series themselves are not reproduced.

This project is not connected with, sponsored or endorsed by Sodir, Equinor, the former Volve licence partners, the IMF,
Norges Bank or the BLS.
