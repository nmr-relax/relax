# Script for model-free analysis using the program Dasha.

# Python module imports.
import __main__
from os import sep
import sys

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()


# Missing temp directory (allow this script to run outside of the system test framework).
if not hasattr(ds, 'tmpdir'):
    ds.tmpdir = 'temp_script'

# Set the data pipe names (also the names of preset model-free models).
pipes = ['m1', 'm2', 'm3']

# Loop over the pipes.
for name in pipes:
    # Create the data pipe.
    pipe.create(name, 'mf')

    # Load the sequence.
    sequence.read(__main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'jw_mapping'+sep+'noe.dat', res_num_col=1, res_name_col=2)

    # Load a PDB file.
    #structure.read_pdb('example.pdb')

    # Load the relaxation data.
    relax_data.read('R1', '600', 600.0 * 1e6, __main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'jw_mapping'+sep+'R1.dat', res_num_col=1, res_name_col=2, data_col=3, error_col=4)
    relax_data.read('R2', '600', 600.0 * 1e6, __main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'jw_mapping'+sep+'R2.dat', res_num_col=1, res_name_col=2, data_col=3, error_col=4)
    relax_data.read('NOE', '600', 600.0 * 1e6, __main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'jw_mapping'+sep+'noe.dat', res_num_col=1, res_name_col=2, data_col=3, error_col=4)

    # Setup other values.
    diffusion_tensor.init(1e-8, fixed=True)
    value.set('15N', 'heteronucleus')
    value.set(1.02 * 1e-10, 'bond_length')
    value.set(-172 * 1e-6, 'csa')

    # Select the model-free model.
    model_free.select_model(model=name)

    # Create the Dasha script.
    dasha.create(algor='NR', dir=ds.tmpdir, force=True)

    # Execute Dasha.
    dasha.execute(dir=ds.tmpdir)

    # Read the data.
    dasha.extract(dir=ds.tmpdir)

    # Write the results.
    results.write(file=ds.tmpdir + sep + 'results_dasha', dir=None, force=True)
