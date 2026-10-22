// Oozedle daily game. Data comes from the inline #game-data JSON written by oozedle/site.py.
(() => {
  "use strict";

  const STATS = ["PP", "A", "G", "B", "T"];
  const STAT_NAMES = ["points played", "assists", "goals", "blocks", "turnovers"];
  const MAX_GUESSES = 6;
  const TZ = "America/Los_Angeles";
  const SHARE_MARK = { up: "🟦", down: "🟧", same: "🟩" };

  const data = JSON.parse(document.getElementById("game-data").textContent);
  const override = data.override || null;
  const root = data.root || "";

  // ---- dates (puzzles change at midnight Pacific) ----

  function pacificToday() {
    return new Intl.DateTimeFormat("en-CA", { timeZone: TZ }).format(new Date());
  }

  function dayNumber(iso) {
    const [y, m, d] = iso.split("-").map(Number);
    return Math.round(Date.UTC(y, m - 1, d) / 86400000);
  }

  function addDays(iso, n) {
    return new Date((dayNumber(iso) + n) * 86400000).toISOString().slice(0, 10);
  }

  function formatDate(iso) {
    const date = new Date(dayNumber(iso) * 86400000);
    const part = (opts) => date.toLocaleDateString("en-US", { timeZone: "UTC", ...opts });
    return `${part({ weekday: "short" })} ${part({ month: "short" })} ${part({ day: "numeric" })}`;
  }

  // ---- puzzle selection ----

  function hash(text) {
    let h = 2166136261;
    for (let i = 0; i < text.length; i++) {
      h ^= text.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    h ^= h >>> 15;
    h = Math.imul(h, 2246822507);
    h ^= h >>> 13;
    return h >>> 0;
  }

  const lines = data.lines.map(([t, p, ...stats]) => ({ t, p, stats }));

  function poolFor(season) {
    return lines.filter(
      (l) =>
        l.stats[0] >= data.minPoints &&
        (season === "all" || data.tournaments[l.t].season === Number(season)),
    );
  }

  function puzzleFor(date, season) {
    const pool = poolFor(season);
    if (!pool.length) return null;
    const answer = pool[hash(`${date}|${season}`) % pool.length];
    const roster = lines.filter((l) => l.t === answer.t);
    return { date, season, answer, roster, number: dayNumber(date) - dayNumber(data.epoch) + 1 };
  }

  function compare(guess, answer) {
    return answer.stats.map((v, i) =>
      v > guess.stats[i] ? "up" : v < guess.stats[i] ? "down" : "same",
    );
  }

  // ---- storage (per viewer; the game works without it) ----

  const store = {
    get(key, fallback) {
      try {
        const raw = localStorage.getItem(key);
        return raw ? JSON.parse(raw) : fallback;
      } catch {
        return fallback;
      }
    },
    set(key, value) {
      try {
        localStorage.setItem(key, JSON.stringify(value));
      } catch {
        /* private mode or blocked storage */
      }
    },
  };

  // ---- state ----

  const params = new URLSearchParams(location.search);
  const seasons = data.seasons.map(String);
  const season = seasons.includes(params.get("season")) ? params.get("season") : "all";
  const today = override ? override.date : pacificToday();
  const puzzle = puzzleFor(today, season);
  if (override) {
    puzzle.number = override.number;
    puzzle.answer = lines.find((l) => l.t === override.tournament && l.p === override.answer);
    puzzle.roster = lines.filter((l) => l.t === override.tournament);
  }
  const storeKey = `oozedle:v1:${today}:${season}`;
  const guesses = (override ? override.guesses : store.get(storeKey, []))
    .map((p) => puzzle.roster.find((l) => l.p === p))
    .filter(Boolean)
    .slice(0, MAX_GUESSES);

  const won = () => guesses.some((g) => g.p === puzzle.answer.p);
  const over = () => won() || guesses.length >= MAX_GUESSES;

  // ---- rendering ----

  const $ = (sel) => document.querySelector(sel);
  const el = (tag, attrs = {}, ...children) => {
    const node = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === "class") node.className = v;
      else if (k === "text") node.textContent = v;
      else node.setAttribute(k, v);
    }
    node.append(...children);
    return node;
  };

  const SVG_NS = "http://www.w3.org/2000/svg";
  // Line arrows (stroked) and the equals bars (filled), drawn to the comp.
  const ICONS = {
    up: { box: "0 0 18 24", d: "M9 22.5V3M2 9.5 9 2.5l7 7", stroke: true },
    down: { box: "0 0 18 24", d: "M9 1.5V21M2 14.5l7 7 7-7", stroke: true },
    same: { box: "0 0 14 10", d: "M0 0h14v3.5H0zM0 6.5h14V10H0z", stroke: false },
  };

  function mark(kind, statIndex) {
    const icon = ICONS[kind];
    const svg = document.createElementNS(SVG_NS, "svg");
    svg.setAttribute("viewBox", icon.box);
    svg.setAttribute("aria-hidden", "true");
    const path = document.createElementNS(SVG_NS, "path");
    path.setAttribute("d", icon.d);
    if (icon.stroke) {
      path.setAttribute("fill", "none");
      path.setAttribute("stroke", "currentColor");
      path.setAttribute("stroke-width", "3");
      path.setAttribute("stroke-linecap", "square");
    } else {
      path.setAttribute("fill", "currentColor");
    }
    svg.append(path);
    const label =
      kind === "same"
        ? `Same ${STAT_NAMES[statIndex]}`
        : `${kind === "up" ? "More" : "Fewer"} ${STAT_NAMES[statIndex]}`;
    return el("span", { class: `mark mark--${kind}`, role: "img", "aria-label": label }, svg);
  }

  const playerName = (line) => data.players[line.p].name;
  const playerUrl = (line) => `${root}players/${data.players[line.p].slug}.html`;
  const tournament = (line) => data.tournaments[line.t];
  const poolLabel = (line) => `${tournament(line).name} · ${tournament(line).season}`;

  function renderHeader() {
    $("[data-puzzle-number]").textContent = `#${puzzle.number}`;
    $("[data-puzzle-date]").textContent = override?.dateLabel || formatDate(today);
    $("[data-puzzle-pool]").textContent = poolLabel(puzzle.answer);
    document.title = `Oozedle #${puzzle.number}`;
  }

  function renderRows(newIndex = -1) {
    const rows = document.querySelectorAll("[data-guess-rows] tr");
    rows.forEach((row, i) => {
      const cells = row.querySelectorAll("td");
      const guess = guesses[i];
      row.className = "";
      for (let c = 1; c < cells.length; c++) cells[c].replaceChildren();
      if (!guess) {
        if (i === guesses.length && !over()) row.classList.add("is-current");
        return;
      }
      const right = guess.p === puzzle.answer.p;
      if (right) row.classList.add("is-answer");
      if (i === newIndex) row.classList.add("is-new");
      cells[1].append(
        right
          ? el("span", { text: playerName(guess) })
          : el("s", {}, el("span", { class: "visually-hidden", text: "Wrong: " }), playerName(guess)),
      );
      compare(guess, puzzle.answer).forEach((kind, s) => cells[s + 2].append(mark(kind, s)));
    });
  }

  function statline(stats) {
    return stats.map((v, i) => `${v} ${STATS[i]}`).join(" · ");
  }

  function shareText() {
    const score = won() ? guesses.length : "X";
    const rows = guesses.map((g) =>
      compare(g, puzzle.answer)
        .map((k) => SHARE_MARK[k])
        .join(""),
    );
    return [
      `Oozedle #${puzzle.number} · ${tournament(puzzle.answer).name} ${tournament(puzzle.answer).season} · ${score}/${MAX_GUESSES}`,
      ...rows,
      "oozedle.thaiv.dev",
    ].join("\n");
  }

  function countdown() {
    const now = new Date();
    const parts = Object.fromEntries(
      new Intl.DateTimeFormat("en-US", {
        timeZone: TZ,
        hour: "numeric",
        minute: "numeric",
        hourCycle: "h23",
      })
        .formatToParts(now)
        .map((p) => [p.type, p.value]),
    );
    const left = 24 * 60 - (Number(parts.hour) * 60 + Number(parts.minute));
    return `Next puzzle in ${Math.floor(left / 60)}h ${left % 60}m`;
  }

  function renderEnd() {
    const form = $("[data-guess-form]");
    const result = $("[data-result]");
    if (!over()) {
      form.hidden = false;
      result.replaceChildren();
      return;
    }
    form.hidden = true;
    $("[data-form-note]").textContent = "";
    const share = el("button", { class: "btn btn--ink", type: "button", text: "Share" });
    share.addEventListener("click", async () => {
      const text = shareText();
      // Phones get the system share sheet (Messages, Copy, ...); desktops copy.
      if (typeof navigator.share === "function" && matchMedia("(pointer: coarse)").matches) {
        try {
          await navigator.share({ text });
          return;
        } catch (error) {
          if (error.name === "AbortError") return; // closed the sheet
        }
      }
      try {
        await navigator.clipboard.writeText(text);
        share.textContent = "Copied";
      } catch {
        window.prompt("Copy your result", text);
      }
      setTimeout(() => (share.textContent = "Share"), 1800);
    });
    result.replaceChildren(
      el(
        "div",
        { class: "result" },
        el("p", {
          class: "result__verdict",
          text: won() ? `Got it in ${guesses.length}.` : "Out of guesses.",
        }),
        el(
          "p",
          { class: "result__answer" },
          el("a", { href: playerUrl(puzzle.answer), text: playerName(puzzle.answer) }),
          ` at ${poolLabel(puzzle.answer)}`,
        ),
        el("p", { class: "statline" }, statline(puzzle.answer.stats)),
        el(
          "div",
          { class: "result__actions" },
          share,
          el("span", { class: "result__next", text: countdown() }),
        ),
      ),
    );
  }

  function renderYesterday() {
    const date = addDays(today, -1);
    if (override?.yesterday) {
      const y = override.yesterday;
      showYesterday(`${y.name} · ${y.pool}`, y.stats, null);
      return;
    }
    if (dayNumber(date) < dayNumber(data.epoch)) return;
    const p = puzzleFor(date, season);
    if (p) showYesterday(`${playerName(p.answer)} · ${poolLabel(p.answer)}`, p.answer.stats, playerUrl(p.answer));
  }

  function showYesterday(label, stats, href) {
    const target = $("[data-yesterday-player]");
    target.replaceChildren(href ? el("a", { href, text: label }) : label);
    $("[data-yesterday-line]").replaceChildren(statline(stats));
    $("[data-yesterday]").hidden = false;
  }

  function renderSeasons() {
    const items = [["all", "All"], ...seasons.map((s) => [s, s])].map(([value, label]) => {
      const a = el("a", { href: value === "all" ? "?" : `?season=${value}`, text: label });
      if (value === season) a.setAttribute("aria-current", "true");
      return el("li", {}, a);
    });
    $("[data-season-switch]").replaceChildren(...items);
  }

  function recordResult() {
    if (override || season !== "all") return;
    const rec = store.get("oozedle:v1:record", { played: 0, wins: 0, streak: 0, best: 0, last: null });
    if (rec.last === today) return;
    rec.played += 1;
    if (won()) {
      rec.wins += 1;
      rec.streak = rec.last === addDays(today, -1) ? rec.streak + 1 : 1;
      rec.best = Math.max(rec.best, rec.streak);
    } else {
      rec.streak = 0;
    }
    rec.last = today;
    store.set("oozedle:v1:record", rec);
  }

  function renderRecord() {
    const rec = store.get("oozedle:v1:record", null);
    if (!rec || !rec.played || override) return;
    const items = [
      ["Played", rec.played],
      ["Won", rec.wins],
      ["Streak", rec.last === today || rec.last === addDays(today, -1) ? rec.streak : 0],
      ["Best", rec.best],
    ].map(([k, v]) => el("div", {}, el("dt", { text: k }), el("dd", { text: String(v) })));
    $("[data-record-list]").replaceChildren(...items);
    $("[data-record]").hidden = false;
  }

  // ---- the guess combobox ----

  const input = $("#guess-input");
  const list = $("#guess-options");
  const note = $("[data-form-note]");
  let matches = [];
  let active = -1;

  function candidates() {
    const taken = new Set(guesses.map((g) => g.p));
    return puzzle.roster
      .filter((l) => !taken.has(l.p))
      .sort((a, b) => playerName(a).localeCompare(playerName(b)));
  }

  function openList() {
    const q = input.value.trim().toLowerCase();
    matches = candidates().filter((l) => !q || playerName(l).toLowerCase().includes(q));
    matches.sort(
      (a, b) =>
        Number(!playerName(a).toLowerCase().startsWith(q)) -
        Number(!playerName(b).toLowerCase().startsWith(q)),
    );
    active = q && matches.length ? 0 : -1;
    list.replaceChildren(
      ...matches.map((l, i) => {
        const opt = el("li", {
          class: "combo__option",
          role: "option",
          id: `opt-${l.p}`,
          "aria-selected": String(i === active),
          text: playerName(l),
        });
        opt.addEventListener("mousedown", (e) => {
          e.preventDefault();
          submit(l);
        });
        return opt;
      }),
    );
    const show = matches.length > 0 && document.activeElement === input;
    list.hidden = !show;
    input.setAttribute("aria-expanded", String(show));
    syncActive();
  }

  function closeList() {
    list.hidden = true;
    input.setAttribute("aria-expanded", "false");
    input.removeAttribute("aria-activedescendant");
  }

  function syncActive() {
    [...list.children].forEach((opt, i) => {
      opt.setAttribute("aria-selected", String(i === active));
      if (i === active) opt.scrollIntoView({ block: "nearest" });
    });
    if (active >= 0) input.setAttribute("aria-activedescendant", `opt-${matches[active].p}`);
    else input.removeAttribute("aria-activedescendant");
  }

  function resolveTyped() {
    const q = input.value.trim().toLowerCase();
    if (!q) return null;
    const pool = candidates();
    return (
      pool.find((l) => playerName(l).toLowerCase() === q) ||
      (active >= 0 && matches[active]) ||
      (pool.filter((l) => playerName(l).toLowerCase().includes(q)).length === 1
        ? pool.find((l) => playerName(l).toLowerCase().includes(q))
        : null)
    );
  }

  function submit(line) {
    if (!line || over()) return;
    guesses.push(line);
    store.set(storeKey, guesses.map((g) => g.p));
    input.value = "";
    note.textContent = "";
    closeList();
    renderRows(guesses.length - 1);
    if (over()) recordResult();
    renderEnd();
    renderRecord();
    if (!over()) input.focus();
  }

  input.addEventListener("input", openList);
  input.addEventListener("focus", openList);
  input.addEventListener("click", openList); // already focused after a guess, so focus alone would not reopen it
  input.addEventListener("blur", () => setTimeout(closeList, 100));
  input.addEventListener("keydown", (e) => {
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault();
      if (list.hidden) openList();
      if (!matches.length) return;
      active = (active + (e.key === "ArrowDown" ? 1 : -1) + matches.length) % matches.length;
      syncActive();
    } else if (e.key === "Escape") {
      closeList();
    }
  });

  $("[data-guess-form]").addEventListener("submit", (e) => {
    e.preventDefault();
    const line = resolveTyped();
    if (line) submit(line);
    else note.textContent = input.value.trim()
      ? "No player by that name at this tournament. Pick one from the list."
      : "Type a player's name.";
  });

  // ---- go ----

  renderHeader();
  renderRows();
  renderEnd();
  renderYesterday();
  renderSeasons();
  renderRecord();
})();
