from physical_constants import NH_BOND_LENGTH_RDC, dipolar_constant, g15N, g1H
from generic_fns.align_tensor import calc_chi_tensor


# The data pipe.
self._execute_uf('AtoX', 'N-state', uf_name='pipe.create')

# The dipolar constant.
const = 3.0 / (2.0*pi) * dipolar_constant(g15N, g1H, NH_BOND_LENGTH_RDC)

# The tensor.
tensor = 'A'
self._execute_uf(align_id=tensor, params=(5.090/const,  12.052/const, 0, 0, 0), param_types=2, uf_name='align_tensor.init')

# The temperature.
self._execute_uf(uf_name='temperature', id=tensor, temp=298)

# The frequency.
self._execute_uf(uf_name='frq.set', id=tensor, frq=900.0 * 1e6)

# The magnetic susceptibility tensor.
cdp.chi = calc_chi_tensor(cdp.align_tensors[0].A, cdp.frq[tensor], cdp.temperature[tensor])
print(cdp.chi)

cdp.chi_ref = [2.729e-32,   6.462e-32,  -9.191e-32]

# Comp.
for i in range(3):
    print("Chi eigenvalue ratio %i: %s " % (i+1, cdp.chi_ref[i] / cdp.chi[i, i]))
