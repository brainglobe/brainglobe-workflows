# README

## Overview
We use [`asv`](https://asv.readthedocs.io) to benchmark some representative BrainGlobe workflows. The `asv` workflow is roughly as follows:
1. `asv` creates a virtual environment to run the benchmarks on, as defined in the `asv.bg-requirements.conf.json` file.
1. It installs the version of the `brainglobe-workflows` package corresponding to the tip of the locally checked-out branch.
1. It runs the benchmarks as defined (locally) under `benchmarks/benchmarks` and saves the results to `benchmarks/results` as json files.
1. With `asv publish`, the output json files are 'published' into an html directory (`benchmarks/html`).
1. With `asv preview` the html directory can be visualised using a local web server.



We include code to benchmark the workflows defined under `brainglobe_workflows`. There are three main ways in which these benchmarks can be useful to developers:
1. Developers can run the available benchmarks on their machine on either
    - [a small test dataset](#running-benchmarks-on-a-small-default-dataset), or
    - on [custom data](#running-benchmarks-on-custom-data).
1. We also run the benchmarks internally on a large dataset, and make the results publicly available.

Additionally, we ship an `asv` configuration file, which defines an environment for `asv` to create and run the benchmarks in (`asv.bg-requirements.conf.json`). The BrainGlobe dependencies in that environment are specified in the `bg-requirements.txt` file. By default, they are all set to the GitHub `main` branch, but that can be modified in the file. Note that all `asv` commands will need to specify the configuration file with the `--config` flag.

See the `asv` [reference docs](https://asv.readthedocs.io/en/stable/reference.html) for further details on the tool, and on [how to run benchmarks](https://asv.readthedocs.io/en/stable/using.html#running-benchmarks). The first time running benchmarks on a new machine, you will need to run `asv machine --yes` to set up the machine for benchmarking.


## Installation

To run the benchmarks, [install asv](https://asv.readthedocs.io/en/stable/installing.html) in your current environment:
```
pip install asv
```
Note that to run the benchmarks, you do not need to install a development version of `brainglobe-workflows` in your current environment (`asv` takes care of this).


## Running benchmarks on a small default dataset

To run the benchmarks on the default dataset:

1. Git clone the `brainglobe-workflows` repository:
    ```
    git clone https://github.com/brainglobe/brainglobe-workflows.git
    ```
1. Run `asv` from the `benchmarks` directory:
    ```
    cd brainglobe-workflows/benchmarks
    asv run --config asv.bg-requirements.conf.json  # brainglobe dependencies are as specified in bg-requirements.txt
    ```
    This will benchmark the workflows defined in `brainglobe_workflows/` using a default set of parameters and a default small dataset. The default parameters are defined as config files under `brainglobe_workflows/configs`. The default dataset is downloaded from [GIN](https://gin.g-node.org/G-Node/info/wiki). By default, the brainglobe dependencies are installed from the tip of the `main` branches on GitHub. To use other versions of these dependencies, you can edit the `bg-requirements.txt` file.

## Running `cellfinder` benchmarks on custom data
To benchmark the `cellfinder` workflow on a custom local dataset:

1. Git clone the `brainglobe-workflows` repository
    ```
    git clone https://github.com/brainglobe/brainglobe-workflows.git
    ```
1. Define a new `cellfinder` workflow config file that points to the input data of interest.
    - You can use config at `brainglobe_workflows/configs/cellfinder.json` as reference.
    - You will need to edit/add the fields pointing to the input data.
        - For the `cellfinder` workflow, the config file will need to include an `input_data_dir` field pointing to the data of interest. The signal and background data are assumed to be in `signal` and `background` directories, under the `input_data_dir` directory. If they are under directories with a different name, you can specify their names with the `signal_subdir` and `background_subdir` fields.

1. Benchmark the workflow, passing the path to your custom config file as an environment variable.
    - To benchmark a `cellfinder` workflow, you will need to prepend the environment variable definition to the `asv run` command (valid for Unix systems):
    ```
    CELLFINDER_CONFIG_PATH=/path/to/your/config/file asv run --config <path-to-asv-config>
    ```

## Defining a new workflow
To define a new workflow, you can use the `brainglobe_workflows/cellfinder/cellfinder.py` module as a reference. Usually, a workflow will use a config file to define its input parameters. You may use the config file for the `cellfinder` workflow as reference `brainglobe_workflows/configs/cellfinder.json`.



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
asv run --config <path-to-asv-config> --bench TimeFullWorkflow --dry-run --show-stderr --quick
```
