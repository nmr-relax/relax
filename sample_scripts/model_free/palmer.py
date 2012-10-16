###############################################################################
#                                                                             #
# Copyright (C) 2001-2012 Edward d'Auvergne                                   #
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

"""Script for model-free analysis using Art Palmer's program 'Modelfree4'.

The three stages in this script, which can be set below, are:
  Stage 1:  Initial model-free minimisation.
  Stage 2:  Model-free model selection.
  Stage 3:  Final optimisation of diffusion tensor parameters together with model-free parameters.
"""

# relax module imports.
from relax_errors import RelaxError


# Set the stage of analysis.
STAGE = 1


def exec_stage_1(pipes):
    """Stage 1 function.

    Initial model-free minimisation.
    """

    # Loop over the data pipes.
    for name in pipes:
        # Create the data pipe.
        print("\n\n# " + name + " #")
        pipe.create(name, 'mf')

        # Set up the 15N spins.
        sequence.read('noe.500.out', res_num_col=1, res_name_col=2)
        spin.name('N')
        spin.element(element='N', spin_id='@N')
        spin.isotope('15N', spin_id='@N')

        # PDB.
        #structure.read_pdb('Ap4Aase_new_3.pdb')

        # Load the relaxation data.
        relax_data.read(ri_id='R1_600',  ri_type='R1',  frq=600.0*1e6, file='r1.600.out', res_num_col=1, data_col=3, error_col=4)
        relax_data.read(ri_id='R2_600',  ri_type='R2',  frq=600.0*1e6, file='r2.600.out', res_num_col=1, data_col=3, error_col=4)
        relax_data.read(ri_id='NOE_600', ri_type='NOE', frq=600.0*1e6, file='noe.600.out', res_num_col=1, data_col=3, error_col=4)
        relax_data.read(ri_id='R1_500',  ri_type='R1',  frq=500.0*1e6, file='r1.500.out', res_num_col=1, data_col=3, error_col=4)
        relax_data.read(ri_id='R2_500',  ri_type='R2',  frq=500.0*1e6, file='r2.500.out', res_num_col=1, data_col=3, error_col=4)
        relax_data.read(ri_id='NOE_500', ri_type='NOE', frq=500.0*1e6, file='noe.500.out', res_num_col=1, data_col=3, error_col=4)

        # Set up the diffusion tensor.
        diffusion_tensor.init(1e-8)

        # Generate 1H spins for the magnetic dipole-dipole relaxation interaction.
        sequence.attach_protons()

        # Define the magnetic dipole-dipole relaxation interaction.
        dipole_pair.define(spin_id1='@N', spin_id2='@H', direct_bond=True)
        dipole_pair.set_dist(spin_id1='@N', spin_id2='@H', ave_dist=1.02 * 1e-10)

        # Define the chemical shift relaxation interaction.
        value.set(-172 * 1e-6, 'csa', spin_id='@N')

        # Select the model-free model.
        model_free.select_model(model=name)

        # Create the Modelfree4 files.
        palmer.create(force=False, sims=0)

        # Run Modelfree4.
        palmer.execute(force=True)

    # Save the program state.
    state.save('stage1.save', force=True)


def exec_stage_2(pipes):
    """Stage 2 function.

    Model-free model selection.
    """

    # Load the saved state from stage 1.
    state.load('stage1.save')

    # Print out.
    print("\n\nLoading all the Modelfree 4 data.")

    # Loop over the data pipes.
    for name in pipes:
        # Switch to the data pipe.
        pipe.switch(name)

        # Extract the Modelfree4 data from the 'mfout' files.
        palmer.extract(dir=name)

    # Print out.
    print("\n\nModel selection.")

    # Model selection.
    model_selection(method='AIC', modsel_pipe='aic')

    # Write the results.
    results.write(file='results', force=True)

    # Save the program state.
    state.save('stage2.save', force=True)


def exec_stage_3():
    """Stage 3 function.

    Final optimisation of diffusion tensor parameters together with model-free parameters.
    """

    # Load the saved state from stage 2.
    state.load('stage2.save')

    # Let the diffusion tensor parameters be optimised.
    fix('diff', False)

    # Create the Modelfree4 files (change sims as needed, see below).
    palmer.create(dir='final', force=True, sims=0)

    # Run Modelfree4.
    palmer.execute(dir='final', force=True)

    # Extract the Modelfree4 data from the 'mfout' file.
    palmer.extract(dir='final')

    # Save the program state.
    state.save('stage3.save', force=True)


# Main section of the script.
#############################

# Set the data pipe names (also the name of a preset model-free model).
pipes = ['m1', 'm2', 'm3', 'm4', 'm5']

# Run the stages.
if STAGE == 1:
    exec_stage_1(pipes)
elif STAGE == 2:
    exec_stage_2(pipes)
elif STAGE == 3:
    exec_stage_3()
else:
    raise RelaxError("The stage value, which is set to " + repr(stage) + ", should be either 1, 2, or 3.")

# Either repeat all the above with the optimised diffusion tensor or run Monte Carlo simulations on the final results.
