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

At present, the package currently offers the following workflows:

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

# Cellfinder

**TODO: move this information to an appropriate place on the website**

Whole-brain cell detection, registration and analysis.

**N.B. If you want to just use the cell detection part of cellfinder, please see the standalone [cellfinder-core](https://github.com/brainglobe/cellfinder-core) package, or the [cellfinder plugin](https://github.com/brainglobe/cellfinder-napari) for [napari](https://napari.org/).**

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

This software is at a very early stage, and was written with our data in mind.
Over time we hope to support other data types/formats.
If you have any issues, please get in touch [on the forum](https://forum.image.sc/tag/brainglobe) or by [raising an issue](https://github.com/brainglobe/cellfinder/issues/new/choose).

## Illustration

### Introduction

cellfinder takes a stitched, but otherwise raw whole-brain dataset with at least two channels:

- Background channel (i.e. autofluorescence),
- Signal channel, the one with the cells to be detected:

![Raw coronal serial two-photon mouse brain image showing labelled cells](https://raw.githubusercontent.com/brainglobe/cellfinder/master/resources/raw.png)

### Cell candidate detection

Classical image analysis (e.g. filters, thresholding) is used to find cell-like objects (with false positives):

![Candidate cells (including many artefacts)](https://raw.githubusercontent.com/brainglobe/cellfinder/master/resources/detect.png)

### Cell candidate classification

A deep-learning network (ResNet) is used to classify cell candidates as true cells (yellow) or artefacts (blue):

![Cassified cell candidates. Yellow - cells, Blue - artefacts](https://raw.githubusercontent.com/brainglobe/cellfinder/master/resources/classify.png)

### Registration and segmentation (`brainreg`)

Using [`brainreg`](https://github.com/brainglobe/brainreg), `cellfinder` aligns a template brain and atlas annotations (e.g. the Allen Reference Atlas, ARA) to the sample allowing detected cells to be assigned a brain region.

This transformation can be inverted, allowing detected cells to be transformed to a standard anatomical space.

![ARA overlaid on sample image](https://raw.githubusercontent.com/brainglobe/cellfinder/master/resources/register.png)

### Analysis of cell positions in a common anatomical space

Registration to a template allows for powerful group-level analysis of cellular distributions.
*(Example to come)*

## Examples

*(more to come)*

### Tracing of inputs to retrosplenial cortex (RSP)

Input cell somas detected by cellfinder, aligned to the Allen Reference Atlas, and visualised in [brainrender](https://github.com/brainglobe/brainrender) along
with RSP.

![brainrender](https://raw.githubusercontent.com/brainglobe/cellfinder/master/resources/brainrender.png)

Data courtesy of Sepiedeh Keshavarzi and Chryssanthi Tsitoura.
[Details here](https://www.youtube.com/watch?v=pMHP0o-KsoQ)

## Visualisation

You can view your data using the [brainglobe-napari-io](https://github.com/brainglobe/brainglobe-napari-io) plugin for [napari](https://github.com/napari/napari).

- Open napari (however you normally do it, but typically just type `napari` into your terminal, or click on your desktop icon).
- Load your raw data (drag and drop the data directories into napari, one at a time). ![Loading raw data](https://raw.githubusercontent.com/brainglobe/brainglobe-napari-io/master/resources/load_data.gif)
- Drag and drop your cellfinder XML file (e.g. `cell_classification.xml`) and/or cellfinder output directory into napari. ![Loading cellfinder results](https://raw.githubusercontent.com/brainglobe/brainglobe-napari-io/master/resources/load_results.gif)

The plugin will then load your detected cells (in yellow) and the rejected cell candidates (in blue).
If you carried out registration, then these results will be overlaid (similarly to the loading `brainreg` data, but transformed to the coordinate space of your raw data).
