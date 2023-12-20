"""Pytest fixtures shared across unit and integration tests"""


from pathlib import Path

import pytest

# @pytest.fixture()
# def default_input_config_cellfinder() -> Path:  # do I need this?
#     """Return path to default input config for cellfinder workflow

#     Returns
#     -------
#     Path
#         Path to default input config

#     """
#     from brainglobe_workflows.utils import
# DEFAULT_JSON_CONFIG_PATH_CELLFINDER

#     return DEFAULT_JSON_CONFIG_PATH_CELLFINDER


@pytest.fixture(autouse=True)
def mock_home_directory(monkeypatch: pytest.MonkeyPatch):
    # define mock home path
    home_path = Path.home()  # actual home path
    mock_home_path = home_path / ".brainglobe-tests"  # tmp_path  #

    # create dir if it doesn't exist
    if not mock_home_path.exists():
        mock_home_path.mkdir()

    # monkeypatch Path.home() to point to the mock home
    def mock_home():
        return mock_home_path

    monkeypatch.setattr(Path, "home", mock_home)


# @pytest.fixture()  # Do I need this?
# def input_configs_dir() -> Path:
#     """Return the directory path to the input configs
#     used for testing

#     Returns
#     -------
#     Path
#         Test data directory path
#     """
#     return Path(__file__).parents[1] / "data"
