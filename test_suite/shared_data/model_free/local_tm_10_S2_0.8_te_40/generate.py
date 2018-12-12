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
tm = 10e-9
S2 = 0.8
te = 40e-12

# The proton frequencies.
vals = [400, 500, 600, 700, 800, 900, 1000]
frq = array(vals, float64)
frq = frq * 1e6

# The spectral density values.
J = spectral_density_mf_orig(frq=frq, tm=tm, S2=S2, te=te, heteronuc='15N')

# The relaxation data.
Ri = relaxation_data(J, frq=frq, heteronuc='15N', r=1.02e-10, csa=-172e-6)
print("Ri:\n%s" % Ri)

# Write out the data.
for i in range(len(vals)):
    # The files.
    file_r1 =  open('r1.%s.out' % vals[i], 'w')
    file_r2 =  open('r2.%s.out' % vals[i], 'w')
    file_noe = open('noe.%s.out' % vals[i], 'w')

    # Write out the values.
    file_r1.write('%s %s %s %s\n' %  ('5', 'GLU', Ri[i, 0], Ri[i, 0] * 0.02))
    file_r2.write('%s %s %s %s\n' %  ('5', 'GLU', Ri[i, 1], Ri[i, 1] * 0.02))
    file_noe.write('%s %s %s %s\n' % ('5', 'GLU', Ri[i, 2], 0.05))

