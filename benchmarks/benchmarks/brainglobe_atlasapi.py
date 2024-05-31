from brainglobe_workflows.brainglobe_atlasapi.create_mouse_atlas import (
    create_mouse_atlas,
)


class TimeBenchmark:
    # Timing attributes
    timeout = 3600  # default: 60 s
    version = (
        None  # benchmark version. Default:None (i.e. hash of source code)
    )
    warmup_time = 0.1  # seconds
    rounds = 2
    repeat = 0
    sample_time = 0.01  # default: 10 ms = 0.01 s;
    min_run_count = 2  # default:2

    def time_create_mouse_atlas(self):
        create_mouse_atlas()
