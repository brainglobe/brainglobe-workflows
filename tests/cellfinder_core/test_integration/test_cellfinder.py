import subprocess
import sys
from pathlib import Path
from typing import Optional

import pytest

from brainglobe_workflows.cellfinder_core.cellfinder import main


@pytest.mark.parametrize(
    "input_config",
    [
        None,
        "input_config_fetch_GIN",
        "input_config_fetch_local",
    ],
)
def test_main(
    input_config: Optional[str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    request: pytest.FixtureRequest,
):
    """Test main function for setting up and running cellfinder workflow

    Parameters
    ----------
    input_config : Optional[str]
        Path to input config json file
    monkeypatch : pytest.MonkeyPatch
        Pytest fixture to use monkeypatching utils
    tmp_path : Path
        Pytest fixture providing a temporary path for each test
    request : pytest.FixtureRequest
        Pytest fixture to enable requesting fixtures by name
    """
    # monkeypatch to change current directory to
    # pytest temporary directory
    # (cellfinder cache directory is created in cwd)
    monkeypatch.chdir(tmp_path)

    # run main
    if not input_config:
        cfg = main()
    else:
        cfg = main(str(request.getfixturevalue(input_config)))

    # check output files exist
    assert Path(cfg.detected_cells_path).is_file()


@pytest.mark.parametrize(
    "input_config",
    [
        None,
        "input_config_fetch_GIN",
        "input_config_fetch_local",
    ],
)
def test_script(
    input_config: Optional[str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    request: pytest.FixtureRequest,
):
    """Test running the cellfinder worklfow from the command line

    Parameters
    ----------
    input_config : Optional[str]
        Path to input config json file
    monkeypatch : pytest.MonkeyPatch
        Pytest fixture to use monkeypatching utils
    tmp_path : Path
        Pytest fixture providing a temporary path for each test
    request : pytest.FixtureRequest
        Pytest fixture to enable requesting fixtures by name
    """
    # monkeypatch to change current directory to
    # pytest temporary directory
    # (cellfinder cache directory is created in cwd)
    monkeypatch.chdir(tmp_path)

    # define CLI input
    script_path = (
        Path(__file__).resolve().parents[3]
        / "brainglobe_workflows"
        / "cellfinder_core"
        / "cellfinder.py"
    )
    subprocess_input = [
        sys.executable,
        str(script_path),
    ]
    # append config if required
    if input_config:
        subprocess_input.append("--config")
        subprocess_input.append(str(request.getfixturevalue(input_config)))

    # run workflow script from the CLI
    subprocess_output = subprocess.run(
        subprocess_input,
    )

    # check returncode
    assert subprocess_output.returncode == 0


@pytest.mark.parametrize(
    "input_config",
    [
        None,
        "input_config_fetch_GIN",
        "input_config_fetch_local",
    ],
)
def test_entry_point(
    input_config: Optional[str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    request: pytest.FixtureRequest,
):
    """Test running the cellfinder workflow via the predefined entry point

    Parameters
    ----------
    input_config : Optional[str]
        Path to input config json file
    monkeypatch : pytest.MonkeyPatch
        Pytest fixture to use monkeypatching utils
    tmp_path : Path
        Pytest fixture providing a temporary path for each test
    request : pytest.FixtureRequest
        Pytest fixture to enable requesting fixtures by name
    """
    # monkeypatch to change current directory to
    # pytest temporary directory
    # (cellfinder cache directory is created in cwd)
    monkeypatch.chdir(tmp_path)

    # define CLI input
    subprocess_input = ["cellfinder-workflow"]
    # append config if required
    if input_config:
        subprocess_input.append("--config")
        subprocess_input.append(str(request.getfixturevalue(input_config)))

    # run workflow with no CLI arguments,
    subprocess_output = subprocess.run(
        subprocess_input,
    )

    # check returncode
    assert subprocess_output.returncode == 0
