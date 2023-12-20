import subprocess
import sys
from pathlib import Path
from brainglobe_workflows.cellfinder_core.cellfinder_core import main


def test_main():
    """Test main function for setting up and running cellfinder workflow
    without inputs
    """

    # run main
    cfg = main()

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
    without inputs
    """

    # define CLI input
    subprocess_input = ["cellfinder-workflow"]

    # run workflow with no CLI arguments,
    subprocess_output = subprocess.run(
        subprocess_input,
    )

    # check returncode
    assert subprocess_output.returncode == 0
