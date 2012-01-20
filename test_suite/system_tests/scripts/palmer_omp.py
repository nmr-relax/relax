# Script for model-free analysis using the program 'Modelfree4'.

# Python module imports.
from os import sep
import sys

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# Missing temp directory (allow this script to run outside of the system test framework).
if not hasattr(ds, 'tmpdir'):
    ds.tmpdir = 'temp_script'

# Path of the relaxation data.
DATA_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'OMP'


def exec_stage_1(pipes):
    """Stage 1 function.

    Initial model-free minimisation.
    """

    # Loop over the data pipes.
    for name in pipes:
        # Create the data pipe.
        print(("\n\n# " + name + " #"))
        pipe.create(name, 'mf')

        # Copy the sequence.
        sequence.copy('data')

        # Read a PDB file.
        structure.read_pdb(file='1F35_N_H_trunc.pdb', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures', parser='internal')

        # Select only 3 spins (residues 9, 10, and 11).
        deselect.all()
        select.spin(':9')
        select.spin(':10')
        select.spin(':11')

        # Copy the relaxation data.
        relax_data.copy('data')

        # Setup other values.
        diffusion_tensor.init((1e-8, 0, 0, 0))
        value.set('15N', 'heteronuc_type')
        value.set('1H', 'proton_type')
        value.set(1.02 * 1e-10, 'r')
        value.set(-172 * 1e-6, 'csa')

        # Select the model-free model.
        model_free.select_model(model=name)

        # Create the Modelfree4 files.
        palmer.create(dir=ds.tmpdir + sep + name, force=True, sims=0)

        # Run Modelfree4.
        palmer.execute(dir=ds.tmpdir + sep + name, force=True)

    # Save the program state.
    state.save(state='stage1.save', dir=ds.tmpdir, force=True)


def exec_stage_2(pipes):
    """Stage 2 function.

    Model-free model selection.
    """

    # Print out.
    print("\n\nLoading all the Modelfree 4 data.")

    # Loop over the data pipes.
    for name in pipes:
        # Switch to the data pipe.
        pipe.switch(name)

        # Extract the Modelfree4 data from the 'mfout' files.
        palmer.extract(dir=ds.tmpdir + sep + name)

    # Print out.
    print("\n\nModel selection.")

    # Model selection.
    model_selection(method='AIC', modsel_pipe='aic')

    # Write the results.
    results.write(file='results', dir=ds.tmpdir, force=True)

    # Save the program state.
    state.save(state='stage2.save', dir=ds.tmpdir, force=True)


def exec_stage_3():
    """Stage 3 function.

    Final optimisation of diffusion tensor parameters together with model-free parameters.
    """

    # Let the diffusion tensor parameters be optimised.
    fix('diff', False)

    # Create the Modelfree4 files (change sims as needed, see below).
    palmer.create(dir=ds.tmpdir + sep+'final', force=True, sims=0)

    # Run Modelfree4.
    palmer.execute(dir=ds.tmpdir + sep+'final', force=True)

    # Extract the Modelfree4 data from the 'mfout' file.
    palmer.extract(dir=ds.tmpdir + sep+'final')

    # Write the results.
    results.write(file='final', dir=ds.tmpdir, force=True)

    # Save the program state.
    state.save(state='stage3.save', dir=ds.tmpdir, force=True)


# Main section of the script.
#############################

# Read the results file to get the relaxation data from.
pipe.create('data', 'mf')
results.read(file='final_results_trunc_1.3', dir=DATA_PATH)

# Set the pipe names (also the name of a preset model-free model).
pipes = ['m1', 'm2', 'm3']

# Run the stages.
exec_stage_1(pipes)
exec_stage_2(pipes)
exec_stage_3()
