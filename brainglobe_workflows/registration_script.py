import logging
import os
from pathlib import Path
import subprocess
import json
from typing import Dict, Union, Tuple

from pathlib import Path

from brainglobe_utils.general.numerical import check_positive_int
from brainglobe_utils.general.system import ensure_directory_exists
from fancylog import fancylog

import brainreg as program_for_log
from brainreg import __version__
from brainreg.backend.niftyreg.parser import niftyreg_parse
from brainreg.main import main as register
from brainreg.paths import Paths
from brainreg.utils.misc import get_arg_groups, log_metadata
from brainreg.cli import prep_registration

from dataclasses import dataclass, make_dataclass

Pathlike = Union[str, bytes, os.PathLike]
# TODO: use pydanti`c or attrs, and/or a dataclass, for this?? And grab default test data off pooch!

@dataclass
class BrainregConfig():
    image_paths: Pathlike
    brainreg_directory: Pathlike
    voxel_sizes: Tuple[float]
    orientation: str
    atlas: str
    debug: bool = False
    image_paths : Pathlike
    backend: str = "niftyreg"
    sort_input_file: bool = False
    save_original_orientation: bool = False
    brain_geometry: str = "full"
    n_free_cpus: int = 1
    additional_images = False
    preprocessing: Dict[str, str] = None,
    niftyreg_backend_options = None

def example_registration_script():
    input_config_path = Path(os.environ["BRAINGLOBE_REGISTRATION_CONFIG_PATH"])
    if input_config_path.exists():
        print(f"Read config from: {input_config_path}")
        with open(input_config_path) as config_file:
            config_dict = json.load(config_file)
        config = BrainregConfig(**config_dict)
    else:
        raise NotImplementedError
        # TODO: define some defaults here? load from local json file or pooch
        # config = BrainregConfig(**default_dict)
    
    with open(Path(__file__).parent / "niftyreg_defaults.json") as niftyreg_defaults_file:
        niftyreg_defaults_dict = json.load(niftyreg_defaults_file)
        NiftyregOptions = make_dataclass("NiftyregOptions", niftyreg_defaults_dict.keys())
        config.niftyreg_backend_options = NiftyregOptions(**niftyreg_defaults_dict)

    config.preprocessing = {"preprocessing": "default"}
    
    config, additional_images_downsample = prep_registration(config)

    paths = Paths(config.brainreg_directory)

    log_metadata(paths.metadata_path, config)

    fancylog.start_logging(
        paths.registration_output_folder,
        program_for_log,
        variables=[config],
        verbose=config.debug,
        log_header="BRAINREG LOG",
        multiprocessing_aware=False,
    )

    logging.info("Starting registration")

    register(
        config.atlas,
        config.orientation,
        config.image_paths,
        paths,
        config.voxel_sizes,
        config.niftyreg_backend_options,
        None,
        sort_input_file=config.sort_input_file,
        n_free_cpus=config.n_free_cpus,
        additional_images_downsample=additional_images_downsample,
        backend=config.backend,
        debug=config.debug,
        save_original_orientation=config.save_original_orientation,
        brain_geometry=config.brain_geometry,
    )

    # TODO save(results) # or maybe assert stuff around results???

if __name__ == "__main__":
	example_registration_script()

"""
To run brainreg, you need to pass:
    * The path to the sample data
    * The path to the directory to save the results
    * The voxel sizes
    * The orientation
    * The atlas to use

We put this all together in a single command:

brainreg test_brain brainreg_output -v 50 40 40  --orientation psl --atlas allen_mouse_50um
"""