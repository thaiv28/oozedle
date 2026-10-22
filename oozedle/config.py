"""Paths and source folders for the stats data."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
MANIFEST = RAW_DIR / "manifest.json"
PLAYERS_FILE = ROOT / "players.yml"
OUTPUT_DIR = ROOT / "output"
SEASON_FOLDERS: dict[int, str] = {
    2024: "1yoSAskG38yq8k9PalbrivHZopKhkucUv",
    2025: "1V5zom_cnQYJZT7W7IIkdaoD3Ilfjia5j",
    2026: "1R7Ep1Ne-3GV0GjlniSRIDBjnqtsr9YNA",
}
