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
from numpy import array, matrix
import sys

# relax module imports.
from float import isNaN


def print_frame_order_2nd_degree(daeg, name=None, epsilon=1e-15, integer=False, dot=False, comma=True, file=sys.stdout):
    """Nicely print out the Frame Order matrix of the 2nd degree.

    @param daeg:        The 3D, rank-4 Frame Order matrix.
    @type daeg:         numpy 3D, rank-4 array
    @keyword name:      The name of the matrix.
    @type name:         None or str
    @keyword epsilon:   The minimum value, below which is considered zero.
    @type epsilon:      float
    @keyword integer:   A flag which if true will only print the integer part of the number.
    @type integer:      bool
    @keyword dot:       A flag which if true replaces all zeros with dot characters.
    @type dot:          bool
    @keyword comma:     A flag which if true causes commas to be printed between the elements.
    @type comma:        bool
    @keyword file:      The file object to write to.
    @type file:         file object
    """

    # Default name.
    if not name:
        name = 'Frame Order matrix, 2nd degree'

    # Header and first row start.
    file.write("\n%s:\n" % name)
    file.write('[[')

    # Convert to an array, if necessary.
    if isinstance(daeg, matrix):
        daeg = array(daeg)

    # Loop over the rows.
    for i in range(len(daeg)):
        # 2nd to last row start.
        if i != 0:
            file.write(' [')

        # Row end character.
        char2 = ''
        if comma:
            char2 = ','
        if i == len(daeg) - 1:
            char2 = ']'

        # Loop over the columns.
        for j in range(len(daeg[i])):
            # Column end character.
            char1 = ''
            if comma:
                char1 = ','
            if j == len(daeg[i]) - 1:
                char1 = ']%s\n' % char2

            # Write out the elements.
            if abs(daeg[i, j]) > epsilon:
                # Integer print out.
                if integer:
                    val = int(daeg[i, j])
                    format = "%4i%s"

                # Float print out.
                else:
                    val = daeg[i, j]
                    format = "%10.4f%s"

            # NaN.
            elif isNaN(daeg[i, j]):
                val = 'NaN'
                if integer:
                    format = "%4i%s"
                else:
                    format = "%10s%s"

            # Write out the zero elements.
            else:
                # Integer print out.
                if integer:
                    format = "%4s%s"

                # Float print out.
                else:
                    format = "%10s%s"

                # The character.
                if dot:
                    val = '.'
                else:
                    val = '0'

            # Write.
            file.write(format % (val, char1))
