// Two published versions of one horizon along a line between well picks, in two-way time.
// state: { stage } 1 = well picks only, 2 = + base survey, 3 = + reprocessed survey and the gap.
import { onSchemeChange } from "../runtime/js/subscout.js";
import { frame, plotHeight, rungs, styleAxis, label, c1, hi, ink, hover } from "./_common.js";

export default function transect(el, datasets, opts = {}) {
  const T = datasets.transect.map((r) => ({ d: +r.dist_m, a: +r.twt_base_ms, b: +r.twt_reprocessed_ms }));
  const P = datasets.picks.map((r) => ({ d: +r.dist_m, t: +r.pick_twt_ms, well: r.well }));
  const lad = rungs(datasets);
  let last = null;
  function draw(width, state = {}) {
    last = [width, state];
    const stage = state.stage ?? 3;
    const H = plotHeight(width, opts, { ratio: 0.55, max: 480 });
    const { plot: g } = frame(el, width, H, lad, state.rung ?? "field", "Two-way time of one horizon along a line, two published versions and the well picks");
    const m = { l: 44, r: 12, t: 12, b: 30 };
    const all = [...T.flatMap((r) => [r.a, r.b]), ...P.map((p) => p.t)];
    const x = d3.scaleLinear().domain([0, d3.max(T, (r) => r.d)]).range([m.l, width - m.r]);
    const y = d3.scaleLinear().domain([d3.min(all) - 6, d3.max(all) + 6]).range([m.t, H - m.b]);
    styleAxis(g.append("g").attr("transform", `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(4).tickSize(-(width - m.l - m.r))).call((s) => s.select(".domain").remove()), { grid: true });
    styleAxis(g.append("g").attr("transform", `translate(0,${H - m.b})`).call(d3.axisBottom(x).ticks(5).tickFormat((d) => `${d / 1000} km`)));
    label(g, 4, m.t + 8, "ms TWT", { size: 10 });
    if (stage >= 3) g.append("path").attr("fill", hi()).attr("opacity", 0.18).attr("d", d3.area().x((r) => x(r.d)).y0((r) => y(r.a)).y1((r) => y(r.b))(T));
    const line = (k) => d3.line().x((r) => x(r.d)).y((r) => y(r[k]))(T);
    if (stage >= 2) g.append("path").attr("d", line("a")).attr("fill", "none").attr("stroke", c1()).attr("stroke-width", 2);
    if (stage >= 3) g.append("path").attr("d", line("b")).attr("fill", "none").attr("stroke", hi()).attr("stroke-width", 2);
    const w = T.reduce((p, r) => (Math.abs(r.a - r.b) > Math.abs(p.a - p.b) ? r : p));
    const aUp = w.a < w.b;
    const lab = (txt, c, tv, up) => label(g, x(w.d), y(tv) + (up ? -8 : 17), txt, { anchor: w.d > T[T.length - 1].d * 0.8 ? "end" : "middle", size: 12, weight: 600, fill: c });
    if (stage >= 2) lab("base survey", c1(), w.a, aUp);
    if (stage >= 3) lab("reprocessed survey", hi(), w.b, !aUp);
    hover(g.selectAll("circle.pick").data(P).join("circle").attr("class", "pick").attr("cx", (p) => x(p.d)).attr("cy", (p) => y(p.t)).attr("r", 5)
      .attr("fill", "none").attr("stroke", ink()).attr("stroke-width", 1.75), (p) => `${p.well}: ${p.t.toFixed(0)} ms`);
    label(g, width - m.r, m.t + 8, "○ well picks within 150 m of the line", { anchor: "end", size: 11 });
  }
  onSchemeChange(() => last && draw(...last));
  return { draw, repaint: () => last && draw(...last) };
}
