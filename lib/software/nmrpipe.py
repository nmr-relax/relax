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


def read_list_intensity_seriestab(file_data=None, int_col=None):
    """Return the peak intensity information from the NMRPipe SeriesTab peak intensity file.

    The residue number, heteronucleus and proton names, and peak intensity will be returned.


    @keyword file_data: The data extracted from the file converted into a list of lists.
    @type file_data:    list of lists of str
    @keyword int_col:  The column which to multiply the peak intensity data (used by the SeriesTab intensity file format).
    @type int_col:     int
    @raises RelaxError: When the expected peak intensity is not a float.
    @return:            The extracted data as a list of lists.  The first dimension corresponds to the spin.  The second dimension consists of the proton name, heteronucleus name, residue number, the intensity value, and the original line of text.
    @rtype:             list of lists of str, str, int, float, str
    """

    # Set start variables
    modeline = False
    mode = False
    varsline = False
    header = False

    # Loop over lines, to extract variables and find header size
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

    # Raise RelaxError, if the MODE is not found
    if not (modeline and mode):
        raise RelaxError("MODE not detected. Expecting line 2:\nREMARK Mode: Summation")

    # Raise RelaxError, if the VARS line is not found
    if not (varsline):
        raise RelaxError("VARS not detected. Expecting line 8:\nVARS INDEX X_AXIS Y_AXIS X_PPM Y_PPM VOL ASS Z_A0")

    # Raise RelaxError, if the header size is not found
    if not header:
        raise RelaxError("'1' not detected in start of line. Cannot determine header size.")

    # Find index of assignment ASS
    ass_i = varsline.index('ASS')

    # Make a regular search for Z_A entries
    Z_A = re.compile("Z_A*")
    spectra = filter(Z_A.search, varsline)

    # Find index of Z_A entries
    spectra_i = [[x for x in varsline].index(y) for y in spectra]

    # Remove the header.
    file_data = file_data[header:]

    # Define a list, for storing all the data
    data_all = []

    # Define a current counter
    i = 0

    # Loop over the spectra
    for spectrum in spectra:
        # Define a list, for storing the current spectrum data
        data = []

        # Current intensity index
        int_i = spectra_i[i]

        for line in file_data:
            # Skip non-assigned peaks.
            if line[ass_i] == '?-?':
                continue

            # First split by the 2D separator.
            x_assign, h_assign = re.split('-', line[ass_i])

            # The proton info.
            h_row = re.split('([A-Z]+)', h_assign)
            h_name = h_row[-2] + h_row[-1]

            # The heteronucleus info.
            x_row = re.split('([A-Z]+)', x_assign)
            x_name = x_row[-2] + x_row[-1]

            # The residue number.
            try:
                res_num = int(x_row[-3])
            except:
                raise RelaxError("Improperly formatted NMRPipe SeriesTab file.")

            # Intensity.
            try:
                intensity = float(line[int_i])*float(line[5])
            except ValueError:
                raise RelaxError("The peak intensity value %s from the line %s is invalid."%(intensity,line))

            # Append the data.
            data.append([h_name, x_name, res_num, intensity])

        # Append to all data
        data_all.append([data,spectrum])

        # Add 1 to counter
        i += 1
    # Return the data.
    return data_all
