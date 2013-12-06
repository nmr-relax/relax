###############################################################################
#                                                                             #
# Copyright (C) 2004-2013 Edward d'Auvergne                                   #
# Copyright (C) 2008 Sebastien Morin                                          #
# Copyright (C) 2013 Troels E. Linnet                                         #
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


# Python module imports.
from warnings import warn

# relax module imports.
from lib.errors import RelaxError
from lib.io import strip
from lib.warnings import RelaxWarning


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
    w1_col = 3
    w2_col = 2
    ass_w1_col = 7
    ass_w2_col = 4
    res_name1_col = 9
    res_name2_col = 5
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
        if line[ass_w1_col] == 'inv.' or line[ass_w2_col] == 'inv.':
            continue

        # The residue number for dimension 1.
        try:
            res_num1 = int(line[8])
        except:
            raise RelaxError("Improperly formatted XEasy file, cannot process the residue number for dimension 1 in assignment: %s." % line)

        # The residue number for dimension 2.
        try:
            res_num2 = int(line[5])
        except:
            warn(RelaxWarning("Improperly formatted XEasy file, cannot process the residue number for dimension 2 in assignment: %s. Setting residue number to None." % line))
            res_num2 = None

        # Nuclei names.
        name1 = line[ass_w1_col]
        name2 = line[ass_w2_col]

        # Residue names.
        res_name1 = line[res_name1_col]
        res_name2 = line[res_name2_col]

        # Chemical shifts.
        try:
            w1 = float(line[w1_col])
        except ValueError:
            raise RelaxError("The w1 chemical shift from the line %s is invalid." % line)
        try:
            w2 = float(line[w2_col])
        except ValueError:
            raise RelaxError("The w2 chemical shift from the line %s is invalid." % line)

        # Intensity.
        try:
            intensity = float(line[int_col])
        except ValueError:
            raise RelaxError("The peak intensity value from the line %s is invalid." % line)

        # Add the assignment to the peak list object.
        peak_list.add(res_nums=[res_num1, res_num2], res_names=[res_name1, res_name2], spin_names=[name1, name2], shifts=[w1, w2], intensity=intensity)
