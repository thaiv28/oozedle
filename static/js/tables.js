(() => {
  "use strict";
  const states = new Map();
  const triangle = (descending) => {
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 10 8");
    svg.setAttribute("aria-hidden", "true");
    const path = document.createElementNS(svg.namespaceURI, "path");
    path.setAttribute("d", descending ? "M0 0h10L5 8z" : "M0 8h10L5 0z");
    svg.append(path);
    return svg;
  };
  const sort = (table) => {
    const state = states.get(table);
    const headers = [...table.tHead.rows[0].cells];
    headers.forEach((th, i) => {
      th.setAttribute("aria-sort", i === state.column ? state.direction : "none");
      th.querySelector("svg")?.remove();
      if (i === state.column) th.querySelector("button").append(triangle(state.direction === "descending"));
    });
    const rows = [...table.tBodies[0].rows];
    const value = (row) => (row.cells[state.column].dataset.value ?? row.cells[state.column].textContent.trim()).replace("−", "-");
    rows.sort((a, b) => {
      const numeric = headers[state.column].dataset.type === "number";
      const aValue = value(a), bValue = value(b);
      if (numeric) {
        const aMissing = aValue === "" || !Number.isFinite(Number(aValue));
        const bMissing = bValue === "" || !Number.isFinite(Number(bValue));
        if (aMissing !== bMissing) return aMissing ? 1 : -1;
        if (aMissing) return a.cells[0].textContent.localeCompare(b.cells[0].textContent);
      }
      const cmp = numeric ? Number(aValue) - Number(bValue) : aValue.localeCompare(bValue);
      return (state.direction === "descending" ? -cmp : cmp) || a.cells[0].textContent.localeCompare(b.cells[0].textContent);
    });
    table.tBodies[0].append(...rows);
  };
  document.querySelectorAll("table[data-sortable]").forEach((table) => {
    const headers = [...table.tHead.rows[0].cells];
    const first = table.dataset.sort || "PP";  // default sort column, by header label
    states.set(table, {column: headers.findIndex(th => th.textContent.trim() === first), direction: "descending"});
    headers.forEach((th, column) => th.querySelector("button").addEventListener("click", () => {
      const old = states.get(table);
      const direction = old.column === column
        ? (old.direction === "descending" ? "ascending" : "descending")
        : (th.dataset.type === "number" ? "descending" : "ascending");
      states.set(table, {column, direction});
      sort(table);
    }));
    sort(table);
  });
  document.querySelectorAll(".view-switch").forEach(control => {
    const table = document.getElementById(control.dataset.table);
    const setView = view => {
      table.dataset.view = view;
      document.querySelectorAll("[data-shared-view]").forEach(other => other.dataset.view = view);
      control.querySelectorAll("button").forEach(button =>
        button.setAttribute("aria-pressed", String(button.dataset.view === view)));
      const key = view === "advanced" ? "adj_ma" : "points_played";
      const column = [...table.tHead.rows[0].cells].findIndex(th => th.dataset.key === key);
      states.set(table, {column, direction: "descending"});
      sort(table);
    };
    const view = new URL(location.href).searchParams.get("view");
    setView(view === "advanced" ? "advanced" : "box");
    control.querySelectorAll("button").forEach(button => button.addEventListener("click", () => {
      setView(button.dataset.view);
      const next = new URL(location.href);
      if (button.dataset.view === "advanced") next.searchParams.set("view", "advanced");
      else next.searchParams.delete("view");
      history.replaceState(null, "", next);
    }));
  });
  const format = (value, decimals) => {
    if (value === null) return "—";
    let text = decimals === undefined ? String(value) : value.toFixed(decimals);
    if (Number(text) === 0) text = text.replace("-", "");  // no "−0.0" from rounding
    return text.replace(/-/g, "−");
  };
  const data = document.getElementById("players-data");
  if (!data) return;
  const {lines, weights} = JSON.parse(data.textContent);
  const table = document.getElementById("players-table");
  const input = document.getElementById("player-search");
  const buttons = [...document.querySelectorAll("[data-player-seasons] button")];
  const url = new URL(location.href);
  let season = url.searchParams.get("season") || "all";
  if (!buttons.some(b => b.dataset.season === season)) season = "all";
  const keys = ["tournaments", "games_played", "points_played", "assists", "goals", "blocks", "turnovers", "wins", "losses", "adj_ma"];
  const update = () => {
    buttons.forEach(b => b.setAttribute("aria-pressed", String(b.dataset.season === season)));
    const players = new Map();
    lines.filter(line => season === "all" || String(line.season) === season).forEach(line => {
      if (!players.has(line.player_id)) players.set(line.player_id, {name: line.name, ...Object.fromEntries(keys.map(k => [k, 0]))});
      const player = players.get(line.player_id);
      keys.forEach(k => player[k] += line[k]);
    });
    const rows = [];
    players.forEach((p, slug) => {
      if (!p.name.toLocaleLowerCase().includes(input.value.toLocaleLowerCase())) return;
      const row = document.createElement("tr");
      const name = document.createElement("th");
      name.scope = "row";
      const link = document.createElement("a");
      link.href = `players/${slug}.html`;
      link.textContent = p.name;
      name.append(link);
      row.append(name);
      p.ma = Object.entries(weights).reduce((sum, [key, weight]) => sum + p[key] * weight, 0);
      p.win_pct = p.wins + p.losses ? p.wins / (p.wins + p.losses) : null;
      // Same cutoff as per10 on the server.
      p.adj_ma_per10 = p.points_played < 20 ? null : 10 * p.adj_ma / p.points_played;
      [...table.tHead.rows[0].cells].slice(1).forEach(header => {
        const key = header.dataset.key;
        const cell = document.createElement("td");
        cell.className = header.className;
        cell.dataset.value = p[key] === null ? "" : p[key];
        cell.textContent = key === "wins" ? `${p.wins}–${p.losses}`
          : key === "win_pct" ? (p.win_pct === null ? "—" : `${Math.round(100 * p.win_pct)}%`)
          : format(p[key], ["ma", "adj_ma", "adj_ma_per10"].includes(key) ? 1 : undefined);
        row.append(cell);
      });
      rows.push(row);
    });
    table.tBodies[0].replaceChildren(...rows);
    sort(table);
  };
  buttons.forEach(b => b.addEventListener("click", () => {
    season = b.dataset.season;
    const next = new URL(location.href);
    if (season === "all") next.searchParams.delete("season");
    else next.searchParams.set("season", season);
    history.replaceState(null, "", next);
    update();
  }));
  input.addEventListener("input", update);
  update();
})();
