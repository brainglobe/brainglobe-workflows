import subprocess
import sys
from pathlib import Path

import pytest

from brainglobe_workflows.cellfinder import main


# TODO: test main with default and custom json (local and GIN)?
def test_main(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    """Test main function for setting up and running cellfinder workflow

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Pytest fixture to use monkeypatching utils
    tmp_path : Path
        Pytest fixture providing a temporary path for each test
    """
    # monkeypatch to change current directory to
    # pytest temporary directory
    # (cellfinder cache directory is created in cwd)
    monkeypatch.chdir(tmp_path)

    # run main
    cfg = main()

    # check output files are those expected?
    assert (cfg.detected_cells_path).is_file()


# TODO: test main CLI with default and specific json?
def test_app_wrapper(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    """Test running the cellfinder worklfow from the command line

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Pytest fixture to use monkeypatching utils
    tmp_path : Path
        Pytest fixture providing a temporary path for each test
    """
    # monkeypatch to change current directory to
    # pytest temporary directory
    # (cellfinder cache directory is created in cwd)
    monkeypatch.chdir(tmp_path)

    # run workflow script with no CLI arguments,
    subprocess_output = subprocess.run(
        [
            sys.executable,
            Path(__file__).resolve().parents[3]
            / "brainglobe_workflows"
            / "cellfinder.py",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
    )

    # check returncode
    assert subprocess_output.returncode == 0


# TODO: test main CLI with default and specific json?
def test_main_entry_point(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    """Test running the cellfinder workflow via the predefined entry point

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Pytest fixture to use monkeypatching utils
    tmp_path : Path
        Pytest fixture providing a temporary path for each test
    """
    #  monkeypatch to change current directory to
    # pytest temporary directory
    # (cellfinder cache directory is created in cwd)
    monkeypatch.chdir(tmp_path)

    # run workflow with no CLI arguments,
    subprocess_output = subprocess.run(
        ["cellfinder-workflow"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
    )

    # check returncode
    assert subprocess_output.returncode == 0
