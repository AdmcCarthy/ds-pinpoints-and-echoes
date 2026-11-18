// The pore. view "tubes": a sketch of sand grains with the throats between them, and two tubes whose radii differ by
// two, carrying flows that differ by sixteen (Hagen–Poiseuille; a diagram, not data). view "curves": the eleven
// mercury-injection curves of 15/9-19 A, mercury saturation against the throat radius it has entered.
// view "r35": the same with the radius at 35 % saturation marked on each curve.
import { onSchemeChange } from "../runtime/js/subscout.js";
import { frame, plotHeight, rungs, styleAxis, label, sig, c1, c2, hi, ink, muted, ctx, isNarrow } from "./_common.js";

export default function pore(el, datasets, opts = {}) {
  const curves = d3.group(datasets.micp.map((r) => ({ d: +r.depth_m, r: +r.pore_radius_um, s: +r.hg_sat_frac })), (p) => p.d);
  const S = datasets.micp_samples.map((r) => ({ d: +r.depth_m, r35: +r.r35_um, k: +r.k_md }));
  const lad = rungs(datasets);
  let last = null;

  function tubes(g, x0, x1, H) {
    const w = x1 - x0, cy = H * 0.5, r = Math.min(H * 0.16, w * 0.12);
    const rows = [{ y: cy - r * 1.6, rad: r, flow: 1, lab: "radius r: flow 1" }, { y: cy + r * 1.6, rad: r / 2, flow: 1 / 16, lab: "radius r/2: flow 1/16" }];
    for (const t of rows) {
      g.append("rect").attr("x", x0).attr("y", t.y - t.rad).attr("width", w * 0.55).attr("height", 2 * t.rad).attr("rx", t.rad * 0.2).attr("fill", "none").attr("stroke", ink()).attr("stroke-width", 1.4);
      g.append("rect").attr("x", x0 + 2).attr("y", t.y - t.rad + 2).attr("width", (w * 0.55 - 4) * Math.max(t.flow, 0.04)).attr("height", 2 * t.rad - 4).attr("fill", c1()).attr("opacity", 0.55);
      label(g, x0 + w * 0.58, t.y + 4, t.lab, { size: 11, weight: 600, fill: ink() });
    }
    label(g, x0, H - 4, w < 420 ? "flow grows as the radius to the fourth power" : "flow through a tube grows as the radius to the fourth power", { size: 10 });
  }

  function grains(g, x0, x1, H) {
    const bottom = H - 20; // room for the caption
    const R = Math.min((x1 - x0) / 9, (bottom - 8) / 9);
    const pts = [];
    for (let j = 0; j < 9; j++) for (let i = 0; i < 9; i++) pts.push([x0 + R + i * 2.05 * R + (j % 2) * R, 4 + R + j * 1.8 * R]);
    const inside = pts.filter((p) => p[0] + R * 0.93 <= x1 && p[1] + R * 0.93 <= bottom);
    g.append("rect").attr("x", x0).attr("y", 4).attr("width", x1 - x0).attr("height", bottom - 4).attr("fill", c2()).attr("opacity", 0.18);
    g.selectAll("circle.grain").data(inside).join("circle").attr("class", "grain").attr("cx", (p) => p[0]).attr("cy", (p) => p[1]).attr("r", R * 0.93)
      .attr("fill", ctx()).attr("opacity", 0.75);
    const p = inside[Math.min(10, inside.length - 1)], q = inside[Math.min(11, inside.length - 1)];
    const mx = (p[0] + q[0]) / 2, my = (p[1] + q[1]) / 2;
    g.append("circle").attr("cx", mx).attr("cy", my).attr("r", R * 0.35).attr("fill", "none").attr("stroke", hi()).attr("stroke-width", 2);
    label(g, x0, H - 4, "sand grains (grey) and the pore space between them (blue); the ring marks a throat", { size: 10 });
  }

  function draw(width, state = {}) {
    last = [width, state];
    const view = state.view || "tubes";
    const H = plotHeight(width, opts, { ratio: 0.55 });
    const { plot: g } = frame(el, width, H, lad, state.rung ?? "throat", "Pore throats: a sketch, then the mercury-injection curves");
    const narrow = isNarrow(width);
    if (view === "tubes") {
      if (narrow) tubes(g, 8, width - 8, H);
      else { grains(g, 8, width * 0.46, H); tubes(g, width * 0.52, width - 8, H); }
      return;
    }
    const m = { l: 40, r: 12, t: 10, b: 30 };
    const x = d3.scaleLog().domain([300, 0.02]).range([m.l, width - m.r]);
    const y = d3.scaleLinear().domain([0, 1]).range([H - m.b, m.t]);
    styleAxis(g.append("g").attr("transform", `translate(0,${H - m.b})`).call(d3.axisBottom(x).tickValues([100, 10, 1, 0.1]).tickFormat((d) => `${d} µm`).tickSize(3)));
    styleAxis(g.append("g").attr("transform", `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(4).tickFormat(d3.format(".0%")).tickSize(-(width - m.l - m.r))).call((s) => s.select(".domain").remove()), { grid: true });
    label(g, (m.l + width - m.r) / 2, H - 2, "pore-throat radius the mercury has entered (larger to the left)", { anchor: "middle", size: 10 });
    for (const [, pts] of curves) {
      const p = pts.filter((q) => q.r > 0).sort((a, b) => b.r - a.r);
      g.append("path").attr("d", d3.line().x((q) => x(q.r)).y((q) => y(Math.min(1, Math.max(0, q.s))))(p)).attr("fill", "none").attr("stroke", c1()).attr("stroke-width", 1.3).attr("opacity", 0.8);
    }
    if (view === "r35") {
      g.append("line").attr("x1", m.l).attr("x2", width - m.r).attr("y1", y(0.35)).attr("y2", y(0.35)).attr("stroke", hi()).attr("stroke-dasharray", "4 3");
      g.selectAll("circle.r35").data(S.filter((s) => s.r35 > 0)).join("circle").attr("class", "r35").attr("cx", (s) => x(s.r35)).attr("cy", y(0.35)).attr("r", 4).attr("fill", hi());
      const lo = d3.min(S, (s) => s.r35), hiR = d3.max(S, (s) => s.r35);
      label(g, width - m.r, y(0.35) - 8, `R35, the radius at 35 % mercury: ${sig(lo)} to ${sig(hiR)} µm`, { anchor: "end", size: 11, weight: 600, fill: hi() });
    } else {
      label(g, width - m.r, m.t + 10, `${curves.size} samples, 15/9-19 A`, { anchor: "end", size: 11, fill: muted() });
    }
  }
  onSchemeChange(() => last && draw(...last));
  return { draw, repaint: () => last && draw(...last) };
}
