# Script for model-free analysis using the program 'Modelfree4'.

# Python module imports.
import sys

# Set the stage of analysis.
#
# The three stages in this script are:
#   Stage 1:  Initial model-free minimisation.
#   Stage 2:  Model-free model selection.
#   Stage 3:  Final optimisation of diffusion tensor parameters together with model-free parameters.


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
        sequence.read(sys.path[-1] + '/test_suite/system_tests/data/jw_mapping/noe.dat')

        # Load the relaxation data.
        relax_data.read('R1', '600', 600.0 * 1e6, sys.path[-1] + '/test_suite/system_tests/data/jw_mapping/R1.dat')
        relax_data.read('R2', '600', 600.0 * 1e6, sys.path[-1] + '/test_suite/system_tests/data/jw_mapping/R2.dat')
        relax_data.read('NOE', '600', 600.0 * 1e6, sys.path[-1] + '/test_suite/system_tests/data/jw_mapping/noe.dat')

        # Setup other values.
        diffusion_tensor.init(1e-8)
        value.set('15N', 'heteronucleus')
        value.set(1.02 * 1e-10, 'bond_length')
        value.set(-172 * 1e-6, 'csa')

        # Select the model-free model.
        model_free.select_model(model=name)

        # Create the Modelfree4 files.
        palmer.create(dir=name, force=True, sims=0)

        # Run Modelfree4.
        palmer.execute(dir=name, force=True)

    # Save the program state.
    state.save('stage1.save', force=True)


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
        palmer.extract(dir=name)

    # Print out.
    print "\n\nModel selection."

    # Create the model selection run.
    name = 'aic'
    pipe.create(name, 'mf')

    # Model selection.
    model_selection(method='AIC', modsel_run=name)

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

    # Set the run name.
    name = 'aic'

    # Let the diffusion tensor parameters be optimised.
    fix(name, 'diff', False)

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

# Set the run name (also the name of a preset model-free model).
runs = ['m1', 'm2', 'm3']

# Run the stages.
exec_stage_1(runs)
exec_stage_2(runs)
exec_stage_3()
