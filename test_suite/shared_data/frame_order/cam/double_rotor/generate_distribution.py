###############################################################################
#                                                                             #
# Copyright (C) 2011-2012,2014 Edward d'Auvergne                              #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""Script for generating the distribution of PDB structures."""

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
    N = 4500

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
            [-0.487095774865268, -0.60362450312215, -0.63116968030708 ],
            [ -7.778375610280605e-01, 6.284649244351433e-01, -7.532653237683726e-04]
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
