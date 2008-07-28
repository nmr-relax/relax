# Script for model-free analysis using the program 'Modelfree4'.

# The RelaxError system.
from relax_errors import RelaxError

# Set the stage of analysis.
#
# The three stages in this script are:
#   Stage 1:  Initial model-free minimisation.
#   Stage 2:  Model-free model selection.
#   Stage 3:  Final optimisation of diffusion tensor parameters together with model-free parameters.
stage = 2


# Functions.

def exec_stage_1(runs):
    """Stage 1 function.

    Initial model-free minimisation.
    """

    # Loop over the runs.
    for name in runs:
        # Create the run.
        print "\n\n# " + name + " #"
        pipe.create(name, 'mf')

        # Load the sequence.
        sequence.read(name, 'noe.500.out')

        # PDB.
        #structure.read_pdb(name, 'Ap4Aase_new_3.pdb')

        # Load the relaxation data.
        relax_data.read(name, 'R1', '600', 600.0 * 1e6, 'r1.600.out')
        relax_data.read(name, 'R2', '600', 600.0 * 1e6, 'r2.600.out')
        relax_data.read(name, 'NOE', '600', 600.0 * 1e6, 'noe.600.out')
        relax_data.read(name, 'R1', '500', 500.0 * 1e6, 'r1.500.out')
        relax_data.read(name, 'R2', '500', 500.0 * 1e6, 'r2.500.out')
        relax_data.read(name, 'NOE', '500', 500.0 * 1e6, 'noe.500.out')

        # Setup other values.
        diffusion_tensor.init(name, 1e-8)
        value.set(name, 1.02 * 1e-10, 'bond_length')
        value.set(name, -172 * 1e-6, 'csa')

        # Select the model-free model.
        model_free.select_model(model=name)

        # Create the Modelfree4 files.
        palmer.create(force=0, sims=0)

        # Run Modelfree4.
        palmer.execute(force=1)

    # Save the program state.
    state.save('stage1.save', force=1)


def exec_stage_2(runs):
    """Stage 2 function.

    Model-free model selection.
    """

    # Load the saved state from stage 1.
    state.load('stage1.save')

    # Print out.
    print "\n\nLoading all the Modelfree 4 data."

    # Extract the Modelfree4 data from the 'mfout' files.
    for name in runs:
        palmer.extract()

    # Print out.
    print "\n\nModel selection."

    # Create the model selection run.
    name = 'aic'
    pipe.create(name, 'mf')

    # Model selection.
    model_selection(method='AIC', modsel_run=name)

    # Write the results.
    results.write(file='results', force=1)

    # Save the program state.
    state.save('stage2.save', force=1)


def exec_stage_3():
    """Stage 3 function.

    Final optimisation of diffusion tensor parameters together with model-free parameters.
    """

    # Load the saved state from stage 2.
    state.load('stage2.save')

    # Set the run name.
    name = 'aic'

    # Let the diffusion tensor parameters be optimised.
    fix(name, 'diff', 0)

    # Create the Modelfree4 files (change sims as needed, see below).
    palmer.create(dir='final', force=1, sims=0)

    # Run Modelfree4.
    palmer.execute(dir='final', force=1)

    # Extract the Modelfree4 data from the 'mfout' file.
    palmer.extract(dir='final')

    # Save the program state.
    state.save('stage3.save', force=1)


# Main section of the script.
#############################

# Nuclei type.
nuclei('N')

# Set the run name (also the name of a preset model-free model).
runs = ['m1', 'm2', 'm3', 'm4', 'm5']

# Run the stages.
if stage == 1:
    exec_stage_1(runs)
elif stage == 2:
    exec_stage_2(runs)
elif stage == 3:
    exec_stage_3()
else:
    raise RelaxError, "The stage value, which is set to " + `stage` + ", should be either 1, 2, or 3."

# Either repeat all the above with the optimised diffusion tensor or run Monte Carlo simulations on the final results.
