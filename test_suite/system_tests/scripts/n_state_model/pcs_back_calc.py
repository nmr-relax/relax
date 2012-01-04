# Python module imports.
from os import sep

# relax imports.
from physical_constants import NH_BOND_LENGTH_RDC, dipolar_constant, g15N, g1H
from status import Status; status = Status()


# Path of the files.
str_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

# The data pipe.
pipe.create('pcs_back_calc', 'N-state')

# Load the structures.
structure.read_pdb('trunc_ubi_pcs.pdb', dir=str_path)

# Load the proton spins.
structure.load_spins('@H')

# The dipolar constant.
const = 3.0 / (2.0*pi) * dipolar_constant(g15N, g1H, NH_BOND_LENGTH_RDC)

# The tensor.
tensor = 'A'
align_id = tensor
align_tensor.init(tensor, (4.724/const,  11.856/const, 0, 0, 0), align_id=align_id, param_types=2)

# The temperature.
temperature(id=align_id, temp=298)

# The frequency.
frq.set(id=align_id, frq=900.0 * 1e6)

# One state model.
n_state_model.select_model('fixed')
n_state_model.number_of_states(N=1)

# Ln3+ position.
paramag.centre([0, 0, 0])

# Back calc.
pcs.back_calc(tensor)
