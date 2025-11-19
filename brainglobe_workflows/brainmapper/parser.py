"""
parser
========
All the various arguments that may be needed by the various submodules.
Defined together so they can also be called by any other entry points.
"""

from argparse import (
    ArgumentDefaultsHelpFormatter,
    ArgumentParser,
    ArgumentTypeError,
)
from functools import partial

from brainglobe_utils.general.numerical import (
    check_positive_float,
    check_positive_int,
)
from brainglobe_utils.general.string import check_str
from brainreg.core.cli import atlas_parse, geometry_parser, niftyreg_parse
from brainreg.core.cli import backend_parse as brainreg_backend_parse
from cellfinder.core.download.cli import download_parser
from cellfinder.core.tools.source_files import user_specific_configuration_path

from brainglobe_workflows import __version__

# TODO: Gradually move all paths as strings to Path objects

models = {
    "18": "18-layer",
    "34": "34-layer",
    "50": "50-layer",
    "101": "101-layer",
    "152": "152-layer",
}


def valid_model_depth(depth):
    """
    Ensures a correct existing_model is chosen
    :param value: Input value
    :param models: Dict of allowed models
    :return: Input value, if it corresponds to a valid existing_model
    """

    if depth in models.keys():
        return depth
    else:
        raise ArgumentTypeError(
            f"Model depth: {depth} is not valid. Please "
            f"choose one of: {list(models.keys())}"
        )


def brainmapper_parser():
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser = main_parse(parser)
    parser = config_parse(parser)
    parser = pixel_parser(parser)
    parser = run_parse(parser)
    parser = io_parse(parser)
    parser = cell_detect_parse(parser)
    parser = classification_parse(parser)
    parser = cube_extract_parse(parser)
    parser = misc_parse(parser)
    parser = figures_parse(parser)
    parser = download_parser(parser)

    # brainreg options
    parser = atlas_parse(parser)
    parser = geometry_parser(parser)
    parser = brainreg_backend_parse(parser)
    # This needs to be abstracted away into brainreg for multiple backends
    parser = niftyreg_parse(parser)

    return parser


def main_parse(parser):
    main_parser = parser.add_argument_group("General options")

    main_parser.add_argument(
        "-s",
        "--signal-planes-paths",
        dest="signal_planes_paths",
        type=str,
        nargs="+",
        required=True,
        help="Path to the directory of the signal files. Can also be a text"
        "file pointing to the files. For a 3d tiff, data is in z, y, x order",
    )
    main_parser.add_argument(
        "-b",
        "--background-planes-path",
        dest="background_planes_path",
        type=str,
        nargs=1,
        required=True,
        help="Path to the directory of the background files. Can also be a "
        "text file pointing to the files. For a 3d tiff, data is in z, y, x "
        "order",
    )
    main_parser.add_argument(
        "-o",
        "--output-dir",
        dest="output_dir",
        type=str,
        required=True,
        help="Output directory for all intermediate and final results.",
    )
    main_parser.add_argument(
        "--signal-channel-ids",
        dest="signal_ch_ids",
        type=check_positive_int,
        nargs="+",
        help="Channel ID numbers, in the same order as 'signal-planes-paths'."
        " Will default to '0, 1, 2' etc, but maybe useful to specify.",
    )
    main_parser.add_argument(
        "--background-channel-id",
        dest="background_ch_id",
        type=check_positive_int,
        help="Channel ID number, corresponding to 'background-planes-path'.",
    )
    main_parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=__version__),
    )
    return parser


def pixel_parser(parser):
    # TODO: separate the two groups. Image pixel sizes are needed in lots of
    # places that the network pixel sizes are not
    pixel_opt_parser = parser.add_argument_group(
        "Options to define pixel sizes of raw data"
    )
    pixel_opt_parser.add_argument(
        "-v",
        "--voxel-sizes",
        dest="voxel_sizes",
        required=True,
        nargs=3,
        type=partial(check_positive_float, none_allowed=False),
        help="Voxel sizes in microns, in the order of data orientation "
        "(z, y, x). E.g. '5 2 2'",
    )
    pixel_opt_parser.add_argument(
        "--network-voxel-sizes",
        dest="network_voxel_sizes",
        nargs=3,
        type=partial(check_positive_float, none_allowed=False),
        default=[5, 1, 1],
        help="Voxel sizes in microns that the machine learning network was "
        "trained on, in the order of data orientation. e.g. '5 2 2'."
        "Set this to adjust the pixel sizes of the extracted cubes",
    )
    return parser


