# Script for model-free analysis using the program Dasha.

# Python module imports.
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
    sequence.read(sys.path[-1] + '/test_suite/shared_data/jw_mapping/noe.dat')

    # Load a PDB file.
    #structure.read_pdb('example.pdb')

    # Load the relaxation data.
    relax_data.read('R1', '600', 600.0 * 1e6, sys.path[-1] + '/test_suite/shared_data/jw_mapping/R1.dat')
    relax_data.read('R2', '600', 600.0 * 1e6, sys.path[-1] + '/test_suite/shared_data/jw_mapping/R2.dat')
    relax_data.read('NOE', '600', 600.0 * 1e6, sys.path[-1] + '/test_suite/shared_data/jw_mapping/noe.dat')

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
    results.write(file=ds.tmpdir + '/' + 'results_dasha', dir=None, force=True)
