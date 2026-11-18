// Closure area against depth for the Volve high on the Hugin top, with the 2005 plan's contact cases.
// Depth points down; area grows to the right. state: { cases } draws the P90 / P50 / P10 contacts.
import { onSchemeChange } from "../runtime/js/subscout.js";
import { frame, plotHeight, rungs, styleAxis, label, c1, hi, isNarrow } from "./_common.js";

export default function closure(el, datasets, opts = {}) {
  const C = datasets.closure.map((r) => ({ z: +r.depth_m, a: +r.area_km2 })).sort((p, q) => p.z - q.z);
  const Q = datasets.field_notes.closure; // the plan's P90, P50 and P10 contacts as kit-surfaces digitised them
  const at = (p) => Q[`P${p}`];
  const lad = rungs(datasets);
  let last = null;
  function draw(width, state = {}) {
    last = [width, state];
    const narrow = isNarrow(width);
    const H = plotHeight(width, opts, { ratio: 0.65 });
    const { plot: g } = frame(el, width, H, lad, state.rung ?? "field", "Closure area against depth with the plan's contact cases");
    const m = { l: 48, r: narrow ? 12 : 24, t: 14, b: 32 };
    const cases = [{ name: "P90 (low)", z: at(90) }, { name: "P50", z: at(50) }, { name: "P10 (high)", z: at(10) }];
    const zmax = Math.max(d3.max(C, (p) => p.z), state.cases ? d3.max(cases, (c) => c.z) + 10 : 0);
    const y = d3.scaleLinear().domain([C[0].z - 10, zmax + 10]).range([m.t, H - m.b]);
    const x = d3.scaleLinear().domain([0, d3.max(C, (p) => p.a) * 1.05]).range([m.l, width - m.r]);
    styleAxis(g.append("g").attr("transform", `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(6).tickSize(-(width - m.l - m.r))).call((s) => s.select(".domain").remove()), { grid: true });
    styleAxis(g.append("g").attr("transform", `translate(0,${H - m.b})`).call(d3.axisBottom(x).ticks(5).tickSize(3)));
    label(g, 2, 10, "m below MSL", { size: 10 });
    label(g, (m.l + width - m.r) / 2, H - 2, "area inside the closing contour, km²", { anchor: "middle", size: 10.5 });
    g.append("path").attr("d", d3.area().x0(m.l).x1((p) => x(p.a)).y((p) => y(p.z)).curve(d3.curveStepAfter)(C)).attr("fill", c1()).attr("opacity", 0.18);
    g.append("path").attr("d", d3.line().x((p) => x(p.a)).y((p) => y(p.z)).curve(d3.curveStepAfter)(C)).attr("fill", "none").attr("stroke", c1()).attr("stroke-width", 2);
    const zEnd = C[C.length - 1].z;
    label(g, x(C[C.length - 1].a) - 4, y(zEnd) + 14, "surface not mapped deeper", { anchor: "end", size: 10 });
    if (!state.cases) return;
    cases.forEach((c, i) => {
      const a = c.z <= zEnd ? C.filter((p) => p.z <= c.z).slice(-1)[0]?.a : null;
      g.append("line").attr("x1", m.l).attr("x2", width - m.r).attr("y1", y(c.z)).attr("y2", y(c.z)).attr("stroke", hi()).attr("stroke-width", i === 1 ? 2 : 1.2).attr("stroke-dasharray", i === 1 ? null : "4 3");
      label(g, width - m.r - 4, y(c.z) - 4, `contact ${c.name}: ${c.z} m${a != null ? `, ${a.toFixed(1)} km²` : ", beyond the mapped surface"}`, { anchor: "end", size: 11, weight: i === 1 ? 600 : 400, fill: hi() });
      if (a != null) g.append("circle").attr("cx", x(a)).attr("cy", y(c.z)).attr("r", 4.5).attr("fill", hi());
    });
  }
  onSchemeChange(() => last && draw(...last));
  return { draw, repaint: () => last && draw(...last) };
}
