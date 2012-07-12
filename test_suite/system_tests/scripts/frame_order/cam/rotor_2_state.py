###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
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

# relax module imports.
from base_script import Base_script


class Analysis(Base_script):

    # Set up some class variables.
    directory = 'rotor_2_state'
    model = 'rotor'
    ave_pos_alpha = 4.3434999280669997
    ave_pos_beta = 0.43544332764249905
    ave_pos_gamma = 3.8013235235956007
    axis_theta = 0.52344988559983696152
    axis_phi = 0.89068285262982982431
    cone_sigma_max = 10.0 / 360.0 * 2.0 * pi
    cone = True
    num_int_pts = 50


# Execute the analysis.
Analysis(self._execute_uf)
