"""Offline site builds and link integrity across both workbook layouts."""

import json
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
