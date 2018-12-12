#! /usr/bin/env python

###############################################################################
#                                                                             #
# Copyright (C) 2011 Edward d'Auvergne                                        #
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
from numpy import array, float64
from os import pardir, sep
import sys

# The path to the back-calculation module.
sys.path.append(sys.path[0] + sep + pardir)

# The back-calculation module.
from back_calc import relaxation_data, spectral_density_mf_orig


# The model-free parameters.
tm = [2e-9, 10e-9, 21e-9]
s2 = [0.2, 0.8, 0.95]

# The proton frequencies.
vals = [400, 500, 600, 700, 800, 900, 1000]
frq = array(vals, float64)
frq = frq * 1e6

# Write out the data.
for i in range(len(vals)):
    # The files.
    file_r1 =  open('r1.%s.out' % vals[i], 'w')
    file_r2 =  open('r2.%s.out' % vals[i], 'w')
    file_noe = open('noe.%s.out' % vals[i], 'w')

    # Residue number.
    res_num = 1

    # Loop over s2.
    for s2_index in range(3):
        # Loop over tm.
        for tm_index in range(3):
            # The spectral density values.
            J = spectral_density_mf_orig(frq=frq, tm=tm[tm_index], S2=s2[s2_index], heteronuc='13C')

            # The relaxation data.
            Ri = relaxation_data(J, frq=frq, heteronuc='13C', r=1.20e-10, csa=200e-6)

            # The model info.
            info = "# tm2 = {local_tm=%s; s2=%s}" % (tm[tm_index], s2[s2_index])

            # Write out the values.
            file_r1.write('%-15s %-5s %-15s %-5s %-5s %-20s %-20s %s\n' %  ('Polycarbonate', res_num, 'Bisphenol_A', '1', 'C1', Ri[i, 0], Ri[i, 0] * 0.02, info))
            file_r2.write('%-15s %-5s %-15s %-5s %-5s %-20s %-20s %s\n' %  ('Polycarbonate', res_num, 'Bisphenol_A', '1', 'C1', Ri[i, 1], Ri[i, 1] * 0.02, info))
            file_noe.write('%-15s %-5s %-15s %-5s %-5s %-20s %-20s %s\n' % ('Polycarbonate', res_num, 'Bisphenol_A', '1', 'C1', Ri[i, 2], 0.05, info))

            # Increment the spin number.
            res_num += 1

    # Close the files.
    file_r1.close()
    file_r2.close()
    file_noe.close()
