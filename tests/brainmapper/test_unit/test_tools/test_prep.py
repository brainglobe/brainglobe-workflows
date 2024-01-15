import os

import pytest
from brainglobe_utils.general.exceptions import CommandLineInputError

from brainglobe_workflows.brainmapper import prep

data_dir = os.path.join("tests", "data")


def test_check_return_ch_ids():
    signal_ch = [0, 1, 3]
    bg_ch = 6
    signal_list = ["file1.txt", "file_2.txt", "file_3.txt"]
    # None given
    assert ([0, 1, 2], 3) == prep.check_and_return_ch_ids(
        None, None, signal_list
    )
    # Only signal given
    assert (signal_ch, 4) == prep.check_and_return_ch_ids(
        signal_ch, None, signal_list
    )

    # Only background given
    assert ([7, 8, 9], bg_ch) == prep.check_and_return_ch_ids(
        None, bg_ch, signal_list
    )

    # Both given (no overlap)
    assert (signal_ch, bg_ch) == prep.check_and_return_ch_ids(
        signal_ch, bg_ch, signal_list
    )

    # Both given (overlap)
    with pytest.raises(CommandLineInputError):
        assert prep.check_and_return_ch_ids(signal_ch, 3, signal_list)


class Args:
    def __init__(
        self,
        model_dir=None,
        empty=None,
        no_detection=False,
        no_classification=False,
        no_register=False,
        no_analyse=False,
        no_standard_space=False,
        output_dir=None,
        registration_output_folder=None,
        cells_file_path=None,
        cubes_output_dir=None,
        classification_out_file=None,
        cells_in_standard_space=None,
    ):
        self.cell_count_model_dir = model_dir
        self.empty = empty

        self.no_detection = no_detection
        self.no_classification = no_classification
        self.no_register = no_register
        self.no_summarise = no_analyse
        self.no_standard_space = no_standard_space

        self.output_dir = output_dir

        self.paths = Paths(
            output_dir=registration_output_folder,
            cells_file_path=cells_file_path,
            cubes_output_dir=cubes_output_dir,
            classification_out_file=classification_out_file,
            cells_in_standard_space=cells_in_standard_space,
        )


class Paths:
    def __init__(
        self,
        output_dir=None,
        cells_file_path=None,
        cubes_output_dir=None,
        classification_out_file=None,
        cells_in_standard_space=None,
    ):
        self.registration_output_folder = output_dir
        self.cells_file_path = cells_file_path
        self.tmp__cubes_output_dir = cubes_output_dir
        self.classification_out_file = classification_out_file
        self.cells_in_standard_space = cells_in_standard_space


def make_and_fill_directory(directory):
    os.mkdir(directory)
    for file_size in range(100, 200, 20):
        with open(os.path.join(directory, str(file_size)), "wb") as fout:
            fout.write(os.urandom(file_size))