def run_parse(parser):
    run_parser = parser.add_argument_group(
        "Options to disable part of brainmapper"
    )
    run_parser.add_argument(
        "--no-detection",
        dest="no_detection",
        action="store_true",
        help="Dont run cell candidate detection",
    )

    run_parser.add_argument(
        "--no-classification",
        dest="no_classification",
        action="store_true",
        help="Do not run cell classification",
    )
    run_parser.add_argument(
        "--no-register",
        dest="no_register",
        action="store_true",
        help="Do not perform registration",
    )
    run_parser.add_argument(
        "--no-analyse",
        dest="no_analyse",
        action="store_true",
        help="Do not analyse and export cell positions",
    )
    run_parser.add_argument(
        "--no-figures",
        dest="no_figures",
        action="store_true",
        help="Do not create figures (e.g. heatmap)",
    )

    return parser


def io_parse(parser):
    io_parser = parser.add_argument_group("Input & output options")
    io_parser.add_argument(
        "--start-plane",
        dest="start_plane",
        type=check_positive_int,
        default=0,
        help="The first plane index to process in the Z dimension (inclusive, "
        "to process a subset of the data).",
    )
    io_parser.add_argument(
        "--end-plane",
        dest="end_plane",
        type=int,
        default=-1,
        help="The last plane to process in the Z dimension (exclusive, to "
        "process a subset of the data).",
    )
    return parser


def cell_detect_parse(parser):
    # TODO: improve the help on these files
    cell_detect_parser = parser.add_argument_group(
        "Detection options", description="Cell detection options"
    )
    cell_detect_parser.add_argument(
        "--save-planes",
        dest="save_planes",
        action="store_true",
        help="Whether to save the individual planes after "
        "processing and thresholding. Useful for debugging.",
    )

    cell_detect_parser.add_argument(
        "--outlier-keep",
        dest="outlier_keep",
        action="store_true",
        help="Dont remove putative cells that fall outside initial clusters",
    )

    cell_detect_parser.add_argument(
        "--artifact-keep",
        dest="artifact_keep",
        action="store_true",
        help="Save artifacts into the initial xml file",
    )

    cell_detect_parser.add_argument(
        "--max-cluster-size",
        dest="max_cluster_size",
        type=check_positive_int,
        default=100000,
        help="Largest detected cell cluster (in cubic um) where splitting "
        "should be attempted. Clusters above this size will be labeled as "
        "artifacts.",
    )

    cell_detect_parser.add_argument(
        "--soma-diameter",
        dest="soma_diameter",
        type=check_positive_float,
        default=16,
        help="The expected in-plane (xy) soma diameter (microns).",
    )

    cell_detect_parser.add_argument(
        "--ball-xy-size",
        dest="ball_xy_size",
        type=check_positive_int,
        default=6,
        help="3d filter's in-plane (xy) filter ball size (microns).",
    )
    cell_detect_parser.add_argument(
        "--ball-z-size",
        dest="ball_z_size",
        type=check_positive_int,
        default=15,
        help="3d filter's axial (z) filter ball size (microns).",
    )
    cell_detect_parser.add_argument(
        "--ball-overlap-fraction",
        dest="ball_overlap_fraction",
        type=check_positive_float,
        default=0.6,
        help="3d filter's fraction of the ball filter needed to be filled by "
        "foreground voxels, centered on a voxel, to retain the voxel.",
    )

    cell_detect_parser.add_argument(
        "--log-sigma-size",
        dest="log_sigma_size",
        type=check_positive_float,
        default=0.2,
        help="Gaussian filter width (as a fraction of soma diameter) used "
        "during 2d in-plane Laplacian of Gaussian filtering.",
    )
    cell_detect_parser.add_argument(
        "--threshold",
        dest="n_sds_above_mean_thresh",
        type=float,
        default=10,
        help="Per-plane intensity threshold (the number of standard "
        "deviations above the mean) of the filtered 2d planes used to mark "
        "pixels as foreground or background.",
    )
    cell_detect_parser.add_argument(
        "--tiled-threshold",
        dest="n_sds_above_mean_tiled_thresh",
        type=float,
        default=10,
        help="Per-plane, per-tile intensity threshold (the number of standard"
        " deviations above the mean) for the filtered 2d planes used to mark "
        "pixels as foreground or background. When used, (tile size is not "
        "zero) a pixel is marked as foreground if its intensity is above both"
        " the per-plane and per-tile threshold. I.e. it's above the set "
        "number of standard deviations of the per-plane average and of the "
        "per-plane per-tile average for the tile that contains it.",
    )
    cell_detect_parser.add_argument(
        "--tiled-threshold-tile-size",
        dest="tiled_thresh_tile_size",
        type=check_positive_float,
        default=None,
        help="The tile size used to tile the x, y plane to calculate the "
        "local average intensity for the tiled threshold. The value is "
        "multiplied by soma diameter (i.e. 1 means one soma diameter). If "
        "zero or None, the tiled threshold is disabled and only the per-plane"
        " threshold is used. Tiling is done with 50%% overlap when striding.",
    )
    cell_detect_parser.add_argument(
        "--soma-spread-factor",
        dest="soma_spread_factor",
        type=check_positive_float,
        default=1.4,
        help="Cell spread factor for determining the largest cell volume "
        "before splitting up cell clusters. Structures with spherical volume "
        "of diameter `soma_spread_factor * soma_diameter` or less will not "
        "be split.",
    )
    cell_detect_parser.add_argument(
        "--detection-batch-size",
        dest="detection_batch_size",
        type=check_positive_int,
        default=None,
        help="The number of planes of the original data volume to process at "
        "once. When None (the default), it defaults to 1 for GPU and 4 for "
        "CPU. The GPU/CPU memory must be able to contain this many planes "
        "for all the filters. For performance-critical applications, tune to "
        "maximize memory usage without running out. Check your GPU/CPU memory"
        " to verify it's not full.",
    )
    cell_detect_parser.add_argument(
        "--detect-coi",
        dest="detect_centre_of_intensity",
        action="store_true",
        help="If False, a candidate cell's center is just the mean of the "
        "positions of all voxels marked as above background, or bright, in "
        "that candidate. The voxel intensity is not taken into account. If "
        "True, the center is calculated similar to the center of mass, but "
        "using the intensity. So the center gets pulled towards the brighter "
        "voxels in the volume.",
    )

    return parser


