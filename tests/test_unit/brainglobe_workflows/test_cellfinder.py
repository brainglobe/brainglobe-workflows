import json
import re
from pathlib import Path

import pooch
import pytest

from brainglobe_workflows.cellfinder import (
    add_signal_and_background_files,
    read_cellfinder_config,
    setup_workflow,
)
from brainglobe_workflows.utils import setup_logger


@pytest.fixture()
def input_configs_dir():
    return Path(__file__).parents[2] / "data"


@pytest.fixture(scope="session")
def cellfinder_GIN_data() -> dict:
    """Return the URL and hash to the GIN repository with the input data

    Returns
    -------
    dict
        URL and hash of the GIN repository with the cellfinder test data
    """
    return {
        "url": "https://gin.g-node.org/BrainGlobe/test-data/raw/master/cellfinder/cellfinder-test-data.zip",
        "hash": "b0ef53b1530e4fa3128fcc0a752d0751909eab129d701f384fc0ea5f138c5914",  # noqa
    }


@pytest.fixture()
def input_config_default():
    from brainglobe_workflows.utils import DEFAULT_JSON_CONFIG_PATH_CELLFINDER

    return DEFAULT_JSON_CONFIG_PATH_CELLFINDER


@pytest.fixture()
def input_config_fetch_GIN(input_configs_dir):
    return input_configs_dir / "input_data_GIN.json"


@pytest.mark.parametrize(
    "input_config",
    [
        "input_data_GIN.json",
        "input_data_locally.json",
        "input_data_missing_background.json",
        "input_data_missing_signal.json",
        "input_data_not_locally_or_GIN.json",
    ],
)
def test_read_cellfinder_config(input_config, input_configs_dir):
    # path to config json file
    input_config_path = input_configs_dir / input_config

    # read json as Cellfinder config
    config = read_cellfinder_config(input_config_path)

    # read json as dict
    with open(input_config_path) as cfg:
        config_dict = json.load(cfg)

    # check keys of dictionary are a subset of Cellfinder config attributes
    assert all(
        [ky in config.__dataclass_fields__.keys() for ky in config_dict.keys()]
    )


@pytest.mark.parametrize(
    "input_config, message_pattern",
    [
        (
            "input_data_GIN.json",
            "Fetching input data from the provided GIN repository",
        ),
        (
            "input_data_locally.json",
            "Fetching input data from the local directories",
        ),
        (
            "input_data_missing_background.json",
            "The directory .+ does not exist$",
        ),
        ("input_data_missing_signal.json", "The directory .+ does not exist$"),
        (
            "input_data_not_locally_or_GIN.json",
            "Input data not found locally, and URL/hash to "
            "GIN repository not provided",
        ),
    ],
)
def test_add_signal_and_background_files(
    caplog,
    tmp_path,
    cellfinder_GIN_data,
    input_configs_dir,
    input_config,
    message_pattern,
):
    """_summary_

    Parameters
    ----------
    caplog : _type_
        _description_
    tmp_path : Path
        path to pytest-generated temporary directory
    input_configs_dir : _type_
        _description_
    input_config : _type_
        _description_
    message : _type_
        _description_
    """
    # instantiate our custom logger
    _ = setup_logger()

    # read json as Cellfinder config
    config = read_cellfinder_config(input_configs_dir / input_config)

    # monkeypatch cellfinder config:
    # set install_path to pytest temporary directory
    config.install_path = tmp_path / config.install_path

    # check lists of signal and background files are not defined
    assert not (config.list_signal_files and config.list_background_files)

    # build fullpaths to input data directories
    config.signal_dir_path = str(
        Path(config.install_path)
        / config.data_dir_relative
        / config.signal_subdir
    )
    config.background_dir_path = str(
        Path(config.install_path)
        / config.data_dir_relative
        / config.background_subdir
    )

    # monkeypatch cellfinder config:
    # if config is "local" or "signal/background missing":
    # ensure signal and background data from GIN are downloaded locally
    if input_config in [
        "input_data_locally.json",
        "input_data_missing_signal.json",
        "input_data_missing_background.json",
    ]:
        # fetch data from GIN and download locally
        pooch.retrieve(
            url=cellfinder_GIN_data["url"],
            known_hash=cellfinder_GIN_data["hash"],
            path=config.install_path,  # path to download zip to
            progressbar=True,
            processor=pooch.Unzip(
                extract_dir=config.data_dir_relative
                # path to unzipped dir, *relative*  to 'path'
            ),
        )

    # add signal and background files lists to config
    add_signal_and_background_files(config)

    # check log messages
    assert len(caplog.messages) > 0
    out = re.fullmatch(message_pattern, caplog.messages[-1])
    assert out.group() is not None


@pytest.mark.parametrize(
    "input_config, message",
    [
        ("input_config_default", "Using default config file"),
        ("input_config_fetch_GIN", "Input config read from"),
    ],
)
def test_setup_workflow(
    input_config, message, monkeypatch, tmp_path, caplog, request
):
    """Test setup steps for the cellfinder workflow are completed

    These setup steps include:
    - instantiating a CellfinderConfig object with the required parameters,
    - add signal and background files to config if these do not exist
    - creating a timestamped directory for the output of the workflow if
    it doesn't exist and adding its path to the config
    """

    # setup logger
    _ = setup_logger()

    # monkeypatch to change current directory to
    # pytest temporary directory
    # (cellfinder cache directory is created in cwd)
    monkeypatch.chdir(tmp_path)

    # setup workflow
    config = setup_workflow(request.getfixturevalue(input_config))

    # check logs
    assert message in caplog.text

    # check all signal files exist
    assert all([Path(f).is_file() for f in config.list_signal_files])

    # check all background files exist
    assert all([Path(f).is_file() for f in config.list_background_files])

    # check output directory exists
    assert Path(config.output_path).resolve().is_dir()

    # check output directory name has correct format
    out = re.fullmatch(
        config.output_path_basename_relative + "\\d{8}_\\d{6}$",
        Path(config.output_path).stem,
    )
    assert out.group() is not None

    # check output file path
    assert (
        config.detected_cells_path
        == config.output_path / config.detected_cells_filename
    )
