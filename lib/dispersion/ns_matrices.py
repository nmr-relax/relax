###############################################################################
#                                                                             #
# Copyright (C) 2013 Edward d'Auvergne                                        #
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
"""A collection of functions for generating the relaxation matrices for the numerical solutions.

These are for the numerical solutions to the Bloch-McConnell equations for relaxation dispersion.
"""

# Python module imports.
from numpy import matrix


def rcpmg_2d(R2E=None, R2G=None, df=None, kGE=None, kEG=None):
    """Definition of the 2D exchange matrix.

    @keyword R2E:   The transverse, spin-spin relaxation rate for state A.
    @type R2E:      float
    @keyword R2G:   The transverse, spin-spin relaxation rate for state B.
    @type R2G:      float
    @keyword df:    FIXME - add description.
    @type df:       float
    @keyword kGE:   The forward exchange rate from state A to state B.
    @type kGE:      float
    @keyword kEG:   The reverse exchange rate from state B to state A.
    @type kEG:      float
    @return:        The relaxation matrix.
    @rtype:         numpy rank-2, 4D array
    """

    # Parameter conversions.
    fG = 0
    fE = fG + df 

    # Create the matrix.
    temp = matrix([
        [-R2G-kGE,          -fG,        kEG,        0.0],
        [      fG,     -R2G-kGE,        0.0,        kEG], 
        [     kGE,          0.0,   -R2E-kEG,        -fE], 
        [     0.0,          kGE,         fE,   -R2E-kEG]
    ])

    # Return the matrix.
    return temp


def rcpmg_3d(R1E=None, R1G=None, R2E=None, R2G=None, df=None, kGE=None, kEG=None):
    """Definition of the 3D exchange matrix.

    @keyword R1E:   The longitudinal, spin-lattice relaxation rate for state A.
    @type R1E:      float
    @keyword R1G:   The longitudinal, spin-lattice relaxation rate for state B.
    @type R1G:      float
    @keyword R2E:   The transverse, spin-spin relaxation rate for state A.
    @type R2E:      float
    @keyword R2G:   The transverse, spin-spin relaxation rate for state B.
    @type R2G:      float
    @keyword df:    FIXME - add description.
    @type df:       float
    @keyword kGE:   The forward exchange rate from state A to state B.
    @type kGE:      float
    @keyword kEG:   The reverse exchange rate from state B to state A.
    @type kEG:      float
    @return:        The relaxation matrix.
    @rtype:         numpy rank-2, 7D array
    """

    # Parameter conversions.
    fG = 0.0
    fE = df
    IGeq = kEG / (kEG + kGE)
    IEeq = kGE / (kEG + kGE)

    # Create the matrix.
    temp = matrix([
        [        0.0,       0.0,         0.0,       0.0,       0.0,        0.0,      0.0], 
        [        0.0,  -R2G-kGE,         -fG,       0.0,       kEG,        0.0,      0.0],
        [        0.0,        fG,    -R2G-kGE,       0.0,       0.0,        kEG,      0.0], 
        [2.0*R1G*IGeq,      0.0,         0.0,  -R1G-kGE,       0.0,        0.0,      kEG],
        [        0.0,       kGE,         0.0,       0.0,  -R2E-kEG,        -fE,      0.0], 
        [        0.0,       0.0,         kGE,       0.0,        fE,   -R2E-kEG,      0.0],
        [2.0*R1E*IEeq,      0.0,         0.0,       kGE,       0.0,        0.0, -R1E-kEG]
    ])

    # Return the matrix.
    return temp
