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
from math import sqrt
import sys
from warnings import warn

# relax module imports.
from lib.errors import RelaxError, RelaxImplementError, RelaxNoSequenceError, RelaxNoSpectraError
from lib.io import write_data
from lib.software import nmrpipe, nmrview, sparky, xeasy
from lib.spectrum.peak_list import read_peak_list
from lib.warnings import RelaxWarning, RelaxNoSpinWarning
from pipe_control import pipes
from pipe_control.mol_res_spin import exists_mol_res_spin_data, generate_spin_id_unique, return_spin, spin_loop


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
            raise RelaxError("The RMSD of the base plane noise for spin '%s' has not been set." % spin_id)

        # Set the error to the RMSD.
        spin.intensity_err = spin.baseplane_rmsd


def __errors_repl(subset=None, verbosity=0):
    """Calculate the errors for peak intensities from replicated spectra.

    @keyword subset:    The list of spectrum ID strings to restrict the analysis to.
    @type subset:       list of str
    @keyword verbosity: The amount of information to print.  The higher the value, the greater the verbosity.
    @type verbosity:    int
    """

    # Replicated spectra.
    repl = replicated_flags()

    # Are all spectra replicated?
    if False in repl.values():
        all_repl = False
        print("All spectra replicated:  No.")
    else:
        all_repl = True
        print("All spectra replicated:  Yes.")

    # Initialise.
    if not hasattr(cdp, 'sigma_I'):
        cdp.sigma_I = {}
    if not hasattr(cdp, 'var_I'):
        cdp.var_I = {}

    # The subset.
    subset_flag = False
    if not subset:
        subset_flag = True
        subset = cdp.spectrum_ids

    # Loop over the spectra.
    for id in subset:
        # Skip non-replicated spectra.
        if not repl[id]:
            continue

        # Skip replicated spectra which already have been used.
        if id in cdp.var_I and cdp.var_I[id] != 0.0:
            continue

        # The replicated spectra.
        for j in range(len(cdp.replicates)):
            if id in cdp.replicates[j]:
                spectra = cdp.replicates[j]

        # Number of spectra.
        num_spectra = len(spectra)

        # Print out.
        print("\nReplicated spectra:  " + repr(spectra))
        if verbosity:
            print("%-5s%-6s%-20s%-20s" % ("Num", "Name", "Average", "SD"))

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

            # Missing data.
            missing = False
            for j in range(num_spectra):
                if not spectra[j] in spin.intensities:
                    missing = True
            if missing:
                continue

            # Average intensity.
            ave_intensity = 0.0
            for j in range(num_spectra):
                ave_intensity = ave_intensity + spin.intensities[spectra[j]]
            ave_intensity = ave_intensity / num_spectra

            # Sum of squared errors.
            SSE = 0.0
            for j in range(num_spectra):
                SSE = SSE + (spin.intensities[spectra[j]] - ave_intensity) ** 2

            # Variance.
            #
            #                   1
            #       sigma^2 = ----- * sum({Xi - Xav}^2)]
            #                 n - 1
            #
            var_I = 1.0 / (num_spectra - 1.0) * SSE

            # Print out.
            if verbosity:
                print("%-5i%-6s%-20s%-20s" % (spin.num, spin.name, repr(ave_intensity), repr(var_I)))

            # Sum of variances (for average).
            if not id in cdp.var_I:
                cdp.var_I[id] = 0.0
            cdp.var_I[id] = cdp.var_I[id] + var_I
            count = count + 1

        # No data catch.
        if not count:
            raise RelaxError("No data is present, unable to calculate errors from replicated spectra.")

        # Average variance.
        cdp.var_I[id] = cdp.var_I[id] / float(count)

        # Set all spectra variances.
        for j in range(num_spectra):
            cdp.var_I[spectra[j]] = cdp.var_I[id]

        # Print out.
        print("Standard deviation:  %s" % sqrt(cdp.var_I[id]))


    # Average across all spectra if there are time points with a single spectrum.
    if not all_repl:
        # Print out.
        if subset_flag:
            print("\nVariance averaging over the spectra subset.")
        else:
            print("\nVariance averaging over all spectra.")

        # Initialise.
        var_I = 0.0
        num_dups = 0

        # Loop over all time points.
        for id in cdp.var_I.keys():
            # Single spectrum (or extraordinarily accurate NMR spectra!).
            if cdp.var_I[id] == 0.0:
                continue

            # Sum and count.
            var_I = var_I + cdp.var_I[id]
            num_dups = num_dups + 1

        # Average value.
        var_I = var_I / float(num_dups)

        # Assign the average value to all time points.
        for id in subset:
            cdp.var_I[id] = var_I

        # Print out.
        print("Standard deviation for all spins:  " + repr(sqrt(var_I)))

    # Loop over the spectra.
    for id in cdp.var_I.keys():
        # Create the standard deviation data structure.
        cdp.sigma_I[id] = sqrt(cdp.var_I[id])

    # Set the spin specific errors.
    for spin in spin_loop():
        # Skip deselected spins.
        if not spin.select:
            continue

        # Set the error.
        spin.intensity_err = cdp.sigma_I


