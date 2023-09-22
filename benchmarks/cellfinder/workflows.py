import shutil

from brainglobe_utils.IO.cells import save_cells
from cellfinder_core.main import main as cellfinder_run
from cellfinder_core.tools.IO import read_with_dask

from brainglobe_workflows.cellfinder.cellfinder_main import (
    Workflow,
    workflow_from_cellfinder_run,
)


class TimeBenchmark:
    """
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

    timeout = 60  # default: 60 s
    version = None  # default: None (i.e. hash of source code)
    warmup_time = 0.1  # default:0.1;
    rounds = 2  # default:2
    repeat = 0  # default: 0
    sample_time = 0.01  # default: 10 ms = 0.01 s;
    min_run_count = 2  # default:2

    @classmethod
    def setup(self):
        cfg = Workflow()
        cfg.setup_parameters()
        cfg.setup_input_data()
        self.cfg = cfg

    def teardown(self):
        shutil.rmtree(self.cfg.install_path)


class TimeFullWorkflow(TimeBenchmark):
    def time_workflow_from_cellfinder_run(self):
        workflow_from_cellfinder_run(self.cfg)


class TimeReadInputDask(TimeBenchmark):
    def time_read_signal_w_dask(self):
        read_with_dask(self.cfg.signal_parent_dir)

    def time_read_background_w_dask(self):
        read_with_dask(self.cfg.background_parent_dir)


class TimeCellfinderRun(TimeBenchmark):
    def setup(self):
        TimeBenchmark.setup()
        self.signal_array = read_with_dask(self.cfg.signal_parent_dir)
        self.background_array = read_with_dask(self.cfg.background_parent_dir)

    def time_cellfinder_run(self):
        cellfinder_run(
            self.signal_array, self.background_array, self.cfg.voxel_sizes
        )


class TimeSaveCells(TimeBenchmark):
    def setup(self):
        TimeBenchmark.setup()
        signal_array = read_with_dask(self.cfg.signal_parent_dir)
        background_array = read_with_dask(self.cfg.background_parent_dir)

        self.detected_cells = cellfinder_run(
            signal_array, background_array, self.cfg.voxel_sizes
        )

    def time_save_cells(self):
        save_cells(self.detected_cells, self.cfg.detected_cells_filepath)
