import json
import subprocess
from pathlib import Path

import pytest
from asv import util


@pytest.fixture()
def asv_config_monkeypatched_path(tmp_path: Path) -> Path:
    """
    Create a monkeypatched asv.conf.json file
    in a Pytest-generated temporary directory
    and return its path

    Parameters
    ----------
    tmp_path : Path
        path to pytest-generated temporary directory

    Returns
    -------
    Path
        Path to monkeypatched asv config file
    """
    # read reference asv config
    asv_original_path = Path(__file__).resolve().parents[2] / "asv.conf.json"
    asv_monkeypatched_dict = util.load_json(
        asv_original_path, js_comments=True
    )

    # point to benchmarks directory in config
    asv_monkeypatched_dict["benchmark_dir"] = str(
        Path(__file__).resolve().parents[2] / "benchmarks"
    )

    # change env, results and html directories
    for ky in ["env_dir", "results_dir", "html_dir"]:
        asv_monkeypatched_dict[ky] = str(
            Path(tmp_path) / asv_monkeypatched_dict[ky]
        )

    # ensure repo points to URL
    asv_monkeypatched_dict[
        "repo"
    ] = "https://github.com/brainglobe/brainglobe-workflows.git"

    # define path to a temp json file to dump config data
    asv_monkeypatched_path = tmp_path / "asv.conf.json"

    # save monkeypatched config data to json file
    with open(asv_monkeypatched_path, "w") as js:
        json.dump(asv_monkeypatched_dict, js)

    # check json file exists
    assert asv_monkeypatched_path.is_file()

    return asv_monkeypatched_path


def test_asv_run(asv_config_monkeypatched_path: Path):
    asv_machine_output = subprocess.run(
        [
            "asv",
            "machine",
            "--yes",
            "--config",
            str(asv_config_monkeypatched_path),  # use monkeypatched config
        ]
    )
    assert asv_machine_output.returncode == 0

    asv_benchmark_output = subprocess.run(
        [
            "asv",
            "run",
            "--quick",  # each benchmark function is run only once
            "--config",
            str(asv_config_monkeypatched_path),
        ],
    )
    assert asv_benchmark_output.returncode == 0


def test_asv_run_machine_specific(
    asv_config_monkeypatched_path: Path,
):
    # setup machine
    asv_specific_machine_name = "CURRENT_MACHINE"
    asv_machine_output = subprocess.run(
        [
            "asv",
            "machine",
            "--machine",
            asv_specific_machine_name,  # name of the current machine
            "--yes",
            "--config",
            str(asv_config_monkeypatched_path),  # use monkeypatched config
        ]
    )
    assert asv_machine_output.returncode == 0

    # run benchmarks on machine
    asv_benchmark_output = subprocess.run(
        [
            "asv",
            "run",
            "--quick",  # each benchmark function is run only once
            "--config",
            str(asv_config_monkeypatched_path),
            "--machine",
            asv_specific_machine_name,
        ],
    )
    assert asv_benchmark_output.returncode == 0
