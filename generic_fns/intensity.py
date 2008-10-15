###############################################################################
#                                                                             #
# Copyright (C) 2004, 2007-2008 Edward d'Auvergne                             #
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
"""Module containing functions for the handling of peak intensities."""


# Python module imports.
from re import split
from warnings import warn
import string
import sys

# relax module imports.
from generic_fns.mol_res_spin import exists_mol_res_spin_data, generate_spin_id, return_spin
from generic_fns import pipes
from relax_errors import RelaxError, RelaxArgNotInListError, RelaxNoSequenceError
from relax_io import extract_data, strip
from relax_warnings import RelaxWarning, RelaxNoSpinWarning


def det_dimensions():
    """Determine which are the proton and heteronuclei dimensions of the XEasy text file.

    @return:    None
    """

    # Loop over the lines of the file until the proton and heteronucleus is reached.
    for i in xrange(len(self.file_data)):
        # Extract the data.
        res_num, w1_name, w2_name, intensity = self.intensity(self.file_data[i])

        # Proton in w1, heteronucleus in w2.
        if w1_name == self.proton and w2_name == self.heteronuc:
            # Set the proton dimension.
            self.H_dim = 'w1'

            # Print out.
            print "The proton dimension is w1"

            # Don't continue (waste of time).
            break

        # Heteronucleus in w1, proton in w2.
        if w1_name == self.heteronuc and w2_name == self.proton:
            # Set the proton dimension.
            self.H_dim = 'w2'

            # Print out.
            print "The proton dimension is w2"

            # Don't continue (waste of time).
            break


def intensity_sparky(line, int_col=None):
    """Function for returning relevant data from the Sparky peak intensity line.

    The residue number, heteronucleus and proton names, and peak intensity will be returned.


    @param line:        The single line of information from the intensity file.
    @type line:         list of str
    @keyword int_col:   The column containing the peak intensity data (for a non-standard formatted
                        file).
    @type int_col:      int
    @raises RelaxError: When the expected peak intensity is not a float.
    """


    # The Sparky assignment.
    assignment = ''
    res_num = ''
    h_name = ''
    x_name = ''
    intensity = ''
    if line[0]!='?-?':
        assignment = split('([A-Z]+)', line[0])
        assignment = assignment[1:-1]

    # The residue number.
        try:
            res_num = int(assignment[1])
        except:
            raise RelaxError, "Improperly formatted Sparky file."

    # Nuclei names.
        x_name = assignment[2]
        h_name = assignment[4]

    # The peak intensity column.
        if int_col == None:
            int_col = 3

    # Intensity.
        try:
            intensity = float(line[int_col])
        except ValueError:
            raise RelaxError, "The peak intensity value " + `intensity` + " from the line " + `line` + " is invalid."

    # Return the data.
    return res_num, h_name, x_name, intensity


def intensity_xeasy(line, int_col=None):
    """Function for returning relevant data from the XEasy peak intensity line.

    The residue number, heteronucleus and proton names, and peak intensity will be returned.


    @param line:        The single line of information from the intensity file.
    @type line:         list of str
    @keyword int_col:   The column containing the peak intensity data (for a non-standard formatted
                        file).
    @type int_col:      int
    @raises RelaxError: When the expected peak intensity is not a float.
    """

    # Test for invalid assignment lines which have the column numbers changed and return empty data.
    if line[4] == 'inv.':
        return None, None, None, 0.0

    # The residue number.
    try:
        res_num = int(line[5])
    except:
        raise RelaxError, "Improperly formatted XEasy file."

    # Nuclei names.
    if H_dim == 'w1':
        h_name = line[4]
        x_name = line[7]
    else:
        x_name = line[4]
        h_name = line[7]

    # The peak intensity column.
    if int_col == None:
        int_col = 10

    # Intensity.
    try:
        intensity = float(line[int_col])
    except ValueError:
        raise RelaxError, "The peak intensity value " + `intensity` + " from the line " + `line` + " is invalid."

    # Return the data.
    return res_num, h_name, x_name, intensity


def intensity_nmrview(line, int_col=None):
    """Function for returning relevant data from the NMRView peak intensity line.

    The residue number, heteronucleus and proton names, and peak intensity will be returned.


    @param line:        The single line of information from the intensity file.
    @type line:         list of str
    @keyword int_col:   The column containing the peak intensity data (for a non-standard formatted
                        file).
    @type int_col:      int
    @raises RelaxError: When the expected peak intensity is not a float.
    """

    # The residue number
    res_num = ''
    try:
        res_num = string.strip(line[1],'{')
        res_num = string.strip(res_num,'}')
        res_num = string.split(res_num,'.')
        res_num = res_num[0]
    except ValueError:
        raise RelaxError, "The peak list is invalid."

    # Nuclei names.
    x_name = ''
    if line[8]!='{}':
        x_name = string.strip(line[8],'{')
        x_name = string.strip(x_name,'}')
        x_name = string.split(x_name,'.')
        x_name = x_name[1]
    h_name = ''
    if line[1]!='{}':
        h_name = string.strip(line[1],'{')
        h_name = string.strip(h_name,'}')
        h_name = string.split(h_name,'.')
        h_name = h_name[1]

    # The peak intensity column.
    if int_col == None:
        int_col = 15

    # Intensity.
    try:
        intensity = float(line[int_col])
    except ValueError:
        raise RelaxError, "The peak intensity value " + `intensity` + " from the line " + `line` + " is invalid."

    # Return the data.
    return res_num, h_name, x_name, intensity


