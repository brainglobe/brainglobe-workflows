import json
import subprocess
from pathlib import Path

import pytest
from asv import util


@pytest.fixture()
def asv_config_monkeypatched_path(tmp_path):
    """Create a monkeypatched asv.conf.json file
    in tmp_path and return its path

    Parameters
    ----------
    tmp_path : Path
        path to pytest-generated temporary directory


    Returns
    -------
    _type_
        _description_
    """
    # read reference asv config
    asv_original_path = Path(__file__).resolve().parents[3] / "asv.conf.json"
    asv_monkeypatched_dict = util.load_json(
        asv_original_path, js_comments=True
    )

    # change directories
    for ky in ["env_dir", "results_dir", "html_dir"]:
        asv_monkeypatched_dict[ky] = str(
            Path(tmp_path) / asv_monkeypatched_dict[ky]
        )

    # change repo to URL rather than local
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

    return str(asv_monkeypatched_path)


@pytest.mark.skip(reason="will be worked on a separate PR")
def test_run_benchmarks(asv_config_monkeypatched_path):
    # --- ideally monkeypatch an asv config so that results are in tmp_dir?

    # set up machine (env_dir, results_dir, html_dir)
    asv_machine_output = subprocess.run(
        [
            "asv",
            "machine",
            "--yes",
            "--config",
            asv_config_monkeypatched_path,
        ]
    )
    assert asv_machine_output.returncode == 0

    # run benchmarks
    asv_benchmark_output = subprocess.run(
        [
            "asv",
            "run",
            "--config",
            asv_config_monkeypatched_path,
            # "--dry-run"
            # # Do not save any results to disk? not truly testing then
        ],
        cwd=str(
            Path(asv_config_monkeypatched_path).parent
        ),  # run from where asv config is
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
    )
    # STDOUT: "· Cloning project\n· Fetching recent changes\n·
    # Creating environments\n· No __init__.py file in 'benchmarks'\n"

    # check returncode
    assert asv_benchmark_output.returncode == 0

    # check logs?

    # delete directories?
    # check teardown after yield:
    # https://docs.pytest.org/en/6.2.x/fixture.html#yield-fixtures-recommended
