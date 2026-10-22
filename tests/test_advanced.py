"""Offline model recovery and advanced-stat rendering."""

import json

import numpy as np
import pandas as pd
import pytest
from conftest import make_layout_a

from oozedle.advanced import fit, game_totals, margin_added, per10, plus_minus
from oozedle.dataset import build_dataset
from oozedle.site import build, stats_context


def test_fit_recovers_coefficients():
    rng = np.random.default_rng(42)
    x = rng.normal(size=(150, 3))
    design = np.column_stack([np.ones(len(x)), x])
    noise = rng.normal(scale=0.001, size=len(x))
    # Remove its projection so the tiny noise cannot shift the known coefficients.
    noise -= design @ np.linalg.lstsq(design, noise, rcond=None)[0]
    coefficients = np.array([1.3, 0.35, -0.17])
    frame = pd.DataFrame(x, columns=["S", "blocks", "turnovers"])
    frame["margin"] = 2 + x @ coefficients + noise
    result = fit(frame, frame.columns[:3])
    assert np.allclose(result.coef, coefficients, atol=0.05)
    assert result.intercept == pytest.approx(2, abs=0.05)
    assert np.all(np.array(result.low) < coefficients)
    assert np.all(np.array(result.high) > coefficients)
    assert result.r2 > 0.99 and result.cv_r2 > 0.99
    assert result.n == 150
    assert result == fit(frame, frame.columns[:3])


def test_stat_helpers():
    row = dict(assists=2, goals=3, blocks=1, turnovers=8)
    weights = dict(assists=0.5, goals=0.5, blocks=0.3, turnovers=-0.2)
    assert plus_minus(row) == -2
    assert margin_added(row, weights) == pytest.approx(1.2)
    assert per10(12, 19) is None
    assert per10(12, 0) is None
    assert per10(12, 20) == 6
    assert per10(-2, 25) == -0.8


def test_advanced_build(tmp_path):
    raw = tmp_path / "raw" / "2024"
    raw.mkdir(parents=True)
    make_layout_a(raw / "Test Stats.xlsx")
    ds = build_dataset(raw.parent, manifest=[], aliases={})
    totals = game_totals(ds)
    assert totals.assists.sum() == ds.player_games.assists.sum()
    assert totals.margin.iloc[0] == 5.5
    context = stats_context(ds)
    payload = json.loads(context["players_json"])
    assert set(payload["weights"]) == {"assists", "goals", "blocks", "turnovers"}
    for player in context["players"]:
        assert player["career"]["plus_minus"] == plus_minus(player["career"])
        assert player["career"]["ma"] == pytest.approx(
            margin_added(player["career"], payload["weights"])
        )
    out = tmp_path / "output"
    build(ds, out)
    assert (out / "advanced.html").is_file()
    assert '"weights":' in (out / "players.html").read_text()
    assert 'data-view="advanced"' in (out / "players.html").read_text()
