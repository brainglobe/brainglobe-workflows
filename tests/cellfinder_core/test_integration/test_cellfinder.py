import subprocess
import sys
from pathlib import Path
from brainglobe_workflows.cellfinder_core.cellfinder_core import main
import pytest
from typing import Optional


def test_main():
    """Test main function for setting up and running cellfinder workflow
    without inputs
    """

    # run main
    cfg = main()

    # check output files exist
    assert Path(cfg._detected_cells_path).is_file()


@pytest.mark.parametrize(
    "input_config",
    [
        None,
        # "input_config_fetch_GIN",
        # "input_config_fetch_local",
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
    # monkeypatch to change current directory to
    # pytest temporary directory
    # (cellfinder cache directory is created in cwd)
    # monkeypatch.chdir(tmp_path)

    # run main
    cfg = main(str(request.getfixturevalue(input_config)))

    # check output files exist
    assert Path(cfg._detected_cells_path).is_file()


def test_script():
    """Test running the cellfinder worklfow from the command line
    without inputs
    """

    # define CLI input
    script_path = (
        Path(__file__).resolve().parents[3]
        / "brainglobe_workflows"
        / "cellfinder_core"
        / "cellfinder_core.py"
    )
    subprocess_input = [
        sys.executable,
        str(script_path),
    ]

    # run workflow script from the CLI
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
    # monkeypatch to change current directory to
    # pytest temporary directory
    # (cellfinder cache directory is created in cwd)
    # monkeypatch.chdir(tmp_path)

    # define CLI input
    subprocess_input = ["cellfinder-workflow"]

    # run workflow with no CLI arguments,
    subprocess_output = subprocess.run(
        subprocess_input,
    )

    # check returncode
    assert subprocess_output.returncode == 0