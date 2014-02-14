###############################################################################
#                                                                             #
# Copyright (C) 2012-2014 Edward d'Auvergne                                   #
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
"""Script for optimising the rotor frame order test model of CaM."""

# Python module imports
from numpy import arcsin, array, dot, float64, zeros

# relax module imports.
from base_script import Base_script
from lib.geometry.coord_transform import spherical_to_cartesian


class Analysis(Base_script):

    # Set up some class variables.
    DIRECTORY = 'rotor'
    MODEL = 'rotor'
    CONE_SIGMA_MAX = 30.0 / 360.0 * 2.0 * pi

    # Translate the system.
    axis_theta = 0.9600799785953431
    axis_phi = 4.0322755062196229
    r_ax = zeros(3, float64)
    spherical_to_cartesian([1, axis_theta, axis_phi], r_ax)
    AXIS_ALPHA = arcsin(dot(r_ax, array([0, 0, 1], float64)))

# Execute the analysis.
Analysis(self._execute_uf)
