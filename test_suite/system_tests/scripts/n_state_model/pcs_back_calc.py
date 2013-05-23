# Python module imports.
from os import sep

# relax imports.
from lib.physical_constants import NH_BOND_LENGTH_RDC, dipolar_constant, g15N, g1H
from status import Status; status = Status()


# Path of the files.
str_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

# The data pipe.
self._execute_uf(uf_name='pipe.create', pipe_name='pcs_back_calc', pipe_type='N-state')

# Load the structures.
self._execute_uf(uf_name='structure.read_pdb', file='trunc_ubi_pcs.pdb', dir=str_path)

# Load the proton spins.
self._execute_uf(uf_name='structure.load_spins', spin_id='@H')

# The dipolar constant.
const = 3.0 / (2.0*pi) * dipolar_constant(g15N, g1H, NH_BOND_LENGTH_RDC)

# The tensor.
tensor = 'A'
align_id = tensor
self._execute_uf(uf_name='align_tensor.init', tensor=tensor, params=(4.724/const,  11.856/const, 0, 0, 0), align_id=align_id, param_types=2)

# The temperature.
self._execute_uf(uf_name='spectrometer.temperature', id=align_id, temp=298)

# The frequency.
self._execute_uf(uf_name='spectrometer.frequency', id=align_id, frq=900.0 * 1e6)

# One state model.
self._execute_uf(uf_name='n_state_model.select_model', model='fixed')
self._execute_uf(uf_name='n_state_model.number_of_states', N=1)

# Ln3+ position.
self._execute_uf(uf_name='paramag.centre', pos=[0, 0, 0])

# Back calc.
self._execute_uf(uf_name='pcs.back_calc', align_id=tensor)
