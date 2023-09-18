# %%
import os
from pathlib import Path

import tifffile
from brainglobe_utils.IO.cells import get_cells, save_cells  # imlib?
from cellfinder_core.classify import classify
from cellfinder_core.detect import detect
from cellfinder_core.main import main as cellfinder_run
from cellfinder_core.tools.IO import read_with_dask
from cellfinder_core.tools.prep import prep_classification


# %%
class Workflow:
    def setup(self):  # ---these are things that wont be timed
        # install path
        home = Path.home()
        self.install_path = home / ".cellfinder-benchmarks"

        # input data path - GIN?
        # Use environment variable to pass the path to the test data -- why environment var?
        self.input_data_path = Path(os.environ("BENCHMARK_DATA"))
        assert self.input_data_path.exists()

        # output path to save data
        self.output_path = self.install_path / "output"

        self.voxel_sizes = [5, 2, 2]  # in microns

        # preprocess params -- do we want to sweep thru these?
        self.start_plane = 0
        self.end_plane = -1
        self.trained_model = None  # if None will use default (right?)
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

    def read(
        self, with_dask
    ):  # this will be time_read()? split dask or no dask?
        if with_dask:
            signal_array = read_with_dask(
                self.input_data_path
            )  # "/path/to/signal_image_directory")
            background_array = read_with_dask(
                self.input_data_path
                # "/path/to/background_image_directory"
            )
        else:
            signal_array = tifffile.imread(
                self.input_data_path
            )  # "/path/to/signal_image.tif")
            background_array = tifffile.imread(
                self.input_data_path
            )  # "/path/to/background_image.tif")


        return signal_array, background_array

    def preprocess(self):  # this will be time_preprocess()
        # prep for classification -- inputs should be available from setup 
        model_weights = prep_classification(
            self.trained_model,
            self.model_weights,
            self.install_path,
            self.model,
            self.n_free_cpus,
        )
        return model_weights

    def detect_cells(self, signal_array): # this will be time_detect (it should have its own setup with signal_array?)
        # inputs should be available from setup and from reading data
        cell_candidates = detect.main(
            signal_array,
            self.start_plane,
            self.end_plane,
            self.voxel_sizes,
            self.soma_diameter,
            self.max_cluster_size,
            self.ball_xy_size,
            self.ball_z_size,
            self.ball_overlap_fraction,
            self.soma_spread_factor,
            self.n_free_cpus,
            self.log_sigma_size,
            self.n_sds_above_mean_thresh,
        )
        return cell_candidates

    def classify_cells(self, signal_array, background_array, cell_candidates, model_weights):
        classified_cells = []
        if (
            len(cell_candidates) > 0
        ):  # Don't run if there's nothing to classify
            classified_cells = classify.main(
                cell_candidates,
                signal_array,
                background_array,
                self.n_free_cpus,
                self.voxel_sizes,
                self.network_voxel_sizes,
                self.batch_size,
                self.cube_height,
                self.cube_width,
                self.cube_depth,
                self.trained_model,
                model_weights,
                self.network_depth,
            )
        return classified_cells

    def save(self, detected_cells):
        save_cells(detected_cells, self.output_path)  # "/path/to/cells.xml")

    # def load(input_path):  # not part of the workflow?
    #     cells = get_cells(input_path)  # "/path/to/cells.xml")
    #     return cells


# -------


def workflow_from_cellfinder_run():
    # instantiate config
    cfg = Workflow.setup()

    # read data
    signal_array, background_array = Workflow.read(cfg, with_dask=False)

    # run workflow using cellfinder_run
    detected_cells = cellfinder_run(
        signal_array, background_array, cfg.voxel_sizes
    )

    # save data
    Workflow.save(detected_cells, cfg.output_path)


def workflow_from_steps():
    # instantiate config
    cfg = Workflow.setup()

    # read input data
    signal_array, background_array = Workflow.read(cfg, with_dask=False)

    # run preprocessing
    model_weights = Workflow.preprocess(cfg)

    # detect cell candidates
    cell_candidates = Workflow.detect_cells(cfg, signal_array)

    # classify cells
    classified_cells = Workflow.classify_cells(
        cfg, signal_array, background_array, cell_candidates, model_weights
    )

    # save data
    Workflow.save(cfg, classified_cells)


# def workflow_load_data():
#     cells = load(input_path)


# run whole workflow
# what type? with/without dask? -- CLI
if __name__ == "__main__":
    workflow_from_cellfinder_run()

# if True:
#     workflow_from_cellfinder_run()
# else:
#     workflow_from_cellfinder_run()
