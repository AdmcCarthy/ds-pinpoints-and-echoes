// What Volve cost and what it gave: investment by year (real 2025 USD) and, below it, production by year.
// state: { both } adds the production panel; { rung } names the ladder rung (default none lit).
import { onSchemeChange } from "../runtime/js/subscout.js";
import { frame, plotHeight, rungs, styleAxis, label, num, c1, hi, ink, isNarrow, hover } from "./_common.js";

export default function volve(el, datasets, opts = {}) {
  const R = datasets.volve_money.map((r) => ({ y: +r.year, capex: +r.investment_usd_mn_real, oe: +r.oe_sm3 / 1e6 }));
  const lad = rungs(datasets);
  let last = null;
  function draw(width, state = {}) {
    last = [width, state];
    const H = plotHeight(width, opts, { ratio: 0.55 });
    const { plot: g } = frame(el, width, H, lad, state.rung, "Volve investment and production by year");
    const narrow = isNarrow(width);
    const m = { l: narrow ? 36 : 48, r: 10, t: 18, b: 22 };
    const both = !!state.both;
    const gap = 26;
    const h1 = both ? (H - m.t - m.b - gap) / 2 : H - m.t - m.b;
    const x = d3.scaleBand().domain(R.map((r) => r.y)).range([m.l, width - m.r]).padding(0.25);
    const panel = (y0, h, key, colour, title, unit) => {
      const y = d3.scaleLinear().domain([Math.min(0, d3.min(R, (r) => r[key])), d3.max(R, (r) => r[key]) * 1.12]).nice().range([y0 + h, y0]);
      styleAxis(g.append("g").attr("transform", `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(3).tickSize(-(width - m.l - m.r))).call((s) => s.select(".domain").remove()), { grid: true });
      const bars = g.append("g").selectAll("rect").data(R).join("rect").attr("x", (r) => x(r.y)).attr("width", x.bandwidth())
        .attr("y", (r) => y(Math.max(0, r[key]))).attr("height", (r) => Math.abs(y(r[key]) - y(0))).attr("rx", 2).attr("fill", colour);
      hover(bars, (r) => `${r.y}: ${num(r[key], key === "oe" ? 2 : 0)} ${unit}`);
      label(g, m.l, y0 - 6, `${title} (${unit})`, { size: 11, weight: 600, fill: ink() });
    };
    panel(m.t, h1, "capex", c1(), "Investment", "USD million, 2025 money");
    if (both) panel(m.t + h1 + gap, h1, "oe", hi(), "Production", "million Sm³ o.e.");
    const every = narrow ? 3 : 1;
    styleAxis(g.append("g").attr("transform", `translate(0,${H - m.b})`).call(d3.axisBottom(x).tickValues(R.map((r) => r.y).filter((v, i) => i % every === 0)).tickSize(0)));
    if (!both) {
      const total = d3.sum(R, (r) => r.capex);
      label(g, width - m.r, m.t + 12, `${num(total / 1000, 2)} billion USD in all`, { anchor: "end", size: 11, weight: 600, fill: c1() });
    }
  }
  onSchemeChange(() => last && draw(...last));
  return { draw, repaint: () => last && draw(...last) };
}
