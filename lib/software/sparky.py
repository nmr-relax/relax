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
from lib.io import open_write_file, strip


def read_list_intensity(peak_list=None, file_data=None, int_col=3):
    """Return the peak intensity information from the Sparky peak intensity file.

    @keyword peak_list: The peak list object to place all data into.
    @type peak_list:    lib.spectrum.objects.Peak_list instance
    @keyword file_data: The data extracted from the file converted into a list of lists.
    @type file_data:    list of lists of str
    @keyword int_col:   The column containing the peak intensity data (for a non-standard formatted file).
    @type int_col:      int
    @raises RelaxError: When the expected peak intensity is not a float.
    """

    # The number of header lines.
    num = 0
    if file_data[0][0] == 'Assignment':
        num = num + 1
    if file_data[1] == '':
        num = num + 1
    print("Number of header lines found: %s" % num)

    # Default intensity column.
    if int_col == None:
        int_col = 3

    # Remove the header.
    file_data = file_data[num:]

    # Strip the data.
    file_data = strip(file_data)

    # Loop over the file data.
    data = []
    for line in file_data:
        # Skip non-assigned peaks.
        if line[0] == '?-?':
            continue

        # First split by the 2D separator.
        assign2, assign1 = split('-', line[0])

        # The assignment of the first dimension.
        row1 = split('([A-Z]+)', assign1)
        name1 = row1[-2] + row1[-1]

        # The assignment of the second dimension.
        row2 = split('([A-Z]+)', assign2)
        name2 = row2[-2] + row2[-1]

        # The residue number.
        try:
            res_num = int(row2[-3])
        except:
            raise RelaxError("Improperly formatted Sparky file, cannot process the assignment '%s'." % line[0])

        # Intensity.
        try:
            intensity = float(line[int_col])
        except ValueError:
            raise RelaxError("The peak intensity value %s from the line %s is invalid." % (intensity, line))

        # Add the assignment to the peak list object.
        peak_list.add(res_nums=[res_num, res_num], spin_names=[name1, name2], intensity=intensity)


def write_list(file_prefix=None, dir=None, res_names=None, res_nums=None, atom1_names=None, atom2_names=None, w1=None, w2=None, data_height=None, force=True):
    """Create a Sparky .list file.

    @keyword file_prefix:   The base part of the file name without the .list extension.
    @type file_prefix:      str
    @keyword dir:           The directory to place the file in.
    @type dir:              str or None
    @keyword res_names:     The residue name list for each peak entry.
    @type res_names:        list of str
    @keyword res_nums:      The residue number list for each peak entry.
    @type res_nums:         list of int
    @keyword atom1_names:   The atom name list for w1 for each peak entry.
    @type atom1_names:      list of str
    @keyword atom2_names:   The atom name list for w2 for each peak entry.
    @type atom2_names:      list of str
    @keyword w1:            The w1 chemical shift list in ppm for each peak entry.
    @type w1:               list of float
    @keyword w2:            The w2 chemical shift list in ppm for each peak entry.
    @type w2:               list of float
    @keyword data_height:   The optional data height list for each peak entry.
    @type data_height:      None or list of float
    @keyword force:         A flag which if True will cause any pre-existing files to be overwritten.
    @type force:            bool
    """

    # Checks.
    N = len(w1)
    if len(res_names) != N:
        raise RelaxError("The %s residue names does not match the %s number of entries." % (len(res_names), N))
    if len(res_nums) != N:
        raise RelaxError("The %s residue numbers does not match the %s number of entries." % (len(res_nums), N))
    if len(atom1_names) != N:
        raise RelaxError("The %s w1 atom names does not match the %s number of entries." % (len(atom1_names), N))
    if len(atom2_names) != N:
        raise RelaxError("The %s w2 atom names does not match the %s number of entries." % (len(atom2_names), N))
    if len(w1) != N:
        raise RelaxError("The %s w1 chemical shifts does not match the %s number of entries." % (len(w1), N))
    if len(w2) != N:
        raise RelaxError("The %s w2 chemical shifts does not match the %s number of entries." % (len(w2), N))
    if data_height and len(data_height) != N:
        raise RelaxError("The %s data heights does not match the %s number of entries." % (len(data_height), N))

    # Printout.
    print("Creating the Sparky list file.")

    # Open the file.
    if isinstance(file_prefix, str):
        file = open_write_file(file_name=file_prefix+".list", dir=dir, force=force)
    else:
        file = file_prefix

    # The header.
    file.write("%17s %10s %10s" % ("Assignment ", "w1 ", "w2 "))
    if data_height != None:
        file.write(" %12s" % "Data Height")
    file.write("\n\n")

    # The data.
    for i in range(N):
        # Generate the assignment.
        assign = "%s%i%s-%s" % (res_names[i], res_nums[i], atom1_names[i], atom2_names[i])

        # Write out the line.
        file.write("%17s %10.3f %10.3f" % (assign, w1[i], w2[i]))
        if data_height != None:
            file.write(" %12i" % data_height[i])
        file.write("\n")
