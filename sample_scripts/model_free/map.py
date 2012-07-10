###############################################################################
#                                                                             #
# Copyright (C) 2003-2012 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax.  If not, see <http://www.gnu.org/licenses/>.              #
#                                                                             #
###############################################################################

"""Script for mapping the model-free space for OpenDX visualisation."""


# The model-free model name.
name = 'm5'

# Create the data pipe.
pipe.create(name, 'mf')


# Set up the 15N spins.
sequence.read('noe.500.out', res_num_col=1)
spin.name('N')
spin.element(element='N', spin_id='@N')
spin.isotope('15N', spin_id='@N')

# Load the relaxation data.
relax_data.read(ri_id='R1_600',  ri_type='R1',  frq=600.0*1e6, file='r1.600.out', res_num_col=1, data_col=3, error_col=4)
relax_data.read(ri_id='R2_600',  ri_type='R2',  frq=600.0*1e6, file='r2.600.out', res_num_col=1, data_col=3, error_col=4)
relax_data.read(ri_id='NOE_600', ri_type='NOE', frq=600.0*1e6, file='noe.600.out', res_num_col=1, data_col=3, error_col=4)
relax_data.read(ri_id='R1_500',  ri_type='R1',  frq=500.0*1e6, file='r1.500.out', res_num_col=1, data_col=3, error_col=4)
relax_data.read(ri_id='R2_500',  ri_type='R2',  frq=500.0*1e6, file='r2.500.out', res_num_col=1, data_col=3, error_col=4)
relax_data.read(ri_id='NOE_500', ri_type='NOE', frq=500.0*1e6, file='noe.500.out', res_num_col=1, data_col=3, error_col=4)

# Set up the diffusion tensor.
diffusion_tensor.init(1e-8)

# Generate the 1H spins for the magnetic dipole-dipole relaxation interaction.
sequence.attach_protons()

# Define the magnetic dipole-dipole relaxation interaction.
dipole_pair.define(spin_id1='@N', spin_id2='@H', direct_bond=True)
dipole_pair.set_dist(spin_id1='@N', spin_id2='@H', ave_dist=1.02 * 1e-10)

# Define the chemical shift relaxation interaction.
value.set(-172 * 1e-6, 'csa', spin_id='@N')

# Select the model-free model.
model_free.select_model(model=name)

# Map data.
inc = 5
from math import pi
if name == 'm4':
    params = ['s2', 'te', 'rex']
    lower = [0, 0, 0]
    upper = [1.0, 10000e-12, 2.0 / (2.0 * pi * 600000000.0)**2]
    point = [0.970, 2048.0e-12, 0.149 / (2.0 * pi * 600000000.0)**2]
elif name == 'm5':
    params = ['s2', 's2f', 'ts']
    lower = [0.5, 0.5, 0]
    upper = [1.0, 1.0, 300e-12]
    point = [0.622, 0.555446, 281.74*1e-12]
else:
    params = None
    lower = None
    upper = None
    point = None
dx.map(params=params, spin_id=":1", inc=inc, lower=lower, upper=upper, point=point)
dx.execute()
