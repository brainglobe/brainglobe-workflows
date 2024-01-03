from brainglobe_workflows.brainmapper.export.abc4d import (
    export_points as abc4d_export,
)
from brainglobe_workflows.brainmapper.export.brainrender import (
    export_points as brainrender_export,
)


def export_points(
    point_info, points, resolution, brainrender_points_path, abc4d_points_path
):
    brainrender_export(points, resolution, brainrender_points_path)
    abc4d_export(point_info, resolution, abc4d_points_path)