def classification_parse(parser):
    classification_parser = parser.add_argument_group(
        "Cell classification options"
    )
    classification_parser.add_argument(
        "--trained-model",
        dest="trained_model",
        type=str,
        help="Path to the trained model",
    )
    classification_parser.add_argument(
        "--model-weights",
        dest="model_weights",
        type=str,
        help="Path to existing model weights",
    )
    classification_parser.add_argument(
        "--network-depth",
        dest="network_depth",
        type=valid_model_depth,
        default="50",
        help="Resnet depth (based on He et al. (2015)",
    )
    classification_parser.add_argument(
        "--batch-size",
        dest="classification_batch_size",
        type=check_positive_int,
        default=64,
        help="Deprecated. Use classification-batch-size instead.",
    )
    classification_parser.add_argument(
        "--classification-batch-size",
        dest="classification_batch_size",
        type=check_positive_int,
        default=64,
        help="How many potential cells to classify at one time. The GPU/CPU "
        "memory must be able to contain at once this many data cubes for the "
        "models. For performance-critical applications, tune to maximize "
        "memory usage without running out. Check your GPU/CPU memory to "
        "verify it's not full.",
    )
    classification_parser.add_argument(
        "--norm-channels",
        dest="normalize_channels",
        action="store_true",
        help="For classification only - whether to normalize the cubes to the "
        "mean/std of the image channels before classification. If the model "
        "used for classification was trained on normalized data, this should "
        "be enabled.",
    )
    classification_parser.add_argument(
        "--norm-sampling",
        dest="normalization_down_sampling",
        type=check_positive_int,
        default=32,
        help="If normalizing the cubes is enabled, the input channels will be "
        "down-sampled in z by this value before calculating their mean/std. "
        "E.g. a value of 2 means every second z plane will be used.",
    )
    classification_parser.add_argument(
        "--classification-max-workers",
        dest="classification_max_workers",
        type=check_positive_int,
        default=6,
        help="The max number of sub-processes to use for data loading / processing during classification.",
    )
    return parser


