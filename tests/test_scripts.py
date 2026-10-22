from __future__ import annotations

import pytest

from oozedle.drive import SyncResult
from scripts import check_data, sync_data


@pytest.mark.parametrize("has_local, expected", [(False, 1), (True, 0)])
def test_sync_exit_for_affected_season(tmp_path, monkeypatch, capsys, has_local, expected):
    if has_local:
        season = tmp_path / "2024"
        season.mkdir()
        (season / "existing.xlsx").write_bytes(b"old")
    output = tmp_path / "github-output"
    result = SyncResult(failed=["PDQ Stats"], failed_seasons=[2024], fingerprint="abc")
    monkeypatch.setattr(sync_data, "RAW_DIR", tmp_path)
    monkeypatch.setattr(sync_data, "sync", lambda force: result)
    monkeypatch.setattr("sys.argv", ["sync_data.py"])
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    assert sync_data.main() == expected
    assert "PDQ Stats" in capsys.readouterr().out
    assert output.read_text() == "fingerprint=abc\n"


def test_fingerprint_does_not_sync(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["sync_data.py", "--fingerprint"])
    monkeypatch.delenv("GITHUB_OUTPUT", raising=False)
    monkeypatch.setattr(sync_data, "listing_fingerprint", lambda: "abc")

    def unexpected_sync(**kwargs):
        pytest.fail("Fingerprint mode must not download")

    monkeypatch.setattr(sync_data, "sync", unexpected_sync)
    assert sync_data.main() == 0
    assert capsys.readouterr().out == "abc\n"


def test_check_data_prints_and_exports(tmp_path, monkeypatch, capsys):
    from conftest import make_layout_a

    from oozedle.dataset import build_dataset

    season = tmp_path / "2024"
    season.mkdir()
    make_layout_a(season / "PDQ Stats.xlsx")
    dataset = build_dataset(tmp_path, [], {})
    output = tmp_path / "csv"
    monkeypatch.setattr(check_data, "build_dataset", lambda: dataset)
    monkeypatch.setattr("sys.argv", ["check_data.py", "--csv", str(output)])
    assert check_data.main() == 0
    printed = capsys.readouterr().out
    assert "PDQ: 1-2" in printed
    assert "2 players, 3 games, 4 player_games" in printed
    assert "Warning:" in printed
    assert len(list(output.glob("*.csv"))) == 5
