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
"""Module containing functions for handling NMRView files."""


# Python module imports.
from warnings import warn

# relax module imports.
from lib.errors import RelaxError
from lib.io import strip
from lib.warnings import RelaxWarning


def read_list(peak_list=None, file_data=None, int_col=None):
    """Extract the peak intensity information from the NMRView peak intensity file.

    @keyword peak_list: The peak list object to place all data into.
    @type peak_list:    lib.spectrum.objects.Peak_list instance
    @keyword file_data: The data extracted from the file converted into a list of lists.
    @type file_data:    list of lists of str
    @keyword int_col:   The column containing the peak intensity data. The default is 16 for intensities. Setting the int_col argument to 15 will use the volumes (or evolumes). For a non-standard formatted file, use a different value.
    @type int_col:      int
    @raises RelaxError: When the expected peak intensity is not a float.
    """

    # Assume the NMRView file has six header lines!
    num = 6
    print("Number of header lines: %s" % num)

    # Remove the header.
    file_data = file_data[num:]

    # Strip the data.
    file_data = strip(file_data)

    # The chemical shift columns.
    w2_col = 2
    w1_col = 9

    # The peak intensity column.
    if int_col == None:
        int_col = 16
    if int_col == 16:
        print('Using peak heights.')
    if int_col == 15:
        print('Using peak volumes (or evolumes).')

    # Loop over the file data.
    for line in file_data:
        # Unknown assignment.
        if line[1] == '{}':
            warn(RelaxWarning("The assignment '%s' is unknown, skipping this peak." % line[1]))
            continue

        # The residue number
        res_num = ''
        try:
            res_num = line[1].strip('{')
            res_num = res_num.strip('}')
            res_num = res_num.split('.')
            res_num = res_num[0]
        except ValueError:
            raise RelaxError("The peak list is invalid.")

        # Nuclei names.
        name2 = ''
        if line[1]!='{}':
            name2 = line[1].strip('{')
            name2 = name2.strip('}')
            name2 = name2.split('.')
            name2 = name2[1]
        name1 = ''
        if line[8]!='{}':
            name1 = line[8].strip('{')
            name1 = name1.strip('}')
            name1 = name1.split('.')
            name1 = name1[1]

        # Chemical shifts.
        w1 = None
        w2 = None
        if w1_col != None:
            try:
                w1 = float(line[w1_col])
            except ValueError:
                raise RelaxError("The chemical shift from the line %s is invalid." % line)
        if w2_col != None:
            try:
                w2 = float(line[w2_col])
            except ValueError:
                raise RelaxError("The chemical shift from the line %s is invalid." % line)

        # Intensity.
        try:
            intensity = float(line[int_col])
        except ValueError:
            raise RelaxError("The peak intensity value " + repr(intensity) + " from the line " + repr(line) + " is invalid.")

        # Add the assignment to the peak list object.
        peak_list.add(res_nums=[res_num, res_num], spin_names=[name1, name2], shifts=[w1, w2], intensity=intensity)
