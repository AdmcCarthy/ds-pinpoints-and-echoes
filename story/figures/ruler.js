// The wellbore and the distance to the next one on a logarithmic ruler, with the width of the area the wells span.
// state: { coin } rescales every length so that the wellbore is a 1 cm coin.
import { onSchemeChange } from "../runtime/js/subscout.js";
import { frame, plotHeight, rungs, styleAxis, fmtLen, ink, hi, ctx, isNarrow } from "./_common.js";

export default function ruler(el, datasets, opts = {}) {
  const geo = Object.fromEntries(datasets.geometry.map((r) => [r.key, +r.value]));
  const hole = geo.reservoir_hole_mm / 1000;
  const marks = [
    { row: 0, label: "wellbore", m: hole, strong: true },
    { row: 1, label: "nearest well, close case", m: geo.nn_p10_km * 1000 },
    { row: 2, label: "nearest well, typical", m: geo.nn_median_km * 1000, strong: true },
    { row: 3, label: "nearest well, far case", m: geo.nn_p90_km * 1000 },
    { row: 0, label: "width of the area", m: Math.sqrt(geo.hull_area_km2) * 1000, strong: true },
  ];
  const lad = rungs(datasets);
  let last = null;
  function draw(width, state = {}) {
    last = [width, state];
    const f = state.coin ? 0.01 / hole : 1;
    const H = Math.min(plotHeight(width, opts, { ratio: 0.4, max: 260 }), 240);
    const { plot: g } = frame(el, width, H, lad, state.rung ?? ["hole", "spacing"], "Logarithmic ruler from the wellbore to the area the wells span");
    const narrow = isNarrow(width);
    const m = { l: 12, r: 12, t: 16, b: 30 };
    const lo = Math.log10(hole * 0.5), top = Math.log10(Math.sqrt(geo.hull_area_km2) * 1000 * 2);
    const x = d3.scaleLinear().domain([lo, top]).range([m.l, width - m.r]);
    const ticks = d3.range(-2, 7).map((k) => 10 ** k).filter((d) => Math.log10(d / f) >= lo && Math.log10(d / f) <= top);
    styleAxis(g.append("g").attr("transform", `translate(0,${H - m.b})`).call(d3.axisBottom(x).tickValues(ticks.map((t) => Math.log10(t / f))).tickFormat((v) => fmtLen(10 ** v * f)).tickSize(4)));
    const rowH = (H - m.t - m.b - 10) / 4;
    marks.forEach((k) => {
      const px = x(Math.log10(k.m)), top = m.t + k.row * rowH;
      g.append("line").attr("x1", px).attr("x2", px).attr("y1", top + 6).attr("y2", H - m.b).attr("stroke", k.strong ? hi() : ctx()).attr("stroke-width", k.strong ? 2 : 1.2);
      const anchor = px > width - 130 ? "end" : px < 130 ? "start" : "middle";
      g.append("text").attr("x", px).attr("y", top).attr("text-anchor", anchor).attr("font-size", narrow ? 10.5 : 12).attr("font-weight", k.strong ? 600 : 400)
        .attr("fill", ink()).text(`${k.label}: ${fmtLen(k.m * f)}`);
    });
  }
  onSchemeChange(() => last && draw(...last));
  return { draw, repaint: () => last && draw(...last) };
}
