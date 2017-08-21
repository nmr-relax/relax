###############################################################################
#                                                                             #
# Copyright (C) 2011-2012 Edward d'Auvergne                                   #
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
from math import acos
from numpy import dot

# relax module imports.
from lib.geometry.rotations import R_random_hypersphere

# Base module import.
from generate_base import Main


class Generate(Main):
    # The number of structures.
    N = 20000000

    # Cone parameters.
    THETA_MAX = 1.0

    def __init__(self):
        """Model specific setup."""

        # Alias the required methods.
        self.axes_to_pdb = self.axes_to_pdb_main_axis
        self.build_axes = self.build_axes_pivot_com


    def rotation(self, i, motion_index=0):
        """Set up the rotation for state i."""

        # Loop until a valid rotation matrix is found.
        while True:
            # The random rotation matrix.
            R_random_hypersphere(self.R)

            # Rotate the Z-axis.
            rot_axis = dot(self.R, self.axes[:, 2])

            # Calculate the projection and angle.
            proj = dot(self.axes[:, 2], rot_axis)

            # Calculate the angle, taking float16 truncation errors into account.
            if proj > 1.0:
                proj = 1.0
            elif proj < -1.0:
                proj = -1.0
            theta = acos(proj)

            # Skip the rotation if the angle is violated.
            if theta > self.THETA_MAX:
                continue

            # Rotation is ok, so stop looping.
            break


# Execute the code.
generate = Generate()
generate.run()
