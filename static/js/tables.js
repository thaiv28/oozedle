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
    const value = (row) => row.cells[state.column].dataset.value ?? row.cells[state.column].textContent.trim();
    rows.sort((a, b) => {
      const cmp = headers[state.column].dataset.type === "number"
        ? Number(value(a)) - Number(value(b)) : value(a).localeCompare(value(b));
      return (state.direction === "descending" ? -cmp : cmp) || a.cells[0].textContent.localeCompare(b.cells[0].textContent);
    });
    table.tBodies[0].append(...rows);
  };
  document.querySelectorAll("table[data-sortable]").forEach((table) => {
    const headers = [...table.tHead.rows[0].cells];
    states.set(table, {column: headers.findIndex(th => th.textContent.trim() === "PP"), direction: "descending"});
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
  const data = document.getElementById("players-data");
  if (!data) return;
  const lines = JSON.parse(data.textContent);
  const table = document.getElementById("players-table");
  const input = document.getElementById("player-search");
  const buttons = [...document.querySelectorAll("[data-player-seasons] button")];
  const url = new URL(location.href);
  let season = url.searchParams.get("season") || "all";
  if (!buttons.some(b => b.dataset.season === season)) season = "all";
  const keys = ["tournaments", "games_played", "points_played", "assists", "goals", "blocks", "turnovers", "wins", "losses"];
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
      keys.slice(0, 7).forEach(k => {
        const cell = document.createElement("td");
        cell.textContent = p[k];
        row.append(cell);
      });
      const record = document.createElement("td");
      record.textContent = `${p.wins}–${p.losses}`;
      record.dataset.value = p.wins;
      row.append(record);
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