def number_of_header_lines(file_data, format, int_col, intensity):
    """Function for determining how many header lines are in the intensity file.

    @param file_data:   The processed results file data.
    @type file_data:    list of lists of str
    @param format:      The type of file containing peak intensities.  This can currently be one of
                        'sparky', 'xeasy' or 'nmrview'.
    @type format:       str
    @param int_col:     The column containing the peak intensity data (for a non-standard
                        formatted file).
    @type int_col:      int
    @param intensity:   The intensity extraction function.
    @type intensity:    func
    @return:            The number of header lines.
    @rtype:             int
    """

    # Sparky.
    #########

    # Assume the Sparky file has two header lines!
    if format == 'sparky':
        return 2


    # XEasy.
    ########

    # Loop over the lines of the file until a peak intensity value is reached.
    if format == 'xeasy':
        header_lines = 0
        for i in xrange(len(file_data)):
            # Try to see if the intensity can be extracted.
            try:
                if int_col:
                    intensity(file_data[i], int_col)
                else:
                    intensity(file_data[i])
            except RelaxError:
                header_lines = header_lines + 1
            except IndexError:
                header_lines = header_lines + 1
            else:
                break

        # Return the number of lines.
        return header_lines


    # NMRView.
    ##########

    # Assume the NMRView file has six header lines!
    elif format == 'nmrview':
        return 6


def read(file=None, dir=None, format=None, heteronuc=None, proton=None, int_col=None, assign_func=None, spectrum_type=None):
    """Read the peak intensity data.

    @keyword file:          The name of the file containing the peak intensities.
    @type file:             str
    @keyword dir:           The directory where the file is located.
    @type dir:              str
    @keyword format:        The type of file containing peak intensities.  This can currently be
                            one of 'sparky', 'xeasy' or 'nmrview'.
    @type format:           str
    @keyword heteronuc:     The name of the heteronucleus as specified in the peak intensity
                            file.
    @type heteronuc:        str
    @keyword proton:        The name of the proton as specified in the peak intensity file.
    @type proton:           str
    @keyword int_col:       The column containing the peak intensity data (for a non-standard
                            formatted file).
    @type int_col:          int
    @keyword assign_func:   A function used to place the intensity data within the spin container.
    @type assign_func:      func
    @keyword spectrum_type: The optional spectrum type to be sent back into assign_func().
    @type spectrum_type:    str
    """

    # Format argument.
    format_list = ['sparky', 'xeasy', 'nmrview']
    if format not in format_list:
        raise RelaxArgNotInListError, ('format', format, format_list)

    # Sparky.
    if format == 'sparky':
        # Print out.
        print "Sparky formatted data file.\n"

        # Set the intensity reading function.
        intensity_fn = intensity_sparky

    # XEasy.
    elif format == 'xeasy':
        # Print out.
        print "XEasy formatted data file.\n"

        # Set the default proton dimension.
        H_dim = 'w1'

        # Set the intensity reading function.
        intensity_fn = intensity_xeasy(H_dim)

    # NMRView.
    elif format == 'nmrview':
        # Print out.
        print "NMRView formatted data file.\n"

        # Set the intensity reading function.
        intensity_fn = intensity_nmrview

    # Test if the current data pipe exists.
    pipes.test()

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Extract the data from the file.
    file_data = extract_data(file, dir)

    # Determine the number of header lines.
    num = number_of_header_lines(file_data, format, int_col, intensity_fn)
    print "Number of header lines found: " + `num`

    # Remove the header.
    file_data = file_data[num:]

    # Strip the data.
    file_data = strip(file_data)

    # Determine the proton and heteronucleus dimensions in the XEasy text file.
    if format == 'xeasy':
        det_dimensions()

    # Loop over the peak intensity data.
    for i in xrange(len(file_data)):
        # Extract the data.
        res_num, H_name, X_name, intensity = intensity_fn(file_data[i])

        # Skip data.
        if X_name != heteronuc or H_name != proton:
            warn(RelaxWarning("Proton and heteronucleus names do not match, skipping the data %s: " % `file_data[i]`))
            continue

        # Get the spin container.
        spin_id = generate_spin_id(res_num=res_num, spin_name=X_name)
        spin = return_spin(spin_id)
        if not spin:
            warn(RelaxNoSpinWarning(spin_id))
            continue

        # Skip deselected spins.
        if not spin.select:
            continue

        # Assign the data.
        assign_func(spin=spin, intensity=intensity, spectrum_type=spectrum_type)
