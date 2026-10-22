"""Offline rating joins, neutral handling, and difficulty regression."""

from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from oozedle.advanced import Difficulty, fit_difficulty
from oozedle.ratings import game_ratings, load_aliases, load_ratings


def test_load_and_join(tmp_path):
    (tmp_path / "2026.csv").write_text(
        "# USAU college; data through May 4; source https://example.test\n"
        "rank,team,record,rating\n1,Strong,3-0,1500\n2,Ooze,2-1,1000\n3,Other,1-2,500\n"
    )
    path = tmp_path / "aliases.yml"
    path.write_text("ooze: Ooze\nopponents:\n  A: Strong\n  B: null\n  C: Absent\n")
    ratings = load_ratings(tmp_path)
    assert ratings[2026].as_of == "May 4"
    assert ratings[2026].source == "https://example.test"
    assert ratings[2026].ranks["Ooze"] == 2
    games = pd.DataFrame(
        dict(game_id=list("abcde"), season=[2026] * 4 + [2025], opponent=list("ABCDE"))
    )
    result = game_ratings(SimpleNamespace(games=games), ratings, load_aliases(path))
    assert result.loc["a", "gap"] == 500
    assert result.loc[list("bcde"), "gap"].isna().all()
    assert load_ratings(tmp_path / "absent") == {}
    assert load_aliases(tmp_path / "absent.yml") == ("", {})


def test_factor_clamps_and_neutral():
    fit = Difficulty(0, -0.001, 4, 4, 1, -500, 500, 20)
    assert fit.factor(np.nan) == 1
    assert fit.factor(-1000) == fit.factor(-500)
    assert fit.factor(1000) == fit.factor(500)
    assert fit.factor(20) == 1
    assert fit.factor(np.inf) == fit.factor(500)
    assert fit.factor(-np.inf) == fit.factor(-500)


def test_fit_recovers_exponential():
    gaps = np.array([-500, -100, 0, 200, 500, 700.0])
    a, b = -0.7, -0.0012
    games = pd.DataFrame(dict(game_id=list("abcdef"), goals_for=[10] * 6, goals_against=[10] * 6))
    values = 20 * np.exp(a + b * gaps)
    # The final game has nonpositive MA, remains rated, and is excluded from fitting.
    values[-1] = -1
    lines = pd.DataFrame(dict(game_id=games.game_id, assists=values))
    ds = SimpleNamespace(games=games, player_games=lines)
    rated = pd.DataFrame(dict(gap=gaps), index=games.game_id)
    fit = fit_difficulty(ds, dict(assists=1), rated)
    assert fit.a == pytest.approx(a)
    assert fit.b == pytest.approx(b)
    assert fit.r2 == pytest.approx(1)
    assert fit.n_rated == 6 and fit.n_fit == 5
    assert fit.gap_max == 700
    assert fit.gap_mean == pytest.approx(gaps.mean())
