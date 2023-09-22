# Write the benchmarking functions here.
# See "Writing benchmarks" in the asv docs for more information.

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

      - sample: `number` is determined so that each sample takes
        approx sample_time=10ms
    """

    timeout = 60  # default: 60
    version = None  # default: None (i.e. hash of source code)

    # time benchmarks
    warmup_time = 0.1  # default:0.1;
    rounds = 2  # default:2
    repeat = 0  # default: 0 samples to collect per round.
    sample_time = 10  # default 10 ms; `
    min_run_count = 2  # default:2


# I dont know how to have a common part for the setup fn for all
# without doing cahce
def setup_cache():
    cfg = Workflow()
    cfg.setup_parameters()
    cfg.setup_input_data()
    return cfg


class TimeFullWorkflow(TimeBenchmark):
    def time_workflow_from_cellfinder_run(self, cfg):
        workflow_from_cellfinder_run(cfg)

    #  def teardown(self, model_name): -- after each benchmark or after all?
    #     # remove .cellfinder-benchmarks dir after benchmarks
    #     shutil.rmtree(self.install_path)


class TimeReadInputDask(TimeBenchmark):
    def time_read_signal_w_dask(self, cfg):
        read_with_dask(cfg.signal_parent_dir)

    def time_read_background_w_dask(self, cfg):
        read_with_dask(cfg.background_parent_dir)

    #  def teardown(self, model_name): -- after each benchmark or after all?
    #     # remove .cellfinder-benchmarks dir after benchmarks
    #     shutil.rmtree(self.install_path)


class TimeCellfinderRun(TimeBenchmark):
    def setup(self, cfg):
        self.signal_array = read_with_dask(cfg.signal_parent_dir)
        self.background_array = read_with_dask(cfg.background_parent_dir)

    def time_cellfinder_run(self, cfg):
        cellfinder_run(
            self.signal_array, self.background_array, cfg.voxel_sizes
        )

    #  def teardown(self, model_name): -- after each benchmark or after all?
    #     # remove .cellfinder-benchmarks dir after benchmarks
    #     shutil.rmtree(self.install_path)


class TimeSaveCells(TimeBenchmark):
    def setup(self, cfg):
        signal_array = read_with_dask(cfg.signal_parent_dir)
        background_array = read_with_dask(cfg.background_parent_dir)

        self.detected_cells = cellfinder_run(
            signal_array, background_array, cfg.voxel_sizes
        )

    def time_save_cells(self, cfg):
        save_cells(self.detected_cells, cfg.detected_cells_filepath)

    #  def teardown(self, model_name): -- after each benchmark or after all?
    #     # remove .cellfinder-benchmarks dir after benchmarks
    #     shutil.rmtree(self.install_path)
