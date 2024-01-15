import os
from pathlib import Path

import pytest
from brainglobe_utils.general.exceptions import CommandLineInputError
from brainglobe_utils.general.system import ensure_directory_exists

import brainglobe_workflows.brainmapper.tools.system as system

data_dir = Path(__file__).parents[4] / Path("tests", "data")
background_im_dir = os.path.join(data_dir, "background")


def write_file_single_size(directory, file_size):
    with open(os.path.join(directory, str(file_size)), "wb") as fout:
        fout.write(os.urandom(file_size))


def test_check_path_exists(tmpdir):
    num = 10
    tmpdir = str(tmpdir)

    assert system.check_path_exists(os.path.join(tmpdir))
    no_exist_dir = os.path.join(tmpdir, "i_dont_exist")
    with pytest.raises(FileNotFoundError):
        assert system.check_path_exists(no_exist_dir)

    write_file_single_size(tmpdir, num)
    assert system.check_path_exists(os.path.join(tmpdir, str(num)))
    with pytest.raises(FileNotFoundError):
        assert system.check_path_exists(os.path.join(tmpdir, "20"))


def test_catch_input_file_error(tmpdir):
    tmpdir = str(tmpdir)
    # check no error is raised:
    system.catch_input_file_error(tmpdir)

    no_exist_dir = os.path.join(tmpdir, "i_dont_exist")
    with pytest.raises(CommandLineInputError):
        system.catch_input_file_error(no_exist_dir)


def test_ensure_directory_exists():
    home = os.path.expanduser("~")
    exist_dir = os.path.join(home, ".cellfinder_test_dir")
    ensure_directory_exists(exist_dir)
    assert os.path.exists(exist_dir)
    os.rmdir(exist_dir)
