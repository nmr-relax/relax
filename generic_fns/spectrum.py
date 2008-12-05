###############################################################################
#                                                                             #
# Copyright (C) 2004, 2007-2008 Edward d'Auvergne                             #
# Copyright (C) 2008 Sebastien Morin                                          #
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
from math import sqrt
from re import split
import string
import sys
from warnings import warn

# relax module imports.
from generic_fns.mol_res_spin import count_spins, exists_mol_res_spin_data, generate_spin_id, generate_spin_id_data_array, return_spin, spin_loop
from generic_fns import pipes
from relax_errors import RelaxError, RelaxArgNotInListError, RelaxImplementError, RelaxNoSequenceError
from relax_io import extract_data, strip
from relax_warnings import RelaxWarning, RelaxNoSpinWarning


def __errors_height_no_repl():
    """Calculate the errors for peak heights when no spectra are replicated."""

    # Loop over the spins and set the error to the RMSD of the base plane noise.
    for spin, spin_id in spin_loop(return_id=True):
        # Skip deselected spins.
        if not spin.select:
            continue

        # Skip spins missing intensity data.
        if not hasattr(spin, 'intensities'):
            continue

        # Test if the RMSD has been set.
        if not hasattr(spin, 'baseplane_rmsd'):
            raise RelaxError, "The RMSD of the base plane noise for spin '%s' has not been set." % spin_id

        # Set the error to the RMSD.
        spin.intensity_err = spin.baseplane_rmsd


def __errors_repl(verbosity=0):
    """Calculate the errors for peak intensities from replicated spectra.

    @keyword verbosity: The amount of information to print.  The higher the value, the greater the
                        verbosity.
    @type verbosity:    int
    """

    # Get the current data pipe.
    cdp = pipes.get_pipe()

    # replicated spectra.
    repl = [False] * len(cdp.spectrum_ids)
    for i in xrange(len(cdp.replicates)):
        for j in xrange(len(cdp.replicates[i])):
            repl[cdp.spectrum_ids.index(cdp.replicates[i][j])] = True

    # Are all spectra replicated?
    all_repl = not (False in repl)
    if all_repl:
        print "All spectra replicated:  Yes."
    else:
        print "All spectra replicated:  No."


    # Test if the standard deviation has already been calculated.
    if hasattr(cdp, 'sigma_I'):
        raise RelaxError, "The peak intensity standard deviation of all spectra has already been calculated."

    # Initialise.
    cdp.sigma_I = [0.0] * len(cdp.spectrum_ids)
    cdp.var_I = [0.0] * len(cdp.spectrum_ids)

    # Loop over the spectra.
    for i in xrange(len(cdp.spectrum_ids)):
        # Skip non-replicated spectra.
        if not repl[i]:
            continue

        # Skip replicated spectra which already have been used.
        if cdp.var_I[i] != 0.0:
            continue

        # The replicated spectra.
        for j in xrange(len(cdp.replicates)):
            if cdp.spectrum_ids[i] in cdp.replicates[j]:
                spectra = cdp.replicates[j]

        # Number of spectra.
        num_spectra = len(spectra)

        # Indices of the spectra.
        indices = [None] * num_spectra
        for j in xrange(num_spectra):
            indices[j] = cdp.spectrum_ids.index(spectra[j])

        # Print out.
        print "\nReplicated spectra:  " + `spectra`
        if verbosity:
            print "%-5s%-6s%-20s%-20s" % ("Num", "Name", "Average", "SD")

        # Calculate the mean value.
        count = 0
        for spin in spin_loop():
            # Skip deselected spins.
            if not spin.select:
                continue

            # Skip and deselect spins which have no data.
            if not hasattr(spin, 'intensities'):
                spin.select = False
                continue

            # Average intensity.
            ave_intensity = 0.0
            for j in xrange(num_spectra):
                ave_intensity = ave_intensity + spin.intensities[indices[j]]
            ave_intensity = ave_intensity / num_spectra

            # Sum of squared errors.
            SSE = 0.0
            for j in xrange(num_spectra):
                SSE = SSE + (spin.intensities[indices[j]] - ave_intensity) ** 2

            # Variance.
            #
            #                   1
            #       sigma^2 = ----- * sum({Xi - Xav}^2)]
            #                 n - 1
            #
            var_I = 1.0 / (num_spectra - 1.0) * SSE

            # Print out.
            if verbosity:
                print "%-5i%-6s%-20s%-20s" % (spin.num, spin.name, `ave_intensity`, `var_I`)

            # Sum of variances (for average).
            cdp.var_I[indices[0]] = cdp.var_I[indices[0]] + var_I
            count = count + 1

        # Average variance.
        cdp.var_I[indices[0]] = cdp.var_I[indices[0]] / float(count)

        # Set all spectra variances.
        for j in xrange(num_spectra):
            cdp.var_I[indices[j]] = cdp.var_I[indices[0]]

        # Print out.
        print "Standard deviation:  %s" % sqrt(cdp.var_I[indices[0]])


    # Average across all spectra if there are time points with a single spectrum.
    if not all_repl:
        # Print out.
        print "\nVariance averaging over all spectra."

        # Initialise.
        var_I = 0.0
        num_dups = 0

        # Loop over all time points.
        for i in xrange(len(cdp.spectrum_ids)):
            # Single spectrum (or extraordinarily accurate NMR spectra!).
            if cdp.var_I[i] == 0.0:
                continue

            # Sum and count.
            var_I = var_I + cdp.var_I[i]
            num_dups = num_dups + 1

        # Average value.
        var_I = var_I / float(num_dups)

        # Assign the average value to all time points.
        for i in xrange(len(cdp.spectrum_ids)):
            cdp.var_I[i] = var_I

        # Print out.
        print "Standard deviation for all spins:  " + `sqrt(var_I)`

    # Loop over the spectra.
    for i in xrange(len(cdp.spectrum_ids)):
        # Create the standard deviation data structure.
        cdp.sigma_I[i] = sqrt(cdp.var_I[i])

    # Set the spin specific errors.
    for spin in spin_loop():
        # Skip deselected spins.
        if not spin.select:
            continue

        # Set the error.
        spin.intensity_err = cdp.sigma_I


