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

import pooch

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
    config, additional_images_downsample = setup_workflow()
    run_workflow(config, additional_images_downsample)

def run_workflow(config, additional_images_downsample):
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

def setup_workflow():
    if "BRAINGLOBE_REGISTRATION_CONFIG_PATH" in os.environ.keys():
        print(f"Read config from: {input_config_path}")
        input_config_path = Path(os.environ["BRAINGLOBE_REGISTRATION_CONFIG_PATH"])
        assert input_config_path.exists()
        with open(input_config_path) as config_file:
            config_dict = json.load(config_file)
        config = BrainregConfig(**config_dict)
    else:
        print(f"Using default config and test data")
        _ = pooch.retrieve(
          url=f"https://gin.g-node.org/BrainGlobe/test-data/raw/master/brainreg/brainreg-test-data.zip",
          known_hash="000fc4e040db9d84a0fd0beca96b4870ea33f30008c9ab69883ac46c0b1c3ed6",
          processor=pooch.Unzip(extract_dir=Path.home()/".brainglobe/workflow-data/brainreg/"),
        )

        # now input paths and expected outputs exist
        default_config_dict = {
            "image_paths": Path.home()/".brainglobe/workflow-data/brainreg/input/brain",
            "brainreg_directory": Path.home()/".brainglobe/workflow-data/brainreg/actual-output",
            "voxel_sizes": [
                50,
                40,
                40
            ],
            "orientation": "psl",
            "atlas": "allen_mouse_25um"
        }
        config = BrainregConfig(**default_config_dict)
    
    # always use defaults for niftyreg and preprocessing
    with open(Path(__file__).parent / "niftyreg_defaults.json") as niftyreg_defaults_file:
        niftyreg_defaults_dict = json.load(niftyreg_defaults_file)
        NiftyregOptions = make_dataclass("NiftyregOptions", niftyreg_defaults_dict.keys())
        config.niftyreg_backend_options = NiftyregOptions(**niftyreg_defaults_dict)

    config.preprocessing = {"preprocessing": "default"}    
    config, additional_images_downsample = prep_registration(config)
    return config,additional_images_downsample

if __name__ == "__main__":
	example_registration_script()