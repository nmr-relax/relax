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
"""Script for optimising the second rotor frame order test model of CaM."""

# Python module imports
from numpy import array, float32

# relax module imports.
from base_script import Base_script


class Analysis(Base_script):
    # The directory containing the data files.
    DIRECTORY = 'double_rotor'

    # The frame order model.
    MODEL = 'double rotor'

    # The model parameters.
    AXIS_THETA = 1.494291741547518
    AXIS_PHI = 2.525044022476957
    CONE_SIGMA_MAX = 10.5 / 360.0 * 2.0 * pi
    AXIS_THETA2 = 2.30381499622381
    AXIS_PHI2 = -2.249696457768556
    CONE_SIGMA_MAX2 = 11.5 / 360.0 * 2.0 * pi

    # The pivot points.
    PIVOT = array([41.739, 6.03, -0.764], float32)
    PIVOT2 = array([26.837, -12.379, 28.342], float32)


# Execute the analysis.
Analysis(self._execute_uf)
