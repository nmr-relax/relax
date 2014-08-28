from lib.periodic_table import periodic_table
from lib.physical_constants import NH_BOND_LENGTH_RDC, dipolar_constant
from pipe_control.align_tensor import calc_chi_tensor


# The data pipe.
self._execute_uf('AtoX', 'N-state', uf_name='pipe.create')

# The dipolar constant.
const = 3.0 / (2.0*pi) * dipolar_constant(periodic_table.gyromagnetic_ratio('15N'), periodic_table.gyromagnetic_ratio('1H'), NH_BOND_LENGTH_RDC)

# The tensor.
tensor = 'A'
self._execute_uf(align_id=tensor, params=(5.090/const,  12.052/const, 0, 0, 0), param_types=2, uf_name='align_tensor.init')

# The temperature.
self._execute_uf(uf_name='spectrometer.temperature', id=tensor, temp=298)

# The frequency.
self._execute_uf(uf_name='spectrometer.frequency', id=tensor, frq=900.0 * 1e6)

# The magnetic susceptibility tensor.
cdp.chi = calc_chi_tensor(cdp.align_tensors[0].A, cdp.spectrometer_frq[tensor], cdp.temperature[tensor])
print(cdp.chi)

cdp.chi_ref = [2.729e-32,   6.462e-32,  -9.191e-32]

# Comp.
for i in range(3):
    print("Chi eigenvalue ratio %i: %s " % (i+1, cdp.chi_ref[i] / cdp.chi[i, i]))
