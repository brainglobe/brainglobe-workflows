"""
main
===============

Runs each part of the brainmapper pipeline in turn.
"""

import logging
import os
from datetime import datetime

import brainglobe_space as bgs
import pandas as pd
import tifffile
from brainglobe_utils.cells.cells import MissingCellsError
from brainglobe_utils.general.system import ensure_directory_exists
from brainglobe_utils.image.heatmap import heatmap_from_points
from brainglobe_utils.IO.cells import get_cells, save_cells
from brainglobe_utils.IO.image.load import read_z_stack

BRAINREG_PRE_PROCESSING_ARGS = None


def get_downsampled_space(atlas, downsampled_image_path):
    target_shape = tifffile.imread(downsampled_image_path).shape
    downsampled_space = bgs.AnatomicalSpace(
        atlas.metadata["orientation"],
        shape=target_shape,
        resolution=atlas.resolution,
    )
    return downsampled_space


def cells_exist(points_file):
    try:
        get_cells(points_file, cells_only=True)
        return True
    except MissingCellsError:
        return False


def main():
    from brainreg.core.main import main as register

    from brainglobe_workflows.brainmapper import prep

    start_time = datetime.now()
    args, arg_groups, what_to_run, atlas = prep.prep_brainmapper_general()

    if what_to_run.register:
        # TODO: add register_part_brain option
        logging.info("Registering to atlas")
        args, additional_images_downsample = prep.prep_registration(args)
        register(
            args.atlas,
            args.orientation,
            args.target_brain_path,
            args.brainreg_paths,
            args.voxel_sizes,
            arg_groups["NiftyReg registration backend options"],
            BRAINREG_PRE_PROCESSING_ARGS,
            sort_input_file=args.sort_input_file,
            n_free_cpus=args.n_free_cpus,
            additional_images_downsample=additional_images_downsample,
            backend=args.backend,
            debug=args.debug,
        )

    else:
        logging.info("Skipping registration")

    if len(args.signal_planes_paths) > 1:
        base_directory = args.output_dir

        for idx, signal_paths in enumerate(args.signal_planes_paths):
            channel = args.signal_ch_ids[idx]
            logging.info("Processing channel: " + str(channel))
            channel_directory = os.path.join(
                base_directory, "channel_" + str(channel)
            )
            if not os.path.exists(channel_directory):
                os.makedirs(channel_directory)

            # prep signal channel specific args
            args.signal_planes_paths[0] = signal_paths
            # TODO: don't overwrite args.output_dir - use Paths instead
            args.output_dir = channel_directory
            args.signal_channel = channel
            # Run for each channel
            run_all(args, what_to_run, atlas)

    else:
        args.signal_channel = args.signal_ch_ids[0]
        run_all(args, what_to_run, atlas)
    logging.info(
        "Finished. Total time taken: {}".format(datetime.now() - start_time)
    )


def run_all(args, what_to_run, atlas):
    from cellfinder.core.classify import classify
    from cellfinder.core.detect import detect
    from cellfinder.core.tools import prep

    from brainglobe_workflows.brainmapper import analyse
    from brainglobe_workflows.brainmapper.prep import (
        prep_candidate_detection,
        prep_channel_specific_general,
    )

    points = None
    signal_array = None
    args, what_to_run = prep_channel_specific_general(args, what_to_run)

    if what_to_run.detect:
        logging.info("Detecting cell candidates")
        args = prep_candidate_detection(args)
        signal_array = read_z_stack(
            args.signal_planes_paths[args.signal_channel]
        )

        points = detect.main(
            signal_array,
            args.start_plane,
            args.end_plane,
            args.voxel_sizes,
            args.soma_diameter,
            args.max_cluster_size,
            args.ball_xy_size,
            args.ball_z_size,
            args.ball_overlap_fraction,
            args.soma_spread_factor,
            args.n_free_cpus,
            args.log_sigma_size,
            args.n_sds_above_mean_thresh,
            save_planes=args.save_planes,
            plane_directory=args.plane_directory,
        )
        ensure_directory_exists(args.paths.points_directory)

        save_cells(
            points,
            args.paths.detected_points,
            save_csv=args.save_csv,
            artifact_keep=args.artifact_keep,
        )

    else:
        logging.info("Skipping cell detection")
        points = get_cells(args.paths.detected_points)

    if what_to_run.classify:
        model_weights = prep.prep_model_weights(
            args.model_weights,
            args.install_path,
            args.model,
        )
        if what_to_run.classify:
            if points is None:
                points = get_cells(args.paths.detected_points)
            if signal_array is None:
                signal_array = read_z_stack(
                    args.signal_planes_paths[args.signal_channel]
                )
            logging.info("Running cell classification")
            background_array = read_z_stack(args.background_planes_path[0])

            points = classify.main(
                points,
                signal_array,
                background_array,
                args.n_free_cpus,
                args.voxel_sizes,
                args.network_voxel_sizes,
                args.batch_size,
                args.cube_height,
                args.cube_width,
                args.cube_depth,
                args.trained_model,
                model_weights,
                args.network_depth,
            )
            save_cells(
                points,
                args.paths.classified_points,
                save_csv=args.save_csv,
            )

            what_to_run.cells_exist = cells_exist(args.paths.classified_points)

        else:
            logging.info("No cells were detected, skipping classification.")

    else:
        logging.info("Skipping cell classification")

    what_to_run.update_if_cells_required()

    if what_to_run.analyse or what_to_run.figures:
        downsampled_space = get_downsampled_space(
            atlas, args.brainreg_paths.boundaries_file_path
        )

    if what_to_run.analyse:
        points = get_cells(args.paths.classified_points, cells_only=True)
        if len(points) == 0:
            logging.info("No cells detected, skipping cell position analysis")
        else:
            logging.info("Analysing cell positions")
            analyse.run(args, points, atlas, downsampled_space)
    else:
        logging.info("Skipping cell position analysis")

    if what_to_run.figures:
        points = get_cells(args.paths.classified_points, cells_only=True)
        if len(points) == 0:
            logging.info("No cells detected, skipping")
        else:
            logging.info("Generating heatmap")

            if args.mask_figures:
                mask_image = tifffile.imread(
                    args.brainreg_paths.registered_atlas
                )
            else:
                mask_image = None

            downsampled_points = pd.read_hdf(
                args.paths.downsampled_points
            ).values

            heatmap_from_points(
                downsampled_points,
                atlas.resolution[0],  # assumes isotropic atlas
                downsampled_space.shape,
                output_filename=args.paths.heatmap,
                smoothing=args.heatmap_smooth,
                mask_image=mask_image,
            )
    else:
        logging.info("Skipping figure generation")


if __name__ == "__main__":
    main()
