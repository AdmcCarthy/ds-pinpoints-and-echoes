// Shared pieces for the story's figures: sizing for the pinned phone panel, axis styling, number formats and the scale
// ladder, a thin logarithmic ruler from a micrometre to a thousand kilometres that sits along the top of every figure and
// marks the rung the step is on.
import { token, tooltip } from "../runtime/js/subscout.js";

// One tooltip for the page. hover(selection, html) shows html(d) beside the pointer; marks keep their own size, so
// small marks get an invisible larger target via `hitR` where the caller draws one.
let tip = null;
export function hover(sel, html) {
  tip = tip || tooltip();
  sel.style("cursor", "default")
    .on("pointerenter pointermove", (ev, d) => tip.show(html(d), ev.clientX, ev.clientY))
    .on("pointerleave", () => tip.hide());
  return sel;
}

// Sequential scale on one hue: from a pale tint of the story colour to the story colour itself, log in the value.
export function sequentialLog(domain) {
  const strong = token("data-story-1") || "#2b5d8a";
  const pale = d3.interpolateRgb(token("surface") || token("bg") || "#f4f6f8", strong)(0.18);
  return d3.scaleSequentialLog(d3.interpolateRgb(pale, strong)).domain(domain);
}

export const LADDER_H = 30;
const LO = -6.3, HI = 6.3; // log10 metres shown on the ladder

export const ink = () => token("text") || "currentColor";
export const muted = () => token("text-muted") || "#888";
export const ctx = () => token("data-context") || "#999";
export const hi = () => token("data-highlight") || "#c60";
export const c1 = () => token("data-story-1") || "#369";
export const c2 = () => token("data-story-2") || "#69c";

export const isNarrow = (width) => width < 600;

// Height of the plot area: about 28 % of the screen on a phone (the card needs the rest), otherwise the share of the
// screen the build allows for a full-width figure, or a ratio of the width beside a lane.
export function plotHeight(width, opts = {}, { ratio = 0.62, min = 220, max = 620 } = {}) {
  if (opts.export && opts.height) return opts.height() - LADDER_H;
  const vh = window.innerHeight || 800;
  if (isNarrow(width)) return Math.round(Math.max(150, vh * 0.28 - LADDER_H));
  const share = opts.vhShare || 0.56;
  return Math.round(Math.max(min, Math.min(width * ratio, vh * share, max)));
}

export const fmtLen = (m) => {
  if (m < 1e-3) return `${+(m * 1e6).toPrecision(2)} µm`;
  if (m < 1e-2) return `${+(m * 1e3).toPrecision(2)} mm`;
  if (m < 1) return `${+(m * 100).toPrecision(2)} cm`;
  if (m < 1000) return `${+m.toPrecision(2)} m`;
  return `${Math.round(m / 1000).toLocaleString("en-GB")} km`;
};

export const num = (v, digits = 0) => (+v).toLocaleString("en-GB", { maximumFractionDigits: digits, minimumFractionDigits: digits });
export const sig = (v, n = 2) => (+(+v).toPrecision(n)).toLocaleString("en-GB");

export function styleAxis(g, { grid = false } = {}) {
  g.call((s) => s.select(".domain").attr("stroke", muted()))
    .call((s) => s.selectAll("line").attr("stroke", grid ? ctx() : muted()).attr("opacity", grid ? 0.3 : 1))
    .call((s) => s.selectAll("text").attr("fill", muted()).attr("font-size", 10));
  return g;
}

// Text with a halo in the figure's surface colour, so a label stays legible where it crosses a line or a mark.
export function label(svg, x, y, text, { anchor = "start", size = 10.5, weight = 400, fill = null } = {}) {
  return svg.append("text").attr("x", x).attr("y", y).attr("text-anchor", anchor).attr("font-size", size).attr("font-weight", weight)
    .attr("fill", fill || muted()).attr("paint-order", "stroke").attr("stroke", token("surface") || "#fff").attr("stroke-width", 3)
    .attr("stroke-linejoin", "round").text(text);
}

// The ladder: decade ticks, every rung as a dot, the active rungs highlighted and named. `active` is a key or a list of
// keys of the ladder dataset; "all" lights every rung.
export function ladder(svg, width, rows, active) {
  const keys = active === "all" ? rows.map((r) => r.key) : [].concat(active || []);
  const x = d3.scaleLinear().domain([LO, HI]).range([8, width - 8]).clamp(true);
  const g = svg.append("g").attr("class", "ladder");
  const y = 12;
  g.append("line").attr("x1", x(LO)).attr("x2", x(HI)).attr("y1", y).attr("y2", y).attr("stroke", ctx()).attr("stroke-width", 1);
  const narrow = isNarrow(width);
  for (let k = -6; k <= 6; k += narrow ? 3 : 1) {
    g.append("line").attr("x1", x(k)).attr("x2", x(k)).attr("y1", y - 3).attr("y2", y + 3).attr("stroke", ctx());
    if (k % 3 === 0) g.append("text").attr("x", x(k)).attr("y", y + 14).attr("text-anchor", k === -6 ? "start" : k === 6 ? "end" : "middle").attr("font-size", 9).attr("fill", muted()).text(fmtLen(10 ** k));
  }
  for (const r of rows) {
    const on = keys.includes(r.key);
    g.append("circle").attr("cx", x(Math.log10(+r.m))).attr("cy", y).attr("r", on ? 4.5 : 2.2).attr("fill", on ? hi() : ctx());
  }
  const named = rows.filter((r) => keys.includes(r.key));
  if (named.length === 1) {
    const r = named[0], px = x(Math.log10(+r.m));
    const anchor = px > width - 140 ? "end" : px < 140 ? "start" : "middle";
    g.append("text").attr("x", px).attr("y", y - 6).attr("text-anchor", anchor).attr("font-size", 10).attr("font-weight", 600).attr("fill", ink())
      .text(`${r.label}: ${fmtLen(+r.m)}`);
  }
  return LADDER_H;
}

// A ladder in its own svg, for figures drawn on a canvas.
export function ladderBar(el, width, rows, active) {
  const svg = d3.select(el).selectAll("svg.ladder-bar").data([0]).join("svg").attr("class", "ladder-bar").attr("aria-hidden", "true")
    .style("display", "block");
  svg.attr("viewBox", `0 0 ${width} ${LADDER_H}`).attr("width", width).attr("height", LADDER_H).selectAll("*").remove();
  ladder(svg, width, rows, active);
  return LADDER_H;
}

// The ladder rows of a figure's datasets (the `ladder` dataset of story.py), or null when the figure has none.
export const rungs = (datasets) => (datasets.ladder ? datasets.ladder.map((r) => ({ ...r, m: +r.m })) : null);

// One svg per figure, with the ladder on top and a plot group below it. Returns { svg, plot, W, H } where H is the plot height.
export function frame(el, width, height, rows, active, aria) {
  const svg = d3.select(el).selectAll("svg.fig").data([0]).join("svg").attr("class", "fig").attr("role", "img").attr("aria-label", aria);
  const total = height + (rows ? LADDER_H : 0);
  svg.attr("viewBox", `0 0 ${width} ${total}`).attr("width", width).attr("height", total).selectAll("*").remove();
  if (rows) ladder(svg, width, rows, active);
  const plot = svg.append("g").attr("transform", `translate(0,${rows ? LADDER_H : 0})`);
  return { svg, plot, W: width, H: height };
}
