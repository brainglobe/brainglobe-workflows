import logging

import numpy as np
from brainglobe_utils.brainmapper.analysis import (
    summarise_points_by_atlas_region,
)
from brainglobe_utils.brainmapper.export import export_points_to_brainrender
from brainglobe_utils.brainreg.transform import transform_points_to_atlas_space


def run(args, cells, atlas, downsampled_space):
    deformation_field_paths = [
        args.brainreg_paths.deformation_field_0,
        args.brainreg_paths.deformation_field_1,
        args.brainreg_paths.deformation_field_2,
    ]

    cell_list = []
    for cell in cells:
        cell_list.append([cell.z, cell.y, cell.x])
    cells = np.array(cell_list)

    run_analysis(
        cells,
        args.signal_planes_paths[0],
        args.orientation,
        args.voxel_sizes,
        atlas,
        deformation_field_paths,
        downsampled_space,
        args.paths.downsampled_points,
        args.paths.atlas_points,
        args.paths.brainrender_points,
        args.brainreg_paths.volume_csv_path,
        args.paths.all_points_csv,
        args.paths.summary_csv,
    )


def run_analysis(
    cells,
    signal_planes,
    orientation,
    voxel_sizes,
    atlas,
    deformation_field_paths,
    downsampled_space,
    downsampled_points_path,
    atlas_points_path,
    brainrender_points_path,
    volume_csv_path,
    all_points_csv_path,
    summary_csv_path,
):
    logging.info("Transforming points to atlas space")
    transformed_cells, points_out_of_bounds = transform_points_to_atlas_space(
        cells,
        signal_planes,
        orientation,
        voxel_sizes,
        downsampled_space,
        atlas,
        deformation_field_paths,
        downsampled_points_path=downsampled_points_path,
        atlas_points_path=atlas_points_path,
    )
    logging.warning(
        f"{len(points_out_of_bounds)} points ignored due to falling outside "
        f"of atlas. This may be due to inaccuracies with "
        f"cell detection or registration. Please inspect the results."
    )

    logging.info("Summarising cell positions")
    summarise_points_by_atlas_region(
        cells,
        transformed_cells,
        atlas,
        volume_csv_path,
        all_points_csv_path,
        summary_csv_path,
    )
    logging.info("Exporting data to brainrender")
    export_points_to_brainrender(
        transformed_cells, atlas.resolution[0], brainrender_points_path
    )
