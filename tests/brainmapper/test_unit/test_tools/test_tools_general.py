import numpy as np

import brainglobe_workflows.brainmapper.tools.tools as tools

a = [1, "a", 10, 30]
b = [30, 10, "c", "d"]

test_2d_img = np.array([[1, 2, 10, 100], [5, 25, 300, 1000], [1, 0, 0, 125]])
validate_2d_img = np.array(
    [
        [65.535, 131.07, 655.35, 6553.5],
        [327.675, 1638.375, 19660.5, 65535],
        [65.535, 0, 0, 8191.875],
    ]
)


def test_check_unique_list():
    assert (True, []) == tools.check_unique_list(a)
    repeating_list = [1, 2, 3, 3, "dog", "cat", "dog"]
    assert (False, [3, "dog"]) == tools.check_unique_list(repeating_list)


def test_common_member():
    assert (True, [10, 30]) == tools.common_member(a, b)
