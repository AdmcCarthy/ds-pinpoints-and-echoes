// The ledger: for each rung of the story, the factor between the low and the high value it leaves open, on a logarithmic
// axis. The bars are not multiplied together: each rung's factor is measured in its own way (basis in the tooltip).
// state: { upto } shows the bars up to that key.
import { onSchemeChange } from "../runtime/js/subscout.js";
import { frame, rungs, styleAxis, label, num, c1, hi, ink, isNarrow, hover } from "./_common.js";

export default function ledger(el, datasets) {
  const R = datasets.ledger.map((r) => ({ ...r, factor: +r.factor, order: +r.order })).sort((a, b) => a.order - b.order);
  const lad = rungs(datasets);
  let last = null;
  function draw(width, state = {}) {
    last = [width, state];
    const narrow = isNarrow(width);
    const k = state.upto ? R.findIndex((r) => r.key === state.upto) : R.length - 1;
    const m = { l: narrow ? 8 : 230, r: 56, t: 6, b: 26 };
    const rowH = narrow ? 32 : 34, H = m.t + m.b + R.length * rowH;
    const { plot: g } = frame(el, width, H, lad, state.rung ?? "all", "The factor each rung leaves open, from the pore to the decision");
    const x = d3.scaleLog().domain([1, 400]).range([m.l, width - m.r]);
    styleAxis(g.append("g").attr("transform", `translate(0,${H - m.b})`).call(d3.axisBottom(x).tickValues([1, 2, 5, 10, 30, 100, 300]).tickFormat((d) => `×${d}`).tickSize(3)));
    R.forEach((r, i) => {
      const y = m.t + i * rowH, on = i <= k;
      const row = g.append("g").attr("opacity", on ? 1 : 0.12);
      row.append("text").attr("x", narrow ? m.l : m.l - 8).attr("y", narrow ? y + 10 : y + rowH / 2 + 4).attr("text-anchor", narrow ? "start" : "end")
        .attr("font-size", narrow ? 11 : 12).attr("fill", ink()).text(r.label);
      const by = narrow ? y + 14 : y + rowH / 2 - 7, bh = narrow ? 12 : 14;
      row.append("rect").attr("x", x(1)).attr("y", by).attr("width", Math.max(2, x(r.factor) - x(1))).attr("height", bh).attr("rx", 3).attr("fill", i === k ? hi() : c1());
      row.append("text").attr("x", x(r.factor) + 6).attr("y", by + bh - 2).attr("font-size", 11.5).attr("font-weight", 600).attr("fill", ink()).text(`×${num(r.factor, r.factor < 10 ? 1 : 0)}`);
      hover(row, () => `${r.label}: ×${num(r.factor, 1)}<br>${r.basis}<br>${r.confidence}`);
    });
  }
  onSchemeChange(() => last && draw(...last));
  return { draw, repaint: () => last && draw(...last) };
}
