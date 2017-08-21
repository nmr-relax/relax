###############################################################################
#                                                                             #
# Copyright (C) 2013 Edward d'Auvergne                                        #
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

# Module docstring.
"""Script for generating blank input data for cpmg_fit."""

# Python module imports.
from os import sep


# The data.
data = [
    ['NS', 'S', 'N15', 0.04, 1000.0],
    ['HS', 'S', 'H1', 0.03, 2667.0],
    ['DQ', 'D', 'H1/N15', 0.03, 1067.0],
    ['ZQ', 'Z', 'H1/N15', 0.03, 1067.0],
    ['NM', 'M', 'N15/H1', 0.02, 1000.0],
    ['HM', 'M', 'H1/N15', 0.02, 2500.0],
]

# Loop over the data.
for file_root, Q, nuc, time, max_frq in data:
    # Loop over some magnetic field strengths.
    for mag_frq in [400, 600, 800, 1000]:
        # Open the output file.
        file_name = "%s_%i.res" % (file_root, mag_frq)
        file = open('blank' + sep + file_name, 'w')

        # The minimum nu value.
        nu = 1.0 / time

        # Loop over nu until the max is reached.
        i = 0
        while True:
            # The CPMG frequency.
            frq = nu*(i+1)

            # Max reached.
            if frq > max_frq:
                break

            # Write out the data.
            file.write("%20.12f %10.1f %10.1f\n" % (frq, 0.0, 0.5))

            # Increment the nu counter.
            i += 1
