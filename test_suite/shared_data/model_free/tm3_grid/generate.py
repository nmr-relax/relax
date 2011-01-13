#! /usr/bin/env python

###############################################################################
#                                                                             #
# Copyright (C) 2011 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

# Python module imports.
from math import pi
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
rex = [0.5, 4]

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

    # Loop over te.
    for rex_index in range(len(rex)):
        # Loop over s2.
        for s2_index in range(len(s2)):
            # Loop over tm.
            for tm_index in range(len(tm)):
                # The spectral density values.
                J = spectral_density_mf_orig(frq=frq, tm=tm[tm_index], s2=s2[s2_index], heteronuc='13C')

                # The relaxation data.
                Ri = relaxation_data(J, frq=frq, heteronuc='13C', rex=rex[rex_index] / (2.0 * pi * frq[i])**2, r=1.20e-10, csa=200e-6)

                # The model info.
                info = "# tm3 = {local_tm=%s; s2=%s; rex=%s}" % (tm[tm_index], s2[s2_index], rex[rex_index])

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
