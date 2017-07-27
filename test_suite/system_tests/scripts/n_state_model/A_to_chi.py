###############################################################################
#                                                                             #
# Copyright (C) 2010 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Python module imports.
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
