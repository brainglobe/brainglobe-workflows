from pathlib import Path

import pooch
from brainglobe_utils.IO.cells import save_cells
from cellfinder_core.main import main as cellfinder_run
from cellfinder_core.tools.IO import read_with_dask

# Input data URL and hash
DATA_URL = "https://gin.g-node.org/BrainGlobe/test-data/raw/master/cellfinder/cellfinder-test-data.zip"
DATA_HASH = "b0ef53b1530e4fa3128fcc0a752d0751909eab129d701f384fc0ea5f138c5914"

# Local cached directories
CELLFINDER_CACHE_DIR = Path.home() / ".cellfinder_benchmarks"
INPUT_DATA_CACHE_DIR = CELLFINDER_CACHE_DIR / "cellfinder_test_data"
SIGNAL_DATA_PATH = INPUT_DATA_CACHE_DIR / "signal"
BACKGROUND_DATA_PATH = INPUT_DATA_CACHE_DIR / "background"
OUTPUT_DATA_CACHE_DIR = CELLFINDER_CACHE_DIR / "cellfinder_output"


class Workflow:
    """
    Defines the cellfinder workflow built around running the
    cellfinder_core.main.main() function.

    It includes `setup` methods that encapsulate steps which are required
    to run the workflow, but that we don't expect to benchmark
    (such as defining processing parameters or downloading the test data).
    """

    def setup_parameters(self):
        """
        Define input and output data locations and parameters for
        preprocessing steps.

        Methods that start with `setup_` will in principle not be benchmarked.
        """

        # cellfinder benchmarks cache directory
        self.install_path = CELLFINDER_CACHE_DIR

        # origin of data to download
        self.data_url = DATA_URL
        self.data_hash = DATA_HASH

        # cached subdirectory to save data to
        self.local_path = INPUT_DATA_CACHE_DIR
        self.output_path = OUTPUT_DATA_CACHE_DIR
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.detected_cells_filepath = self.output_path / "detected_cells.xml"

        # preprocessing parameters
        self.voxel_sizes = [5, 2, 2]  # microns
        self.start_plane = 0
        self.end_plane = -1
        self.trained_model = None  # if None, it will use a default model
        self.model_weights = None
        self.model = "resnet50_tv"
        self.batch_size = 32
        self.n_free_cpus = 2
        self.network_voxel_sizes = [5, 1, 1]
        self.soma_diameter = 16
        self.ball_xy_size = 6
        self.ball_z_size = 15
        self.ball_overlap_fraction = 0.6
        self.log_sigma_size = 0.2
        self.n_sds_above_mean_thresh = 10
        self.soma_spread_factor = 1.4
        self.max_cluster_size = 100000
        self.cube_width = 50
        self.cube_height = 50
        self.cube_depth = 20
        self.network_depth = "50"

    def setup_input_data(self):
        """
        Retrieve input data from GIN repository, and add relevant
        parent directories and list of files as attributes of the
        workflow class.

        Methods that start with `setup_` will in principle not be benchmarked.
        """

        # retrieve data from GIN repository
        list_files_archive = pooch.retrieve(
            url=self.data_url,
            known_hash=self.data_hash,
            path=self.install_path,  # path to download zip to
            progressbar=True,
            processor=pooch.Unzip(
                extract_dir=self.local_path  # path to unzipped dir
            ),
        )

        # signal data: parent dir and list of files
        self.signal_parent_dir = str(SIGNAL_DATA_PATH)
        self.list_signal_files = [
            f
            for f in list_files_archive
            if f.startswith(self.signal_parent_dir)
        ]

        # background data: parent dir and list of files
        self.background_parent_dir = str(BACKGROUND_DATA_PATH)
        self.list_background_files = [
            f
            for f in list_files_archive
            if f.startswith(self.background_parent_dir)
        ]


def workflow_from_cellfinder_run(cfg):
    """
    Run workflow based on the cellfinder_core.main.main()
    function.

    The steps are:
    1. Read the input signal and background data as two separate
       Dask arrays.
    2. Run the main cellfinder pipeline on the input Dask arrays,
       with the parameters defined in the input configuration (cfg).
    3. Save the detected cells as an xml file to the location specified in
       the input configuration (cfg).

    We plan to time each of the steps in the workflow individually,
    as well as the full workflow.

    Parameters
    ----------
    cfg : Workflow
        a class with the required setup methods and parameters for
        the cellfinder workflow
    """
    # Read input data as Dask arrays
    signal_array = read_with_dask(cfg.signal_parent_dir)
    background_array = read_with_dask(cfg.background_parent_dir)

    # Run main analysis using `cellfinder_run`
    detected_cells = cellfinder_run(
        signal_array, background_array, cfg.voxel_sizes
    )

    # Save results to xml file
    save_cells(detected_cells, cfg.detected_cells_filepath)


if __name__ == "__main__":
    # Run setup steps (these won't be timed)
    cfg = Workflow()
    cfg.setup_parameters()
    cfg.setup_input_data()

    # Run full workflow (this will be timed)
    workflow_from_cellfinder_run(cfg)
