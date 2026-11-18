// Composite log of 15/9-F-11 T2: four tracks against depth below sea level, the Hugin Fm shaded. state: { zoom } shows
// the reservoir only, so the 10 cm sampling is visible. Depth points down.
import { onSchemeChange, token } from "../runtime/js/subscout.js";
import { frame, plotHeight, rungs, styleAxis, label, hi, ink, ctx, isNarrow } from "./_common.js";

const TRACKS = [
  { key: "gr_api", label: "Gamma ray", unit: "API", dom: [0, 150] },
  { key: "rhob_g_cm3", label: "Density", unit: "g/cm³", dom: [1.95, 2.95] },
  { key: "rt_ohm_m", label: "Resistivity", unit: "ohm·m", dom: [0.2, 200], log: true },
  { key: "dt_us_ft", label: "Sonic", unit: "µs/ft", dom: [140, 40] },
];
const HUGIN = [3181.5, 3282.84]; // the interpreters' top and base picks in this well, m below MSL (log_notes.json)

export default function log(el, datasets, opts = {}) {
  const rows = datasets.log.map((r) => ({ z: +r.tvdss_m, gr_api: +r.gr_api, rhob_g_cm3: +r.rhob_g_cm3, rt_ohm_m: +r.rt_ohm_m, dt_us_ft: +r.dt_us_ft }));
  const lad = rungs(datasets);
  let last = null;
  function draw(width, state = {}) {
    last = [width, state];
    const zoom = !!state.zoom;
    const narrow = isNarrow(width);
    const H = plotHeight(width, opts, { ratio: 0.7 });
    const { plot: g } = frame(el, width, H, lad, state.rung ?? "log", "Composite well log, four tracks against depth");
    const m = { l: 46, r: 8, t: 30, b: 6 };
    const tracks = narrow ? TRACKS.slice(0, 3) : TRACKS;
    const zdom = zoom ? [HUGIN[0] - 15, HUGIN[1] + 15] : d3.extent(rows, (r) => r.z);
    const y = d3.scaleLinear().domain(zdom).range([m.t, H - m.b]);
    const tw = (width - m.l - m.r) / tracks.length, gap = 10;
    g.append("rect").attr("x", m.l).attr("width", width - m.l - m.r).attr("y", y(HUGIN[0])).attr("height", Math.max(0, y(HUGIN[1]) - y(HUGIN[0]))).attr("fill", hi()).attr("opacity", 0.1);
    label(g, width - m.r - 2, y(HUGIN[0]) - 3, "Hugin Fm", { anchor: "end", size: 10, fill: hi() });
    styleAxis(g.append("g").attr("transform", `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(zoom ? 6 : 8).tickSize(-(width - m.l - m.r))).call((s) => s.select(".domain").remove()), { grid: true });
    label(g, 2, 10, "m below MSL", { size: 10 });
    const colours = [token("data-story-1"), token("data-story-2"), token("data-story-3") || token("data-story-1"), token("data-story-4") || token("data-story-2")];
    tracks.forEach((t, i) => {
      const x0 = m.l + i * tw + gap / 2, x1 = m.l + (i + 1) * tw - gap / 2;
      const x = (t.log ? d3.scaleLog() : d3.scaleLinear()).domain(t.dom).range([x0, x1]).clamp(true);
      label(g, (x0 + x1) / 2, m.t - 16, t.label, { anchor: "middle", size: 11, weight: 600, fill: ink() });
      label(g, (x0 + x1) / 2, m.t - 5, `${t.dom[0]} – ${t.dom[1]} ${t.unit}`, { anchor: "middle", size: 9.5 });
      const pts = rows.filter((r) => r.z >= zdom[0] && r.z <= zdom[1]);
      const line = d3.line().x((r) => x(r[t.key])).y((r) => y(r.z)).defined((r) => Number.isFinite(r[t.key]));
      g.append("path").attr("d", line(pts)).attr("fill", "none").attr("stroke", colours[i]).attr("stroke-width", zoom ? 1.5 : 1);
      if (i) g.append("line").attr("x1", x0 - gap / 2).attr("x2", x0 - gap / 2).attr("y1", m.t).attr("y2", H - m.b).attr("stroke", ctx()).attr("opacity", 0.5);
    });
  }
  onSchemeChange(() => last && draw(...last));
  return { draw, repaint: () => last && draw(...last) };
}
