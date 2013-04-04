###############################################################################
#                                                                             #
# Copyright (C) 2004-2013 Edward d'Auvergne                                   #
# Copyright (C) 2008 Sebastien Morin                                          #
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
"""Module containing functions for handling Sparky files."""


# Python module imports.
from re import split

# relax module imports.
from lib.errors import RelaxError
from lib.io import strip


def read_list_intensity(file_data=None, int_col=None):
    """Return the peak intensity information from the Sparky peak intensity file.

    The residue number, heteronucleus and proton names, and peak intensity will be returned.


    @keyword file_data: The data extracted from the file converted into a list of lists.
    @type file_data:    list of lists of str
    @keyword int_col:   The column containing the peak intensity data (for a non-standard formatted file).
    @type int_col:      int
    @raises RelaxError: When the expected peak intensity is not a float.
    @return:            The extracted data as a list of lists.  The first dimension corresponds to the spin.  The second dimension consists of the proton name, heteronucleus name, residue number, the intensity value, and the original line of text.
    @rtype:             list of lists of str, str, int, float, str
    """

    # The number of header lines.
    num = 0
    if file_data[0][0] == 'Assignment':
        num = num + 1
    if file_data[1] == '':
        num = num + 1
    print("Number of header lines found: %s" % num)

    # Remove the header.
    file_data = file_data[num:]

    # Strip the data.
    file_data = strip(file_data)

    # Loop over the file data.
    data = []
    for line in file_data:
        # The Sparky assignment.
        assignment = ''
        res_num = ''
        h_name = ''
        x_name = ''
        intensity = ''

        # Skip non-assigned peaks.
        if line[0] == '?-?':
            continue

        # First split by the 2D separator.
        x_assign, h_assign = split('-', line[0])

        # The proton info.
        h_row = split('([A-Z]+)', h_assign)
        h_name = h_row[-2] + h_row[-1]

        # The heteronucleus info.
        x_row = split('([A-Z]+)', x_assign)
        x_name = x_row[-2] + x_row[-1]

        # The residue number.
        try:
            res_num = int(x_row[-3])
        except:
            raise RelaxError("Improperly formatted Sparky file.")

        # The peak intensity column.
        if int_col == None:
            int_col = 3

        # Intensity.
        try:
            intensity = float(line[int_col])
        except ValueError:
            raise RelaxError("The peak intensity value " + repr(intensity) + " from the line " + repr(line) + " is invalid.")

        # Append the data.
        data.append([h_name, x_name, res_num, intensity, line])

    # Return the data.
    return data
