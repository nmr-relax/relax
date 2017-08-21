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
"""Python script for truncating the peak intensity files to a couple of residues."""

# Python module imports.
from os import listdir, sep
from re import search

# The directories to go into.
for dir in ['500_MHz', '800_MHz']:
    # Loop over the files in the directory.
    for file in listdir(dir):
        # Skip all files not ending in '.in'.
        if not search('.in_sparky$', file) and not search('.in.bis_sparky$', file):
            continue

        # Read the file data.
        file_data = open(dir + sep + file)
        lines = file_data.readlines()
        file_data.close()

        # The output file.
        out = open(dir + sep + file[:-7] + '_trunc', 'w')

        # Loop over the lines.
        for line in lines:
            # Preserve the header lines.
            if line[0] == '\n' or line[:3] == 'Ass':
                out.write(line)
                continue

            # Skip almost all residues (except 4, 70 and 71).
            if not search('^GLY7[01]', line) and not search('^GLY4N', line):
                continue

            # Write out the data.
            out.write(line)
