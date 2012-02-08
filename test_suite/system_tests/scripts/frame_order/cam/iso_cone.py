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
"""Script for optimising the isotropic cone frame order test model of CaM."""

# Python module imports.
from os import sep

# relax module imports.
from status import Status; status = Status()


# Path of the save file.
DATA_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'frame_order'+sep+'cam'+sep+'iso_cone'

# Load the save file.
reset()
state.load('frame_order', dir=DATA_PATH)

# Set up some variables.
value.set(param='ave_pos_alpha', val=4.3434999280669997)
value.set(param='ave_pos_beta', val=0.43544332764249905)
value.set(param='ave_pos_gamma', val=3.8013235235956007)
value.set(param='axis_theta', val=2.1815126749944502)
value.set(param='axis_phi', val=0.89068285262982982)
value.set(param='cone_theta', val=10.0 * 2.0 * pi / 360.0)
value.set(param='cone_sigma_max', val=20.0 * 2.0 * pi / 360.0)

# Increase the number of Sobol points so the cone is sampled.
cdp.num_int_pts = 100

# Calculate the chi-squared value.
calc()