def __errors_volume_no_repl():
    """Calculate the errors for peak volumes when no spectra are replicated."""

    # Loop over the spins and set the error to the RMSD of the base plane noise.
    for spin, spin_id in spin_loop(return_id=True):
        # Skip deselected spins.
        if not spin.select:
            continue

        # Skip spins missing intensity data.
        if not hasattr(spin, 'intensities'):
            continue

        # Test if the RMSD has been set.
        if not hasattr(spin, 'baseplane_rmsd'):
            raise RelaxError, "The RMSD of the base plane noise for spin '%s' has not been set." % spin_id

        # Test that the total number of points have been set.
        if not hasattr(spin, 'N'):
            raise RelaxError, "The total number of points used in the volume integration has not been specified for spin '%s'." % spin_id

        # Set the error to the RMSD multiplied by the square root of the total number of points.
        spin.intensity_err = spin.baseplane_rmsd * sqrt(spin.N)


def autodetect_format(file_data):
    """Automatically detect the format of the peak list.

    @param file_data:   The processed results file data.
    @type file_data:    list of lists of str
    """

    # The first header line.
    for line in file_data:
        if line != []:
            break

    # Generic format.
    if line[0] in ['mol_name', 'res_num', 'res_name', 'spin_num', 'spin_name'] or line[0] in ['Num', 'Name']:
        return 'generic'

    # Sparky format.
    if line[0] == 'Assignment':
        return 'sparky'

    # NMRView format.
    if line == ['label', 'dataset', 'sw', 'sf']:
        return 'nmrview'

    # XEasy format.
    if line == ['No.', 'Color', 'w1', 'w2', 'ass.', 'in', 'w1', 'ass.', 'in', 'w2', 'Volume', 'Vol.', 'Err.', 'Method', 'Comment']:
        return 'xeasy'

    # Unsupported format.
    raise RelaxError, "The format of the peak list file cannot be determined.  Either the file is of a non-standard format or the format is unsupported."