def __errors_volume_no_repl(subset=None):
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
            raise RelaxError("The RMSD of the base plane noise for spin '%s' has not been set." % spin_id)

        # Test that the total number of points have been set.
        if not hasattr(spin, 'N'):
            raise RelaxError("The total number of points used in the volume integration has not been specified for spin '%s'." % spin_id)

        # Set the error to the RMSD multiplied by the square root of the total number of points.
        for key in spin.intensity.keys():
            spin.intensity_err[key] = spin.baseplane_rmsd[key] * sqrt(spin.N)


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

    # Test the spectrum id string.
    if spectrum_id not in cdp.spectrum_ids:
        raise RelaxError("The peak intensities corresponding to the spectrum id '%s' do not exist." % spectrum_id)

    # The scaling by NC_proc.
    if hasattr(cdp, 'ncproc') and spectrum_id in cdp.ncproc:
        scale = 1.0 / 2**cdp.ncproc[spectrum_id]
    else:
        scale = 1.0

    # Loop over the spins.
    for spin in spin_loop(spin_id):
        # Skip deselected spins.
        if not spin.select:
            continue

        # Initialise or update the baseplane_rmsd data structure as necessary.
        if not hasattr(spin, 'baseplane_rmsd'):
            spin.baseplane_rmsd = {}

        # Set the error.
        spin.baseplane_rmsd[spectrum_id] = float(error) * scale


def delete(spectrum_id=None):
    """Delete spectral data corresponding to the spectrum ID.

    @keyword spectrum_id:   The spectrum ID string.
    @type spectrum_id:      str
    """

    # Test if the current pipe exists.
    pipes.test()

    # Test if the sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Test if data exists.
    if not hasattr(cdp, 'spectrum_ids') or spectrum_id not in cdp.spectrum_ids:
        raise RelaxNoSpectraError(spectrum_id)

    # Remove the ID.
    cdp.spectrum_ids.pop(cdp.spectrum_ids.index(spectrum_id))

    # The ncproc parameter.
    if hasattr(cdp, 'ncproc') and spectrum_id in cdp.ncproc:
        del cdp.ncproc[spectrum_id]

    # Replicates.
    if hasattr(cdp, 'replicates'):
        # Loop over the replicates.
        for i in range(len(cdp.replicates)):
            # The spectrum is replicated.
            if spectrum_id in cdp.replicates[i]:
                # Duplicate.
                if len(cdp.replicates[i]) == 2:
                    cdp.replicates.pop(i)

                # More than two spectra:
                else:
                    cdp.replicates[i].pop(cdp.replicates[i].index(spectrum_id))

                # No need to check further.
                break

    # Errors.
    if hasattr(cdp, 'sigma_I') and spectrum_id in cdp.sigma_I:
        del cdp.sigma_I[spectrum_id]
    if hasattr(cdp, 'var_I') and spectrum_id in cdp.var_I:
        del cdp.var_I[spectrum_id]

    # Loop over the spins.
    for spin in spin_loop():
        # Intensity data.
        if hasattr(spin, 'intensities') and spectrum_id in spin.intensities:
            del spin.intensities[spectrum_id]


