###############################################################################
#                                                                             #
# Copyright (C) 2004-2011 Edward d'Auvergne                                   #
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

"""Script for diffusion tensor optimisation."""


# Set the data pipe names (also the names of preset model-free models).
pipes = ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9']

# Minimise the model-free parameters.
print("\n\n\n\n\n")
print("#####################################")
print("# Minimising model-free parameters. #")
print("#####################################")
print("\n\n\n")

for name in pipes:
    # Create the data pipe.
    pipe.create(name, 'mf')

    # Nuclei type
    value.set('15N', 'heteronucleus')

    # Load the sequence.
    sequence.read('noe.500.out', res_num_col=1)

    # Load a PDB file.
    structure.read_pdb('example.pdb')

    # Load the relaxation data.
    relax_data.read(ri_id='R1_600',  ri_type='R1',  frq=600.0*1e6, file='r1.600.out', res_num_col=1, data_col=3, error_col=4)
    relax_data.read(ri_id='R2_600',  ri_type='R2',  frq=600.0*1e6, file='r2.600.out', res_num_col=1, data_col=3, error_col=4)
    relax_data.read(ri_id='NOE_600', ri_type='NOE', frq=600.0*1e6, file='noe.600.out', res_num_col=1, data_col=3, error_col=4)
    relax_data.read(ri_id='R1_500',  ri_type='R1',  frq=500.0*1e6, file='r1.500.out', res_num_col=1, data_col=3, error_col=4)
    relax_data.read(ri_id='R2_500',  ri_type='R2',  frq=500.0*1e6, file='r2.500.out', res_num_col=1, data_col=3, error_col=4)
    relax_data.read(ri_id='NOE_500', ri_type='NOE', frq=500.0*1e6, file='noe.500.out', res_num_col=1, data_col=3, error_col=4)

    # Setup other values.
    diffusion_tensor.init((1e-8, 1.0, 60, 290), param_types=1, spheroid_type='oblate', fixed=1)
    value.set(1.02 * 1e-10, 'bond_length')
    value.set(-172 * 1e-6, 'csa')

    # Select the model-free model.
    model_free.select_model(model=name)

    # Minimise.
    grid_search(inc=5)
    minimise('newton')

# Minimise the diffusion tensor parameters.
print("\n\n\n\n\n")
print("###########################################")
print("# Minimising diffusion tensor parameters. #")
print("###########################################")
print("\n\n\n")

# Loop over the data pipes.
for name in pipes:
    # Switch to the data pipe.
    pipe.switch(name)

    # Unfix the diffusion tensor.
    fix('diff', fixed=0)

    # Fix all model-free paremeter values.
    fix('all_res')

    # Minimise.
    grid_search(inc=5)
    minimise('newton', max_iter=5000)

    # Write the results.
    results.write(file='results', force=True)

# Save the program state.
state.save('save', force=True)
