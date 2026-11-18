// The whole scale ladder at full size: every rung from the pore throat to the North Sea on one logarithmic axis.
// state: { upto } lights the rungs up to and including that key ("all" for every rung).
import { onSchemeChange } from "../runtime/js/subscout.js";
import { frame, plotHeight, styleAxis, label, fmtLen, ink, muted, ctx, hi, isNarrow } from "./_common.js";

export default function ladderFig(el, datasets, opts = {}) {
  const R = datasets.ladder.map((r) => ({ ...r, m: +r.m, order: +r.order })).sort((a, b) => a.order - b.order);
  let last = null;
  function draw(width, state = {}) {
    last = [width, state];
    const narrow = isNarrow(width);
    const H = plotHeight(width, opts, { ratio: 0.5, max: 420 });
    const { plot: g } = frame(el, width, H, null, null, "Logarithmic ruler from a pore throat to the North Sea");
    const upto = state.upto ?? "all";
    const k = upto === "all" ? R.length - 1 : R.findIndex((r) => r.key === upto);
    const m = { l: 10, r: 10, t: 8, b: 26 };
    const x = d3.scaleLog().domain([5e-7, 2e6]).range([m.l, width - m.r]);
    styleAxis(g.append("g").attr("transform", `translate(0,${H - m.b})`)
      .call(d3.axisBottom(x).tickValues([1e-6, 1e-3, 1, 1e3, 1e6].concat(narrow ? [] : [1e-5, 1e-4, 1e-2, 1e-1, 10, 100, 1e4, 1e5])).tickFormat(fmtLen).tickSize(4)));
    const rowH = (H - m.t - m.b - 6) / R.length;
    R.forEach((r, i) => {
      const on = i <= k, px = x(r.m), y = m.t + i * rowH + rowH * 0.6;
      g.append("line").attr("x1", px).attr("x2", px).attr("y1", y).attr("y2", H - m.b).attr("stroke", on ? hi() : ctx()).attr("stroke-width", on ? 1.4 : 0.8).attr("opacity", on ? 0.9 : 0.4);
      g.append("circle").attr("cx", px).attr("cy", y).attr("r", on ? 4.5 : 3).attr("fill", on ? hi() : ctx());
      const right = px < width * 0.6;
      label(g, px + (right ? 8 : -8), y + 4, `${r.label}, ${fmtLen(r.m)}`, { anchor: right ? "start" : "end", size: narrow ? 10 : 11.5,
        weight: on && i === k ? 600 : 400, fill: on ? ink() : muted() });
    });
  }
  onSchemeChange(() => last && draw(...last));
  return { draw, repaint: () => last && draw(...last) };
}
