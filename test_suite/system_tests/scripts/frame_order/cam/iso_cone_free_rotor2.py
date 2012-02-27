###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

# Module docstring.
"""Script for optimising the second isotropic cone, free rotor frame order test model of CaM."""

# relax module imports.
from base_script import Base_script
from maths_fns.order_parameters import iso_cone_theta_to_S


class Analysis(Base_script):

    # Set up some class variables.
    directory = 'iso_cone_free_rotor2'
    model = 'iso cone, free rotor'
    ave_pos_alpha = 4.3434999280669997
    ave_pos_beta = 0.77485244603476433
    ave_pos_gamma = 0.1420704587263735
    axis_theta = 0.69828059079619353433
    axis_phi = 4.03227550621962294031
    cone_s1 = iso_cone_theta_to_S(1.2)
    cone = True
    num_int_pts = 50


# Execute the analysis.
Analysis(self)
