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
from numpy import array, float32, float64, transpose
from numpy.linalg import norm

# relax module imports.
from base_script import Base_script
from lib.geometry.rotations import R_to_euler_zyz


def eigen_system():
    """Recreate the eigensystem parameters."""

    # The centre of masses of each domain (from the system_create.log file).
    N_COM = array([41.739, 6.03, -0.764], float64)
    C_COM = array([26.837, -12.379, 28.342], float64)

    # The Z-axis as the inter CoM vector.
    z_axis = N_COM - C_COM
    disp = norm(z_axis)
    z_axis /= disp

    # The eigenframe (partly from the system_create.log file).
    eigensystem = transpose(array([
        [-0.487095774865268, -0.60362450312215, -0.63116968030708 ],
        [ -7.778375610280605e-01, 6.284649244351433e-01, -7.532653237683726e-04],
        z_axis
    ], float64))

    # Convert to Euler angles.
    a, b, g = R_to_euler_zyz(eigensystem)

    # Return the parameters.
    return a, b, g, disp



class Analysis(Base_script):
    # The directory containing the data files.
    DIRECTORY = 'double_rotor'

    # The frame order model.
    MODEL = 'double rotor'

    # The model parameters.
    EIGEN_ALPHA, EIGEN_BETA, EIGEN_GAMMA, PIVOT_DISP = eigen_system()
    CONE_SIGMA_MAX = 10.5 / 2.0 / 360.0 * 2.0 * pi
    CONE_SIGMA_MAX_2 = 11.5 / 2.0 / 360.0 * 2.0 * pi

    # The pivot point.
    PIVOT = array([26.837, -12.379, 28.342], float32)


# Execute the analysis.
Analysis(self._execute_uf)
