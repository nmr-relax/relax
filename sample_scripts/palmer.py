# Script for model-free analysis using the program 'Modelfree4'.

# Set the stage of analysis.
#
# The three stages in this script are:
#   Stage 1:  Initial model-free minimisation.
#   Stage 2:  Model-free model selection.
#   Stage 3:  Final optimisation of diffusion tensor parameters together with model-free parameters.
stage = 1


# Functions.

def exec_stage_1(runs):
    """Stage 1 function.

    Initial model-free minimisation.
    """

    # Loop over the runs.
    for run in runs:
        # Create the run.
        print "\n\n# " + run + " #"
        create_run(run, 'mf')

        # Load the sequence.
        sequence.read(run, 'noe.500.out')

        # PDB.
        #pdb(run, 'Ap4Aase_new_3.pdb')
        #vectors(run)

        # Load the relaxation data.
        relax_data.read(run, 'R1', '600', 600.0 * 1e6, 'r1.600.out')
        relax_data.read(run, 'R2', '600', 600.0 * 1e6, 'r2.600.out')
        relax_data.read(run, 'NOE', '600', 600.0 * 1e6, 'noe.600.out')
        relax_data.read(run, 'R1', '500', 500.0 * 1e6, 'r1.500.out')
        relax_data.read(run, 'R2', '500', 500.0 * 1e6, 'r2.500.out')
        relax_data.read(run, 'NOE', '500', 500.0 * 1e6, 'noe.500.out')

        # Setup other values.
        diffusion_tensor.set(run, 1e-8)
        value.set(run, 1.02 * 1e-10, 'bond_length')
        value.set(run, -170 * 1e-6, 'csa')

        # Select the model-free model.
        model_free.select_model(run=run, model=run)

        # Create the Modelfree4 files.
        palmer.create(run=run, force=0, sims=200)

        # Run Modelfree4.
        palmer.execute(run=run, force=1)

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
    for run in runs:
        palmer.extract(run=run)

    # Print out.
    print "\n\nModel selection."

    # Create the model selection run.
    run = 'aic'
    create_run(run, 'mf')

    # Model selection.
    model_selection(method='AIC', modsel_run=run)

    # Write the results.
    write(run=run, file='results', force=1)

    # Save the program state.
    state.save('stage2.save', force=1)


def exec_stage_3():
    """Stage 3 function.

    Final optimisation of diffusion tensor parameters together with model-free parameters.
    """

    # Load the saved state from stage 2.
    state.load('stage2.save')

    # Set the run name.
    run = 'aic'

    # Let the diffusion tensor parameters be optimised.
    fix(run, 'diff', 0)

    # Create the Modelfree4 files (change sims as needed, see below).
    palmer.create(run=run, dir='final', force=1, sims=0)

    # Run Modelfree4.
    palmer.execute(run=run, dir='final', force=1)

    # Extract the Modelfree4 data from the 'mfout' file.
    palmer.extract(run=run, dir='final')

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
