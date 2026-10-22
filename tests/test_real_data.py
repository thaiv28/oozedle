from __future__ import annotations

import pytest

from oozedle.config import MANIFEST
from oozedle.dataset import build_dataset


@pytest.mark.skipif(not MANIFEST.exists(), reason="No synchronized local manifest")
def test_real_data():
    dataset = build_dataset()
    assert len(dataset.tournaments) >= 17
    assert dataset.tournaments.season.nunique() == 3
