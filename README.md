[![Python Version](https://img.shields.io/pypi/pyversions/brainglobe-workflows.svg)](https://pypi.org/project/brainglobe-workflows)
[![PyPI](https://img.shields.io/pypi/v/brainglobe-workflows.svg)](https://pypi.org/project/brainglobe-workflows)
[![Downloads](https://pepy.tech/badge/brainglobe-workflows)](https://pepy.tech/project/brainglobe-workflows)
[![Wheel](https://img.shields.io/pypi/wheel/brainglobe-workflows.svg)](https://pypi.org/project/brainglobe-workflows)
[![Development Status](https://img.shields.io/pypi/status/brainglobe-workflows.svg)](https://github.com/brainglobe/brainglobe-workflows)
[![Tests](https://img.shields.io/github/workflow/status/brainglobe/brainglobe-workflows/tests)](
    https://github.com/brainglobe/brainglobe-workflows/actions)
[![codecov](https://codecov.io/gh/brainglobe/brainglobe-workflows/branch/master/graph/badge.svg?token=s3MweEFPhl)](https://codecov.io/gh/brainglobe/brainglobe-workflows)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Contributions](https://img.shields.io/badge/Contributions-Welcome-brightgreen.svg)](https://brainglobe.info/developers/index.html)
[![Website](https://img.shields.io/website?up_message=online&url=https%3A%2F%2Fbrainglobe.info)](https://brainglobe.info/documentation/brainglobe-workflows/index.html)
[![Twitter](https://img.shields.io/twitter/follow/brain_globe?style=social)](https://twitter.com/brain_globe)

# BrainGlobe Workflows

`brainglobe-workflows` is a package that provides users with a number of out-of-the-box data analysis workflows employed in neuroscience, implemented using BrainGlobe tools.
You can view the [full documentation for each workflow](https://brainglobe.info/documentation/brainglobe-workflows/index.html) online.
You can also find the documentation for the backend BrainGlobe tools these workflows use [on our website](https://brainglobe.info/).

At present, the package offers the following workflows:

- [cellfinder](#cellfinder): Whole-brain detection, registration, and analysis.

## Installation

If you want to install BrainGlobe workflows as a standalone tool, you can run `pip install` in your desired environment:

```bash
pip install brainglobe-workflows
```

`brainglobe-workflows` is built using BrainGlobe tools, and it will automatically fetch the tools that it needs and install them into your environment.
Once BrainGlobe version 1 is available, this package will fetch all BrainGlobe tools and handle their install into your environment, to prevent potential conflicts from partial-installs.

## Contributing

Contributions to BrainGlobe are more than welcome.
Please see the [developers guide](https://brainglobe.info/developers/index.html).

## Citing `brainglobe-workflows`

**If you use any tools in the [brainglobe suite](https://brainglobe.info/documentation/index.html), please [let us know](mailto:code@adamltyson.com?subject=cellfinder), and we'd be happy to promote your paper/talk etc.**

If you find [`cellfinder`](#cellfinder) useful, and use it in your research, please cite the paper outlining the cell detection algorithm:
> Tyson, A. L., Rousseau, C. V., Niedworok, C. J., Keshavarzi, S., Tsitoura, C., Cossell, L., Strom, M. and Margrie, T. W. (2021) “A deep learning algorithm for 3D cell detection in whole mouse brain image datasets’ PLOS Computational Biology, 17(5), e1009074
[https://doi.org/10.1371/journal.pcbi.1009074](https://doi.org/10.1371/journal.pcbi.1009074)
>
If you use any of the image registration functions in `cellfinder`, please also cite [`brainreg`](https://github.com/brainglobe/brainreg#citing-brainreg).

---

## Cellfinder

Whole-brain cell detection, registration and analysis.

If you want to just use the cell detection part of `cellfinder`, please see the standalone [cellfinder-core](https://github.com/brainglobe/cellfinder-core) package, or the [cellfinder plugin](https://github.com/brainglobe/cellfinder-napari) for [napari](https://napari.org/).

`cellfinder` is a collection of tools developed by [Adam Tyson](https://github.com/adamltyson), [Charly Rousseau](https://github.com/crousseau) and [Christian Niedworok](https://github.com/cniedwor) in the [Margrie Lab](https://www.sainsburywellcome.org/web/groups/margrie-lab), generously supported by the [Sainsbury Wellcome Centre](https://www.sainsburywellcome.org/web/).

`cellfinder` is a designed for the analysis of whole-brain imaging data such as [serial-section imaging](https://sainsburywellcomecentre.github.io/OpenSerialSection/) and lightsheet imaging in cleared tissue.
The aim is to provide a single solution for:

- Cell detection (initial cell candidate detection and refinement using  deep learning) (using [cellfinder-core](https://github.com/brainglobe/cellfinder-core)),
- Atlas registration (using [brainreg](https://github.com/brainglobe/brainreg)),
- Analysis of cell positions in a common space.

Basic usage:

```bash
cellfinder -s signal_images -b background_images -o output_dir --metadata metadata
```

Full documentation can be found [here](https://brainglobe.info/documentation/cellfinder/index.html).