def error_analysis(subset=None):
    """Determine the peak intensity standard deviation.

    @keyword subset:    The list of spectrum ID strings to restrict the analysis to.
    @type subset:       list of str
    """

    # Test if the current pipe exists
    pipes.test()

    # Test if the sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Test if spectra have been loaded.
    if not hasattr(cdp, 'spectrum_ids'):
        raise RelaxError("Error analysis is not possible, no spectra have been loaded.")

    # Check the IDs.
    if subset:
        for id in subset:
            if id not in cdp.spectrum_ids:
                raise RelaxError("The spectrum ID '%s' has not been loaded into relax." % id)

    # Peak height category.
    if cdp.int_method == 'height':
        # Print out.
        print("Intensity measure:  Peak heights.")

        # Do we have replicated spectra?
        if hasattr(cdp, 'replicates'):
            # Print out.
            print("Replicated spectra:  Yes.")

            # Set the errors.
            __errors_repl(subset=subset)

        # No replicated spectra.
        else:
            # Print out.
            print("Replicated spectra:  No.")
            if subset:
                print("Spectra ID subset ignored.")

            # Set the errors.
            __errors_height_no_repl()

    # Peak volume category.
    if cdp.int_method == 'point sum':
        # Print out.
        print("Intensity measure:  Peak volumes.")

        # Do we have replicated spectra?
        if hasattr(cdp, 'replicates'):
            # Print out.
            print("Replicated spectra:  Yes.")

            # Set the errors.
            __errors_repl(subset=subset)

        # No replicated spectra.
        else:
            # Print out.
            print("Replicated spectra:  No.")

            # No implemented.
            raise RelaxImplementError

            # Set the errors.
            __errors_vol_no_repl()


def get_ids():
    """Return a list of all spectrum IDs.

    @return:    The list of spectrum IDs.
    @rtype:     list of str
    """

    # No IDs.
    if not hasattr(cdp, 'spectrum_ids'):
        return []

    # Return the IDs.
    return cdp.spectrum_ids


def integration_points(N=0, spectrum_id=None, spin_id=None):
    """Set the number of integration points for the given spectrum.

    @param N:               The number of integration points.
    @type N:                int
    @keyword spectrum_id:   The spectrum ID string.
    @type spectrum_id:      str
    @keyword spin_id:       The spin ID string used to restrict the value to.
    @type spin_id:          None or str
    """

    raise RelaxImplementError


