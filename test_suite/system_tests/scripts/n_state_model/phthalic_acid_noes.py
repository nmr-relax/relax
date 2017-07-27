###############################################################################
#                                                                             #
# Copyright (C) 2009-2010 Edward d'Auvergne                                   #
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
"""Script for testing the loading of phthalic acid NOEs from a generically formatted file."""

# Python module imports.
from os import sep

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# Add a date pipe if one doesn't already exist.
if not len(ds):
    self._execute_uf(uf_name='pipe.create', pipe_name='test', pipe_type='N-state')

# NOE restraint file.
if not hasattr(ds, 'file_name'):
    ds.file_name = 'phthalic_acid'

# Path of the relaxation data.
DATA_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep

# Pseudo-atoms.
PSEUDO = [
['Q7', ['@H16', '@H17', '@H18']],
['Q9', ['@H20', '@H21', '@H22']],
['Q10', ['@H23', '@H24', '@H25']]
]

# Read the structure.
self._execute_uf(uf_name='structure.read_pdb', file='gromacs.pdb', dir=DATA_PATH+sep+'structures'+sep+'phthalic_acid')

# Load all protons as the sequence.
self._execute_uf(uf_name='structure.load_spins', spin_id='@*H*', ave_pos=False)

# Create the pseudo-atoms.
for i in range(len(PSEUDO)):
    self._execute_uf(uf_name='spin.create_pseudo', spin_name=PSEUDO[i][0], res_id=None, members=PSEUDO[i][1], averaging='linear')

# Read the NOE restraints.
self._execute_uf(uf_name='noe.read_restraints', file=ds.file_name, dir=DATA_PATH+'noe_restraints')

# Set the type of N-state model.
self._execute_uf(uf_name='n_state_model.select_model', model='fixed')

# Calculate the average NOE potential.
self._execute_uf(uf_name='minimise.calculate')


