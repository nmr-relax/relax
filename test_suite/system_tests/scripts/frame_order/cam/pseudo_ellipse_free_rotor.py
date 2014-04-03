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
"""Script for optimising the free rotor pseudo-ellipse frame order test model of CaM."""

# relax module imports.
from base_script import Base_script


class Analysis(Base_script):

    # Set up some class variables.
    DIRECTORY = 'pseudo_ellipse_free_rotor'
    MODEL = 'pseudo-ellipse, free rotor'
    EIGEN_ALPHA = 3.1415926535897931
    EIGEN_BETA = 0.96007997859534311
    EIGEN_GAMMA = 4.0322755062196229
    CONE_THETA_X = 0.5
    CONE_THETA_Y = 0.3


# Execute the analysis.
Analysis(self._execute_uf)
