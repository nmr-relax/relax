###############################################################################
#                                                                             #
# Copyright (C) 2008,2011-2012,2014 Edward d'Auvergne                         #
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
"""Script for mapping the {S2, te, Rex} chi2 space for visualisation using OpenDX."""

# Python module imports.
from os import sep

# relax module imports.
from lib.physical_constants import N15_CSA
from status import Status; status = Status()


# Path of the files.
path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'S2_0.970_te_2048_Rex_0.149'

# Set up the 15N spins.
self._execute_uf(uf_name='sequence.read', file='noe.500.out', dir=path, res_num_col=1, res_name_col=2)
self._execute_uf(uf_name='spin.name', name='N')
self._execute_uf(uf_name='spin.element', element='N')
self._execute_uf(uf_name='spin.isotope', isotope='15N', spin_id='@N')

# Read the relaxation data.
self._execute_uf(uf_name='relax_data.read', ri_id='R1_600',  ri_type='R1',  frq=600.0*1e6, file='r1.600.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
self._execute_uf(uf_name='relax_data.read', ri_id='R2_600',  ri_type='R2',  frq=600.0*1e6, file='r2.600.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
self._execute_uf(uf_name='relax_data.read', ri_id='NOE_600', ri_type='NOE', frq=600.0*1e6, file='noe.600.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
self._execute_uf(uf_name='relax_data.read', ri_id='R1_500',  ri_type='R1',  frq=500.0*1e6, file='r1.500.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
self._execute_uf(uf_name='relax_data.read', ri_id='R2_500',  ri_type='R2',  frq=500.0*1e6, file='r2.500.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
self._execute_uf(uf_name='relax_data.read', ri_id='NOE_500', ri_type='NOE', frq=500.0*1e6, file='noe.500.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)

# Initialise the diffusion tensor.
self._execute_uf(uf_name='diffusion_tensor.init', params=1e-8, fixed=True)

# Create all attached protons.
self._execute_uf(uf_name='sequence.attach_protons')

# Define the magnetic dipole-dipole relaxation interaction.
self._execute_uf(uf_name='interatom.define', spin_id1='@N', spin_id2='@H', direct_bond=True)
self._execute_uf(uf_name='interatom.set_dist', spin_id1='@N', spin_id2='@H', ave_dist=1.02 * 1e-10)

# Define the CSA relaxation interaction.
self._execute_uf(uf_name='value.set', val=N15_CSA, param='csa')

# Select the model.
self._execute_uf(uf_name='model_free.select_model', model='m4')

# Map the space.
self._execute_uf(uf_name='dx.map', params=['s2', 'te', 'rex'], spin_id=':2@N', inc=2, lower=[0.0, 0, 0], upper=[1.0, 10000e-12, 3.0 / (2.0 * pi * 600000000.0)**2], point=[0.970, 2048.0e-12, 0.149 / (2.0 * pi * 600000000.0)**2], file_prefix='devnull', point_file='devnull')
