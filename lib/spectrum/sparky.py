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
"""Module containing functions for handling Sparky files."""


# Python module imports.
from re import split
from warnings import warn

# relax module imports.
from lib.errors import RelaxError
from lib.io import open_write_file, strip
from lib.warnings import RelaxWarning


def read_list(peak_list=None, file_data=None):
    """Extract the peak intensity information from the Sparky peak intensity file.

    @keyword peak_list: The peak list object to place all data into.
    @type peak_list:    lib.spectrum.objects.Peak_list instance
    @keyword file_data: The data extracted from the file converted into a list of lists.
    @type file_data:    list of lists of str
    @raises RelaxError: When the expected peak intensity is not a float.
    """

    # The number of header lines.
    num = 0
    if file_data[0][0] == 'Assignment':
        num = num + 1
    if file_data[1] == '':
        num = num + 1
    print("Number of header lines found: %s" % num)

    # The columns according to the file.
    w1_col = None
    w2_col = None
    w3_col = None
    w4_col = None
    int_col = None
    for i in range(len(file_data[0])):
        # The chemical shifts.
        if file_data[0][i] == 'w1':
            w1_col = i
        elif file_data[0][i] == 'w2':
            w2_col = i
        elif file_data[0][i] == 'w3':
            w3_col = i
        elif file_data[0][i] == 'w4':
            w4_col = i

        # The peak height.
        elif file_data[0][i] == 'Height':
            # The peak height when exported from CcpNmr Analysis export without 'Data'.
            int_col = i

            # The peak height when exported from Sparky.
            if file_data[0][i-1] == 'Data' and file_data[0][i] == 'Height':
                int_col = i-1

        # The peak volume.
        elif file_data[0][i] == 'Intensity':
            int_col = i

    # Remove the header.
    file_data = file_data[num:]

    # Strip the data.
    file_data = strip(file_data)

    # The dimensionality.
    if w4_col != None:
        dim = 4
    elif w3_col != None:
        dim = 3
    elif w2_col != None:
        dim = 2
    elif w1_col != None:
        dim = 1
    else:
        raise RelaxError("The dimensionality of the peak list cannot be determined.")
    print("%sD peak list detected." % dim)

    # Loop over the file data.
    for line in file_data:
        # Skip non-assigned peaks.
        if line[0] == '?-?':
            continue

        # Split up the assignments.
        if dim == 1:
            assign1 = line[0]
        elif dim == 2:
            assign1, assign2 = split('-', line[0])
        elif dim == 3:
            assign1, assign2, assign3 = split('-', line[0])
        elif dim == 4:
            assign1, assign2, assign3, assign4 = split('-', line[0])

        # Process the assignment for each dimension.
        if dim >= 1:
            row1 = split('([a-zA-Z]+)', assign1)
            name1 = row1[-2] + row1[-1]
        if dim >= 2:
            row2 = split('([a-zA-Z]+)', assign2)
            name2 = row2[-2] + row2[-1]
        if dim >= 3:
            row3 = split('([a-zA-Z]+)', assign3)
            name3 = row3[-2] + row3[-1]
        if dim >= 4:
            row4 = split('([a-zA-Z]+)', assign4)
            name4 = row4[-2] + row4[-1]

        # Get the residue number for dimension 1.
        got_res_num1 = True
        try:
            res_num1 = int(row1[-3])
        except:
            got_res_num1 = False
            raise RelaxError("Improperly formatted Sparky file, cannot process the residue number for dimension 1 in assignment: %s." % line[0])

        # Get the residue number for dimension 2.
        try:
            res_num2 = int(row2[-3])
        except:
            # We cannot always expect dimension 2 to have residue number.
            if got_res_num1:
                res_num2 = res_num1
            else:
                res_num2 = None
                warn(RelaxWarning("Improperly formatted Sparky file, cannot process the residue number for dimension 2 in assignment: %s. Setting residue number to %s." % (line[0], res_num2)))

        # The residue name for dimension 1.
        got_res_name1 = True
        try:
            res_name1 = row1[-4]
        except:
            got_res_name1 = False
            res_name1 = None
            warn(RelaxWarning("Improperly formatted Sparky file, cannot process the residue name for dimension 1 in assignment: %s. Setting residue name to %s." % (line[0], res_name1)))

        # The residue name for dimension 2.
        try:
            res_name2 = row2[-4]
        except:
            # We cannot always expect dimension 2 to have residue name.
            if got_res_name1:
                res_name2 = res_name1
            else:
                res_name2 = None
                warn(RelaxWarning("Improperly formatted NMRPipe SeriesTab file, cannot process the residue name for dimension 2 in assignment: %s. Setting residue name to %s." % (line[0], res_name2)))

        # Chemical shifts.
        w1 = None
        w2 = None
        w3 = None
        w4 = None
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
        if w3_col != None:
            try:
                w3 = float(line[w3_col])
            except ValueError:
                raise RelaxError("The chemical shift from the line %s is invalid." % line)
        if w4_col != None:
            try:
                w4 = float(line[w4_col])
            except ValueError:
                raise RelaxError("The chemical shift from the line %s is invalid." % line)

        # Intensity.
        if int_col != None:
            try:
                intensity = float(line[int_col])
            except ValueError:
                raise RelaxError("The peak intensity value from the line %s is invalid." % line)

            # Add the assignment to the peak list object.
            if dim == 1:
                peak_list.add(res_nums=[res_num1], res_names=[res_name1], spin_names=[name1], shifts=[w1], intensity=intensity)
            elif dim == 2:
                peak_list.add(res_nums=[res_num1, res_num2], res_names=[res_name1, res_name2], spin_names=[name1, name2], shifts=[w1, w2], intensity=intensity)
            elif dim == 3:
                peak_list.add(res_nums=[res_num1, res_num2, res_num1], res_names=[res_name1, res_name2, res_name1], spin_names=[name1, name2, name3], shifts=[w1, w2, w3], intensity=intensity)
            elif dim == 4:
                peak_list.add(res_nums=[res_num1, res_num2, res_num1, res_num1], res_names=[res_name1, res_name2, res_name1, res_name1], spin_names=[name1, name2, name3, name4], shifts=[w1, w2, w3, w4], intensity=intensity)

        # If no intensity column, for example when reading spins from a spectrum list.
        elif int_col == None:
            warn(RelaxWarning(("The peak intensity value from the line %s is invalid. The return value will be without intensity." % line)))

            # Add the assignment to the peak list object.
            if dim == 1:
                peak_list.add(res_nums=[res_num1], res_names=[res_name1], spin_names=[name1], shifts=[w1])
            elif dim == 2:
                peak_list.add(res_nums=[res_num1, res_num2], res_names=[res_name1, res_name2], spin_names=[name1, name2], shifts=[w1, w2])
            elif dim == 3:
                peak_list.add(res_nums=[res_num1, res_num2, res_num1], res_names=[res_name1, res_name2, res_name1], spin_names=[name1, name2, name3], shifts=[w1, w2, w3])
            elif dim == 4:
                peak_list.add(res_nums=[res_num1, res_num2, res_num1, res_num1], res_names=[res_name1, res_name2, res_name1, res_name1], spin_names=[name1, name2, name3, name4], shifts=[w1, w2, w3, w4])


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
