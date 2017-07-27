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
"""Script for testing J(w) mapping."""

# Python module imports.
from os import sep

# relax module imports.
from lib.physical_constants import N15_CSA
from status import Status; status = Status()


# Data directory.
dir = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'jw_mapping'+sep

# The data.
ri_ids = ['NOE_600', 'R1_600', 'R2_600']
ri_type = ['NOE', 'R1', 'R2']
frq = [600e6]*3
data_paths = [dir + 'noe.dat', dir + 'R1.dat', dir + 'R2.dat']

# Read the sequence.
self._execute_uf(uf_name='sequence.read', file='test_seq', dir=status.install_path + sep+'test_suite'+sep+'shared_data', res_num_col=1, res_name_col=2)

# Read the data.
for i in range(len(ri_ids)):
    self._execute_uf(uf_name='relax_data.read', ri_id=ri_ids[i], ri_type=ri_type[i], frq=frq[i], file=data_paths[i], res_num_col=1, res_name_col=2, data_col=3, error_col=4)

# Set the spin information.
self._execute_uf(uf_name='spin.name', name='N')
self._execute_uf(uf_name='spin.element', element='N')
self._execute_uf(uf_name='sequence.attach_protons')
self._execute_uf(uf_name='spin.isotope', isotope='15N', spin_id='@N')
self._execute_uf(uf_name='spin.isotope', isotope='1H', spin_id='@H')

# Define the magnetic dipole-dipole relaxation interaction.
self._execute_uf(uf_name='interatom.define', spin_id1='@N', spin_id2='@H', direct_bond=True)
self._execute_uf(uf_name='interatom.set_dist', spin_id1='@N', spin_id2='@H', ave_dist=1.02 * 1e-10)

# Define the chemical shift relaxation interaction.
self._execute_uf(uf_name='value.set', val=N15_CSA, param='csa')

# Select the frequency.
self._execute_uf(uf_name='jw_mapping.set_frq', frq=600.0 * 1e6)

# Try the reduced spectral density mapping.
self._execute_uf(uf_name='minimise.calculate')
