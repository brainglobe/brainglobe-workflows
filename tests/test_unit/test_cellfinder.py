import json
import logging

from workflows.cellfinder import read_cellfinder_config, retrieve_input_data
from workflows.utils import DEFAULT_JSON_CONFIG_PATH_CELLFINDER

# @pytest.fixture() --- for where configs are
# def


def test_read_cellfinder_config(
    input_config_path=DEFAULT_JSON_CONFIG_PATH_CELLFINDER,
):
    # read json as Cellfinder config
    config = read_cellfinder_config(input_config_path)

    # read json as dict
    with open(input_config_path) as cfg:
        config_dict = json.load(cfg)

    # check keys of dict are a subset of Cellfinder config attributes
    assert all(
        [ky in config.__dataclass_fields__.keys() for ky in config_dict.keys()]
    )


# define different configs
# @pytest.mark.parametrize(
#     "input_config_path, message",
#     [
#         (DEFAULT_JSON_CONFIG_PATH_CELLFINDER,
# "Fetching input data from the local directories"),
#         (, "The directory does not exist"),
#         (, "The directory does not exist"),
#         (,"Input data not found locally,
# and URL/hash to GIN repository not provided"),
#         (,"Fetching input data from the provided GIN repository")
#     ]
# )
def test_retrieve_input_data(caplog, input_config_path, message):
    # set logger to capture
    caplog.set_level(
        logging.DEBUG, logger="root"
    )  # --- why root? :( "workflows.utils")

    # read json as Cellfinder config
    config = read_cellfinder_config(input_config_path)

    # retrieve data
    retrieve_input_data(config)

    assert message in caplog.messages

    # if (
    #     Path(config.signal_dir_path).exists()
    #     and Path(config.background_dir_path).exists()
    # ):

    #     # with caplog.at_level(
    #     #     logging.DEBUG,
    #     #     logger="root" # why root?
    #     # ):
    #     updated_config = retrieve_input_data(config)

    #     assert message in caplog.messages

    # # If exactly one of the input data directories is missing, print error
    # elif (
    #     Path(config.signal_dir_path).resolve().exists()
    #     or Path(config.background_dir_path).resolve().exists()
    # ):


# def test_setup_workflow():
#     pass
