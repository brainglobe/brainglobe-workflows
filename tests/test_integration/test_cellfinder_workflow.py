import json
import subprocess
import sys
from pathlib import Path

from brainglobe_workflows.cellfinder import CellfinderConfig


def test_run_with_default_config(tmp_path, default_json_config_path):
    """Test workflow run with no command line arguments

    If no command line arguments are provided, the default
    config at brainglobe_workflows/cellfinder/default_config.json
    should be used.

    After the workflow is run we check that:
    - there are no errors (via returncode),
    - the logs reflect the default config file was used, and
    - a single output directory exists with the expected
      output file inside it

    Parameters
    ----------
    tmp_path : Path
        path to a pytest-generated temporary directory.
    """

    # run workflow with no CLI arguments,
    # with cwd=tmp_path
    subprocess_output = subprocess.run(
        [
            sys.executable,
            Path(__file__).resolve().parents[2]
            / "workflows"
            / "cellfinder.py",
        ],
        cwd=tmp_path,  # -------------------
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
    )

    # check returncode
    assert subprocess_output.returncode == 0

    # check logs
    assert "Using default config file" in subprocess_output.stdout

    # Check one output directory exists and has expected
    # output file inside it
    assert_outputs(default_json_config_path, tmp_path)


def test_run_with_GIN_data(
    path_to_config_fetch_GIN,
):
    """Test workflow runs when passing a config that fetches data
    from the GIN repository

    After the workflow is run we check that:
    - there are no errors (via returncode),
    - the logs reflect the input config file was used,
    - the logs reflect the data was downloaded from GIN, and
    - a single output directory exists with the expected
      output file inside it

    Parameters
    ----------
    tmp_path : Path
        path to a pytest-generated temporary directory.
    """
    # run workflow with CLI and capture log
    subprocess_output = subprocess.run(
        [
            sys.executable,
            Path(__file__).resolve().parents[2]
            / "workflows"
            / "cellfinder.py",
            "--config",
            str(path_to_config_fetch_GIN),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
    )

    # check returncode
    assert subprocess_output.returncode == 0

    # check logs
    assert (
        f"Input config read from {str(path_to_config_fetch_GIN)}"
        in subprocess_output.stdout
    )
    assert (
        "Fetching input data from the provided GIN repository"
        in subprocess_output.stdout
    )

    # check one output directory exists and
    # has expected output file inside it
    assert_outputs(path_to_config_fetch_GIN)


def test_run_with_local_data(
    path_to_config_fetch_local,
):
    """Test workflow runs when passing a config that uses
    local data

    After the workflow is run we check that:
    - there are no errors (via returncode),
    - the logs reflect the input config file was used,
    - the logs reflect the data was found locally, and
    - a single output directory exists with the expected
      output file inside it

    Parameters
    ----------
    tmp_path : Path
        path to a pytest-generated temporary directory.
    """

    # run workflow with CLI
    subprocess_output = subprocess.run(
        [
            sys.executable,
            Path(__file__).resolve().parents[2]
            / "workflows"
            / "cellfinder.py",
            "--config",
            str(path_to_config_fetch_local),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
    )

    # check returncode
    assert subprocess_output.returncode == 0

    # check logs
    assert (
        f"Input config read from {str(path_to_config_fetch_local)}"
        in subprocess_output.stdout
    )
    assert (
        "Fetching input data from the local directories"
        in subprocess_output.stdout
    )

    # check one output directory exists and
    # has expected output file inside it
    assert_outputs(path_to_config_fetch_local)


def assert_outputs(path_to_config, parent_dir_of_install_path=""):
    """Helper function to determine whether the output is
    as expected.

    It checks that:
     - a single output directory exists, and
     - the expected output file exists inside it

    Note that config.output_path is only defined after the workflow
    setup is run, because its name is timestamped. Therefore,
    we search for an output directory based on config.output_path_basename.

    Parameters
    ----------
    path_to_config : Path
        path to the input config used to generate the
        output.

    parent_dir_of_install_path : str, optional
        If the install_path in the input config is relative to the
        directory the script is launched from (as is the case in the
        default_config.json file), the absolute path to its parent_dir
        must be specified here. If the paths to install_path is
        absolute, this input is not required. By default "".
    """

    # load input config
    with open(path_to_config) as config:
        config_dict = json.load(config)
    config = CellfinderConfig(**config_dict)

    # check one output directory exists and
    # it has expected output file inside it
    output_path_without_timestamp = (
        Path(parent_dir_of_install_path)
        / config.install_path
        / config.output_path_basename_relative
    )
    output_path_timestamped = [
        x
        for x in output_path_without_timestamp.parent.glob("*")
        if x.is_dir() and x.name.startswith(output_path_without_timestamp.name)
    ]

    assert len(output_path_timestamped) == 1
    assert (output_path_timestamped[0]).exists()
    assert (
        output_path_timestamped[0] / config.detected_cells_filename
    ).is_file()
