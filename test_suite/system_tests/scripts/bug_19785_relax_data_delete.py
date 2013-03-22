"""This system test script catches the relax_data.delete bug submitted by Martin Ballaschk.

The bug is:
    - Bug #19785 (https://gna.org/bugs/?19785).
"""

# Python module imports.
from os import sep

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# The data path.
DATA_PATH = status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'model_free' + sep + 'sphere' + sep

# Two pipes for the tests.
pipes = ['delete 1', 'delete 2']

# Load the data for each pipe.
for pipe_name in pipes:
    # Create a data pipe.
    pipe.create(pipe_name, 'mf')

    # Load the sequence.
    sequence.read(file='noe.500.out', dir=DATA_PATH, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5)

    # Name the spins.
    spin.name(name='N')

    # Load the relaxation data.
    relax_data.read(ri_id='R1_900',  ri_type='R1',  frq=900*1e6, file='r1.900.out',  dir=DATA_PATH, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)
    relax_data.read(ri_id='R2_900',  ri_type='R2',  frq=900*1e6, file='r2.900.out',  dir=DATA_PATH, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)
    relax_data.read(ri_id='NOE_900', ri_type='NOE', frq=900*1e6, file='noe.900.out', dir=DATA_PATH, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)
    relax_data.read(ri_id='R1_500',  ri_type='R1',  frq=500*1e6, file='r1.500.out',  dir=DATA_PATH, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)
    relax_data.read(ri_id='R2_500',  ri_type='R2',  frq=500*1e6, file='r2.500.out',  dir=DATA_PATH, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)
    relax_data.read(ri_id='NOE_500', ri_type='NOE', frq=500*1e6, file='noe.500.out', dir=DATA_PATH, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)

    # Relaxation data deletion.
    relax_data.delete('R2_900')
    if pipe_name == 'delete 2':
        relax_data.delete('R1_900')
        relax_data.delete('NOE_900')
        relax_data.delete('R1_500')
        relax_data.delete('R2_500')
        relax_data.delete('NOE_500')