def cube_extract_parse(parser):
    cube_extract_parser = parser.add_argument_group("Cube extraction options")
    cube_extract_parser.add_argument(
        "--cube-width",
        dest="cube_width",
        type=check_positive_int,
        default=50,
        help="The width of the data cube centered on the cell, used for "
        "classification",
    )
    cube_extract_parser.add_argument(
        "--cube-height",
        dest="cube_height",
        type=check_positive_int,
        default=50,
        help="The height of the data cube centered on the cell, used "
        "for classification",
    )
    cube_extract_parser.add_argument(
        "--cube-depth",
        dest="cube_depth",
        type=check_positive_int,
        default=20,
        help="The depth of the data cube centered on the cell, used for "
        "classification",
    )
    cube_extract_parser.add_argument(
        "--save-empty-cubes",
        dest="save_empty_cubes",
        action="store_true",
        help="If a cube cannot be extracted (e.g. to close to the edge of"
        "the image), save an empty cube instead. Useful to keep track"
        "of all cell candidates.",
    )
    return parser


def config_parse(parser):
    config_opt_parser = parser.add_argument_group("Config options")
    config_opt_parser.add_argument(
        "--config",
        dest="registration_config",
        type=str,
        default=user_specific_configuration_path(),
        help="To supply your own, custom configuration file.",
    )

    return parser


def figures_parse(parser):
    figure_parser = parser.add_argument_group(
        "Figure generation specific parameters"
    )
    figure_parser.add_argument(
        "--heatmap-smoothing",
        dest="heatmap_smooth",
        type=check_positive_float,
        default=100,
        help="Gaussian smoothing sigma, in um.",
    )
    figure_parser.add_argument(
        "--no-mask-figs",
        dest="mask_figures",
        action="store_false",
        help="Don't mask the figures (removing any areas outside the brain,"
        "from e.g. smoothing)",
    )
    return parser


def misc_parse(parser):
    misc_parser = parser.add_argument_group("Misc options")
    misc_parser.add_argument(
        "--n-free-cpus",
        dest="n_free_cpus",
        type=check_positive_int,
        default=2,
        help="The number of CPU cores on the machine to leave "
        "unused by the program to spare resources.",
    )
    misc_parser.add_argument(
        "--torch-device",
        dest="torch_device",
        type=check_str,
        default=None,
        help="The device on which to run the computation. If not specified "
        "(None), cuda will be used if a GPU is available, otherwise cpu. You "
        "can also manually specify cuda or cpu.",
    )
    misc_parser.add_argument(
        "--pin-memory",
        dest="pin_memory",
        action="store_true",
        help="Pins data to be sent to the GPU to the CPU memory. This allows "
        "faster GPU data speeds, but can only be used if the data used by the"
        " GPU can stay in the CPU RAM while the GPU uses it. I.e. there's "
        "enough RAM. Otherwise, if there's a risk of the RAM being paged, it "
        "shouldn't be used. Defaults to False.",
    )
    misc_parser.add_argument(
        "--max-ram",
        dest="max_ram",
        type=check_positive_float,
        default=None,
        help="Maximum amount of RAM to use (in GB) - not currently fully "
        "implemented for all parts of brainmapper",
    )
    misc_parser.add_argument(
        "--save-csv",
        dest="save_csv",
        action="store_true",
        help="Save .csv files of cell locations (in addition to xml)."
        "Useful for importing into other software.",
    )
    misc_parser.add_argument(
        "--debug",
        dest="debug",
        action="store_true",
        help="Debug mode. Will increase verbosity of logging and save all "
        "intermediate files for diagnosis of software issues.",
    )
    misc_parser.add_argument(
        "--sort-input-file",
        dest="sort_input_file",
        action="store_true",
        help="If set to true, the input text file will be sorted using "
        "natural sorting. This means that the file paths will be "
        "sorted as would be expected by a human and "
        "not purely alphabetically",
    )
    return parser
