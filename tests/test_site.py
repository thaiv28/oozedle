"""Offline site builds and link integrity across both workbook layouts."""

import json
import re
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

import pytest
from conftest import make_layout_a, make_layout_b, make_single_game_with_stale_sheets

from oozedle.dataset import build_dataset
from oozedle.site import build, stats_context


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.links = []
        self.game = []
        self.in_game = False
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.links.extend(attrs[k] for k in ("href", "src") if k in attrs)
        if tag == "script":
            self.in_game = attrs.get("id") == "game-data"

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_game = False

    def handle_data(self, data):
        if self.in_game:
            self.game.append(data)


@pytest.fixture
def site_dataset(tmp_path):
    raw = tmp_path / "raw"
    for year, factory in [
        (2024, make_layout_a),
        (2025, make_layout_b),
        (2026, make_single_game_with_stale_sheets),
    ]:
        folder = raw / str(year)
        folder.mkdir(parents=True)
        factory(folder / "Test Stats.xlsx")
    return build_dataset(raw, manifest=[], aliases={})


def test_build(site_dataset, tmp_path):
    ds = site_dataset
    out = tmp_path / "output"
    build(ds, out)
    for name in ["index", "players", "tournaments", "advanced", "404"]:
        assert (out / f"{name}.html").is_file()
    assert len(list((out / "players").glob("*.html"))) == len(ds.players)
    assert len(list((out / "tournaments").glob("*.html"))) == len(ds.tournaments)
    for directory, ids in [
        ("players", ds.players.player_id),
        ("tournaments", ds.tournaments.tournament_id),
    ]:
        for slug in ids:
            assert (out / directory / f"{slug}.html").is_file()
    for file in out.rglob("*.html"):
        page = Page(file.read_text())
        for link in page.links:
            url = urlsplit(link)
            if url.scheme or url.netloc or not url.path:
                continue
            if url.path.startswith("/"):
                assert file.name == "404.html"
                continue
            target = (file.parent / unquote(url.path)).resolve()
            assert target.is_relative_to(out.resolve())
            assert target.is_file(), (file, link)
    data = json.loads("".join(Page((out / "index.html").read_text()).game))
    for line in data["lines"]:
        assert 0 <= line[0] < len(data["tournaments"])
        assert 0 <= line[1] < len(data["players"])
    player = ds.players.iloc[0]
    total = ds.player_tournaments.loc[
        ds.player_tournaments.player_id == player.player_id, "points_played"
    ].sum()
    assert f">{int(total)}</td>" in (out / "players" / f"{player.player_id}.html").read_text()
    assert (
        "15.5–10"
        in (out / "tournaments" / f"{ds.tournaments.iloc[0].tournament_id}.html").read_text()
    )


def test_season_totals(site_dataset):
    context = stats_context(site_dataset)
    lines = json.loads(context["players_json"])["lines"]
    for player in context["players"]:
        seasons = [line for line in lines if line["player_id"] == player["player_id"]]
        assert sum(line["points_played"] for line in seasons) == player["career"]["points_played"]


def test_link_preview_tags(site_dataset, tmp_path):
    ds = site_dataset
    out = tmp_path / "preview"
    build(ds, out)
    html = (out / "index.html").read_text()
    image = re.search(r'<meta property="og:image" content="([^"]+)"', html).group(1)
    assert image.startswith("https://oozedle.thaiv.dev/static/og/card.png?v=")
    assert (out / "static/og/card.png").is_file()
    assert (out / "static/apple-touch-icon.png").is_file()
    assert '<meta property="og:url" content="https://oozedle.thaiv.dev/">' in html
    assert '<meta name="twitter:card" content="summary_large_image">' in html
    player = next((out / "players").glob("*.html")).read_text()
    assert re.search(r'<meta property="og:description" content="[^"]* tournaments · ', player)


