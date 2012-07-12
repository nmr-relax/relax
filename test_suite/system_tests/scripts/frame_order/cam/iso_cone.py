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
"""Script for optimising the isotropic cone frame order test model of CaM."""

# relax module imports.
from base_script import Base_script


class Analysis(Base_script):

    # Set up some class variables.
    directory = 'iso_cone'
    model = 'iso cone'
    ave_pos_alpha = 4.3434999280669997
    ave_pos_beta = 0.43544332764249905
    ave_pos_gamma = 3.8013235235956007
    axis_theta = 0.96007997859534299767
    axis_phi = 4.03227550621962294031
    cone_theta = 0.6
    cone_sigma_max = 0.9
    cone = True
    #load_state = True
    num_int_pts = 50


# Execute the analysis.
Analysis(self._execute_uf)
