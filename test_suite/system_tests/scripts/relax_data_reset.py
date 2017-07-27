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
"""This system test script tests out the relax_data.frq and relax_data.type user functions."""

# Python module imports.
from os import sep

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# The data path.
DATA_PATH = status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'model_free' + sep + 'sphere' + sep

# Create a data pipe.
self._execute_uf(uf_name='pipe.create', pipe_name='test', pipe_type='mf')

# Load the sequence.
self._execute_uf(uf_name='sequence.read', file='noe.500.out', dir=DATA_PATH, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5)

# Name the spins.
self._execute_uf(uf_name='spin.name', name='N')

# Load the relaxation data.
self._execute_uf(uf_name='relax_data.read', ri_id='R1_900',  ri_type='R1',  frq=900*1e6, file='r1.900.out',  dir=DATA_PATH, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)
self._execute_uf(uf_name='relax_data.read', ri_id='R2_900',  ri_type='R2',  frq=900*1e6, file='r2.900.out',  dir=DATA_PATH, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)
self._execute_uf(uf_name='relax_data.read', ri_id='NOE_900', ri_type='NOE', frq=900*1e6, file='noe.900.out', dir=DATA_PATH, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)
self._execute_uf(uf_name='relax_data.read', ri_id='R1_500',  ri_type='R1',  frq=500*1e6, file='r1.500.out',  dir=DATA_PATH, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)
self._execute_uf(uf_name='relax_data.read', ri_id='R2_500',  ri_type='R2',  frq=500*1e6, file='r2.500.out',  dir=DATA_PATH, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)
self._execute_uf(uf_name='relax_data.read', ri_id='NOE_500', ri_type='NOE', frq=500*1e6, file='noe.500.out', dir=DATA_PATH, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)

# Reset a few frequencies.
self._execute_uf(uf_name='spectrometer.frequency', id="R1_900", frq=900100000)
self._execute_uf(uf_name='spectrometer.frequency', id="R2_900", frq=900100000)
self._execute_uf(uf_name='spectrometer.frequency', id="NOE_900", frq=900100000)
self._execute_uf(uf_name='spectrometer.frequency', id="R1_500", frq=400100000)

# Reset a few types.
self._execute_uf(uf_name='relax_data.type', ri_id="NOE_900", ri_type="R2")
self._execute_uf(uf_name='relax_data.type', ri_id="NOE_500", ri_type="R2")
