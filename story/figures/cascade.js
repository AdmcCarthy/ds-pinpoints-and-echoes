// Compounding: the spread of recoverable oil as uncertain factors are added one at a time. One row per step, each a
// histogram of the same draws on a shared logarithmic axis, with its P90 to P10 range and the factor between them.
// state: { upto } shows the rows up to that step number; { volve } marks Volve's produced oil.
import { onSchemeChange } from "../runtime/js/subscout.js";
import { frame, plotHeight, rungs, styleAxis, label, num, c1, hi, ink, muted, isNarrow, hover } from "./_common.js";

export default function cascade(el, datasets, opts = {}) {
  const S = datasets.cascade.map((r) => ({ step: +r.step, key: r.key, label: r.label, p90: +r.p90, p50: +r.p50, p10: +r.p10, ratio: +r.ratio }));
  const Hs = d3.group(datasets.cascade_hist.map((r) => ({ step: +r.step, lo: +r.log10_lo, hi: +r.log10_hi, share: +r.share })), (r) => r.step);
  const volveOil = datasets.test_notes?.volve?.produced_oil_mn_sm3;
  const lad = rungs(datasets);
  let last = null;
  function draw(width, state = {}) {
    last = [width, state];
    const upto = state.upto ?? S.length - 1;
    const narrow = isNarrow(width);
    const H = plotHeight(width, opts, { ratio: 0.7 });
    const { plot: g } = frame(el, width, H, lad, state.rung ?? "field", "Spread of recoverable oil as each uncertain factor is added");
    const m = { l: narrow ? 74 : 230, r: narrow ? 44 : 70, t: 6, b: 28 };
    const SHORT = { rock_volume: "rock volume", ntg: "+ net share", porosity: "+ porosity", hc_saturation: "+ oil sat.", bo: "+ Bo", recovery: "+ recovery", correlated: "linked" };
    const x = d3.scaleLog().domain([1, 120]).range([m.l, width - m.r]);
    styleAxis(g.append("g").attr("transform", `translate(0,${H - m.b})`).call(d3.axisBottom(x).tickValues([1, 3, 10, 30, 100]).tickFormat((d) => `${d}`).tickSize(3)));
    label(g, width - m.r, H - 2, "recoverable oil, million Sm³ (log)", { anchor: "end", size: 10 });
    const rowH = (H - m.t - m.b) / S.length;
    const ymax = d3.max(datasets.cascade_hist, (r) => +r.share);
    S.forEach((s, i) => {
      const shown = s.step <= upto;
      const y0 = m.t + i * rowH, base = y0 + rowH * (narrow ? 0.45 : 0.7);
      const row = g.append("g").attr("opacity", shown ? 1 : 0.1);
      const colour = s.key === "correlated" ? hi() : c1();
      const bins = Hs.get(s.step) || [];
      const yy = d3.scaleLinear().domain([0, ymax]).range([base, y0 + (narrow ? 12 : 3)]);
      if (!narrow) row.append("path").attr("d", d3.area().x((b) => x(10 ** ((b.lo + b.hi) / 2))).y0(base).y1((b) => yy(b.share)).curve(d3.curveBasis)(bins.filter((b) => 10 ** b.hi >= 1 && 10 ** b.lo <= 120)))
        .attr("fill", colour).attr("opacity", 0.35);
      row.append("line").attr("x1", x(s.p90)).attr("x2", x(s.p10)).attr("y1", base + 4).attr("y2", base + 4).attr("stroke", colour).attr("stroke-width", 3).attr("stroke-linecap", "round");
      row.append("circle").attr("cx", x(s.p50)).attr("cy", base + 4).attr("r", 4).attr("fill", colour);
      const lab = narrow ? SHORT[s.key] ?? s.label : s.step === 0 || s.key === "correlated" ? s.label : `+ ${s.label}`;
      row.append("text").attr("x", m.l - 8).attr("y", base + 8).attr("text-anchor", "end")
        .attr("font-size", narrow ? 10.5 : 11.5).attr("font-weight", s.key === "correlated" ? 600 : 400).attr("fill", ink()).text(lab);
      row.append("text").attr("x", width - m.r + 8).attr("y", base + 8).attr("font-size", 11.5).attr("font-weight", 600).attr("fill", colour).text(`×${num(s.ratio, 1)}`);
      hover(row, () => `${s.label}<br>P90 ${num(s.p90, 1)}, P50 ${num(s.p50, 1)}, P10 ${num(s.p10, 1)} million Sm³<br>P10 is ${num(s.ratio, 1)} times P90`);
    });
    if (!narrow) label(g, width - m.r + 8, m.t + 9, "P10 / P90", { size: 9.5, fill: muted() });
    if (state.volve && volveOil) {
      g.append("line").attr("x1", x(volveOil)).attr("x2", x(volveOil)).attr("y1", m.t).attr("y2", H - m.b).attr("stroke", ink()).attr("stroke-width", 1.5).attr("stroke-dasharray", "5 3");
      label(g, x(volveOil) + 5, m.t + 10, `Volve produced ${num(volveOil, 1)}`, { size: 11, weight: 600, fill: ink() });
    }
  }
  onSchemeChange(() => last && draw(...last));
  return { draw, repaint: () => last && draw(...last) };
}
