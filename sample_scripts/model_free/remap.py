###############################################################################
#                                                                             #
# Copyright (C) 2003-2011 Edward d'Auvergne                                   #
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


# Set the run name (also the name of a preset model-free model).
name = 'm5'

# Nuclei type
value.set('15N', 'heteronucleus')

# Create the run 'name'.
pipe.create(name, 'mf')

# Load the sequence.
sequence.read(name, 'noe.500.out', res_num_col=1)

# Load the relaxation data.
relax_data.read(name, 'R1', '600', 600.0 * 1e6, 'r1.600.out', res_num_col=1, data_col=3, error_col=4)
relax_data.read(name, 'R2', '600', 600.0 * 1e6, 'r2.600.out', res_num_col=1, data_col=3, error_col=4)
relax_data.read(name, 'NOE', '600', 600.0 * 1e6, 'noe.600.out', res_num_col=1, data_col=3, error_col=4)
relax_data.read(name, 'R1', '500', 500.0 * 1e6, 'r1.500.out', res_num_col=1, data_col=3, error_col=4)
relax_data.read(name, 'R2', '500', 500.0 * 1e6, 'r2.500.out', res_num_col=1, data_col=3, error_col=4)
relax_data.read(name, 'NOE', '500', 500.0 * 1e6, 'noe.500.out', res_num_col=1, data_col=3, error_col=4)

# Setup other values.
diffusion_tensor.init(name, 1e-8)
value.set(name, 1.02 * 1e-10, 'bond_length')
value.set(name, -172 * 1e-6, 'csa')

# Select the model-free model.
model_free.select_model(model=name)

# Map data.
inc = 100
params = ['S2f', 'ts', 'S2s']
lower = [0.5, 0, 0.5]
upper = [1.0, 300e-12, 1.0]
point = [0.952, 32.0e-12, 0.582]
point = [point[0], point[1], point[0]*point[2]]

dx.map(name, params=params, res_num=1, inc=inc, lower=lower, upper=upper, file='remap', point=point, axis_incs=5, remap=remap)
dx.execute(file='remap')
