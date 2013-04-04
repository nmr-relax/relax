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
"""Module containing functions for handling XEasy files."""


# relax module imports.
from lib.errors import RelaxError
from lib.io import strip


def read_list_intensity(file_data=None, heteronuc=None, proton=None, int_col=None):
    """Return the peak intensity information from the XEasy file.

    The residue number, heteronucleus and proton names, and peak intensity will be returned.


    @keyword file_data: The data extracted from the file converted into a list of lists.
    @type file_data:    list of lists of str
    @keyword heteronuc: The name of the heteronucleus as specified in the peak intensity file.
    @type heteronuc:    str
    @keyword proton:    The name of the proton as specified in the peak intensity file.
    @type proton:       str
    @keyword int_col:   The column containing the peak intensity data (for a non-standard formatted file).
    @type int_col:      int
    @raises RelaxError: When the expected peak intensity is not a float.
    @return:            The extracted data as a list of lists.  The first dimension corresponds to the spin.  The second dimension consists of the proton name, heteronucleus name, residue number, the intensity value, and the original line of text.
    @rtype:             list of lists of str, str, int, float, str
    """

    # The columns.
    w1_col = 4
    w2_col = 7
    if int_col == None:
        int_col = 10

    # Set the default proton dimension.
    H_dim = 'w1'

    # Determine the number of header lines.
    num = 0
    for line in file_data:
        # Try to see if the intensity can be extracted.
        try:
            intensity = float(line[int_col])
        except ValueError:
            num = num + 1
        except IndexError:
            num = num + 1
        else:
            break
    print("Number of header lines found: " + repr(num))

    # Remove the header.
    file_data = file_data[num:]

    # Strip the data.
    file_data = strip(file_data)

    # Determine the proton and heteronucleus dimensions.
    for line in file_data:
        # Proton in w1, heteronucleus in w2.
        if line[w1_col] == proton and line[w2_col] == heteronuc:
            # Set the proton dimension.
            H_dim = 'w1'

            # Print out.
            print("The proton dimension is w1")

            # Don't continue (waste of time).
            break

        # Heteronucleus in w1, proton in w2.
        if line[w1_col] == heteronuc and line[w2_col] == proton:
            # Set the proton dimension.
            H_dim = 'w2'

            # Print out.
            print("The proton dimension is w2")

            # Don't continue (waste of time).
            break

    # Loop over the file data.
    data = []
    for line in file_data:
        # Test for invalid assignment lines which have the column numbers changed and return empty data.
        if line[w1_col] == 'inv.':
            continue

        # The residue number.
        try:
            res_num = int(line[5])
        except:
            raise RelaxError("Improperly formatted XEasy file.")

        # Nuclei names.
        if H_dim == 'w1':
            h_name = line[w1_col]
            x_name = line[w2_col]
        else:
            x_name = line[w1_col]
            h_name = line[w2_col]

        # Intensity.
        try:
            intensity = float(line[int_col])
        except ValueError:
            raise RelaxError("The peak intensity value " + repr(intensity) + " from the line " + repr(line) + " is invalid.")

        # Append the data.
        data.append([h_name, x_name, res_num, intensity, line])

    # Return the data.
    return data
