import subprocess
from pathlib import Path
import pytest
from typing import Optional


def test_main():
    """
    Test main function for setting up and running cellfinder workflow
    with no inputs
    """
    # import inside the test function so that required functions are
    # monkeypatched first
    from brainglobe_workflows.cellfinder_core.cellfinder_core import main

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
    """
    Test main function for setting up and running cellfinder workflow
    with inputs

    Parameters
    ----------
    input_config : Optional[str]
        Path to input config JSON file
    request : pytest.FixtureRequest
        Pytest fixture to enable requesting fixtures by name
    """
    from brainglobe_workflows.cellfinder_core.cellfinder_core import main

    # run main
    cfg = main(str(request.getfixturevalue(input_config)))

    # check output files exist
    assert Path(cfg._detected_cells_path).is_file()


def test_entry_point_help():
    """
    Smoke test the cellfinder workflow entry point by checking
    help is printed out successfully
    """

    # define CLI input
    subprocess_input = ["cellfinder-workflow", "--help"]

    # run workflow
    subprocess_output = subprocess.run(
        subprocess_input,
    )

    # check returncode
    assert subprocess_output.returncode == 0