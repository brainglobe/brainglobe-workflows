import subprocess
import sys
from pathlib import Path
from typing import Optional

import pytest


def test_main():
    """Test main function for setting up and running cellfinder workflow
    with no inputs

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Pytest fixture to use monkeypatching utils
    tmp_path : Path
        Pytest fixture providing a temporary path for each test
    """

    from brainglobe_workflows.cellfinder_core.cellfinder import main

    # otherwise imported before monkeypatching?
    # run main
    cfg = main()

    # check output files exist
    assert Path(cfg._detected_cells_path).is_file()


@pytest.mark.parametrize(
    "input_config",
    [
        "config_local_json",
        "config_GIN_json",
    ],
)
def test_main_w_inputs(
    input_config: Optional[str],
    request: pytest.FixtureRequest,
):
    """Test main function for setting up and running cellfinder workflow
    with inputs

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
    from brainglobe_workflows.cellfinder_core.cellfinder import main

    # run main
    cfg = main(str(request.getfixturevalue(input_config)))

    # check output files exist
    assert Path(cfg._detected_cells_path).is_file()


def test_script():
    """Test running the cellfinder worklfow from the command line
    with no inputs
    """
    from brainglobe_workflows.cellfinder_core.cellfinder import (
        __file__ as script_path,
    )

    # define CLI input
    subprocess_input = [
        sys.executable,
        str(script_path),
    ]

    # run workflow
    # Path.home() is not monkeypatched :(
    subprocess_output = subprocess.run(
        subprocess_input,
    )

    # check returncode
    assert subprocess_output.returncode == 0


@pytest.mark.parametrize(
    "input_config",
    [
        "config_local_json",
        "config_GIN_json",
    ],
)
def test_script_w_inputs(
    input_config: Optional[str],
    request: pytest.FixtureRequest,
):
    """Test running the cellfinder worklfow from the command line with inputs

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

    # path to script
    script_path = (
        Path(__file__).resolve().parents[3]
        / "brainglobe_workflows"
        / "cellfinder_core"
        / "cellfinder.py"
    )

    # define CLI input
    subprocess_input = [
        sys.executable,
        str(script_path),
    ]
    subprocess_input.append("--config")
    subprocess_input.append(str(request.getfixturevalue(input_config)))

    # run workflow
    subprocess_output = subprocess.run(
        subprocess_input,
    )

    # check returncode
    assert subprocess_output.returncode == 0


def test_entry_point():
    """Test running the cellfinder workflow via the predefined entry point
    with no inputs

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Pytest fixture to use monkeypatching utils
    tmp_path : Path
        Pytest fixture providing a temporary path for each test
    """

    # define CLI input
    subprocess_input = ["cellfinder-core-workflow"]

    # run workflow
    subprocess_output = subprocess.run(
        subprocess_input,
    )

    # check returncode
    assert subprocess_output.returncode == 0


@pytest.mark.parametrize(
    "input_config",
    [
        "config_local_json",
        "config_GIN_json",
    ],
)
def test_entry_point_w_inputs(
    input_config: Optional[str],
    request: pytest.FixtureRequest,
):
    """Test running the cellfinder workflow via the predefined entry point
    with inputs

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

    # define CLI input
    subprocess_input = ["cellfinder-core-workflow"]
    subprocess_input.append("--config")
    subprocess_input.append(str(request.getfixturevalue(input_config)))

    # run workflow
    subprocess_output = subprocess.run(
        subprocess_input,
    )

    # check returncode
    assert subprocess_output.returncode == 0
