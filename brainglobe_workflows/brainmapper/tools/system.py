from pathlib import Path

from brainglobe_utils.general.exceptions import CommandLineInputError


def check_path_exists(file):
    """
    Returns True is a file exists, otherwise throws a FileNotFoundError
    :param file: Input file
    :return: True, if the file exists
    """
    file = Path(file)
    if file.exists():
        return True
    else:
        raise FileNotFoundError


def catch_input_file_error(path):
    """
    Catches if an input path doesn't exist, and returns an informative error
    :param path: Input file path
    default)
    """
    try:
        check_path_exists(path)
    except FileNotFoundError:
        message = (
            "File path: '{}' cannot be found. Please check your input "
            "arguments.".format(path)
        )
        raise CommandLineInputError(message)
