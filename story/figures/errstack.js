// A chain of vertical errors at the target, one row per link, then the combined spread. Solid bar: typical value.
// Lighter extension: largest value on file. state: { upto } reveals the links one at a time.
import { onSchemeChange } from "../runtime/js/subscout.js";
import { frame, rungs, styleAxis, c1, hi, ink, isNarrow, hover } from "./_common.js";

export default function errstack(el, datasets) {
  const rows = datasets.stack.map((r) => ({ ...r, typical: +r.typical, worst: +r.worst, cum_typical: +r.cum_typical, cum_worst: +r.cum_worst }));
  const end = rows[rows.length - 1];
  const all = [...rows, { link: "Combined at the target", typical: end.cum_typical, worst: end.cum_worst, total: true }];
  const lad = rungs(datasets);
  const fmt = (v) => (v < 10 ? v.toFixed(1) : Math.round(v).toString());
  let last = null;
  function draw(width, state = {}) {
    last = [width, state];
    const upto = state.upto ?? all.length;
    const narrow = isNarrow(width);
    const m = { l: narrow ? 8 : 200, r: 64, t: 6, b: 26 };
    const rowH = narrow ? 34 : 36, H = m.t + m.b + all.length * rowH;
    const { plot: g } = frame(el, width, H, lad, state.rung ?? "hole", "Bar chart of vertical errors by link, with their combined spread");
    const x = d3.scaleLinear().domain([0, d3.max(all, (r) => r.worst) * 1.05]).range([m.l, width - m.r]);
    styleAxis(g.append("g").attr("transform", `translate(0,${H - m.b})`).call(d3.axisBottom(x).ticks(5).tickSize(4).tickFormat((d) => `${d} m`)));
    all.forEach((r, i) => {
      const shown = r.total ? upto >= all.length : i < upto;
      const y = m.t + i * rowH, colour = r.total ? hi() : c1();
      const row = g.append("g").attr("opacity", shown ? 1 : 0.12);
      row.append("text").attr("x", narrow ? m.l : m.l - 8).attr("y", narrow ? y + 10 : y + rowH / 2 + 4).attr("text-anchor", narrow ? "start" : "end")
        .attr("font-size", narrow ? 11 : 12).attr("font-weight", r.total ? 600 : 400).attr("fill", ink()).text(r.link);
      const by = narrow ? y + 15 : y + rowH / 2 - 8, bh = narrow ? 13 : 16;
      row.append("rect").attr("x", x(0)).attr("y", by).attr("height", bh).attr("width", Math.max(1, x(r.worst) - x(0))).attr("rx", 3).attr("fill", colour).attr("opacity", 0.3);
      row.append("rect").attr("x", x(0)).attr("y", by).attr("height", bh).attr("width", Math.max(1.5, x(r.typical) - x(0))).attr("rx", 3).attr("fill", colour);
      row.append("text").attr("x", x(r.worst) + 6).attr("y", by + bh - 3).attr("font-size", 11).attr("fill", ink()).text(`${fmt(r.typical)} | ${fmt(r.worst)} m`);
      hover(row, () => `${r.link}<br>typical ${fmt(r.typical)} m, largest on file ${fmt(r.worst)} m`);
    });
  }
  onSchemeChange(() => last && draw(...last));
  return { draw, repaint: () => last && draw(...last) };
}