def read(file=None, dir=None, spectrum_id=None, dim=1, int_col=None, int_method=None, spin_id_col=None, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None, sep=None, spin_id=None, ncproc=None, verbose=True):
    """Read the peak intensity data.

    @keyword file:          The name of the file containing the peak intensities.
    @type file:             str
    @keyword dir:           The directory where the file is located.
    @type dir:              str
    @keyword spectrum_id:   The spectrum identification string.
    @type spectrum_id:      str or list of str
    @keyword dim:           The dimension of the peak list to associate the data with.
    @type dim:              int
    @keyword int_col:       The column containing the peak intensity data (used by the generic intensity file format).
    @type int_col:          int or list of int
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

    # Test if the current data pipe exists.
    pipes.test()

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Check the file name.
    if file == None:
        raise RelaxError("The file name must be supplied.")

    # Test that the intensity measures are identical.
    if hasattr(cdp, 'int_method') and cdp.int_method != int_method:
        raise RelaxError("The '%s' measure of peak intensities does not match '%s' of the previously loaded spectra." % (int_method, cdp.int_method))

    # Intensity column checks.
    if isinstance(spectrum_id, list) and not isinstance(int_col, list):
        raise RelaxError("If a list of spectrum IDs is supplied, the intensity column argument must also be a list of equal length.")
    if not isinstance(spectrum_id, list) and isinstance(int_col, list):
        raise RelaxError("If a list of intensity columns is supplied, the spectrum ID argument must also be a list of equal length.")
    if isinstance(spectrum_id, list) and len(spectrum_id) != len(int_col):
        raise RelaxError("The spectrum ID list %s has a different number of elements to the intensity column list %s." % (spectrum_id, int_col))

    # Check the intensity measure.
    if not int_method in ['height', 'point sum', 'other']:
        raise RelaxError("The intensity measure '%s' is not one of 'height', 'point sum', 'other'." % int_method)

    # Set the peak intensity measure.
    cdp.int_method = int_method

    # Read the peak list data.
    peak_list = read_peak_list(file=file, dir=dir, int_col=int_col, spin_id_col=spin_id_col, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, sep=sep, spin_id=spin_id)

    # Loop over the assignments.
    data = []
    data_flag = False
    for assign in peak_list:
        # Generate the spin_id.
        spin_id = generate_spin_id_unique(res_num=assign.res_nums[dim-1], spin_name=assign.spin_names[dim-1])

        # Convert the intensity data and spectrum IDs to lists if needed.
        intensity = assign.intensity
        if not isinstance(intensity, list):
            intensity = [intensity]
        if not isinstance(spectrum_id, list):
            spectrum_id = [spectrum_id]

        # Checks for matching length of spectrum IDs and intensities columns.
        if len(spectrum_id) != len(intensity):
            raise RelaxError("The spectrum ID list %s has a different number of elements to the intensity column list %s." % (spectrum_id, len(intensity)))

        # Loop over the intensity data.
        for i in range(len(intensity)):
            # Sanity check.
            if intensity[i] == 0.0:
                warn(RelaxWarning("A peak intensity of zero has been encountered for the spin '%s' - this could be fatal later on." % spin_id))

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



def replicated(spectrum_ids=None):
    """Set which spectra are replicates.

    @keyword spectrum_ids:  A list of spectrum ids corresponding to replicated spectra.
    @type spectrum_ids:     list of str
    """

    # Test if the current pipe exists
    pipes.test()

    # Test if spectra have been loaded.
    if not hasattr(cdp, 'spectrum_ids'):
        raise RelaxError("No spectra have been loaded therefore replicates cannot be specified.")

    # Test the spectrum id strings.
    for spectrum_id in spectrum_ids:
        if spectrum_id not in cdp.spectrum_ids:
            raise RelaxError("The peak intensities corresponding to the spectrum id '%s' do not exist." % spectrum_id)

    # Test for None.
    if spectrum_ids == None:
        warn(RelaxWarning("The spectrum ID list cannot be None."))
        return

    # Test for more than one element.
    if len(spectrum_ids) == 1:
        warn(RelaxWarning("The number of spectrum IDs in the list %s must be greater than one." % spectrum_ids))
        return

    # Initialise.
    if not hasattr(cdp, 'replicates'):
        cdp.replicates = []

    # Check if the spectrum IDs are already in the list.
    found = False
    for i in range(len(cdp.replicates)):
        # Loop over all elements of the first.
        for j in range(len(spectrum_ids)):
            if spectrum_ids[j] in cdp.replicates[i]:
                found = True

        # One of the spectrum IDs already have a replicate specified.
        if found:
            # Add the remaining replicates to the list and quit this function.
            for j in range(len(spectrum_ids)):
                if spectrum_ids[j] not in cdp.replicates[i]:
                    cdp.replicates[i].append(spectrum_ids[j])

            # Nothing more to do.
            return

    # A new set of replicates.
    cdp.replicates.append(spectrum_ids)


def replicated_flags():
    """Create and return a dictionary of flags of whether the spectrum is replicated or not.

    @return:    The dictionary of flags of whether the spectrum is replicated or not.
    @rtype:     dict of bool
    """

    # Initialise all IDs to false.
    repl = {}
    for id in cdp.spectrum_ids:
        repl[id] = False

    # Loop over the replicates.
    for i in range(len(cdp.replicates)):
        for j in range(len(cdp.replicates[i])):
            repl[cdp.replicates[i][j]] = True

    # Return the dictionary.
    return repl


def replicated_ids(spectrum_id):
    """Create and return a list of spectra ID which are replicates of the given ID.

    @param spectrum_id: The spectrum ID to find all the replicates of.
    @type spectrum_id:  str
    @return:            The list of spectrum IDs which are replicates of spectrum_id.
    @rtype:             list of str
    """

    # Initialise the ID list.
    repl = []

    # Loop over the replicate lists.
    for i in range(len(cdp.replicates)):
        # The spectrum ID is in the list.
        if spectrum_id in cdp.replicates[i]:
            # Loop over the inner list.
            for j in range(len(cdp.replicates[i])):
                # Spectrum ID match.
                if spectrum_id == cdp.replicates[i][j]:
                    continue

                # Append the replicated ID.
                repl.append(cdp.replicates[i][j])

    # Nothing.
    if repl == []:
        return repl

    # Sort the list.
    repl.sort()

    # Remove duplicates (backward).
    id = repl[-1]
    for i in range(len(repl)-2, -1, -1):
        # Duplicate.
        if id == repl[i]:
            del repl[i]

        # Unique.
        else:
            id = repl[i]

    # Return the list.
    return repl
