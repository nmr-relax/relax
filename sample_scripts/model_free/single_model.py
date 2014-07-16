###############################################################################
#                                                                             #
# Copyright (C) 2003-2014 Edward d'Auvergne                                   #
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

"""This script performs a model-free analysis for the single model 'm4'."""


# Create the data pipe.
name = 'm4'
pipe.create(name, 'mf')

# Set up the 15N spins.
sequence.read(file='noe.500.out', res_num_col=1, res_name_col=2)
spin.name('N')
spin.element('N')
spin.isotope('15N', spin_id='@N')

# Load a PDB file.
#structure.read_pdb('example.pdb')

# Load the relaxation data.
relax_data.read(ri_id='R1_600',  ri_type='R1',  frq=600.0*1e6, file='r1.600.out', res_num_col=1, data_col=3, error_col=4)
relax_data.read(ri_id='R2_600',  ri_type='R2',  frq=600.0*1e6, file='r2.600.out', res_num_col=1, data_col=3, error_col=4)
relax_data.read(ri_id='NOE_600', ri_type='NOE', frq=600.0*1e6, file='noe.600.out', res_num_col=1, data_col=3, error_col=4)
relax_data.read(ri_id='R1_500',  ri_type='R1',  frq=500.0*1e6, file='r1.500.out', res_num_col=1, data_col=3, error_col=4)
relax_data.read(ri_id='R2_500',  ri_type='R2',  frq=500.0*1e6, file='r2.500.out', res_num_col=1, data_col=3, error_col=4)
relax_data.read(ri_id='NOE_500', ri_type='NOE', frq=500.0*1e6, file='noe.500.out', res_num_col=1, data_col=3, error_col=4)

# Initialise the diffusion tensor.
diffusion_tensor.init(10e-9, fixed=True)
#diffusion_tensor.init((2e-8, 1.3, 60, 290), param_types=0, spheroid_type='prolate', fixed=True)
#diffusion_tensor.init((9e-8, 0.5, 0.3, 60, 290, 100), fixed=False)

# Create all attached protons.
sequence.attach_protons()

# Define the magnetic dipole-dipole relaxation interaction.
interatom.define(spin_id1='@N', spin_id2='@H', direct_bond=True)
interatom.set_dist(spin_id1='@N', spin_id2='@H', ave_dist=1.02 * 1e-10)
#interatom.unit_vectors()

# Define the CSA relaxation interaction.
value.set(-172 * 1e-6, 'csa')

# Set some model-free parameter values.
#value.set(val=1.0, param='s2f')
#value.set(val=0.970, param='s2')
#value.set(val=2048e-12, param='te')
#value.set(val=2048e-12, param='ts')
#value.set(val=2048e-12, param='tf')
#value.set(val=0.149/(2*pi*600e6)**2, param='rex')

# Select the model-free model.
model_free.select_model(model=name)
#model_free.create_model(model=name, equation='mf_ext2', params=['s2f', 's2s', 'ts'])

# Fixed value.
#fix('all_res')

# Grid search.
minimise.grid_search(inc=11)
#value.set()

# Minimise.
minimise.execute('newton')

# Monte Carlo simulations.
#monte_carlo.setup(number=100)
#monte_carlo.create_data()
#monte_carlo.initial_values()
#minimise.execute('newton')
#eliminate()
#monte_carlo.error_analysis()

# Finish.
results.write(file='results', force=True)
state.save('save', force=True)
