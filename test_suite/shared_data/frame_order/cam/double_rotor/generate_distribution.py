# Script for generating the distribution of PDB structures.

# Modify the system path to load the base module.
import sys
sys.path.append('..')

# Python module imports.
from math import pi

# relax module imports.
from lib.geometry.rotations import axis_angle_to_R

# Base module import.
from generate_base import Main


class Generate(Main):
    # The pivot points.
    PIVOT = [
        [26.837, -12.379, 28.342],  # C-domain CoM.
        [41.739, 6.03, -0.764]      # N-domain CoM.
    ]

    # The number of rotation modes.
    MODES = 2

    # The number of states for each rotation mode.
    N = 500

    # The tilt angles.
    TILT_ANGLE = [11.5, 10.5]
    INC = [TILT_ANGLE[0] / float(N - 1), TILT_ANGLE[1] / float(N - 1)]

    # The PDB distribution flag.
    DIST_PDB = False

    # The rotations file.
    ROT_FILE = False

    # The state file.
    SAVE_STATE = False

    def __init__(self):
        """Model specific setup."""


    def build_axes(self):
        """Set up the rotation axis systems."""

        # The rotation axes from the system_create.py script.
        self.axes = [
            [-0.466656683389221, -0.578372959594177, -0.6691160283975  ],
            [-0.813492486210042,  0.576531381125376,  0.076429977479197]
        ]


    def rotation(self, i, motion_index=0):
        """Set up the rotation for state i."""

        # The rotation angle.
        angle = (i - (self.N-1)/2) * self.INC[motion_index] / 360.0 * 2.0 * pi

        # The rotation matrix.
        axis_angle_to_R(self.axes[motion_index], angle, self.R)


# Execute the code.
generate = Generate()
generate.run()
