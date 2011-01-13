###############################################################################
#                                                                             #
# Copyright (C) 2011 Edward d'Auvergne                                        #
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

"""Set up the data pipe for testing optimisation against tm2 relaxation data."""

# relax module imports.
from opt_tm_fns import create_sequence, opt_and_check, setup_data


# The model-free parameters.
tm = [2e-9, 10e-9, 21e-9]
s2 = [0.2, 0.8, 0.95]
te = [2e-12, 40e-12, 1e-9]

# Create the sequence.
create_sequence(len(tm)*len(s2)*len(te))

# Set up the data.
setup_data(dir='tm2_grid')

# Residue index.
res_index = 0

# Loop over the parameters.
for te_index in range(3):
    for s2_index in range(3):
        for tm_index in range(3):
            # Optimise and validate.
            opt_and_check(spin=cdp.mol[0].res[res_index].spin[0], tm=tm[tm_index], s2=s2[s2_index], te=te[te_index])

            # Increment the residue index.
            res_index += 1
