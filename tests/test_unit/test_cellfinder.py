import json
import logging
from pathlib import Path

import pooch
import pytest

from workflows.cellfinder import (
    add_signal_and_background_files,
    read_cellfinder_config,
)


@pytest.fixture()
def input_configs_dir():
    return Path(__file__).parents[1] / "data"


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
    "input_config, message",
    [
        (
            "input_data_GIN.json",
            "Fetching input data from the provided GIN repository",
        ),
        (
            "input_data_locally.json",
            "Fetching input data from the local directories",
        ),
        ("input_data_missing_background.json", "The directory does not exist"),
        ("input_data_missing_signal.json", "The directory does not exist"),
        (
            "input_data_not_locally_or_GIN.json",
            "Input data not found locally, and URL/hash to"
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
    message,
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
    # set logger to capture
    # TODO: --- why root? :( "workflows.utils")
    caplog.set_level(logging.DEBUG, logger="root")

    # read json as Cellfinder config
    config = read_cellfinder_config(input_configs_dir / input_config)

    # monkeypatch cellfinder config:
    # - set install_path to pytest temp directory
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
    # - if config is "local" or "signal/background missing":
    #    ensure signal and background data from GIN are downloaded locally
    if message in [
        "Fetching input data from the local directories",
        "The directory does not exist",
    ]:
        # fetch data from GIN and download locally
        # download GIN data to specified local directory
        # can I download data only once? - but then same pytest directory?
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

    # retrieve data
    add_signal_and_background_files(config)

    assert message in caplog.messages[-1]


# def test_setup_workflow(input_config_path):
#     """Test setup steps for the cellfinder workflow are completed

#     These setup steps include:
#     - instantiating a CellfinderConfig object with the required parameters,
#     - add signal and background files to config if these do not exist
#     - creating a timestamped directory for the output of the workflow if
#     it doesn't exist and adding its path to the config
#     """


#     config = setup_workflow(input_config_path)

#     assert config.list_signal_files # all files exist
#     assert config.list_background_files  # all files exist
#     assert config.output_path
# #---should be timestamped with this format strftime("%Y%m%d_%H%M%S")
#     assert config.detected_cells_path
# # should be config.output_path / config.detected_cells_filename
