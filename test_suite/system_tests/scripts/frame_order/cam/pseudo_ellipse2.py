###############################################################################
#                                                                             #
# Copyright (C) 2012-2013 Edward d'Auvergne                                   #
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
"""Script for optimising the pseudo-ellipse frame order test model of CaM."""

# relax module imports.
from base_script import Base_script
from maths_fns.rotation_matrix import reverse_euler_zyz


class Analysis(Base_script):

    # Set up some class variables.
    directory = 'pseudo_ellipse2'
    model = 'pseudo-ellipse'
    ave_pos_alpha, ave_pos_beta, ave_pos_gamma = reverse_euler_zyz(4.3434999280669997, 0.43544332764249905, 3.8013235235956007)
    eigen_alpha = 3.14159265358979311600
    eigen_beta = 0.69828059079619364535
    eigen_gamma = 4.03227550621962294031
    cone_theta_x = 0.8
    cone_theta_y = 1.2
    cone_sigma_max = 0.9
    cone = True
    num_int_pts = 50


# Execute the analysis.
Analysis(self._execute_uf)
