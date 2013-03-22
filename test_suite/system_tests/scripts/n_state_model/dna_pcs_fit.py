# Script for performing a PCS analysis.

# Python module imports.
from os import sep

# relax imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# Path of the files.
str_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'dna'
data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'pcs_data'

# Create the data pipe.
self._execute_uf('DNA', 'N-state', uf_name='pipe.create')

# Load the structure.
self._execute_uf(uf_name='structure.read_pdb', file='LE_trunc.pdb', dir=str_path)

# Load the sequence information.
self._execute_uf(uf_name='structure.load_spins', spin_id='@H*')

# The PCS.
self._execute_uf(uf_name='pcs.read', align_id='Dy', file='LE_dna', dir=data_path, res_num_col=2, res_name_col=3, spin_name_col=5, data_col=6, error_col=None)
self._execute_uf(uf_name='pcs.display', align_id='Dy')

# The temperature.
self._execute_uf(uf_name='temperature', id='Dy', temp=298)

# The frequency.
self._execute_uf(uf_name='frq.set', id='Dy', frq=799.75376122 * 1e6)

# The paramagnetic centre location.
if ds.para_centre == 'true':
    self._execute_uf(uf_name='paramag.centre', pos=[25.8279, -11.6382, -2.5931])
elif ds.para_centre == 'zero':
    self._execute_uf(uf_name='paramag.centre', pos=[0, 0, 0])

# Set up the model.
self._execute_uf(uf_name='n_state_model.select_model', model='fixed')

 # Minimisation.
self._execute_uf('simplex', scaling=False, constraints=False, uf_name='minimise')

# Show the tensors.
self._execute_uf(uf_name='align_tensor.display')
