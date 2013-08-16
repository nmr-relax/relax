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
"""Module containing functions for the handling of peak intensities."""


# Python module imports.
import sys
from warnings import warn

# relax module imports.
from lib.errors import RelaxError
from lib.io import extract_data, read_spin_data, strip, write_data
from lib.software import nmrpipe, nmrview, sparky, xeasy
from lib.spectrum.objects import Peak_list
from lib.warnings import RelaxWarning, RelaxNoSpinWarning
from pipe_control.mol_res_spin import generate_spin_id_unique, return_spin


def autodetect_format(file_data):
    """Automatically detect the format of the peak list.

    @param file_data:   The processed results file data.
    @type file_data:    list of lists of str
    """

    # The first header line.
    for line in file_data:
        if line != []:
            break

    # Sparky format.
    if line[0] == 'Assignment':
        return 'sparky'

    # NMRView format.
    if line == ['label', 'dataset', 'sw', 'sf']:
        return 'nmrview'

    # NMRPipe SeriesTab.
    if line[0] == 'REMARK' and line[1] == 'SeriesTab':
        return 'seriestab'

    # XEasy format.
    if line == ['No.', 'Color', 'w1', 'w2', 'ass.', 'in', 'w1', 'ass.', 'in', 'w2', 'Volume', 'Vol.', 'Err.', 'Method', 'Comment']:
        return 'xeasy'

    # Assume a generic format.
    return 'generic'


def intensity_generic(peak_list=None, file_data=None, spin_id_col=None, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None, data_col=None, sep=None, spin_id=None):
    """Extract the peak intensity information from the generic column formatted peak list.

    @keyword peak_list:     The peak list object to place all data into.
    @type peak_list:        lib.spectrum.objects.Peak_list instance
    @keyword file_data:     The data extracted from the file converted into a list of lists.
    @type file_data:        list of lists of str
    @keyword spin_id_col:   The column containing the spin ID strings (used by the generic intensity file format).  If supplied, the mol_name_col, res_name_col, res_num_col, spin_name_col, and spin_num_col arguments must be none. @type spin_id_col:      int or None @keyword mol_name_col:  The column containing the molecule name information (used by the generic intensity file format).  If supplied, spin_id_col must be None.
    @type mol_name_col:     int or None
    @keyword res_name_col:  The column containing the residue name information (used by the generic intensity file format).  If supplied, spin_id_col must be None.
    @type res_name_col:     int or None
    @keyword res_num_col:   The column containing the residue number information (used by the generic intensity file format).  If supplied, spin_id_col must be None.
    @type res_num_col:      int or None
    @keyword spin_name_col: The column containing the spin name information (used by the generic intensity file format).  If supplied, spin_id_col must be None.
    @type spin_name_col:    int or None
    @keyword spin_num_col:  The column containing the spin number information (used by the generic intensity file format).  If supplied, spin_id_col must be None.
    @type spin_num_col:     int or None
    @keyword data_col:      The column containing the peak intensities.
    @type data_col:         int or list of int
    @keyword sep:           The column separator which, if None, defaults to whitespace.
    @type sep:              str or None
    @keyword spin_id:       The spin ID string used to restrict data loading to a subset of all spins.
    @type spin_id:          None or str
    @raises RelaxError:     When the expected peak intensity is not a float.
    """

    # Check the intensity column argument.
    if data_col == None:
        raise RelaxError("The data column argument has not been supplied.")

    # Strip the data.
    file_data = strip(file_data)

    # Convert the the data_col argument to a list if needed.
    if not isinstance(data_col, list):
        data_col = [data_col]

    # Loop over the file data.
    for line in file_data:
        # Loop over the intensity columns, storing the data.
        intensity = []
        for i in range(len(data_col)):
            # Extract the data for the single line (loop of a single element).
            for values in read_spin_data(file_data=[line], spin_id_col=spin_id_col, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, data_col=data_col[i], sep=sep, spin_id=spin_id):
                # Check the values.
                if len(values) != 6:
                    raise RelaxError("The molecule name, residue number and name, spin number and name, and value columns could not be found in the data %s." % repr(values))

                # Unpack.
                mol_name, res_num, res_name, spin_num, spin_name, value = values

                # Store the intensity.
                intensity.append(value)

        # Add the assignment to the peak list object.
        peak_list.add(mol_names=[mol_name, mol_name], res_nums=[res_num, res_num], res_names=[res_name, res_name], spin_nums=[spin_num, spin_num], spin_names=[spin_name, spin_name], intensity=intensity)


