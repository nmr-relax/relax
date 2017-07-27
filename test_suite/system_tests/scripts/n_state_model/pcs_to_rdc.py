###############################################################################
#                                                                             #
# Copyright (C) 2010,2012 Edward d'Auvergne                                   #
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

# Python module imports.
from os import sep

# relax imports.
from pipe_control.interatomic import interatomic_loop
from lib.periodic_table import periodic_table
from lib.physical_constants import NH_BOND_LENGTH_RDC, dipolar_constant
from status import Status; status = Status()


# Path of the files.
str_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

# The data pipe.
self._execute_uf(uf_name='pipe.create', pipe_name='rdc_back_calc', pipe_type='N-state')

# Load the structures.
self._execute_uf(uf_name='structure.read_pdb', file='trunc_ubi_pcs.pdb', dir=str_path)

# Load the spins.
self._execute_uf(uf_name='structure.load_spins', spin_id='@N', ave_pos=False)
self._execute_uf(uf_name='structure.load_spins', spin_id='@H', ave_pos=False)

# Define the magnetic dipole-dipole relaxation interaction.
self._execute_uf(uf_name='interatom.define', spin_id1='@N', spin_id2='@H', direct_bond=True)
self._execute_uf(uf_name='interatom.set_dist', spin_id1='@N', spin_id2='@H', ave_dist=NH_BOND_LENGTH_RDC)
self._execute_uf(uf_name='interatom.unit_vectors', ave=True)

# Set the nuclear isotope.
self._execute_uf(uf_name='spin.isotope', isotope='15N', spin_id='@N')
self._execute_uf(uf_name='spin.isotope', isotope='1H', spin_id='@H')

# The dipolar constant.
const = 3.0 / (2.0*pi) * dipolar_constant(periodic_table.gyromagnetic_ratio('15N'), periodic_table.gyromagnetic_ratio('1H'), NH_BOND_LENGTH_RDC)

# The tensor.
tensor = 'A'
self._execute_uf(uf_name='align_tensor.init', tensor=tensor, params=(4.724/const,  11.856/const, 0, 0, 0), align_id=tensor, param_types=2)

# The temperature.
self._execute_uf(uf_name='spectrometer.temperature', id=tensor, temp=298)

# The frequency.
self._execute_uf(uf_name='spectrometer.frequency', id=tensor, frq=900.0 * 1e6)

# One state model.
self._execute_uf(uf_name='n_state_model.select_model', model='fixed')
self._execute_uf(uf_name='n_state_model.number_of_states', N=1)

# Set the RDC data.
rdcs = [-1.390, -6.270, -9.650]
i = 0
for interatom in interatomic_loop():
    interatom.rdc = {}
    interatom.rdc[tensor] = rdcs[i]
    i += 1

# Back calc.
self._execute_uf(uf_name='rdc.back_calc', align_id=tensor)
