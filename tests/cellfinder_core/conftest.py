"""Pytest fixtures shared across unit and integration tests"""


from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def mock_home_directory(monkeypatch: pytest.MonkeyPatch):
    # define mock home path
    home_path = Path.home()  # actual home path
    mock_home_path = home_path / ".brainglobe-tests"

    # create directory if it doesn't exist
    if not mock_home_path.exists():
        mock_home_path.mkdir()

    # monkeypatch Path.home() to point to the mock home
    def mock_home():
        return mock_home_path

    monkeypatch.setattr(Path, "home", mock_home)
