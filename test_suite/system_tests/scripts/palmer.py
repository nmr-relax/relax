# Script for model-free analysis using the program 'Modelfree4'.

# Python module imports.
import sys

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()


# Missing temp directory (allow this script to run outside of the system test framework).
if not hasattr(ds, 'tmpdir'):
    ds.tmpdir = 'temp_script'


def exec_stage_1(pipes):
    """Stage 1 function.

    Initial model-free minimisation.
    """

    # Loop over the data pipes.
    for name in pipes:
        # Create the pipe.
        print "\n\n# " + name + " #"
        pipe.create(name, 'mf')

        # Load the sequence.
        sequence.read(sys.path[-1] + '/test_suite/shared_data/jw_mapping/noe.dat')

        # Read a PDB file.
        structure.read_pdb(file='Ap4Aase_res1-12.pdb', dir=sys.path[-1] + '/test_suite/shared_data/structures', model=1)

        # Load the relaxation data.
        relax_data.read('R1', '600', 600.0 * 1e6, sys.path[-1] + '/test_suite/shared_data/jw_mapping/R1.dat')
        relax_data.read('R2', '600', 600.0 * 1e6, sys.path[-1] + '/test_suite/shared_data/jw_mapping/R2.dat')
        relax_data.read('NOE', '600', 600.0 * 1e6, sys.path[-1] + '/test_suite/shared_data/jw_mapping/noe.dat')

        # Setup other values.
        diffusion_tensor.init((1e-8, 0, 0, 0))
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


def exec_stage_2(pipes):
    """Stage 2 function.

    Model-free model selection.
    """

    # Print out.
    print "\n\nLoading all the Modelfree 4 data."

    # Loop over the data pipes.
    for name in pipes:
        # Switch to the data pipe.
        pipe.switch(name)

        # Extract the Modelfree4 data from the 'mfout' files.
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

    # Let the diffusion tensor parameters be optimised.
    fix('diff', False)

    # Create the Modelfree4 files (change sims as needed, see below).
    palmer.create(dir=ds.tmpdir + '/final', force=True, sims=0)

    # Run Modelfree4.
    palmer.execute(dir=ds.tmpdir + '/final', force=True)

    # Extract the Modelfree4 data from the 'mfout' file.
    palmer.extract(dir=ds.tmpdir + '/final')

    # Write the results.
    results.write(file='final', dir=ds.tmpdir, force=True)

    # Save the program state.
    state.save(state='stage3.save', dir_name=ds.tmpdir, force=True)


# Main section of the script.
#############################

# Set the pipe names (also the name of a preset model-free model).
pipes = ['m1', 'm2', 'm3']

# Run the stages.
exec_stage_1(pipes)
exec_stage_2(pipes)
exec_stage_3()
