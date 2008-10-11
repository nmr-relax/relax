# Script for model-free analysis using the program 'Modelfree4'.

# Python module imports.
import sys

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()


# Set the stage of analysis.
#
# The three stages in this script are:
#   Stage 1:  Initial model-free minimisation.
#   Stage 2:  Model-free model selection.
#   Stage 3:  Final optimisation of diffusion tensor parameters together with model-free parameters.


# Missing temp directory (allow this script to run outside of the system test framework).
if not hasattr(ds, 'tmpdir'):
    ds.tmpdir = 'temp_script'

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
        sequence.read(sys.path[-1] + '/test_suite/shared_data/jw_mapping/noe.dat')

        # Load the relaxation data.
        relax_data.read('R1', '600', 600.0 * 1e6, sys.path[-1] + '/test_suite/shared_data/jw_mapping/R1.dat')
        relax_data.read('R2', '600', 600.0 * 1e6, sys.path[-1] + '/test_suite/shared_data/jw_mapping/R2.dat')
        relax_data.read('NOE', '600', 600.0 * 1e6, sys.path[-1] + '/test_suite/shared_data/jw_mapping/noe.dat')

        # Setup other values.
        diffusion_tensor.init(1e-8)
        value.set('15N', 'heteronucleus')
        value.set(1.02 * 1e-10, 'bond_length')
        value.set(-172 * 1e-6, 'csa')

        # Select the model-free model.
        model_free.select_model(model=name)

        # Create the Modelfree4 files.
        palmer.create(dir=ds.tmpdir + '/' + name, force=True, sims=0)

        # Run Modelfree4.
        palmer.execute(dir=ds.tmpdir + '/' + name, force=True)

    # Save the program state.
    state.save(state='stage1.save', dir_name=ds.tmpdir, force=True)


def exec_stage_2(runs):
    """Stage 2 function.

    Model-free model selection.
    """

    # Load the saved state from stage 1.
    state.load('stage1.save', dir_name=ds.tmpdir)

    # Print out.
    print "\n\nLoading all the Modelfree 4 data."

    # Extract the Modelfree4 data from the 'mfout' files.
    for name in runs:
        palmer.extract(dir=ds.tmpdir + '/' + name)

    # Print out.
    print "\n\nModel selection."

    # Model selection.
    model_selection(method='AIC', modsel_pipe='aic')

    # Write the results.
    results.write(file='results', dir=ds.tmpdir, force=True)

    # Save the program state.
    state.save(state='stage2.save', dir_name=ds.tmpdir, force=True)


def exec_stage_3():
    """Stage 3 function.

    Final optimisation of diffusion tensor parameters together with model-free parameters.
    """

    # Load the saved state from stage 2.
    state.load('stage2.save', dir_name=ds.tmpdir)

    # Set the run name.
    name = 'aic'

    # Let the diffusion tensor parameters be optimised.
    fix(name, 'diff', False)

    # Create the Modelfree4 files (change sims as needed, see below).
    palmer.create(dir=ds.tmpdir + '/final', force=True, sims=0)

    # Run Modelfree4.
    palmer.execute(dir=ds.tmpdir + '/final', force=True)

    # Extract the Modelfree4 data from the 'mfout' file.
    palmer.extract(dir=ds.tmpdir + '/final')

    # Save the program state.
    state.save(state='stage3.save', dir_name=ds.tmpdir, force=True)


# Main section of the script.
#############################

# Set the run name (also the name of a preset model-free model).
runs = ['m1', 'm2', 'm3']

# Run the stages.
exec_stage_1(runs)
exec_stage_2(runs)
exec_stage_3()
