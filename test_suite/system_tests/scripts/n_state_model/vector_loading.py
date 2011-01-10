# Script for checking the loading of bond vectors in the correct order.

# Python module imports.
from os import sep

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# Path of the files.
str_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'


# Create the data pipe.
pipe.create('populations', 'N-state')

# Load the structures.
for i in range(3):
    structure.read_pdb(file='lactose_MCMM4_S1_%i.pdb' % (ds.order_struct[i]+1), dir=str_path, set_model_num=ds.order_model[i]+1, set_mol_name='LE')

# Load the sequence information.
structure.load_spins(spin_id=':UNK@C1', combine_models=False, ave_pos=False)

# Load the CH vectors for the C atoms.
structure.vectors(spin_id='@C*', attached='H*', ave=False)
