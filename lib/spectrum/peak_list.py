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


def intensity_generic(file_data=None, spin_id_col=None, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None, data_col=None, sep=None, spin_id=None):
    """Return the process data from the generic peak intensity file.

    The residue number, heteronucleus and proton names, and peak intensity will be returned.


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
    @return:                The extracted data as a list of lists.  The first dimension corresponds to the spin.  The second dimension consists of the proton name, heteronucleus name, spin ID string, and the intensity value.
    @rtype:                 list of lists of str, str, str, float
    """

    # Check the intensity column argument.
    if data_col == None:
        raise RelaxError("The data column argument has not been supplied.")

    # Strip the data.
    file_data = strip(file_data)

    # Convert the the data_col argument to a list if needed.
    if not isinstance(data_col, list):
        data_col = [data_col]

    # Loop over the data columns.
    data = []
    for i in range(len(data_col)):
        # Loop over the data.
        row_index = 0
        for values in read_spin_data(file_data=file_data, spin_id_col=spin_id_col, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, data_col=data_col[i], sep=sep, spin_id=spin_id):
            # Check the values.
            if len(values) != 6:
                raise RelaxError("The molecule name, residue number and name, spin number and name, and value columns could not be found in the data %s." % repr(values))

            # Unpack.
            mol_name, res_num, res_name, spin_num, spin_name, value = values

            # Create the unique spin ID.
            id = generate_spin_id_unique(mol_name=mol_name, res_num=res_num, res_name=res_name, spin_num=spin_num, spin_name=spin_name)

            # Store the necessary data.
            if i == 0:
                # Convert the value to a list if multiple columns are present.
                if len(data_col) > 1:
                    data.append([None, None, id, [value], id])
                else:
                    data.append([None, None, id, value, id])
            else:
                data[row_index][3].append(value)

            # Go to the next row.
            row_index += 1

    # Return the data.
    return data


