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


# The file data.
file = open('testNOE.txt')
lines = file.readlines()
file.close()

# Get the data.
data = []
in_data = False
index = 0
for line in lines:
    # Split the line.
    row = line.split("\t")

    # Strip the rubbish.
    for j in range(len(row)):
        row[j] = row[j].strip()

    # Empty line.
    if len(row) == 0:
        continue

    # The section.
    if row[0] == 'SECTION:' and row[1] == 'results':
        in_data = True
        continue

    # Not in the data section.
    if not in_data:
        continue

    # The header line.
    if row[0] == 'Peak name':
        continue

    # The residue name and number.
    res_name, res_num = row[0].split()

    # The values.
    data.append([])
    data[index].append(res_name)
    data[index].append(int(res_num[1:-1]))
    data[index].append(float(row[3]))
    data[index].append(float(row[4]))

    # Increment the residue index.
    index += 1

noe = []
noe_err = []
for i in range(len(data)):
    noe.append(data[i][2])
    noe_err.append(data[i][3])

print("\nnoe = %s" % noe)
print("\nnoe_err = %s" % noe_err)
