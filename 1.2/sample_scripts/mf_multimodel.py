###############################################################################
#                                                                             #
# Copyright (C) 2003-2008 Edward d'Auvergne                                   #
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

# Set the run names (also the names of preset model-free models).
#runs = ['tm0', 'tm1', 'tm2', 'tm3', 'tm4', 'tm5', 'tm6', 'tm7', 'tm8', 'tm9']
runs = ['m0', 'm1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9']

# Nuclei type
nuclei('N')

# Loop over the runs.
for name in runs:
    # Create the run.
    run.create(name, 'mf')

    # Load the sequence.
    sequence.read(name, 'noe.500.out')

    # Load a PDB file.
    #pdb(name, 'example.pdb')

    # Load the relaxation data.
    relax_data.read(name, 'R1', '600', 600.0 * 1e6, 'r1.600.out')
    relax_data.read(name, 'R2', '600', 600.0 * 1e6, 'r2.600.out')
    relax_data.read(name, 'NOE', '600', 600.0 * 1e6, 'noe.600.out')
    relax_data.read(name, 'R1', '500', 500.0 * 1e6, 'r1.500.out')
    relax_data.read(name, 'R2', '500', 500.0 * 1e6, 'r2.500.out')
    relax_data.read(name, 'NOE', '500', 500.0 * 1e6, 'noe.500.out')

    # Setup other values.
    diffusion_tensor.init(name, 1e-8, fixed=1)
    #diffusion_tensor.init(name, (1e-8, 1.0, 60, 290), param_types=0, spheroid_type='oblate', fixed=0)
    value.set(name, 1.02 * 1e-10, 'bond_length')
    value.set(name, -172 * 1e-6, 'csa')

    # Select the model-free model.
    model_free.select_model(run=name, model=name)

    # Minimise.
    grid_search(name, inc=11)
    minimise('newton', run=name)

    # Write the results.
    results.write(run=name, file='results', force=1)

# Save the program state.
state.save('save', force=1)
