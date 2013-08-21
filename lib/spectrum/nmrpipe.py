###############################################################################
#                                                                             #
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
"""Module containing functions for handling NMRPipe SeriesTab files."""


# Python module imports.
import re

# relax module imports.
from lib.errors import RelaxError
from lib.io import open_write_file, strip


def read_seriestab(peak_list=None, file_data=None, int_col=None):
    """Extract the intensity information from the NMRPipe SeriesTab peak intensity file.

    @keyword peak_list: The peak list object to place all data into.
    @type peak_list:    lib.spectrum.objects.Peak_list instance
    @keyword file_data: The data extracted from the file converted into a list of lists.
    @type file_data:    list of lists of str
    @keyword int_col:  The column which to multiply the peak intensity data (used by the SeriesTab intensity file format).
    @type int_col:     int
    @raises RelaxError: When the expected peak intensity is not a float.
    """

    # Set start variables.
    modeline = False
    mode = False
    varsline = False
    header = False

    # Loop over lines, to extract variables and find header size.
    line_nr = 0
    for line in file_data:
        if len(line) > 0:
            if line[0] == 'REMARK' and line[1] == 'Mode:':
                modeline = line[2:]
                mode = modeline[0]
            elif line[0] == 'VARS':
                varsline = line[1:]
            elif line[0] == '1':
                header = line_nr
                break
        line_nr += 1

    # Raise RelaxError, if the MODE is not found.
    if not (modeline and mode):
        raise RelaxError("MODE not detected. Expecting line 2:\nREMARK Mode: Summation")

    # Raise RelaxError, if the VARS line is not found.
    if not (varsline):
        raise RelaxError("VARS not detected. Expecting line 8:\nVARS INDEX X_AXIS Y_AXIS X_PPM Y_PPM VOL ASS Z_A0")

    # Raise RelaxError, if the header size is not found.
    if not header:
        raise RelaxError("'1' not detected in start of line. Cannot determine header size.")

    # Find index of assignment ASS.
    ass_i = varsline.index('ASS')

    # Make a regular search for Z_A entries.
    Z_A = re.compile("Z_A*")
    spectra = list(filter(Z_A.search, varsline))

    # Find index of Z_A entries.
    spectra_i = []
    for y in spectra:
        spectra_i.append(varsline.index(y))

    # Remove the header.
    file_data = file_data[header:]

    # Loop over the file data.
    for line in file_data:
        # Skip non-assigned peaks.
        if line[ass_i] == '?-?':
            continue

        # First split by the 2D separator.
        assign1, assign2 = re.split('-', line[ass_i])

        # The assignment of the first dimension.
        row1 = re.split('([a-zA-Z]+)', assign1)
        name1 = row1[-2] + row1[-1]

        # The assignment of the second dimension.
        row2 = re.split('([a-zA-Z]+)', assign2)
        name2 = row2[-2] + row2[-1]

        # Get the residue number.
        try:
            res_num = int(row1[-3])
        except:
            raise RelaxError("Improperly formatted NMRPipe SeriesTab file., cannot process the assignment '%s'." % line[0])

        # Get the intensities.
        try:
            # Loop over the spectra.
            intensities = []
            for i in range(len(spectra)):
                # The intensity is given by column multiplication.
                intensities.append(float(line[spectra_i[i]])*float(line[5]))

        # Bad data.
        except ValueError:
            raise RelaxError("The peak intensity value %s from the line %s is invalid." % (intensity, line))

        # Add the assignment to the peak list object.
        peak_list.add(res_nums=[res_num, res_num], spin_names=[name1, name2], intensity=intensities, intensity_name=spectra)
