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

"""Script for mapping the model-free space."""


# Python module imports.
from numpy import float64, array


def remap(values):
    """Remapping function."""

    # S2f.
    s2f = values[0]

    # S2s.
    if values[0] == 0.0:
        s2s = 1e99
    else:
        s2s = values[1]*values[0]

    # ts.
    ts = values[2]

    return array([s2f, s2s, ts], float64)


# The model-free model name.
name = 'm5'

# Create the data pipe.
pipe.create(name, 'mf')

# Set up the 15N spins.
sequence.read(file='noe.500.out', res_num_col=1, res_name_col=2)
spin.name('N')
spin.element('N')
spin.isotope('15N', spin_id='@N')

# Load the relaxation data.
relax_data.read(ri_id='R1_600',  ri_type='R1',  frq=600.0*1e6, file='r1.600.out', res_num_col=1, data_col=3, error_col=4)
relax_data.read(ri_id='R2_600',  ri_type='R2',  frq=600.0*1e6, file='r2.600.out', res_num_col=1, data_col=3, error_col=4)
relax_data.read(ri_id='NOE_600', ri_type='NOE', frq=600.0*1e6, file='noe.600.out', res_num_col=1, data_col=3, error_col=4)
relax_data.read(ri_id='R1_500',  ri_type='R1',  frq=500.0*1e6, file='r1.500.out', res_num_col=1, data_col=3, error_col=4)
relax_data.read(ri_id='R2_500',  ri_type='R2',  frq=500.0*1e6, file='r2.500.out', res_num_col=1, data_col=3, error_col=4)
relax_data.read(ri_id='NOE_500', ri_type='NOE', frq=500.0*1e6, file='noe.500.out', res_num_col=1, data_col=3, error_col=4)

# Initialise the diffusion tensor.
diffusion_tensor.init(1e-8, fixed=True)

# Create all attached protons.
sequence.attach_protons()

# Define the magnetic dipole-dipole relaxation interaction.
dipole_pair.define(spin_id1='@N', spin_id2='@H', direct_bond=True)
dipole_pair.set_dist(spin_id1='@N', spin_id2='@H', ave_dist=1.02 * 1e-10)

# Define the CSA relaxation interaction.
value.set(N15_CSA, 'csa')

# Select the model-free model.
model_free.select_model(model=name)

# Map data.
inc = 100
params = ['s2f', 'ts', 's2s']
lower = [0.5, 0, 0.5]
upper = [1.0, 300e-12, 1.0]
point = [0.952, 32.0e-12, 0.582]
point = [point[0], point[1], point[0]*point[2]]

dx.map(params=params, spin_id=":1", inc=inc, lower=lower, upper=upper, file_prefix='remap', point=point, axis_incs=5, remap=remap)
dx.execute(file='remap')
