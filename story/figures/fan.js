// Time against depth from every Volve check-shot table. One time, several depths: the fan.
// state: { at } the two-way time at which the depths are read off (ms); { zoom } narrows to it.
import { onSchemeChange, token } from "../runtime/js/subscout.js";
import { frame, plotHeight, rungs, styleAxis, label, hi, ink, isNarrow } from "./_common.js";

export default function fan(el, datasets, opts = {}) {
  const R = datasets.timedepth.map((r) => ({ table: r.table, t: +r.twt_ms, z: +r.tvdss_m }));
  const byT = d3.group(R, (r) => r.table);
  const lad = rungs(datasets);
  let last = null;
  function draw(width, state = {}) {
    last = [width, state];
    const at = state.at ?? 2650;
    const narrow = isNarrow(width);
    const H = plotHeight(width, opts, { ratio: 0.7 });
    const { plot: g } = frame(el, width, H, lad, state.rung ?? "bed", "Two-way time against depth for every Volve check-shot table");
    const m = { l: 48, r: narrow ? 10 : 170, t: 14, b: 30 };
    const tdom = state.zoom ? [at - 150, at + 150] : [0, d3.max(R, (r) => r.t)];
    const rows = R.filter((r) => r.t >= tdom[0] && r.t <= tdom[1]);
    const zdom = state.zoom ? d3.extent(rows, (r) => r.z) : [0, d3.max(R, (r) => r.z)];
    const x = d3.scaleLinear().domain(tdom).range([m.l, width - m.r]);
    const y = d3.scaleLinear().domain(zdom).range([m.t, H - m.b]);
    styleAxis(g.append("g").attr("transform", `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(6).tickSize(-(width - m.l - m.r))).call((s) => s.select(".domain").remove()), { grid: true });
    styleAxis(g.append("g").attr("transform", `translate(0,${H - m.b})`).call(d3.axisBottom(x).ticks(5).tickSize(3)));
    label(g, 2, 10, "m below MSL", { size: 10 });
    label(g, (m.l + width - m.r) / 2, H - 2, "two-way time, ms", { anchor: "middle", size: 10.5 });
    const colours = [1, 2, 3, 4, 5].map((i) => token(`data-cat-${i}`)).concat([token("data-story-2")]);
    const labels = [];
    let k = 0;
    for (const [name, pts] of byT) {
      const c = colours[k++ % colours.length];
      const p = pts.filter((r) => r.t >= tdom[0] && r.t <= tdom[1]).sort((a, b) => a.t - b.t);
      g.append("path").attr("d", d3.line().x((r) => x(r.t)).y((r) => y(r.z))(p)).attr("fill", "none").attr("stroke", c).attr("stroke-width", 2);
      const hit = pts.find((r) => r.t === at);
      if (hit) labels.push({ name, c, z: hit.z });
    }
    g.append("line").attr("x1", x(at)).attr("x2", x(at)).attr("y1", m.t).attr("y2", H - m.b).attr("stroke", ink()).attr("opacity", 0.5).attr("stroke-dasharray", "3 3");
    const zs = labels.map((l) => l.z);
    if (!zs.length) return;
    const z0 = d3.min(zs), z1 = d3.max(zs);
    g.append("rect").attr("x", x(at) - 5).attr("width", 10).attr("y", y(z0)).attr("height", Math.max(2, y(z1) - y(z0))).attr("fill", hi()).attr("opacity", 0.35);
    labels.forEach((l) => g.append("circle").attr("cx", x(at)).attr("cy", y(l.z)).attr("r", 4).attr("fill", l.c));
    const left = x(at) > (m.l + width - m.r) * 0.6;
    label(g, x(at) + (left ? -10 : 10), y((z0 + z1) / 2) + 4, `${Math.round(z1 - z0)} m of depth for one time`, { anchor: left ? "end" : "start", size: 11, weight: 600, fill: ink() });
    if (!narrow) {
      labels.sort((a, b) => a.z - b.z);
      for (let i = 1; i < labels.length; i++) if (y(labels[i].z) - y(labels[i - 1].z) < 13) labels[i].z = y.invert(y(labels[i - 1].z) + 13);
      labels.forEach((l) => {
        g.append("rect").attr("x", width - m.r + 6).attr("y", y(l.z) - 4).attr("width", 8).attr("height", 3).attr("fill", l.c);
        label(g, width - m.r + 18, y(l.z) + 3, l.name, { size: 10, fill: ink() });
      });
    }
  }
  onSchemeChange(() => last && draw(...last));
  return { draw, repaint: () => last && draw(...last) };
}
