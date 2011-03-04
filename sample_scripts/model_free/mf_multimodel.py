###############################################################################
#                                                                             #
# Copyright (C) 2003-2009 Edward d'Auvergne                                   #
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

# This script performs a model-free analysis for the models 'm0' to 'm9' (or 'tm0' to 'tm9').
#############################################################################################

# Set the data pipe names (also the names of preset model-free models).
#pipes = ['tm0', 'tm1', 'tm2', 'tm3', 'tm4', 'tm5', 'tm6', 'tm7', 'tm8', 'tm9']
pipes = ['m0', 'm1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9']

# Loop over the pipes.
for name in pipes:
    # Create the data pipe.
    pipe.create(name, 'mf')

    # Load the sequence.
    sequence.read('noe.500.out', res_num_col=1)

    # Load a PDB file.
    structure.read_pdb('example.pdb')

    # Set the spin name and then load the NH vectors.
    spin.name(name='N')
    structure.vectors(spin_id='@N', attached='H*', ave=False)

    # Load the relaxation data.
    relax_data.read('R1', '600', 600.0 * 1e6, 'r1.600.out', res_num_col=1, data_col=3, error_col=4)
    relax_data.read('R2', '600', 600.0 * 1e6, 'r2.600.out', res_num_col=1, data_col=3, error_col=4)
    relax_data.read('NOE', '600', 600.0 * 1e6, 'noe.600.out', res_num_col=1, data_col=3, error_col=4)
    relax_data.read('R1', '500', 500.0 * 1e6, 'r1.500.out', res_num_col=1, data_col=3, error_col=4)
    relax_data.read('R2', '500', 500.0 * 1e6, 'r2.500.out', res_num_col=1, data_col=3, error_col=4)
    relax_data.read('NOE', '500', 500.0 * 1e6, 'noe.500.out', res_num_col=1, data_col=3, error_col=4)

    # Setup other values.
    diffusion_tensor.init(1e-8, fixed=True)
    #diffusion_tensor.init((1e-8, 1.0, 60, 290), param_types=0, spheroid_type='oblate', fixed=True)
    value.set(1.02 * 1e-10, 'bond_length')
    value.set(-172 * 1e-6, 'csa')
    value.set('15N', 'heteronucleus')
    value.set('1H', 'proton')

    # Select the model-free model.
    model_free.select_model(model=name)

    # Minimise.
    grid_search(inc=11)
    minimise('newton')

    # Write the results.
    results.write(file='results', force=True)

# Save the program state.
state.save('save', force=True)
