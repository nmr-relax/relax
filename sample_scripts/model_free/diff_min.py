###############################################################################
#                                                                             #
# Copyright (C) 2004-2013 Edward d'Auvergne                                   #
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

"""Demonstration script for diffusion tensor optimisation in a model-free analysis.

Importantly, if a model-free analysis is to be based on this script, note that multiple rounds of executing this script will be required for each diffusion tensor.  To understand this concept of finding the universal solution of the optimisation minimum across multiple model-free spaces (or universes), please read:

    d'Auvergne E. J., Gooley P. R. (2007). Set theory formulation of the model-free problem and the diffusion seeded model-free paradigm. Mol. Biosyst., 3(7), 483-494. (http://dx.doi.org/10.1039/b702202f)

    d'Auvergne, E. J. and Gooley, P. R. (2008). Optimisation of NMR dynamic models II. A new methodology for the dual optimisation of the model-free parameters and the Brownian rotational diffusion tensor. J. Biomol. NMR, 40(2), 121-133. (http://dx.doi.org/10.1007/s10858-007-9213-3).


Also note that for a model-free analysis, you should look at the fully contained dauvergne_protocol.py sample script rather than here.

This script requires an initial tensor estimate which can be found using either relax or other software packages.
"""


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
    value.set('15N', 'heteronuc_type')

    # Set up the 15N spins.
    sequence.read('noe.500.out', res_num_col=1)
    spin.name('N')
    spin.element(element='N', spin_id='@N')
    spin.isotope('15N', spin_id='@N')

    # Load a PDB file.
    structure.read_pdb('example.pdb')

    # Load the relaxation data.
    relax_data.read(ri_id='R1_600',  ri_type='R1',  frq=600.0*1e6, file='r1.600.out', res_num_col=1, data_col=3, error_col=4)
    relax_data.read(ri_id='R2_600',  ri_type='R2',  frq=600.0*1e6, file='r2.600.out', res_num_col=1, data_col=3, error_col=4)
    relax_data.read(ri_id='NOE_600', ri_type='NOE', frq=600.0*1e6, file='noe.600.out', res_num_col=1, data_col=3, error_col=4)
    relax_data.read(ri_id='R1_500',  ri_type='R1',  frq=500.0*1e6, file='r1.500.out', res_num_col=1, data_col=3, error_col=4)
    relax_data.read(ri_id='R2_500',  ri_type='R2',  frq=500.0*1e6, file='r2.500.out', res_num_col=1, data_col=3, error_col=4)
    relax_data.read(ri_id='NOE_500', ri_type='NOE', frq=500.0*1e6, file='noe.500.out', res_num_col=1, data_col=3, error_col=4)

    # Set up the diffusion tensor.
    diffusion_tensor.init((1e-8, 1.0, 60, 290), param_types=1, spheroid_type='oblate', fixed=1)

    # Generate the 1H spins for the magnetic dipole-dipole relaxation interaction.
    sequence.attach_protons()

    # Define the magnetic dipole-dipole relaxation interaction.
    structure.get_pos('@N')
    structure.get_pos('@H')
    interatom.define(spin_id1='@N', spin_id2='@H', direct_bond=True)
    interatom.set_dist(spin_id1='@N', spin_id2='@H', ave_dist=1.02 * 1e-10)
    interatom.unit_vectors()

    # Define the chemical shift relaxation interaction.
    value.set(-172 * 1e-6, 'csa', spin_id='@N')

    # Select the model-free model.
    model_free.select_model(model=name)

    # Minimise.
    grid_search(inc=21)
    minimise('newton')

    # Model elimination.
    eliminate()

    # Write the results.
    results.write(file='results', force=True)

# Model selection.
print("\n\n\n\n\n")
print("####################")
print("# Model selection. #")
print("####################")
print("\n\n\n")

# Select the models and save the results.
model_selection(method='AIC', modsel_pipe='aic')
results.write(file='results', force=True)

# Minimise the diffusion tensor parameters.
print("\n\n\n\n\n")
print("###########################################")
print("# Minimising diffusion tensor parameters. #")
print("###########################################")
print("\n\n\n")

# Unfix all parameters.
fix('all', fixed=False)

# Minimise.
grid_search(inc=5)
minimise('newton')

# Write the results.
results.write(file='results', dir='opt', force=True)

# Save the program state.
state.save('save', force=True)
