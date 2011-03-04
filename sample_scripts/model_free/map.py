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

"""Script for mapping the model-free space for OpenDX visualisation."""


# Set the run name (also the name of a preset model-free model).
name = 'm4'
pipe.create(name, 'mf')

# Nuclei type
value.set('15N', 'heteronucleus')

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
value.set(name, 2048.0e-12, 'te')

# Select the model-free model.
model_free.select_model(model=name)
#model_free.create_model(name, name, 'mf_ext2', ['S2f', 'S2s', 'ts'])

# Map data.
inc = 5
from math import pi
if name == 'm4':
    params = ['S2', 'te', 'Rex']
    lower = [0, 0, 0]
    upper = [1.0, 10000e-12, 2.0 / (2.0 * pi * 600000000.0)**2]
    point = [0.970, 2048.0e-12, 0.149 / (2.0 * pi * 600000000.0)**2]
elif name == 'm5':
    params = ['S2', 'S2f', 'ts']
    lower = [0.5, 0.5, 0]
    upper = [1.0, 1.0, 300e-12]
    point = [0.622, 0.555446, 281.74*1e-12]
else:
    params = None
    lower = None
    upper = None
    point = None
dx.map(name, params=params, res_num=1, inc=inc, lower=lower, upper=upper, point=point)
#dx.map(name, swap=None, res_num=1, inc=inc, lower=lower, upper=upper, point=point)
dx.execute()
