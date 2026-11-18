// The money. view "price": the prospect's pre-tax NPV against a flat oil price for its P90, P50 and P10 volumes, the
// break-even price of each, and the band of annual Brent prices 2005 to 2024; { volve } adds Volve's own line.
// view "spread": the prospect's NPV if found, volume and price both uncertain. view "chance": the expected value of
// drilling against the chance of success, with Sodir's technical and commercial base rates marked.
import { onSchemeChange } from "../runtime/js/subscout.js";
import { frame, plotHeight, rungs, styleAxis, label, num, c1, c2, hi, ink, ctx, muted, isNarrow, hover } from "./_common.js";

export default function money(el, datasets, opts = {}) {
  const G = d3.group(datasets.prospect_price.map((r) => ({ p: +r.price, v: r.volume_case, npv: +r.npv / 1000 })), (r) => r.v);
  const N = datasets.prospect_npv.map((r) => ({ lo: +r.npv_lo / 1000, hi: +r.npv_hi / 1000, share: +r.share }));
  const E = datasets.prospect_curve.map((r) => ({ pg: +r.pg, emv: +r.emv / 1000 }));
  const MN = datasets.money_notes;
  const pr = MN.prospect;
  const lad = rungs(datasets);
  let last = null;

  function price(g, width, H, state) {
    const narrow = isNarrow(width);
    const m = { l: 46, r: narrow ? 12 : 90, t: 24, b: 30 };
    const x = d3.scaleLinear().domain([20, 160]).range([m.l, width - m.r]);
    const all = [...G.values()].flat();
    const y = d3.scaleLinear().domain([d3.min(all, (r) => r.npv), d3.max(all, (r) => r.npv)]).nice().range([H - m.b, m.t]);
    g.append("rect").attr("x", x(pr.price.p90)).attr("width", x(pr.price.p10) - x(pr.price.p90)).attr("y", m.t).attr("height", H - m.b - m.t).attr("fill", ctx()).attr("opacity", 0.15);
    label(g, x(pr.price.p90) + 4, m.t + 10, "Brent 2005–24, P90 to P10", { size: 10 });
    styleAxis(g.append("g").attr("transform", `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(5).tickSize(-(width - m.l - m.r))).call((s) => s.select(".domain").remove()), { grid: true });
    styleAxis(g.append("g").attr("transform", `translate(0,${H - m.b})`).call(d3.axisBottom(x).ticks(7).tickSize(3)));
    label(g, 2, 10, "NPV, USD bn", { size: 10 });
    label(g, (m.l + width - m.r) / 2, H - 2, "flat oil price, USD per barrel (2025 money)", { anchor: "middle", size: 10.5 });
    g.append("line").attr("x1", m.l).attr("x2", width - m.r).attr("y1", y(0)).attr("y2", y(0)).attr("stroke", ink()).attr("stroke-width", 1);
    const col = { P90: c2(), P50: c1(), P10: hi() };
    for (const [v, rows] of G) {
      g.append("path").attr("d", d3.line().x((r) => x(r.p)).y((r) => y(r.npv))(rows)).attr("fill", "none").attr("stroke", col[v]).attr("stroke-width", 2);
      const end = rows[rows.length - 1];
      if (!narrow) label(g, width - m.r + 6, y(end.npv) + 4, `${v} volume`, { size: 11, weight: 600, fill: ink() });
      const be = pr.break_even_price[v.toLowerCase()];
      hover(g.append("circle").attr("cx", x(be)).attr("cy", y(0)).attr("r", 5).attr("fill", col[v]), () => `${v} volume breaks even at ${num(be, 0)} USD/bbl`);
    }
    if (state.volve) {
      const V = MN.volve.npv_pre;
      const pts = Object.entries(V).map(([p, n]) => ({ p: +p, npv: n / 1000 }));
      g.append("path").attr("d", d3.line().x((r) => x(r.p)).y((r) => y(r.npv))(pts)).attr("fill", "none").attr("stroke", ink()).attr("stroke-width", 2).attr("stroke-dasharray", "5 3");
      g.append("circle").attr("cx", x(MN.volve.be_pre_usd_bbl)).attr("cy", y(0)).attr("r", 5).attr("fill", ink());
      label(g, x(pts[pts.length - 1].p) + 4, y(pts[pts.length - 1].npv) - 6, "Volve", { size: 11, weight: 600, fill: ink() });
    }
    if (narrow) label(g, width - m.r, H - m.b - 6, "lines: P90, P50, P10 volume", { anchor: "end", size: 10 });
  }

  function spread(g, width, H) {
    const m = { l: 16, r: 16, t: 14, b: 30 };
    const x = d3.scaleLinear().domain([Math.min(0, d3.min(N, (b) => b.lo)), d3.quantile(N.map((b) => b.hi), 0.98)]).range([m.l, width - m.r]);
    const y = d3.scaleLinear().domain([0, d3.max(N, (b) => b.share)]).range([H - m.b, m.t + 20]);
    styleAxis(g.append("g").attr("transform", `translate(0,${H - m.b})`).call(d3.axisBottom(x).ticks(6).tickSize(3)));
    label(g, (m.l + width - m.r) / 2, H - 2, "pre-tax NPV if found, USD bn (2025 money)", { anchor: "middle", size: 10.5 });
    const bars = g.append("g").selectAll("rect").data(N.filter((b) => b.lo < x.domain()[1])).join("rect").attr("x", (b) => x(b.lo) + 1).attr("width", (b) => Math.max(1, x(Math.min(b.hi, x.domain()[1])) - x(b.lo) - 2))
      .attr("y", (b) => y(b.share)).attr("height", (b) => y(0) - y(b.share)).attr("rx", 2).attr("fill", c1());
    hover(bars, (b) => `${num(b.lo, 1)} to ${num(b.hi, 1)} USD bn: ${num(b.share * 100, 1)} % of draws`);
    [["P90", pr.npv_p90], ["P50", pr.npv_p50], ["P10", pr.npv_p10]].forEach(([k, v]) => {
      const px = x(v / 1000);
      g.append("line").attr("x1", px).attr("x2", px).attr("y1", m.t + 14).attr("y2", H - m.b).attr("stroke", hi()).attr("stroke-width", 1.5).attr("stroke-dasharray", "4 3");
      label(g, px, m.t + 10, `${k} ${num(v / 1000, 1)}`, { anchor: "middle", size: 11, weight: 600, fill: hi() });
    });
  }

  function chance(g, width, H) {
    const m = { l: 46, r: 16, t: 24, b: 30 };
    const x = d3.scaleLinear().domain([0, 1]).range([m.l, width - m.r]);
    const y = d3.scaleLinear().domain(d3.extent(E, (r) => r.emv)).nice().range([H - m.b, m.t]);
    styleAxis(g.append("g").attr("transform", `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(5).tickSize(-(width - m.l - m.r))).call((s) => s.select(".domain").remove()), { grid: true });
    styleAxis(g.append("g").attr("transform", `translate(0,${H - m.b})`).call(d3.axisBottom(x).ticks(5).tickFormat(d3.format(".0%")).tickSize(3)));
    label(g, 2, 10, "expected value of drilling, USD bn", { size: 10 });
    label(g, (m.l + width - m.r) / 2, H - 2, "chance the well finds a field that is developed", { anchor: "middle", size: 10.5 });
    g.append("line").attr("x1", m.l).attr("x2", width - m.r).attr("y1", y(0)).attr("y2", y(0)).attr("stroke", ink());
    g.append("path").attr("d", d3.line().x((r) => x(r.pg)).y((r) => y(r.emv))(E)).attr("fill", "none").attr("stroke", c1()).attr("stroke-width", 2);
    const b = MN.base_rate;
    [["commercial, 2000–14", b.pg_commercial, hi()], ["any discovery, since 2000", b.pg_technical, ctx()]].forEach(([lab, p, c], i) => {
      const e = p * pr.npv_mean / 1000 - (1 - p) * b.dry_hole_usd_mn / 1000;
      g.append("line").attr("x1", x(p)).attr("x2", x(p)).attr("y1", y(e)).attr("y2", H - m.b).attr("stroke", c).attr("stroke-dasharray", "4 3");
      hover(g.append("circle").attr("cx", x(p)).attr("cy", y(e)).attr("r", 5).attr("fill", c), () => `${lab}: ${num(p * 100, 0)} %<br>expected value ${num(e, 2)} USD bn`);
      label(g, x(p) + 7, y(e) + (i ? -8 : 14), `${lab}: ${num(p * 100, 0)} %`, { size: 11, weight: 600, fill: ink() });
    });
    label(g, x(0) + 4, y(-b.dry_hole_usd_mn / 1000) + 14, `a dry hole: −${num(b.dry_hole_usd_mn, 0)} USD million`, { size: 10.5, fill: muted() });
  }

  function draw(width, state = {}) {
    last = [width, state];
    const view = state.view || "price";
    const H = plotHeight(width, opts, { ratio: 0.6 });
    const { plot: g } = frame(el, width, H, lad, state.rung ?? null, "The prospect's value against price, its spread, and the value of drilling against chance");
    if (view === "price") price(g, width, H, state);
    else if (view === "spread") spread(g, width, H);
    else chance(g, width, H);
  }
  onSchemeChange(() => last && draw(...last));
  return { draw, repaint: () => last && draw(...last) };
}
