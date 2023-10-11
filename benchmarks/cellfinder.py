import json
import shutil
from pathlib import Path

import pooch

from brainglobe_workflows.cellfinder.cellfinder_main import (
    CellfinderConfig,
    run_workflow_from_cellfinder_run,
)
from brainglobe_workflows.cellfinder.cellfinder_main import (
    setup as setup_cellfinder_workflow,
)


class TimeBenchmarkPrepGIN:
    """
    Setup_cache function downloads the data from GIN

    Base class with sensible options
    See https://asv.readthedocs.io/en/stable/benchmarks.html#benchmark-attributes

    The sample_time, number, repeat, and timer attributes can be adjusted in
    the setup() routine, which can be useful for parameterized benchmarks

    Other attributes for time benchmarks not specified in this class:
    - number: the number of iterations in each sample. If number is specified,
    sample_time is ignored. Note that setup and teardown are not run between
    iterations: setup runs first, then the timed benchmark routine is called
    number times, and after that teardown runs.
    - timer: timeit.default_timer by default

    Notes about some of the default attributes for time benchmarks:
      - warmup_time: asv will spend this time (in seconds) in calling the
        benchmarked function repeatedly, before starting to run the
        actual benchmark

      - repeat: when not provided (repeat set to 0):
        - if rounds==1 the default is
            (min_repeat, max_repeat, max_time) = (1, 10, 20.0),
        - if rounds != 1 the default is
            (min_repeat, max_repeat, max_time) = (1, 5, 10.0)

      - sample_time: `number` is determined so that each sample takes
        approx sample_time=10ms
    """

    timeout = 600  # default: 60 s
    version = None  # default: None (i.e. hash of source code)
    warmup_time = 0.1  # default:0.1;
    rounds = 2  # default:2
    repeat = 0  # default: 0
    sample_time = 0.01  # default: 10 ms = 0.01 s;
    min_run_count = 2  # default:2

    input_config_path = (
        "/Users/sofia/Documents_local/project_BrainGlobe_workflows/"
        "brainglobe-workflows/brainglobe_workflows/cellfinder/default_config.json"
    )

    def setup_cache(
        self,
    ):  # ---> cache so that we dont download data several times?
        """
        We force a download of the data here

        setup_cache method only performs the setup calculation once and
        then caches the result to disk.

        It is run only once also for repeated benchmarks and profiling.
        """
        print("RUN SETUP CACHE")
        # download the data here?
        # Check config file exists
        assert Path(self.input_config_path).exists()

        # Instantiate a CellfinderConfig from the input json file
        # (assumes config is json serializable)
        with open(self.input_config_path) as cfg:
            config_dict = json.load(cfg)
        config = CellfinderConfig(**config_dict)

        # download data
        # get list of files in GIN archive with pooch.retrieve
        _ = pooch.retrieve(
            url=config.data_url,
            known_hash=config.data_hash,
            path=config.install_path,
            progressbar=True,
            processor=pooch.Unzip(extract_dir=config.extract_dir_relative),
        )

        # paths to input data should now exist in config
        assert Path(config.signal_dir_path).exists()
        assert Path(config.background_dir_path).exists()

        return

    def setup(self):
        """ """
        # monkeypatch command line arguments
        # run setup
        print("RUN SETUP")
        cfg = setup_cellfinder_workflow(
            [
                "--config",
                self.input_config_path,  # ----should work without path too!
            ]
        )
        self.cfg = cfg

    def teardown(self):
        """
        Remove the cellfinder benchmarks cache directory
        (typically .cellfinder_benchmarks)
        """
        print("RUN TEARDOWN")
        shutil.rmtree(
            Path(self.cfg.output_path).resolve()
        )  # ---- remove all but input data? i.e., remove output only


class TimeFullWorkflow(TimeBenchmarkPrepGIN):
    def time_workflow_from_cellfinder_run(self):
        run_workflow_from_cellfinder_run(self.cfg)


# class TimeReadInputDask(TimeBenchmark):
#     def time_read_signal_w_dask(self):
#         read_with_dask(self.cfg.signal_parent_dir)

#     def time_read_background_w_dask(self):
#         read_with_dask(self.cfg.background_parent_dir)


# class TimeCellfinderRun(TimeBenchmark):
#     def setup(self):
#         TimeBenchmark.setup()
#         self.signal_array = read_with_dask(self.cfg.signal_parent_dir)
#         self.background_array = read_with_dask(
#           self.cfg.background_parent_dir
#         )

#     def time_cellfinder_run(self):
#         cellfinder_run(
#             self.signal_array, self.background_array, self.cfg.voxel_sizes
#         )


# class TimeSaveCells(TimeBenchmark):
#     def setup(self):
#         TimeBenchmark.setup()
#         signal_array = read_with_dask(self.cfg.signal_parent_dir)
#         background_array = read_with_dask(self.cfg.background_parent_dir)

#         self.detected_cells = cellfinder_run(
#             signal_array, background_array, self.cfg.voxel_sizes
#         )

#     def time_save_cells(self):
#         save_cells(self.detected_cells, self.cfg.detected_cells_filepath)
