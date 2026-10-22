from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from openpyxl import Workbook

from oozedle import drive


def file(id="one", name="PDQ Stats", modified=None):
    return drive.DriveFile(id, name, drive.SHEETS, datetime(2024, 1, 1, tzinfo=UTC), modified)


def test_parse_html():
    entry = [None] * 11
    entry[0], entry[2], entry[3] = "one", "Café Stats".encode().decode("latin1"), drive.SHEETS
    entry[9], entry[10] = 1704067200000, 0
    folder = entry.copy()
    folder[0], folder[2], folder[3] = "folder", "Nested", "application/vnd.google-apps.folder"
    escaped = json.dumps([[entry, folder]], ensure_ascii=True).replace("\\", "\\\\")
    files = drive.parse_folder_html(f"<script>window['_DRIVE_ivd'] = '{escaped}';</script>")
    assert files[0].name == "Café Stats"
    assert files[0].created == datetime(2024, 1, 1, tzinfo=UTC)
    assert files[0].modified is None
    assert files[1].mime == "application/vnd.google-apps.folder"
    assert drive.parse_folder_html("<script>window['_DRIVE_ivd'] = '[null]';</script>") == []
    with pytest.raises(RuntimeError, match="missing _DRIVE_ivd"):
        drive.parse_folder_html("<html></html>")


@pytest.fixture
def local_drive(tmp_path, monkeypatch):
    monkeypatch.setattr(drive, "RAW_DIR", tmp_path)
    monkeypatch.setattr(drive, "MANIFEST", tmp_path / "manifest.json")
    return tmp_path


def test_sync_changes_removal_failure_manifest(local_drive, monkeypatch):
    listing = [file(), file("two", "Other Stats")]
    calls = []
    monkeypatch.setattr(drive, "list_folder", lambda folder: listing)

    def download(item, dest):
        calls.append(item.id)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(item.id)

    monkeypatch.setattr(drive, "download", download)
    result = drive.sync(seasons={2024: "folder"})
    assert len(result.downloaded) == 2
    assert result.fingerprint == drive.listing_fingerprint({2024: "folder"})
    assert len(drive.sync(seasons={2024: "folder"}).unchanged) == 2
    assert calls == ["one", "two"]
    listing[:] = [file(modified=datetime(2024, 2, 1, tzinfo=UTC))]
    result = drive.sync(seasons={2024: "folder"})
    assert result.downloaded == ["PDQ Stats"]
    assert result.removed == ["Other Stats.xlsx"]
    previous = json.loads(drive.MANIFEST.read_text())
    assert previous["files"][0]["path"] == "2024/PDQ Stats.xlsx"
    assert previous["files"][0]["modified"] == "2024-02-01T00:00:00+00:00"
    listing[:] = [file(modified=datetime(2024, 3, 1, tzinfo=UTC))]
    monkeypatch.setattr(drive, "download", lambda *args: (_ for _ in ()).throw(OSError("bad")))
    with pytest.warns(UserWarning, match="Could not download"):
        result = drive.sync(seasons={2024: "folder"})
    assert result.failed == ["PDQ Stats"]
    assert (local_drive / "2024/PDQ Stats.xlsx").read_text() == "one"
    assert json.loads(drive.MANIFEST.read_text()) == previous
    monkeypatch.setattr(drive, "list_folder", lambda *args: (_ for _ in ()).throw(OSError("bad")))
    with pytest.warns(UserWarning, match="Could not list"):
        result = drive.sync(seasons={2024: "folder"})
    assert result.failed == ["2024"]
    assert json.loads(drive.MANIFEST.read_text()) == previous


def test_download_atomic_retries(tmp_path, monkeypatch):
    dest = tmp_path / "stats.xlsx"
    dest.write_text("old")
    calls = []
    monkeypatch.setattr(drive.time, "sleep", lambda seconds: None)

    def bad_download(**kwargs):
        calls.append(kwargs)
        Path(kwargs["output"]).write_text("partial")
        return kwargs["output"]

    monkeypatch.setattr(drive.gdown, "download", bad_download)
    with pytest.raises(Exception):
        drive.download(file(), dest)
    assert len(calls) == 3
    assert dest.read_text() == "old"
    assert list(tmp_path.iterdir()) == [dest]

    def good_download(**kwargs):
        book = Workbook()
        book.save(kwargs["output"])
        return kwargs["output"]

    monkeypatch.setattr(drive.gdown, "download", good_download)
    drive.download(file(), dest)
    assert dest.read_bytes().startswith(b"PK")


def test_list_folder_retries(monkeypatch):
    class Response:
        text = "<script>window['_DRIVE_ivd']='[null]';</script>"

        def raise_for_status(self):
            pass

    class Session:
        calls = 0

        def get(self, url, **kwargs):
            assert kwargs["timeout"] == 30
            assert "User-Agent" in kwargs["headers"]
            self.calls += 1
            if self.calls < 3:
                raise OSError("offline transient")
            return Response()

    sleeps = []
    monkeypatch.setattr(drive.time, "sleep", sleeps.append)
    session = Session()
    assert drive.list_folder("folder", session) == []
    assert session.calls == 3
    assert sleeps == [10, 10]
