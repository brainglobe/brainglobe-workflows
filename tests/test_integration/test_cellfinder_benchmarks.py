import json
import subprocess
from pathlib import Path

import pytest


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
    asv_original_path = Path(__file__).resolve().parents[2] / "asv.conf.json"
    with open(asv_original_path) as asv_config:
        asv_monkeypatched_dict = json.load(asv_config)

    # change directories
    for ky in ["env_dir", "results_dir", "html_dir"]:
        asv_monkeypatched_dict[ky] = str(
            Path(tmp_path) / asv_monkeypatched_dict[ky]
        )

    # define path to a temp json file to dump config data
    asv_monkeypatched_path = tmp_path / "asv.conf.json"

    # save monkeypatched config data to json file
    with open(asv_monkeypatched_path, "w") as js:
        json.dump(asv_monkeypatched_dict, js)

    # check json file exists
    assert asv_monkeypatched_path.is_file()

    return str(asv_monkeypatched_path)


def test_run_benchmarks(asv_config_monkeypatched_path):
    # --- ideally monkeypatch an asv config so that results are in tmp_dir?

    # set up machine (env_dir, results_dir, html_dir)
    subprocess.run(["asv", "machine", "--yes"])

    # run benchmarks
    subprocess_output = subprocess.run(
        [
            "asv",
            "run",
            "--config",  # --- can I pass a dict?
            asv_config_monkeypatched_path,
            # "--dry-run" # Do not save any results to disk. for now!
        ],
        # cwd=tmp_path, ---> from where asv config is
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
    )

    # check returncode
    assert subprocess_output.returncode == 0

    # check logs?

    # delete directories?