def baseplane_rmsd(error=0.0, spectrum_id=None, spin_id=None):
    """Set the peak intensity errors, as defined as the baseplane RMSD.

    @param error:           The peak intensity error value defined as the RMSD of the base plane
                            noise.
    @type error:            float
    @keyword spectrum_id:   The spectrum id.
    @type spectrum_id:      str
    @param spin_id:         The spin identification string.
    @type spin_id:          str
    """

    # Test if the current pipe exists
    pipes.test()

    # Test if the sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Get the current data pipe.
    cdp = pipes.get_pipe()

    # Test the spectrum id string.
    if spectrum_id not in cdp.spectrum_ids:
        raise RelaxError, "The peak intensities corresponding to the spectrum id '%s' do not exist." % spectrum_id

    # The spectrum id index.
    spect_index = cdp.spectrum_ids.index(spectrum_id)

    # Loop over the spins.
    for spin in spin_loop(spin_id):
        # Skip deselected spins.
        if not spin.select:
            continue

        # Initialise or update the baseplane_rmsd data structure as necessary.
        if not hasattr(spin, 'baseplane_rmsd'):
            spin.baseplane_rmsd = [None] * len(cdp.spectrum_ids)
        elif len(spin.baseplane_rmsd) < len(cdp.spectrum_ids):
            spin.baseplane_rmsd.append([None] * (len(cdp.spectrum_ids) - len(spin.baseplane_rmsd)))

        # Set the error.
        spin.baseplane_rmsd[spect_index] = float(error)


def det_dimensions(file_data, proton, heteronuc, int_col):
    """Determine which are the proton and heteronuclei dimensions of the XEasy text file.

    @return:    None
    """

    # Loop over the lines of the file until the proton and heteronucleus is reached.
    for i in xrange(len(file_data)):
        # Extract the data.
        w1_name, w2_name, spin_id, intensity = intensity_xeasy(file_data[i], int_col)

        # Proton in w1, heteronucleus in w2.
        if w1_name == proton and w2_name == heteronuc:
            # Set the proton dimension.
            H_dim = 'w1'

            # Print out.
            print "The proton dimension is w1"

            # Don't continue (waste of time).
            break

        # Heteronucleus in w1, proton in w2.
        if w1_name == heteronuc and w2_name == proton:
            # Set the proton dimension.
            H_dim = 'w2'

            # Print out.
            print "The proton dimension is w2"

            # Don't continue (waste of time).
            break


def error_analysis():
    """Determine the peak intensity standard deviation."""

    # Test if the current pipe exists
    pipes.test()

    # Test if the sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Get the current data pipe.
    cdp = pipes.get_pipe()

    # Test if spectra have been loaded.
    if not hasattr(cdp, 'spectrum_ids'):
        raise RelaxError, "Error analysis is not possible, no spectra have been loaded."

    # Peak height category.
    if cdp.int_method == 'height':
        # Print out.
        print "Intensity measure:  Peak heights."

        # Do we have replicated spectra?
        if hasattr(cdp, 'replicates'):
            # Print out.
            print "Replicated spectra:  Yes."

            # Set the errors.
            __errors_repl()

        # No replicated spectra.
        else:
            # Print out.
            print "Replicated spectra:  No."

            # Set the errors.
            __errors_height_no_repl()

    # Peak volume category.
    if cdp.int_method == 'volume':
        # Print out.
        print "Intensity measure:  Peak volumes."

        # Do we have replicated spectra?
        if hasattr(cdp, 'replicates'):
            # Print out.
            print "Replicated spectra:  Yes."
            raise RelaxImplementError

        # No replicated spectra.
        else:
            # Print out.
            print "Replicated spectra:  No."

            # Set the errors.
            __errors_repl()


def intensity_generic(line, int_col):
    """Function for returning relevant data from the generic peak intensity line.

    The residue number, heteronucleus and proton names, and peak intensity will be returned.


    @param line:        The single line of information from the intensity file.
    @type line:         list of str
    @keyword int_col:   The column containing the peak intensity data (for a non-standard formatted
                        file).
    @type int_col:      int
    @raises RelaxError: When the expected peak intensity is not a float.
    """

    # Determine the number of delays (and associated intensities).
    i = 6
    while 1:
        i = i + 1
        try:
            current_field = line[i-1]
        except:
            num_delays = int(i - 7)
            if num_delays == 0:
                raise RelaxError, "Generic file with no associated delays (and intensities)."
            break

    # The residue number.
    res_num = ''
    try:
        res_num = int(line[1])
    except:
        raise RelaxError, "Improperly formatted generic file."

    # Nuclei names.
    x_name = ''
    x_name = line[4]
    h_name = ''
    h_name = line[5]

    # Extract intensities.
    try:
        intensity = [float(line[6])]
    except ValueError:
        raise RelaxError, "The peak intensity value " + `intensity` + " from the line " + `line` + " is invalid."

    i = 1
    while i < num_delays:
        i = i + 1
        try:
            intensity.append(float(line[i + 5]))
        except ValueError:
            raise RelaxError, "The peak intensity value " + `intensity` + " from the line " + `line` + " is invalid."

    print ''
    print 'The following information was extracted from the intensity file (res_num, h_name, x_name, intensities).'
    print '    ' + `res_num`, h_name, x_name, intensity 

    # Generate the spin identification string.
    spin_id = generate_spin_id_data_array(data=line, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col)

    # Return the data.
    return h_name, x_name, spin_id, intensity


