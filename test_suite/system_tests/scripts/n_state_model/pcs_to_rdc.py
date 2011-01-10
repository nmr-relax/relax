# Python module imports.
from os import sep

# relax imports.
from generic_fns.mol_res_spin import spin_loop
from physical_constants import NH_BOND_LENGTH_RDC, dipolar_constant, g15N, g1H
from status import Status; status = Status()


# Path of the files.
str_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

# The data pipe.
pipe.create('rdc_back_calc', 'N-state')

# Load the structures.
structure.read_pdb('trunc_ubi_pcs.pdb', dir=str_path)

# Load the spins.
structure.load_spins('@N')

# Set the heteronucleus type.
value.set('15N', 'heteronucleus')
value.set('1H', 'proton')
value.set(NH_BOND_LENGTH_RDC, 'r')

# Load the bond vectors.
structure.vectors('H', '@N')

# The dipolar constant.
const = 3.0 / (2.0*pi) * dipolar_constant(g15N, g1H, NH_BOND_LENGTH_RDC)

# The tensor.
tensor = 'A'
align_tensor.init(tensor, (4.724/const,  11.856/const, 0, 0, 0), param_types=2)

# The temperature.
temperature(id=tensor, temp=298)

# The frequency.
frq.set(id=tensor, frq=900.0 * 1e6)

# One state model.
n_state_model.select_model('fixed')
n_state_model.number_of_states(N=1)

# Set the RDC data.
rdcs = [-1.390, -6.270, -9.650]
i = 0
for spin in spin_loop():
    spin.rdc = {}
    spin.rdc[tensor] = rdcs[i]
    i += 1

# Back calc.
rdc.back_calc(tensor)
