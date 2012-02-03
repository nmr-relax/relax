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
    ave_pos_beta = 1.1321377968123119
    ave_pos_gamma = 0.029867114268410672
    axis_theta = 0.69828059268540488
    axis_phi = -2.2509097944247132
    cone_s1 = iso_cone_theta_to_S(20.0 * 2.0 * pi / 360.0)
    cone = True
    num_int_pts = 50


# Execute the analysis.
Analysis(self)
