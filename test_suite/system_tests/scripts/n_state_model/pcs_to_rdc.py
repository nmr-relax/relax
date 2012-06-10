# Python module imports.
from os import sep

# relax imports.
from generic_fns.mol_res_spin import spin_loop
from physical_constants import NH_BOND_LENGTH_RDC, dipolar_constant, g15N, g1H
from status import Status; status = Status()


# Path of the files.
str_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

# The data pipe.
self._execute_uf(uf_name='pipe.create', pipe_name='rdc_back_calc', pipe_type='N-state')

# Load the structures.
self._execute_uf(uf_name='structure.read_pdb', file='trunc_ubi_pcs.pdb', dir=str_path)

# Load the spins.
self._execute_uf(uf_name='structure.load_spins', spin_id='@N')

# Set the heteronucleus type.
self._execute_uf(uf_name='value.set', val='15N', param='heteronuc_type')
self._execute_uf(uf_name='value.set', val='1H', param='proton_type')
self._execute_uf(uf_name='value.set', val=NH_BOND_LENGTH_RDC, param='r')

# Load the bond vectors.
self._execute_uf(uf_name='structure.vectors', attached='H', spin_id='@N')

# The dipolar constant.
const = 3.0 / (2.0*pi) * dipolar_constant(g15N, g1H, NH_BOND_LENGTH_RDC)

# The tensor.
tensor = 'A'
self._execute_uf(uf_name='align_tensor.init', tensor=tensor, params=(4.724/const,  11.856/const, 0, 0, 0), align_id=tensor, param_types=2)

# The temperature.
self._execute_uf(uf_name='temperature', id=tensor, temp=298)

# The frequency.
self._execute_uf(uf_name='frq.set', id=tensor, frq=900.0 * 1e6)

# One state model.
self._execute_uf(uf_name='n_state_model.select_model', model='fixed')
self._execute_uf(uf_name='n_state_model.number_of_states', N=1)

# Set the RDC data.
rdcs = [-1.390, -6.270, -9.650]
i = 0
for spin in spin_loop():
    spin.rdc = {}
    spin.rdc[tensor] = rdcs[i]
    i += 1

# Back calc.
self._execute_uf(uf_name='rdc.back_calc', align_id=tensor)
