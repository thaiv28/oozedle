"""Download and reconcile season folders with a local manifest."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import time
import warnings
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import gdown
import requests
from bs4 import BeautifulSoup
from openpyxl import load_workbook

from oozedle.config import MANIFEST, RAW_DIR, SEASON_FOLDERS

SHEETS = "application/vnd.google-apps.spreadsheet"
XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@dataclass(frozen=True)
class DriveFile:
    id: str
    name: str
    mime: str
    created: datetime | None
    modified: datetime | None


@dataclass
class SyncResult:
    downloaded: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    fingerprint: str = ""
    failed_seasons: list[int] = field(default_factory=list)


def _timestamp(value) -> datetime | None:
    try:
        result = datetime.fromtimestamp(int(value) / 1000, UTC)
        return result if 2010 <= result.year <= 2100 else None
    except (ValueError, TypeError, OverflowError, OSError):
        return None


def parse_folder_html(html: str) -> list[DriveFile]:
    """Decode Drive's embedded folder listing without making requests."""
    script = next(
        (
            s.get_text()
            for s in BeautifulSoup(html, "html.parser").find_all("script")
            if "_DRIVE_ivd" in s.get_text()
        ),
        None,
    )
    if script is None:
        raise RuntimeError("Google Drive folder listing is missing _DRIVE_ivd")
    strings = re.findall(r"'((?:[^'\\]|\\.)*)'", script)
    try:
        entries = json.loads(strings[1].encode().decode("unicode_escape"))[0] or []
        return [
            DriveFile(
                e[0],
                e[2].encode("raw_unicode_escape").decode("utf-8"),
                e[3],
                _timestamp(e[9]),
                _timestamp(e[10]),
            )
            for e in entries
        ]
    except (IndexError, ValueError, UnicodeError) as exc:
        raise RuntimeError("Could not decode Google Drive _DRIVE_ivd listing") from exc


def list_folder(folder_id: str, session: requests.Session | None = None) -> list[DriveFile]:
    """Fetch a public folder with bounded retries."""
    client = session or requests.Session()
    try:
        for attempt in range(3):
            try:
                response = client.get(
                    f"https://drive.google.com/drive/folders/{folder_id}?hl=en",
                    headers={"User-Agent": "Mozilla/5.0"},
                    timeout=30,
                )
                response.raise_for_status()
                return parse_folder_html(response.text)
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(10)
    finally:
        if session is None:
            client.close()
    raise RuntimeError("Folder listing failed")


def download(file: DriveFile, dest: Path) -> None:
    """Validate a temporary download before atomically replacing the local copy."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(3):
        fd, filename = tempfile.mkstemp(dir=dest.parent, suffix=".xlsx")
        os.close(fd)
        tmp = Path(filename)
        try:
            if file.mime == SHEETS:
                with warnings.catch_warnings():
                    # gdown warns that an export URL is not a Drive file link; it still downloads.
                    warnings.simplefilter("ignore", UserWarning)
                    result = gdown.download(
                        url=f"https://docs.google.com/spreadsheets/d/{file.id}/export?format=xlsx",
                        output=str(tmp),
                        quiet=True,
                    )
            elif file.mime == XLSX:
                result = gdown.download(id=file.id, output=str(tmp), quiet=True)
            else:
                raise ValueError(f"Unsupported spreadsheet MIME: {file.mime}")
            if result is None:
                raise RuntimeError(f"Download returned no file: {file.name}")
            workbook = load_workbook(tmp, read_only=True)
            workbook.close()
            os.replace(tmp, dest)
            return
        except Exception:
            if attempt == 2:
                raise
            time.sleep(10)
        finally:
            tmp.unlink(missing_ok=True)


def _iso(value: datetime | None) -> str | None:
    return value.astimezone(UTC).isoformat() if value else None


def _fingerprint(entries: list[dict]) -> str:
    listing = sorted((e["season"], e["id"], e.get("modified")) for e in entries)
    return hashlib.sha256(json.dumps(listing, separators=(",", ":")).encode()).hexdigest()


def _entry(season: int, file: DriveFile) -> dict:
    name = file.name.replace("/", "-")
    filename = name if name.endswith(".xlsx") else f"{name}.xlsx"
    return dict(
        season=season,
        id=file.id,
        name=file.name,
        mime=file.mime,
        created=_iso(file.created),
        modified=_iso(file.modified),
        path=f"{season}/{filename}",
    )


def listing_fingerprint(seasons: dict[int, str] | None = None) -> str:
    """Hash the remote spreadsheet listing without downloading files."""
    entries = [
        _entry(season, file)
        for season, folder in (SEASON_FOLDERS if seasons is None else seasons).items()
        for file in list_folder(folder)
        if file.mime in {SHEETS, XLSX}
    ]
    return _fingerprint(entries)


def sync(force: bool = False, seasons: dict[int, str] | None = None) -> SyncResult:
    """Reconcile listed spreadsheets while preserving files on remote failures."""
    folders = SEASON_FOLDERS if seasons is None else seasons
    old = json.loads(MANIFEST.read_text())["files"] if MANIFEST.exists() else []
    entries = [e for e in old if int(e["season"]) not in folders]
    listing = []
    result = SyncResult()
    for season, folder in folders.items():
        previous = [e for e in old if int(e["season"]) == season]
        try:
            files = list_folder(folder)
        except Exception as exc:
            entries.extend(previous)
            listing.extend(previous)
            result.failed.append(str(season))
            result.failed_seasons.append(season)
            warnings.warn(f"Could not list season {season}: {exc}", stacklevel=2)
            continue
        old_by_id = {e["id"]: e for e in previous}
        listed_paths = set()
        for file in files:
            if file.mime not in {SHEETS, XLSX}:
                result.skipped.append(file.name)
                continue
            entry = _entry(season, file)
            listing.append(entry)
            dest = RAW_DIR / entry["path"]
            listed_paths.add(dest)
            previous_entry = old_by_id.get(file.id)
            if (
                not force
                and dest.exists()
                and previous_entry is not None
                and previous_entry.get("modified") == entry["modified"]
            ):
                result.unchanged.append(file.name)
                entries.append(entry)
                continue
            try:
                download(file, dest)
            except Exception as exc:
                result.failed.append(file.name)
                if season not in result.failed_seasons:
                    result.failed_seasons.append(season)
                warnings.warn(f"Could not download {file.name}: {exc}", stacklevel=2)
                if previous_entry:
                    entries.append(previous_entry)
                    listed_paths.add(RAW_DIR / previous_entry["path"])
            else:
                result.downloaded.append(file.name)
                entries.append(entry)
        for path in (RAW_DIR / str(season)).glob("*.xlsx"):
            if path not in listed_paths:
                path.unlink()
                result.removed.append(path.name)
    result.fingerprint = _fingerprint(listing)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    payload = {"files": sorted(entries, key=lambda e: (e["season"], e["name"], e["id"]))}
    fd, filename = tempfile.mkstemp(dir=MANIFEST.parent, suffix=".json")
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(payload, stream, sort_keys=True, indent=2)
            stream.write("\n")
        os.replace(filename, MANIFEST)
    finally:
        Path(filename).unlink(missing_ok=True)
    return result