def read(file=None, dir=None, spectrum_id=None, heteronuc=None, proton=None, int_col=None, int_method=None, spin_id_col=None, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None, sep=None, spin_id=None, ncproc=None, verbose=True):
    """Read the peak intensity data.

    @keyword file:          The name of the file containing the peak intensities.
    @type file:             str
    @keyword dir:           The directory where the file is located.
    @type dir:              str
    @keyword spectrum_id:   The spectrum identification string.
    @type spectrum_id:      str or list of str
    @keyword heteronuc:     The name of the heteronucleus as specified in the peak intensity file.
    @type heteronuc:        str
    @keyword proton:        The name of the proton as specified in the peak intensity file.
    @type proton:           str
    @keyword int_col:       The column containing the peak intensity data (used by the generic intensity file format).
    @type int_col:          int
    @keyword int_method:    The integration method, one of 'height', 'point sum' or 'other'.
    @type int_method:       str
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
    @keyword spin_id:       The spin ID string used to restrict data loading to a subset of all spins.  If 'auto' is provided for a NMRPipe seriesTab formatted file, the ID's are auto generated in form of Z_Ai.
    @type spin_id:          None or str
    @keyword ncproc:        The Bruker ncproc binary intensity scaling factor.
    @type ncproc:           int or None
    @keyword verbose:       A flag which if True will cause all relaxation data loaded to be printed out.
    @type verbose:          bool
    """

    # Check the file name.
    if file == None:
        raise RelaxError("The file name must be supplied.")

    # Test that the intensity measures are identical.
    if hasattr(cdp, 'int_method') and cdp.int_method != int_method:
        raise RelaxError("The '%s' measure of peak intensities does not match '%s' of the previously loaded spectra." % (int_method, cdp.int_method))

    # Check the intensity measure.
    if not int_method in ['height', 'point sum', 'other']:
        raise RelaxError("The intensity measure '%s' is not one of 'height', 'point sum', 'other'." % int_method)

    # Set the peak intensity measure.
    cdp.int_method = int_method

    # Extract the data from the file.
    file_data = extract_data(file, dir, sep=sep)

    # Automatic format detection.
    format = autodetect_format(file_data)

    # Generic.
    if format == 'generic':
        # Print out.
        print("Generic formatted data file.\n")

        # Checks.
        if isinstance(spectrum_id, list) and not isinstance(int_col, list):
            raise RelaxError("If a list of spectrum IDs is supplied, the intensity column argument must also be a list of equal length.")
        if not isinstance(spectrum_id, list) and isinstance(int_col, list):
            raise RelaxError("If a list of intensity columns is supplied, the spectrum ID argument must also be a list of equal length.")
        if isinstance(spectrum_id, list) and len(spectrum_id) != len(int_col):
            raise RelaxError("The spectrum ID list %s has a different number of elements to the intensity column list %s." % (spectrum_id, int_col))

        # Extract the data.
        intensity_data = intensity_generic(file_data=file_data, spin_id_col=spin_id_col, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, data_col=int_col, sep=sep, spin_id=spin_id)

    # NMRView.
    elif format == 'nmrview':
        # Print out.
        print("NMRView formatted data file.\n")

        # Extract the data.
        intensity_data = nmrview.read_list_intensity(file_data=file_data)

        # Convert the residue number to a spin ID.
        for i in range(len(intensity_data)):
            # Generate the spin_id.
            spin_id = generate_spin_id_unique(res_num=intensity_data[i][2], spin_name=intensity_data[i][1])

            # Replace the data.
            intensity_data[i][2] = spin_id

    # NMRPipe SeriesTab.
    elif format == 'seriestab':
        # Print out.
        print("NMRPipe SeriesTab formatted data file.\n")

        # Extract the data.
        intensity_data = nmrpipe.read_list_intensity_seriestab(file_data=file_data, int_col=int_col)

        # Extract the expected number of spectrum ID's.
        nr_int_col = len(intensity_data[0][3])

        # Make it possible to autogenerate spectrum ID's, if spectrum_id='auto'.
        if not isinstance(spectrum_id, list) and spectrum_id.lower() == 'auto':
            spectrum_id = []
            for i in range(nr_int_col):
                spectrum_id.append('Z_A%s'%i)

        # Convert the residue number to a spin ID.
        for i in range(len(intensity_data)):
            # Generate the spin_id.
            spin_id = generate_spin_id_unique(res_num=intensity_data[i][2], spin_name=intensity_data[i][1])

            # Replace the data.
            intensity_data[i][2] = spin_id

    # Sparky.
    elif format == 'sparky':
        # Print out.
        print("Sparky formatted data file.\n")

        # Extract the data.
        intensity_data = sparky.read_list_intensity(file_data=file_data, int_col=int_col)

        # Convert the residue number to a spin ID.
        for i in range(len(intensity_data)):
            # Generate the spin_id.
            spin_id = generate_spin_id_unique(res_num=intensity_data[i][2], spin_name=intensity_data[i][1])

            # Replace the data.
            intensity_data[i][2] = spin_id

    # XEasy.
    elif format == 'xeasy':
        # Print out.
        print("XEasy formatted data file.\n")

        # Extract the data.
        intensity_data = xeasy.read_list_intensity(file_data=file_data, proton=proton, heteronuc=heteronuc, int_col=int_col)

        # Convert the residue number to a spin ID.
        for i in range(len(intensity_data)):
            # Generate the spin_id.
            spin_id = generate_spin_id_unique(res_num=intensity_data[i][2], spin_name=intensity_data[i][1])

            # Replace the data.
            intensity_data[i][2] = spin_id

    # Loop over the peak intensity data.
    data = []
    data_flag = False

    for i in range(len(intensity_data)):
        # Extract the data.
        H_name, X_name, spin_id, intensity, line = intensity_data[i]

        # Convert the intensity data and spectrum IDs to lists if needed.
        if not isinstance(intensity, list):
            intensity = [intensity]
        if not isinstance(spectrum_id, list):
            spectrum_id = [spectrum_id]

        # Checks for matching length of spectrum IDs and intensities columns.
        if len(spectrum_id) != len(intensity):
            raise RelaxError("The spectrum ID list %s has a different number of elements to the intensity column list %s." % (spectrum_id, nr_int_col))

        # Loop over the data.
        for i in range(len(intensity)):
            # Sanity check.
            if intensity[i] == 0.0:
                warn(RelaxWarning("A peak intensity of zero has been encountered for the spin '%s' - this could be fatal later on." % spin_id))

            # Skip data.
            if (X_name and X_name != heteronuc) or (H_name and H_name != proton):
                warn(RelaxWarning("Proton and heteronucleus names do not match, skipping the data %s." % line))
                continue

            # Get the spin container.
            spin = return_spin(spin_id)
            if not spin:
                warn(RelaxNoSpinWarning(spin_id))
                continue

            # Skip deselected spins.
            if not spin.select:
                continue

            # Initialise.
            if not hasattr(spin, 'intensities'):
                spin.intensities = {}

            # Intensity scaling.
            if ncproc != None:
                intensity[i] = intensity[i] / float(2**ncproc)

            # Add the data.
            spin.intensities[spectrum_id[i]] = intensity[i]

            # Switch the flag.
            data_flag = True

            # Append the data for printing out.
            data.append([spin_id, repr(intensity[i])])

    # Add the spectrum id (and ncproc) to the relax data store.
    spectrum_ids = spectrum_id
    if isinstance(spectrum_id, str):
        spectrum_ids = [spectrum_id]
    if not hasattr(cdp, 'spectrum_ids'):
        cdp.spectrum_ids = []
        if ncproc != None:
            cdp.ncproc = {}
    for i in range(len(spectrum_ids)):
        if not spectrum_ids[i] in cdp.spectrum_ids:
            cdp.spectrum_ids.append(spectrum_ids[i])
            if ncproc != None:
                cdp.ncproc[spectrum_ids[i]] = ncproc

    # No data.
    if not data_flag:
        # Delete all the data.
        delete(spectrum_id)

        # Raise the error.
        raise RelaxError("No data could be loaded from the peak list")

    # Print out.
    if verbose:
        print("\nThe following intensities have been loaded into the relax data store:\n")
        write_data(out=sys.stdout, headings=["Spin_ID", "Intensity"], data=data)