def read_peak_list(file=None, dir=None, int_col=None, spin_id_col=None, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None, sep=None, spin_id=None):
    """Read the peak intensity data.

    @keyword file:          The name of the file containing the peak intensities.
    @type file:             str
    @keyword dir:           The directory where the file is located.
    @type dir:              str
    @keyword int_col:       The column containing the peak intensity data.  If set to None, no intensity data will be returned.
    @type int_col:          None or int
    @keyword spin_id_col:   The column containing the spin ID strings (used by the generic intensity file format).  If supplied, the mol_name_col, res_name_col, res_num_col, spin_name_col, and spin_num_col arguments must be none.
    @type spin_id_col:      int or None
    @keyword mol_name_col:  The column containing the molecule name information (used by the generic intensity file format).  If supplied, spin_id_col must be None.
    @type mol_name_col:     int or None
    @keyword res_name_col:  The column containing the residue name information (used by the generic intensity file format).  If supplied, spin_id_col must be None.
    @type res_name_col:     int or None
    @keyword res_num_col:   The column containing the residue number information (used by the generic intensity file format).  If supplied, spin_id_col must be None.
    @type res_num_col:      int or None
    @keyword spin_name_col: The column containing the spin name information (used by the generic intensity file format).  If supplied, spin_id_col must be None.
    @type spin_name_col:    int or None
    @keyword spin_num_col:  The column containing the spin number information (used by the generic intensity file format).  If supplied, spin_id_col must be None.
    @type spin_num_col:     int or None
    @keyword sep:           The column separator which, if None, defaults to whitespace.
    @type sep:              str or None
    @keyword spin_id:       The spin ID string used to restrict data loading to a subset of all spins.
    @type spin_id:          None or str
    @return:                The peak list object containing all relevant data in the peak list.
    @rtype:                 lib.spectrum.objects.Peak_list instance
    """

    # Extract the data from the file.
    file_data = extract_data(file, dir, sep=sep)

    # Initialise the peak list object.
    peak_list = Peak_list()

    # Automatic format detection.
    format = autodetect_format(file_data)

    # Generic.
    if format == 'generic':
        # Print out.
        print("Generic formatted data file.\n")

        # Extract the data.
        intensity_generic(peak_list=peak_list, file_data=file_data, spin_id_col=spin_id_col, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, data_col=int_col, sep=sep, spin_id=spin_id)

    # NMRView.
    elif format == 'nmrview':
        # Print out.
        print("NMRView formatted data file.\n")

        # Extract the data.
        nmrview.read_list_intensity(peak_list=peak_list, file_data=file_data)

    # NMRPipe SeriesTab.
    elif format == 'seriestab':
        # Print out.
        print("NMRPipe SeriesTab formatted data file.\n")

        # Extract the data.
        nmrpipe.read_list_intensity_seriestab(peak_list=peak_list, file_data=file_data, int_col=int_col, int_col_labels=int_col_labels)

        # Extract the expected number of spectrum ID's.
        nr_int_col = len(peak_list[0].intensity)

        # Make it possible to autogenerate spectrum ID's, if spectrum_id='auto'.
        if not isinstance(spectrum_id, list) and spectrum_id.lower() == 'auto':
            spectrum_id = []
            for i in range(nr_int_col):
                spectrum_id.append('Z_A%s'%i)

    # Sparky.
    elif format == 'sparky':
        # Print out.
        print("Sparky formatted data file.\n")

        # Extract the data.
        sparky.read_list_intensity(peak_list=peak_list, file_data=file_data, int_col=int_col)

    # XEasy.
    elif format == 'xeasy':
        # Print out.
        print("XEasy formatted data file.\n")

        # Extract the data.
        xeasy.read_list_intensity(peak_list=peak_list, file_data=file_data, int_col=int_col)

    # Return the peak list object.
    return peak_list
