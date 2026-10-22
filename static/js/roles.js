(() => {
  "use strict";
  const data = JSON.parse(document.getElementById("roles-data").textContent);
  const chart = document.getElementById("roles-chart");
  const tooltip = document.getElementById("roles-tooltip");
  const input = document.getElementById("roles-search");
  const status = document.getElementById("roles-status");
  const rows = document.getElementById("roles-rows");
  const buttons = [...document.querySelectorAll("#roles-switch button")];
  const ns = "http://www.w3.org/2000/svg";
  const svgNode = (tag, attrs = {}, text) => {
    const node = document.createElementNS(ns, tag);
    Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, value));
    if (text !== undefined) node.textContent = text;
    return node;
  };
  const label = p => `${p.name} · ${p.season}`;
  const stats = p => `${p.points_played} PP · ${p.assists} A · ${p.goals} G · ${p.blocks} B · ${p.turnovers} T · ${(p.turnovers / p.points_played).toFixed(2)} turnovers per point`;
  let mode = "seasons";
  let marks = [];
  let trail;
  let closeTimer;
  const hideTooltip = () => {
    clearTimeout(closeTimer);
    tooltip.hidden = true;
  };
  const scheduleHide = () => {
    clearTimeout(closeTimer);
    closeTimer = setTimeout(hideTooltip, 150);
  };
  tooltip.addEventListener("pointerenter", () => clearTimeout(closeTimer));
  tooltip.addEventListener("pointerleave", () => {
    if (!document.activeElement?.classList.contains("roles-dot")) scheduleHide();
  });
  document.addEventListener("keydown", event => { if (event.key === "Escape") hideTooltip(); });
  const showTooltip = (p, anchor) => {
    clearTimeout(closeTimer);
    tooltip.replaceChildren();
    const heading = document.createElement("strong");
    heading.textContent = label(p);
    const line = document.createElement("div");
    line.textContent = stats(p);
    tooltip.append(heading, line);
    tooltip.hidden = false;
    const outer = chart.getBoundingClientRect();
    const dot = anchor.getBoundingClientRect();
    const x = dot.left + dot.width / 2 - outer.left;
    const y = dot.top - outer.top;
    tooltip.style.left = `${Math.max(0, Math.min(x - tooltip.offsetWidth / 2, outer.width - tooltip.offsetWidth))}px`;
    tooltip.style.top = `${Math.max(0, y - tooltip.offsetHeight - 12)}px`;
  };
  const updateSearch = () => {
    hideTooltip();
    const query = input.value.trim().toLocaleLowerCase();
    const matches = new Map();
    marks.forEach(({p, anchor, dot, x, y}) => {
      const match = query && p.name.toLocaleLowerCase().includes(query);
      anchor.classList.toggle("is-match", Boolean(match));
      dot.style.fill = match ? "var(--orange)" : "var(--ink)";
      dot.style.fillOpacity = query ? (match ? "1" : "0.2") : "0.55";
      if (match) {
        if (!matches.has(p.player_id)) matches.set(p.player_id, []);
        matches.get(p.player_id).push({p, x, y});
      }
    });
    trail.replaceChildren();
    if (mode === "seasons") matches.forEach(points => {
      points.sort((a, b) => a.p.season - b.p.season);
      if (points.length > 1) trail.append(svgNode("polyline", {
        points: points.map(p => `${p.x},${p.y}`).join(" "),
        fill: "none", stroke: "var(--orange)", "stroke-width": 2,
      }));
    });
    status.textContent = query ? `${matches.size} matching ${matches.size === 1 ? "player" : "players"}` : `${marks.length} ${mode === "seasons" ? "player-seasons" : "players"} · 60+ points played`;
  };
  const updateTable = points => {
    const body = document.createDocumentFragment();
    points.forEach(p => {
      const row = document.createElement("tr");
      const name = document.createElement("th");
      name.scope = "row";
      const link = document.createElement("a");
      link.href = `players/${p.player_id}.html`;
      link.textContent = p.name;
      name.append(link);
      row.append(name);
      [p.season, p.points_played, `${(100 * p.assist_share).toFixed(0)}%`, p.blocks_per_point.toFixed(2)].forEach(value => {
        const cell = document.createElement("td");
        cell.textContent = value;
        row.append(cell);
      });
      body.append(row);
    });
    rows.replaceChildren(body);
  };
  const render = () => {
    hideTooltip();
    chart.querySelector("svg")?.remove();
    const width = chart.clientWidth;
    if (!width) return;
    const height = width * (window.matchMedia("(max-width: 519px)").matches ? 1 : 0.75);
    const left = 58, right = width - 18, top = 24, bottom = height - 84;
    const points = data[mode];
    const maximum = Math.max(0.01, ...points.map(p => p.blocks_per_point));
    const rawStep = maximum / 5;
    const magnitude = 10 ** Math.floor(Math.log10(rawStep));
    const step = [1, 2, 5, 10].find(n => n * magnitude >= rawStep) * magnitude;
    const yMax = Math.ceil(maximum / step) * step;
    const x = value => left + value * (right - left);
    const y = value => bottom - value / yMax * (bottom - top);
    const svg = svgNode("svg", {viewBox: `0 0 ${width} ${height}`, role: "group", "aria-label": `Player roles by ${mode}`});
    svg.append(svgNode("title", {}, "Assist share and blocks per point"));
    const text = (value, tx, ty, attrs = {}) => svgNode("text", {x: tx, y: ty, ...attrs}, value);
    const grid = (x1, y1, x2, y2) => svgNode("line", {x1, y1, x2, y2, stroke: "var(--rule)", "stroke-width": 1});
    for (let i = 0; i <= Math.round(yMax / step); i++) {
      const value = i * step;
      svg.append(grid(left, y(value), right, y(value)), text(value.toFixed(Math.max(2, -Math.floor(Math.log10(step)))), left - 8, y(value) + 4, {"text-anchor": "end"}));
    }
    [0, 0.25, 0.5, 0.75, 1].forEach(value => {
      svg.append(grid(x(value), top, x(value), bottom), text(String(value), x(value), bottom + 20, {"text-anchor": "middle"}));
    });
    svg.append(text("More goals", left, bottom + 42), text("More assists", right, bottom + 42, {"text-anchor": "end"}), text("Assist share of scoring plays", (left + right) / 2, bottom + 70, {"text-anchor": "middle", class: "roles-axis"}), text("Blocks per point", 16, (top + bottom) / 2, {transform: `rotate(-90 16 ${(top + bottom) / 2})`, "text-anchor": "middle", class: "roles-axis"}));
    trail = svgNode("g", {"aria-hidden": "true", "pointer-events": "none"});
    svg.append(trail);
    const sizes = points.map(p => Math.sqrt(p.points_played));
    const minSize = Math.min(...sizes), maxSize = Math.max(...sizes);
    marks = [];
    // Large marks first so a small season stays reachable when dots coincide.
    [...points].sort((a, b) => b.points_played - a.points_played).forEach(p => {
      const cx = x(p.assist_share), cy = y(p.blocks_per_point);
      const r = maxSize === minSize ? 9 : 5 + 8 * (Math.sqrt(p.points_played) - minSize) / (maxSize - minSize);
      const anchor = svgNode("a", {href: `players/${p.player_id}.html`, tabindex: 0, class: "roles-dot", "aria-label": `${label(p)}: ${stats(p)}`, "aria-describedby": "roles-tooltip"});
      const dot = svgNode("circle", {cx, cy, r, fill: "var(--ink)", "fill-opacity": 0.55, stroke: "var(--board)", "stroke-width": 2});
      anchor.append(dot, svgNode("circle", {cx, cy, r: Math.max(12, r + 3), fill: "transparent", class: "roles-hit"}));
      anchor.addEventListener("pointerenter", () => showTooltip(p, dot));
      anchor.addEventListener("pointerleave", () => { if (document.activeElement !== anchor) scheduleHide(); });
      anchor.addEventListener("focus", () => showTooltip(p, dot));
      anchor.addEventListener("blur", hideTooltip);
      anchor.addEventListener("keydown", event => { if (event.key === "Escape") hideTooltip(); });
      svg.append(anchor);
      marks.push({p, anchor, dot, x: cx, y: cy});
    });
    chart.prepend(svg);
    updateSearch();
  };
  input.addEventListener("input", updateSearch);
  buttons.forEach(button => button.addEventListener("click", () => {
    mode = button.dataset.mode;
    buttons.forEach(b => b.setAttribute("aria-pressed", String(b === button)));
    updateTable(data[mode]);
    render();
  }));
  new ResizeObserver(render).observe(chart);
})();
