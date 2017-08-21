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
"""Format the input files."""

# Python module imports.
from re import search


files = ['600_MHz_1000.res', '600_MHz_100.res', '600_MHz_1500.res', '600_MHz_2000.res', '600_MHz_200.res', '600_MHz_2500.res', '600_MHz_3000.res', '600_MHz_300.res', '600_MHz_3500.res', '600_MHz_4000.res', '600_MHz_400.res', '600_MHz_4500.res', '600_MHz_5000.res', '600_MHz_500.res', '600_MHz_50.res', '600_MHz_5500.res', '600_MHz_6000.res', '600_MHz_75.res', '800_MHz_1000.res', '800_MHz_100.res', '800_MHz_1500.res', '800_MHz_2000.res', '800_MHz_200.res', '800_MHz_2500.res', '800_MHz_3000.res', '800_MHz_300.res', '800_MHz_3500.res', '800_MHz_4000.res', '800_MHz_400.res', '800_MHz_4500.res', '800_MHz_5000.res', '800_MHz_500.res', '800_MHz_50.res', '800_MHz_5500.res', '800_MHz_6000.res', '800_MHz_75.res']

# Loop over the files.
for file_name in files:
    # Open the original.
    file = open('../%s'%file_name)
    lines = file.readlines()
    file.close()

    # Open the new file.
    file = open(file_name, 'w')

    # Loop over the lines.
    for line in lines:
        # Skip the header.
        if search('^#', line):
            continue

        # Split the line.
        row = line.split()

        # Write out the data.
        file.write("%20s %20s %20s\n" % (row[5], row[9], row[8]))

    # Close the file.
    file.close()
