// Core against log: the permeability a plug measured beside the permeability the petrophysical interpretation gives at the
// same depth, both on log axes, with the line of agreement. The interpretation is calibrated to the core, so this is a
// consistency check. Points at the interpretation's 0.1 mD floor are drawn hollow.
import { onSchemeChange } from "../runtime/js/subscout.js";
import { frame, plotHeight, rungs, styleAxis, label, num, sig, c1, c2, ink, ctx, muted, isNarrow, hover } from "./_common.js";

export default function corelog(el, datasets, opts = {}) {
  const P = datasets.core_log_pairs.map((r) => ({ well: r.well_name, core: +r.k_core_md, log: +r.k_log_md, floor: String(r.k_log_at_floor) === "true" }))
    .filter((p) => p.core > 0 && p.log > 0);
  const wells = [...new Set(P.map((p) => p.well))];
  const lad = rungs(datasets);
  let last = null;
  function draw(width, state = {}) {
    last = [width, state];
    const H = plotHeight(width, opts, { ratio: 0.7 });
    const { plot: g } = frame(el, width, H, lad, state.rung ?? "log", "Core permeability against interpreted log permeability");
    const narrow = isNarrow(width);
    const side = Math.min(width - 60, H - 40);
    const m = { l: narrow ? 44 : Math.max(54, (width - side) / 2), t: 10, b: 30 };
    const x = d3.scaleLog().domain([0.005, 40000]).range([m.l, m.l + side]);
    const y = d3.scaleLog().domain([0.005, 40000]).range([H - m.b, H - m.b - side]);
    const ticks = [0.01, 1, 100, 10000];
    styleAxis(g.append("g").attr("transform", `translate(0,${H - m.b})`).call(d3.axisBottom(x).tickValues(ticks).tickFormat((d) => num(d, d < 1 ? 2 : 0)).tickSize(3)));
    styleAxis(g.append("g").attr("transform", `translate(${m.l},0)`).call(d3.axisLeft(y).tickValues(ticks).tickFormat((d) => num(d, d < 1 ? 2 : 0)).tickSize(3)));
    label(g, m.l + side / 2, H - 2, "plug (core), mD", { anchor: "middle", size: 10 });
    label(g, m.l - 4, H - m.b - side - 2, "log, mD", { anchor: "end", size: 10 });
    g.append("line").attr("x1", x(0.005)).attr("y1", y(0.005)).attr("x2", x(40000)).attr("y2", y(40000)).attr("stroke", ctx()).attr("stroke-dasharray", "4 3");
    label(g, x(8000), y(8000) - 6, "agreement", { anchor: "end", size: 10, fill: muted() });
    const col = (w) => (w === wells[0] ? c1() : c2());
    const dots = g.append("g").selectAll("circle").data(P).join("circle").attr("cx", (p) => x(p.core)).attr("cy", (p) => y(p.log)).attr("r", 2.8)
      .attr("fill", (p) => (p.floor ? "none" : col(p.well))).attr("stroke", (p) => col(p.well)).attr("stroke-width", 1).attr("opacity", 0.75);
    hover(dots, (p) => `${p.well}<br>plug ${sig(p.core, 3)} mD, log ${sig(p.log, 3)} mD`);
    wells.forEach((w, i) => {
      g.append("circle").attr("cx", m.l + 10).attr("cy", m.t + 8 + i * 15).attr("r", 4).attr("fill", col(w));
      label(g, m.l + 18, m.t + 12 + i * 15, w, { size: 10.5, fill: ink() });
    });
  }
  onSchemeChange(() => last && draw(...last));
  return { draw, repaint: () => last && draw(...last) };
}