def test_adjusted_build_and_neutral_fallback(site_dataset, tmp_path):
    ratings = tmp_path / "ratings"
    ratings.mkdir()
    (ratings / "2024.csv").write_text(
        "# college; data through May 4; source https://example.test\n"
        "rank,team,record,rating\n1,Ooze,2-0,1000\n2,Chico State,1-1,700\n"
        "3,San Jose State,0-2,1200\n"
    )
    (ratings / "aliases.yml").write_text(
        "ooze: Ooze\nopponents:\n  Chico: Chico State\n  SJSU: San Jose State\n"
    )
    context = stats_context(site_dataset, ratings_dir=ratings)
    assert context["ratings_available"]
    assert context["difficulty"].n_rated == 3
    lines = json.loads(context["players_json"])["lines"]
    assert all("adj_ma" in row for row in lines)
    for player in context["players"]:
        assert player["career"]["adj_ma"] == pytest.approx(
            sum(row["adj_ma"] for row in player["season_rows"])
        )
    build(site_dataset, tmp_path / "adjusted", ratings_dir=ratings)
    assert not (tmp_path / "adjusted" / "roles.html").exists()
    neutral = stats_context(site_dataset, ratings_dir=tmp_path / "absent")
    assert not neutral["ratings_available"]
    for player in neutral["players"]:
        assert player["career"]["adj_ma"] == pytest.approx(player["career"]["ma"])
    build(site_dataset, tmp_path / "neutral", ratings_dir=tmp_path / "absent")
    assert "ratings are unavailable" in (tmp_path / "neutral" / "advanced.html").read_text().lower()


def test_summary_adjustment_uses_player_weights_and_missing_game_fallback(
    site_dataset, tmp_path, monkeypatch
):
    from oozedle.advanced import Difficulty

    ratings = tmp_path / "ratings"
    ratings.mkdir()
    for year in (2024, 2025, 2026):
        (ratings / f"{year}.csv").write_text(
            "# data through May 4; source fixture\n"
            "rank,team,record,rating\n1,Ooze,1-1,1000\n2,SJSU,1-1,1500\n"
            "3,Chico,1-1,500\n"
        )
    (ratings / "aliases.yml").write_text("ooze: Ooze\nopponents:\n  SJSU: SJSU\n  Chico: Chico\n")
    # Preserve Ben's authoritative Summary totals but remove all per-game records.
    ds = site_dataset
    ds.player_games = ds.player_games[ds.player_games.player_id != "ben"].copy()
    ada_2024 = (ds.player_games.player_id == "ada") & (ds.player_games.season == 2024)
    ds.player_games.loc[ada_2024, "points_played"] = [1, 3, 8]
    fit = Difficulty(0, -0.001, 6, 6, 1, -500, 500, 0)
    monkeypatch.setattr("oozedle.site.fit_difficulty", lambda *_: fit)
    context = stats_context(ds, ratings_dir=ratings)
    tournament = next(t for t in context["tournaments"] if t["season"] == 2024)
    by_player = {line["player_id"]: line for line in tournament["box"]}
    factors = [game["factor"] for game in tournament["games_list"]]
    assert by_player["ada"]["adj_ma"] == pytest.approx(
        by_player["ada"]["ma"] * sum(p * f for p, f in zip([1, 3, 8], factors)) / 12
    )
    points = [game["goals_for"] + game["goals_against"] for game in tournament["games_list"]]
    assert by_player["ben"]["adj_ma"] == pytest.approx(
        by_player["ben"]["ma"] * sum(p * f for p, f in zip(points, factors)) / sum(points)
    )
    assert by_player["ben"]["adj_ma"] != pytest.approx(by_player["ben"]["ma"] * sum(factors) / 3)


def test_plays_most_like_neighbors(site_dataset, tmp_path):
    ds = site_dataset
    ds.player_tournaments["points_played"] *= 10
    context = stats_context(ds, ratings_dir=tmp_path / "absent")
    for player in context["players"]:
        if player["career"]["points_played"] < 60:
            assert "most_like" not in player
            continue
        assert len(player["most_like"]) == 3
        assert all(row["player_id"] != player["player_id"] for row in player["most_like"])
