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


def read_list(peak_list=None, file_data=None, int_col=None):
    """Extract the peak intensity information from the XEasy file.

    @keyword peak_list: The peak list object to place all data into.
    @type peak_list:    lib.spectrum.objects.Peak_list instance
    @keyword file_data: The data extracted from the file converted into a list of lists.
    @type file_data:    list of lists of str
    @keyword int_col:   The column containing the peak intensity data (for a non-standard formatted file).
    @type int_col:      int
    @raises RelaxError: When the expected peak intensity is not a float.
    """

    # The hardcoded column positions (note that w1 and w2 are swapped!).
    w1_col = 7
    w2_col = 4
    if int_col == None:
        int_col = 10

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

    # Loop over the file data.
    for line in file_data:
        # Test for invalid assignment lines which have the column numbers changed and return empty data.
        if line[w1_col] == 'inv.' or line[w2_col] == 'inv.':
            continue

        # The residue number.
        try:
            res_num = int(line[5])
        except:
            raise RelaxError("Improperly formatted XEasy file, cannot read the line %s." % line)

        # Nuclei names.
        name1 = line[w1_col]
        name2 = line[w2_col]

        # Intensity.
        try:
            intensity = float(line[int_col])
        except ValueError:
            raise RelaxError("The peak intensity value %s from the line %s is invalid." % (intensity, line))

        # Add the assignment to the peak list object.
        peak_list.add(res_nums=[res_num, res_num], spin_names=[name1, name2], intensity=intensity)
