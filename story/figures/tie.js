// The well tie: the synthetic seismogram made from the log beside the real trace at the well, in time.
// state: { shifted } shows the synthetic after the single bulk shift reported in the ledger.
import { onSchemeChange } from "../runtime/js/subscout.js";
import { frame, plotHeight, rungs, styleAxis, label, c1, hi, ink, ctx } from "./_common.js";

export default function tie(el, datasets, opts = {}) {
  const T = datasets.tie.map((r) => ({ t: +r.t_ms, real: +r.real, syn: +r.synthetic, shf: +r.synthetic_shifted }));
  const lad = rungs(datasets);
  let last = null;
  function wiggle(g, x0, pts, key, colour, y, scale) {
    const area = d3.area().x0(x0).x1((p) => x0 + Math.max(0, p[key]) * scale).y((p) => y(p.t)).curve(d3.curveMonotoneY);
    g.append("path").attr("d", area(pts)).attr("fill", colour).attr("opacity", 0.45);
    g.append("path").attr("d", d3.line().x((p) => x0 + p[key] * scale).y((p) => y(p.t)).curve(d3.curveMonotoneY)(pts)).attr("fill", "none").attr("stroke", colour).attr("stroke-width", 1.2);
  }
  function draw(width, state = {}) {
    last = [width, state];
    const H = plotHeight(width, opts, { ratio: 0.75 });
    const { plot: g } = frame(el, width, H, lad, state.rung ?? "bed", "Synthetic seismogram from the log beside the real trace at the well");
    const m = { l: 44, r: 8, t: 26, b: 6 };
    const tdom = [2300, 3100];
    const y = d3.scaleLinear().domain(tdom).range([m.t, H - m.b]);
    styleAxis(g.append("g").attr("transform", `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(8).tickSize(-(width - m.l - m.r))).call((s) => s.select(".domain").remove()), { grid: true });
    label(g, 2, 10, "ms TWT", { size: 10 });
    const pts = T.filter((p) => p.t >= tdom[0] && p.t <= tdom[1]);
    const amax = d3.max(pts, (p) => Math.max(Math.abs(p.real), Math.abs(p.syn))) || 1;
    const lanes = [
      { key: state.shifted ? "shf" : "syn", label: state.shifted ? "synthetic from the log, shifted" : "synthetic from the log", colour: c1() },
      { key: "real", label: "real trace at the well", colour: hi() },
    ];
    const laneW = (width - m.l - m.r) / lanes.length;
    lanes.forEach((L, i) => {
      const x0 = m.l + laneW * (i + 0.5);
      g.append("line").attr("x1", x0).attr("x2", x0).attr("y1", m.t).attr("y2", H - m.b).attr("stroke", ctx()).attr("opacity", 0.6);
      wiggle(g, x0, pts, L.key, L.colour, y, (laneW * 0.42) / amax);
      label(g, x0, m.t - 10, L.label, { anchor: "middle", size: 11, weight: 600, fill: ink() });
    });
  }
  onSchemeChange(() => last && draw(...last));
  return { draw, repaint: () => last && draw(...last) };
}
