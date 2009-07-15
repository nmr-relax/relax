###############################################################################
#                                                                             #
# Copyright (C) 2009 Edward d'Auvergne                                        #
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

# Module docstring.
"""Module containing functions related to the Frame Order theories."""

# Python module imports.
from sys import stdout


def print_frame_order_2nd_degree(matrix, name=None):
    """Nicely print out the Frame Order matrix of the 2nd degree.

    @param matrix:  The 3D, rank-4 Frame Order matrix.
    @type name:     numpy 3D, rank-4 array
    @keyword name:  The name of the matrix.
    @type name:     None or str
    """

    # Default name.
    if not name:
        name = 'Frame Order matrix, 2nd degree'

    # Header and first row start.
    stdout.write("\n%s:\n" % name)
    stdout.write('[[')

    # Loop over the rows.
    for i in range(len(matrix)):
        # 2nd to last row start.
        if i != 0:
            stdout.write(' [')

        # Row end character.
        char2 = ','
        if i == len(matrix) - 1:
            char2 = ']'

        # Loop over the columns.
        for j in range(len(matrix[i])):
            # Column end character.
            char1 = ','
            if j == len(matrix[i]) - 1:
                char1 = ']%s\n' % char2

            # Write out the elements.
            if matrix[i, j]:
                stdout.write("%10.4f%s" % (matrix[i, j], char1))
            else:
                stdout.write("%10s%s" % (0, char1))
