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
"""Script for optimising the isotropic cone, free rotor frame order test model of CaM."""

# relax module imports.
from base_script import Base_script


class Analysis(Base_script):

    # Set up some class variables.
    directory = 'iso_cone_free_rotor'
    model = 'iso cone, free rotor'
    ave_pos_beta = 1.1983544319568078
    ave_pos_gamma = 0.333131539777762
    axis_theta = 0.9600799785953431
    axis_phi = 4.0322755062196229
    cone_s1 = 0.91322057310490712
    cone = True
    num_int_pts = 50


# Execute the analysis.
Analysis(self)
