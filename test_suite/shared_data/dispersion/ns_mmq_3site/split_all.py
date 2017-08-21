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
"""Script for splitting up the all.res file."""

# Translation table.
table = {
    'H-S': 'HS',
    'N-S': 'NS',
    'NHZ': 'ZQ',
    'NHD': 'DQ',
    'HNM': 'HM',
    'NHM': 'NM'
}

# Open the file and extract the data.
file = open('all.res')
lines = file.readlines()
file.close()

# Separate the header.
head = lines[0]
lines = lines[1:]

# Loop over the data.
file = None
old_name = None
for line in lines:
    # Split up.
    row = line.split()

    # The file name.
    file_name = "%s_%s.res" % (table[row[1]], row[2])

    # A new file name.
    if file_name != old_name:
        # Close the old file.
        if file != None:
            file.close()

        # Open the new.
        file = open(file_name, 'w')

        # Write the header.
        file.write(head)

    # Write out the line.
    file.write(line)

    # Update the file name.
    old_name = file_name
