import json
import os
from pathlib import Path

from brainglobe_workflows.brainglobe_atlasapi.create_mouse_atlas import (
    create_mouse_atlas,
)


class TimeBenchmark:
    # Timing attributes
    timeout = 3600  # default: 60 s

    def setup(self):
        # read input config: environment variable if it exists, else default
        input_config_path = os.getenv(
            "ATLAS_CONFIG_PATH",
            default=str(
                Path(__file__).parents[2]
                / "brainglobe_workflows"
                / "configs"
                / "brainglobe_atlasapi_small.json"
            ),
        )

        assert Path(input_config_path).exists()

        # read as dict
        with open(input_config_path) as cfg:
            config_dict = json.load(cfg)

        # pass dict to class
        self.config = config_dict

    def time_create_mouse_atlas(self):
        create_mouse_atlas(**self.config)
