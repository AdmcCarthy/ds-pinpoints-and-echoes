// Every routine plug of 15/9-19 A and BT2: permeability (log) against porosity. state: { band } highlights the plugs
// between 19 and 21 % porosity and their range; { throat } colours every plug by its fitted R35; { mercury } adds the
// eleven mercury-injection samples as rings.
import { onSchemeChange } from "../runtime/js/subscout.js";
import { frame, plotHeight, rungs, styleAxis, label, sig, num, hi, ink, c1, isNarrow, hover, sequentialLog } from "./_common.js";

export default function plugs(el, datasets, opts = {}) {
  const P = datasets.plugs.map((r) => ({ k: +r.k_md, phi: +r.phi_pct, r35: +r.r35_um, well: r.well })).filter((p) => p.k > 0 && p.phi > 0);
  const M = datasets.micp_samples.map((r) => ({ k: +r.k_md, phi: +r.phi * 100 })).filter((p) => p.k > 0 && p.phi > 0);
  const lad = rungs(datasets);
  let last = null;
  function draw(width, state = {}) {
    last = [width, state];
    const H = plotHeight(width, opts, { ratio: 0.62 });
    const { plot: g } = frame(el, width, H, lad, state.rung ?? "plug", "Plug permeability against porosity");
    const narrow = isNarrow(width);
    const m = { l: narrow ? 44 : 54, r: 12, t: 10, b: 30 };
    const x = d3.scaleLinear().domain([0, 36]).range([m.l, width - m.r]);
    const y = d3.scaleLog().domain([0.005, 40000]).range([H - m.b, m.t]);
    styleAxis(g.append("g").attr("transform", `translate(0,${H - m.b})`).call(d3.axisBottom(x).ticks(6).tickFormat((d) => `${d} %`).tickSize(3)));
    styleAxis(g.append("g").attr("transform", `translate(${m.l},0)`).call(d3.axisLeft(y).tickValues([0.01, 0.1, 1, 10, 100, 1000, 10000]).tickFormat((d) => num(d, d < 1 ? 2 : 0)).tickSize(-(width - m.l - m.r))).call((s) => s.select(".domain").remove()), { grid: true });
    label(g, 2, m.t + 2, "mD", { size: 10 });
    label(g, (m.l + width - m.r) / 2, H - 2, "porosity (helium)", { anchor: "middle", size: 10 });
    const inBand = (p) => p.phi >= 19 && p.phi <= 21;
    const colour = state.throat ? sequentialLog([0.2, 40]) : null;
    if (state.band) g.append("rect").attr("x", x(19)).attr("width", x(21) - x(19)).attr("y", m.t).attr("height", H - m.b - m.t).attr("fill", hi()).attr("opacity", 0.12);
    const dots = g.append("g").selectAll("circle").data(P).join("circle").attr("cx", (p) => x(p.phi)).attr("cy", (p) => y(p.k)).attr("r", narrow ? 2.5 : 3)
      .attr("fill", (p) => (colour ? colour(Math.max(0.2, p.r35)) : state.band && inBand(p) ? hi() : c1()))
      .attr("opacity", (p) => (state.band && !colour && !inBand(p) ? 0.25 : 0.8));
    hover(dots, (p) => `${p.well}<br>${num(p.phi, 1)} % porosity, ${sig(p.k, 3)} mD${p.r35 > 0 ? `<br>fitted R35 ${sig(p.r35)} µm` : ""}`);
    if (state.band) {
      const b = P.filter(inBand), lo = d3.min(b, (p) => p.k), top = d3.max(b, (p) => p.k);
      g.append("line").attr("x1", x(21) + 6).attr("x2", x(21) + 6).attr("y1", y(lo)).attr("y2", y(top)).attr("stroke", hi()).attr("stroke-width", 2);
      label(g, x(21) + 12, y(Math.sqrt(lo * top)) + 4, `${num(lo, 0)} to ${num(top, 0)} mD at one porosity`, { size: 11, weight: 600, fill: hi() });
    }
    if (state.mercury) {
      g.append("g").selectAll("circle").data(M).join("circle").attr("cx", (p) => x(p.phi)).attr("cy", (p) => y(p.k)).attr("r", 6).attr("fill", "none").attr("stroke", ink()).attr("stroke-width", 1.6);
      label(g, width - m.r, H - m.b - 8, "○ mercury-injection samples", { anchor: "end", size: 10.5, fill: ink() });
    }
    if (colour) {
      const lx = narrow ? m.l + 6 : m.l + 12, ly = m.t + 8, lw = narrow ? 90 : 140;
      const stops = d3.range(0, 1.01, 0.1).map((t) => colour(0.2 * (40 / 0.2) ** t));
      const grad = g.append("defs").append("linearGradient").attr("id", "r35grad");
      stops.forEach((c, i) => grad.append("stop").attr("offset", `${i * 10}%`).attr("stop-color", c));
      g.append("rect").attr("x", lx).attr("y", ly).attr("width", lw).attr("height", 8).attr("fill", "url(#r35grad)");
      label(g, lx, ly + 20, "0.2 µm", { size: 9.5 });
      label(g, lx + lw, ly + 20, "40 µm", { anchor: "end", size: 9.5 });
      label(g, lx + lw + 6, ly + 8, "fitted throat radius, R35", { size: 10, fill: ink() });
    } else if (!state.band) {
      label(g, width - m.r, m.t + 10, `${num(P.length)} plugs; ${sig(d3.min(P, (p) => p.k))} to ${num(d3.max(P, (p) => p.k))} mD`, { anchor: "end", size: 11, weight: 600, fill: ink() });
    }
  }
  onSchemeChange(() => last && draw(...last));
  return { draw, repaint: () => last && draw(...last) };
}
