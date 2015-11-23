###############################################################################
#                                                                             #
# Copyright (C) 2004-2015 Edward d'Auvergne                                   #
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

"""Back-calculate and save relaxation data starting from a saved model-free results file."""


# Load the results as a state file.
state.load('results')

# Loop over each relaxation data set.
for ri_id in cdp.ri_ids:
    # Back calculate the relaxation data.
    relax_data.back_calc(ri_id=ri_id, ri_type=cdp.ri_type[ri_id], frq=cdp.spectrometer_frq[ri_id])

    # Write the data.
    relax_data.write(ri_id=ri_id, file='%s.out' % ri_id.lower(), bc=True, force=True)
