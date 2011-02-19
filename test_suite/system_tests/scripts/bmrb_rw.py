# Script for testing the reading and writing of BMRB files.

# Python module imports.
import sys

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()


# Missing temp file (allow this script to run outside of the system test framework).
if not hasattr(ds, 'tmpfile'):
    ds.tmpfile = 'temp_bmrb'
    ds.version = '3.1'

# Create the data pipe.
pipe.create(pipe_name='results', pipe_type='mf')

# Read the results.
results.read(file='final_results_trunc_1.3', dir=sys.path[-1] + '/test_suite/shared_data/model_free/OMP')

# Play with the data.
deselect.all()
spin.copy(spin_from=':9', spin_to=':9@NE')
select.spin(':9')
select.spin(':10')
select.spin(':11')
spin.name(name='N')
molecule.name(name='OMP')

# Display the data (as a test).
relax_data.display(ri_label='R1', frq_label='800')

# Write, then read the data to a new data pipe.
bmrb.write(file=ds.tmpfile, dir=None, version=ds.version, force=True)
pipe.create(pipe_name='new', pipe_type='mf')
bmrb.read(file=ds.tmpfile, version=ds.version)

# Display tests.
sequence.display()
relax_data.display(ri_label='R1', frq_label='800')
