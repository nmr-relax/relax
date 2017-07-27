###############################################################################
#                                                                             #
# Copyright (C) 2008,2011-2012 Edward d'Auvergne                              #
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
"""Script for setting up the data pipe for testing optimisation.

The data set is:
    S2 = 0.970.
    te = 2048 ps.
    Rex = 0.149 s^-1.
"""

# Python module imports.
from os import sep

# relax module imports.
from status import Status; status = Status()


# Path of the files.
cdp.path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'local_tm_10_S2_0.8_te_40'

# Create the two spins.
spin.create(res_num=5, res_name='GLU', spin_name='N')
spin.create(res_num=5, res_name='GLU', spin_name='H')
spin.element('N', '@N')
spin.element('H', '@H')
spin.isotope('15N', spin_id='@N')
spin.isotope('1H', spin_id='@H')

# Define the magnetic dipole-dipole relaxation interaction.
interatom.define(spin_id1='@N', spin_id2='@H', direct_bond=True)
interatom.set_dist(spin_id1='@N', spin_id2='@H', ave_dist=1.02 * 1e-10)

# Define the chemical shift relaxation interaction.
value.set(-172 * 1e-6, 'csa')

# Select the model-free model.
model_free.select_model(model='tm2')