def intensity_nmrview(line, int_col):
    """Function for returning relevant data from the NMRView peak intensity line.

    The residue number, heteronucleus and proton names, and peak intensity will be returned.


    @param line:        The single line of information from the intensity file.
    @type line:         list of str
    @keyword int_col:   The column containing the peak intensity data. The default is 16 for
                        intensities. Setting the int_col argument to 15 will use the volumes (or
                        evolumes). For a non-standard formatted file, use a different value.
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
        int_col = 16
    if int_col == 16:
        print 'Using peak heights.'
    if int_col == 15:
        print 'Using peak volumes (or evolumes).'

    # Intensity.
    try:
        intensity = float(line[int_col])
    except ValueError:
        raise RelaxError, "The peak intensity value " + `intensity` + " from the line " + `line` + " is invalid."

    # Generate the spin_id.
    spin_id = generate_spin_id(res_num=res_num, spin_name=x_name)

    # Return the data.
    return h_name, x_name, spin_id, intensity


def intensity_sparky(line, int_col):
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

    # Generate the spin_id.
    spin_id = generate_spin_id(res_num=res_num, spin_name=x_name)

    # Return the data.
    return h_name, x_name, spin_id, intensity


def intensity_xeasy(line, int_col, H_dim='w1'):
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

    # Generate the spin_id.
    spin_id = generate_spin_id(res_num=res_num, spin_name=x_name)

    # Return the data.
    return h_name, x_name, spin_id, intensity


def number_of_header_lines(file_data, format, int_col, intensity):
    """Function for determining how many header lines are in the intensity file.

    @param file_data:   The processed results file data.
    @type file_data:    list of lists of str
    @param format:      The type of file containing peak intensities.  This can currently be one of
                        'generic', 'nmrview', 'sparky' or 'xeasy'.
    @type format:       str
    @param int_col:     The column containing the peak intensity data (for a non-standard
                        formatted file).
    @type int_col:      int
    @param intensity:   The intensity extraction function.
    @type intensity:    func
    @return:            The number of header lines.
    @rtype:             int
    """

    # Generic.
    ##########

    # Assume the generic file has two header lines!
    if format == 'generic':
        return 2

    # NMRView.
    ##########

    # Assume the NMRView file has six header lines!
    elif format == 'nmrview':
        return 6


    # Sparky.
    #########

    # Assume the Sparky file has two header lines!
    elif format == 'sparky':
        return 2


    # XEasy.
    ########

    # Loop over the lines of the file until a peak intensity value is reached.
    elif format == 'xeasy':
        header_lines = 0
        for i in xrange(len(file_data)):
            # Try to see if the intensity can be extracted.
            try:
                if int_col:
                    intensity(file_data[i], int_col)
                else:
                    intensity(file_data[i], int_col)
            except RelaxError:
                header_lines = header_lines + 1
            except IndexError:
                header_lines = header_lines + 1
            else:
                break

        # Return the number of lines.
        return header_lines


def read(file=None, dir=None, spectrum_id=None, heteronuc=None, proton=None, int_col=None, int_method=None, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None, sep=None):
    """Read the peak intensity data.

    @keyword file:          The name of the file containing the peak intensities.
    @type file:             str
    @keyword dir:           The directory where the file is located.
    @type dir:              str
    @keyword spectrum_id:   The spectrum identification string.
    @type spectrum_id:      str
    @keyword heteronuc:     The name of the heteronucleus as specified in the peak intensity
                            file.
    @type heteronuc:        str
    @keyword proton:        The name of the proton as specified in the peak intensity file.
    @type proton:           str
    @keyword int_col:       The column containing the peak intensity data (for a non-standard
                            formatted file).
    @type int_col:          int
    @keyword int_method:    The integration method, one of 'height', 'point sum' or 'other'.
    @type int_method:       str
    @param mol_name_col:    The column containing the molecule name information.
    @type mol_name_col:     int or None
    @param res_name_col:    The column containing the residue name information.
    @type res_name_col:     int or None
    @param res_num_col:     The column containing the residue number information.
    @type res_num_col:      int or None
    @param spin_name_col:   The column containing the spin name information.
    @type spin_name_col:    int or None
    @param spin_num_col:    The column containing the spin number information.
    @type spin_num_col:     int or None
    @param sep:             The column seperator which, if None, defaults to whitespace.
    @type sep:              str or None
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Get the current data pipe.
    cdp = pipes.get_pipe()

    # Test that the intensity measures are identical.
    if hasattr(cdp, 'int_method') and cdp.int_method != int_method:
        raise RelaxError, "The '%s' measure of peak intensities does not match '%s' of the previously loaded spectra." % (int_method, cdp.int_method)

    # Check the intensity measure.
    if not int_method in ['height', 'volume', 'other']:
        raise RelaxError, "The intensity measure '%s' is not one of 'height', 'volume', 'other'." % int_method

    # Set the peak intensity measure.
    cdp.int_method = int_method

    # Extract the data from the file.
    file_data = extract_data(file, dir, sep=sep)

    # Automatic format detection.
    format = autodetect_format(file_data)

    # Generic.
    if format == 'generic':
        # Print out.
        print "Generic formatted data file.\n"

        # Set the intensity reading function.
        intensity_fn = intensity_generic

    # NMRView.
    elif format == 'nmrview':
        # Print out.
        print "NMRView formatted data file.\n"

        # Set the intensity reading function.
        intensity_fn = intensity_nmrview

    # Sparky.
    elif format == 'sparky':
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
        intensity_fn = intensity_xeasy

    # Determine the number of header lines.
    num = number_of_header_lines(file_data, format, int_col, intensity_fn)
    print "Number of header lines found: " + `num`

    # Remove the header.
    file_data = file_data[num:]

    # Strip the data.
    file_data = strip(file_data)

    # Determine the proton and heteronucleus dimensions in the XEasy text file.
    if format == 'xeasy':
        det_dimensions(file_data=file_data, proton=proton, heteronuc=heteronuc, int_col=int_col)

    # Add the spectrum id to the relax data store.
    if not hasattr(cdp, 'spectrum_ids'):
        cdp.spectrum_ids = []
    if spectrum_id in cdp.spectrum_ids:
        raise RelaxError, "The spectrum identification string '%s' already exists." % spectrum_id
    else:
        cdp.spectrum_ids.append(spectrum_id)

    # Loop over the peak intensity data.
    for i in xrange(len(file_data)):
        # Extract the data.
        H_name, X_name, spin_id, intensity = intensity_fn(file_data[i], int_col)

        # Skip data.
        if X_name != heteronuc or H_name != proton:
            warn(RelaxWarning("Proton and heteronucleus names do not match, skipping the data %s." % `file_data[i]`))
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
            spin.intensities = []

        # Add the data.
        if format == 'generic':
            spin.intensities = intensity
        else:
            spin.intensities.append(intensity)


