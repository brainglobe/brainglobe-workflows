[![Python Version](https://img.shields.io/pypi/pyversions/brainglobe-workflows.svg)](https://pypi.org/project/brainglobe-workflows)
[![PyPI](https://img.shields.io/pypi/v/brainglobe-workflows.svg)](https://pypi.org/project/brainglobe-workflows)
[![Downloads](https://pepy.tech/badge/brainglobe-workflows)](https://pepy.tech/project/brainglobe-workflows)
[![Wheel](https://img.shields.io/pypi/wheel/brainglobe-workflows.svg)](https://pypi.org/project/brainglobe-workflows)
[![Development Status](https://img.shields.io/pypi/status/brainglobe-workflows.svg)](https://github.com/brainglobe/brainglobe-workflows)
[![Tests](https://img.shields.io/github/actions/workflow/status/brainglobe/brainglobe-workflows/test_and_deploy.yml?branch=main)](https://github.com/brainglobe/brainglobe-workflows/actions)
[![codecov](https://codecov.io/gh/brainglobe/brainglobe-workflows/branch/master/graph/badge.svg?token=s3MweEFPhl)](https://codecov.io/gh/brainglobe/brainglobe-workflows)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Contributions](https://img.shields.io/badge/Contributions-Welcome-brightgreen.svg)](https://brainglobe.info/developers/index.html)
[![Website](https://img.shields.io/website?up_message=online&url=https%3A%2F%2Fbrainglobe.info)](https://brainglobe.info/documentation/brainglobe-workflows/index.html)
[![Twitter](https://img.shields.io/twitter/follow/brain_globe?style=social)](https://twitter.com/brain_globe)

# BrainGlobe Workflows

`brainglobe-workflows` is a package that provides users with a number of out-of-the-box data analysis workflows employed in neuroscience, implemented using BrainGlobe tools.

These workflows represent the most common use-cases and are meant to be easy to reuse. They also serve as an example of how to combine several BrainGlobe tools  (possibly together with other tools) to achieve a goal, such as whole brain cell detection and atlas registration.

You can view the [full documentation for each workflow](https://brainglobe.info/documentation/brainglobe-workflows/index.html) online.
You can also find the documentation for the backend BrainGlobe tools these workflows use [on our website](https://brainglobe.info/).

At present, the package offers the following workflows to users:

- [brainmapper](#brainmapper-command-line-interface-cli): A command-line tool for whole-brain detection, registration, and analysis.

Additionally, this repository provides functionalities to support code developers. See the [developer documentation](#developer-documentation) for further details.

## User documentation

### Installation

At the moment, users can install all available workflows by running `pip install` in your desired environment:

```bash
pip install brainglobe-workflows
```

`brainglobe-workflows` is built using BrainGlobe tools, and it will automatically fetch the tools that it needs and install them into your environment.
Once BrainGlobe version 1 is available, this package will fetch all BrainGlobe tools and handle their install into your environment, to prevent potential conflicts from partial installs.

See the sections below for more information about the workflows and command-line tools provided.

#### `brainmapper` Command Line Interface (CLI)

Whole-brain cell detection, registration and analysis.

If you want to just use the cell detection part of `brainmapper`, please see the standalone [cellfinder](https://github.com/brainglobe/cellfinder) package and its [`napari`](https://napari.org/) plugin.

`brainmapper` is a workflow designed for the analysis of whole-brain imaging data such as [serial-section imaging](https://sainsburywellcomecentre.github.io/OpenSerialSection/) and lightsheet imaging in cleared tissue.
The aim is to provide a single solution for:

- Cell detection (initial cell candidate detection and refinement using  deep learning) (using the [cellfinder](https://github.com/brainglobe/cellfinder) backend package),
- Atlas registration (using [brainreg](https://github.com/brainglobe/brainreg)),
- Analysis of cell positions in a common space.

Basic usage:

```bash
brainmapper -s signal_images -b background_images -o output_dir --metadata metadata
```

Full documentation can be found [here](https://brainglobe.info/documentation/brainglobe-workflows/brainmapper/index.html).

NOTE: The `brainmapper` workflow previously used the name "cellfinder", but this has been discontinued following the release of the [unified `cellfinder`](https://github.com/brainglobe/cellfinder) backend package to avoid conflation of terms.
See our [blog post](https://brainglobe.info/blog/version1/cellfinder-core-and-plugin-merge.html) from the release for more information.

## Developer documentation

This repository also includes workflow scripts that are benchmarked to support code development.
These benchmarks are run regularly to ensure performance is stable, as the tools are developed and extended.

- Developers can install these benchmarks locally via `pip install .[dev]`. By executing `asv run`, the benchmarks will run with default parameters on a small dataset that is downloaded from [GIN](https://gin.g-node.org/G-Node/info/wiki). See [the asv docs](https://asv.readthedocs.io/en/v0.6.1/using.html#running-benchmarks) for further details on how to run benchmarks.
- Developers can also run these benchmarks on data they have stored locally, by specifying the relevant paths in an input (JSON) file.
- We also maintain an internal runner that benchmarks the workflows over a large, exemplar dataset, of the scale we expect users to be handling. The result of these benchmarks are made publicly available.

Contributions to BrainGlobe are more than welcome.
Please see the [developer guide](https://brainglobe.info/developers/index.html).

## Citing `brainglobe-workflows`

**If you use any tools in the [brainglobe suite](https://brainglobe.info/documentation/index.html), please [let us know](mailto:code@adamltyson.com?subject=BrainGlobe), and we'd be happy to promote your paper/talk etc.**

If you find `brainmapper` useful, and use it in your research, please cite the paper outlining the cell detection algorithm:
> Tyson, A. L., Rousseau, C. V., Niedworok, C. J., Keshavarzi, S., Tsitoura, C., Cossell, L., Strom, M. and Margrie, T. W. (2021) “A deep learning algorithm for 3D cell detection in whole mouse brain image datasets’ PLOS Computational Biology, 17(5), e1009074
[https://doi.org/10.1371/journal.pcbi.1009074](https://doi.org/10.1371/journal.pcbi.1009074)
>
If you use any of the image registration functions in `brainmapper`, please also cite [`brainreg`](https://github.com/brainglobe/brainreg#citing-brainreg).
