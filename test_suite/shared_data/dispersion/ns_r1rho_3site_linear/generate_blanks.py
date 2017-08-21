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
frqs = [600, 800]
fields = [50, 75, 100, 200, 300, 400, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000]
offsets = []
for i in range(21):
    offsets.append(i * 100.0 - 1000.0)

# Loop over the magnetic fields.
for frq in frqs:
    # Loop over the different spin-lock field strengths.
    for field in fields:
        # Open the output file.
        file_name = "%i_MHz_%i.res" % (frq, field)
        file = open('blank' + sep + file_name, 'w')

        # Loop over the offsets.
        for offset in offsets:
            # Write out the data.
            file.write("%20.12f %10.1f %10.1f\n" % (offset, 0.0, 0.5))