def replicated(spectrum_ids=None):
    """Set which spectra are replicates.

    @keyword spectrum_ids:  A list of spectrum ids corresponding to replicated spectra.
    @type spectrum_ids:     list of str
    """

    # Test if the current pipe exists
    pipes.test()

    # Get the current data pipe.
    cdp = pipes.get_pipe()

    # Test if spectra have been loaded.
    if not hasattr(cdp, 'spectrum_ids'):
        raise RelaxError, "No spectra have been loaded therefore replicates cannot be specified."

    # Test the spectrum id strings.
    for spectrum_id in spectrum_ids:
        if spectrum_id not in cdp.spectrum_ids:
            raise RelaxError, "The peak intensities corresponding to the spectrum id '%s' do not exist." % spectrum_id

    # Initialise.
    if not hasattr(cdp, 'replicates'):
        cdp.replicates = []

    # Check if the spectrum id is already in the list.
    for i in xrange(len(cdp.replicates)):
        found = False
        for j in xrange(len(spectrum_ids)):
            if spectrum_ids[j] in cdp.replicates[i]:
                found = True
                spectrum_ids.pop(j)

        # Add the remaining replicates to the list and quit this function.
        if found:
            cdp.replicates[i] = cdp.replicates[i] + spectrum_ids
            return

    # Set the replicates.
    cdp.replicates.append(spectrum_ids)
