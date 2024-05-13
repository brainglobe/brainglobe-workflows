# README

## Overview
We use [`asv`](https://asv.readthedocs.io) to benchmark some representative brainglobe workflows. The `asv` workflow is roughly as follows:
1. `asv` creates a virtual environment to run the benchmarks on, as defined in the `asv.conf.json` file.
1. It installs the version of the `brainglobe-workflows` package corresponding to the tip of the locally checked-out branch.
1. It runs the benchmarks as defined (locally) under `benchmarks/benchmarks` and saves the results to `benchmarks/results` as json files.
1. With `asv publish`, the output json files are 'published' into an html directory (`benchmarks/html`).
1. With `asv preview` the html directory can be visualised using a local web server.


We include code to benchmark the workflows defined under `brainglobe_workflows`. There are three main ways in which these benchmarks can be useful to developers:
1. Developers can run the available benchmarks locally [on a small test dataset](#running-benchmarks-locally-on-default-small-dataset).
1. Developers can run these benchmarks locally on [data they have stored locally](#running-benchmarks-locally-on-custom-data).
1. We also plan to run the benchmarks internally on a large dataset, and make the results publicly available.

See the `asv` [reference docs](https://asv.readthedocs.io/en/v0.6.3/reference.html) for further details on the tool, and on [how to run benchmarks](https://asv.readthedocs.io/en/stable/using.html#running-benchmarks).

## Installation

To run the benchmarks, [install asv](https://asv.readthedocs.io/en/stable/installing.html) in your current environment:
```
pip install asv
```

## Running benchmarks on a default small dataset

To run the benchmarks on a default small dataset:

1. Git clone the `brainglobe-workflows` repository:
    ```
    git clone https://github.com/brainglobe/brainglobe-workflows.git
    ```
1. Run `asv` from the `benchmarks` directory:
    ```
    cd brainglobe-workflows/benchmarks
    asv run
    ```
    This will benchmark the workflows defined in `brainglobe_workflows/` using a default set of parameters and a default small dataset. The default parameters are defined as config files under `brainglobe_workflows/configs`. The default dataset is downloaded from [GIN](https://gin.g-node.org/G-Node/info/wiki).

## Running benchmarks on custom data available locally
To run the benchmarks on a custom local dataset:

1. Git clone the `brainglobe-workflows` repository
    ```
    git clone https://github.com/brainglobe/brainglobe-workflows.git
    ```
1. Define a config file for the workflow to benchmark.
    - You can use the default config files at `brainglobe_workflows/configs/` as reference.
    - You will need to edit/add the fields pointing to the input data.
        - For example, for the `cellfinder` workflow, the config file will need to include an `input_data_dir` field pointing to the data of interest. The signal and background data are assumed to be in `signal` and `background` directories, under the `input_data_dir` directory. If they are under directories with a different name, you can specify their names with the `signal_subdir` and `background_subdir` fields.

1. Benchmark the workflow, passing the path to your custom config file as an environment variable.
    - For example, to benchmark the `cellfinder` workflow, you will need to prepend the environment variable definition to the `asv run` command (valid for Unix systems):
    ```
    CELLFINDER_CONFIG_PATH=/path/to/your/config/file asv run
    ```

## Running benchmarks in development
The following flags to `asv run` are often useful in development:
- `--quick`: will only run one repetition per benchmark, and no results to disk.
- `--verbose`: provides further info on intermediate steps.
- `--show-stderr`: will print out stderr.
- `--dry-run`: will not write results to disk.
- `--bench`: to specify a subset of benchmarks (e.g., `TimeFullWorkflow`). Regexp can be used.
- `--python=same`: runs the benchmarks in the same environment that `asv` was launched from

Example:
```
asv run --bench TimeFullWorkflow --dry-run --show-stderr --quick
```
