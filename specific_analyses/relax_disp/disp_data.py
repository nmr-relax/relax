###############################################################################
#                                                                             #
# Copyright (C) 2004-2013 Edward d'Auvergne                                   #
# Copyright (C) 2009 Sebastien Morin                                          #
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
"""Functions for handling relaxation dispersion data within the relax data store."""

# Python module imports.
from numpy import float64, int32, ones, zeros

# relax module imports.
from lib.errors import RelaxError, RelaxNoSpectraError
from lib.list import count_unique_elements, unique_elements
from specific_analyses.relax_disp.variables import CPMG_EXP, FIXED_TIME_EXP, R1RHO_EXP



def cpmg_frq(spectrum_id=None, cpmg_frq=None):
    """Set the CPMG frequency associated with a given spectrum.

    @keyword spectrum_id:   The spectrum identification string.
    @type spectrum_id:      str
    @keyword cpmg_frq:      The frequency, in Hz, of the CPMG pulse train.
    @type cpmg_frq:         float
    """

    # Test if the spectrum id exists.
    if spectrum_id not in cdp.spectrum_ids:
        raise RelaxNoSpectraError(spectrum_id)

    # Initialise the global CPMG frequency data structures if needed.
    if not hasattr(cdp, 'cpmg_frqs'):
        cdp.cpmg_frqs = {}
    if not hasattr(cdp, 'cpmg_frqs_list'):
        cdp.cpmg_frqs_list = []

    # Add the frequency at the correct position, converting to a float if needed.
    if cpmg_frq == None:
        cdp.cpmg_frqs[spectrum_id] = cpmg_frq
    else:
        cdp.cpmg_frqs[spectrum_id] = float(cpmg_frq)

    # The unique curves for the R2eff fitting (CPMG).
    if cdp.cpmg_frqs[spectrum_id] not in cdp.cpmg_frqs_list:
        cdp.cpmg_frqs_list.append(cdp.cpmg_frqs[spectrum_id])
    cdp.cpmg_frqs_list.sort()

    # Update the exponential curve count (skipping the reference if present).
    cdp.dispersion_points = len(cdp.cpmg_frqs_list)
    if None in cdp.cpmg_frqs_list:
        cdp.dispersion_points -= 1

    # Printout.
    print("Setting the '%s' spectrum CPMG frequency %s Hz." % (spectrum_id, cdp.cpmg_frqs[spectrum_id]))


def exp_curve_index_from_key(key):
    """Convert the exponential curve key into the corresponding index.

    @param key: The exponential curve key - either the CPMG frequency or R1rho spin-lock field strength.
    @type key:  float
    @return:    The corresponding index.
    @rtype:     int
    """

    # CPMG data.
    if cdp.exp_type in CPMG_EXP:
        return cdp.cpmg_frqs_list.index(key)

    # R1rho data.
    else:
        return cdp.spin_lock_nu1_list.index(key)


def exp_curve_key_from_index(index):
    """Convert the exponential curve key into the corresponding index.

    @param index:   The exponential curve index.
    @type index:    int
    @return:        The exponential curve key - either the CPMG frequency or R1rho spin-lock field strength.
    @rtype:         float
    """

    # CPMG data.
    if cdp.exp_type in CPMG_EXP:
        return cdp.cpmg_frqs_list[index]

    # R1rho data.
    else:
        return cdp.spin_lock_nu1_list[index]


def intensity_key(exp_key=None, relax_time=None):
    """Return the intensity key corresponding to the given exponential curve key and relaxation time.

    @keyword exp_key:       The CPMG frequency or R1rho spin-lock field strength used as a key to identify each exponential curve.
    @type exp_key:          float
    @keyword relax_time:    The time, in seconds, of the relaxation period.
    @type relax_time:       float
    """

    # Find all keys corresponding to the given relaxation time.
    time_keys = []
    for key in cdp.relax_times:
        if cdp.relax_times[key] == relax_time:
            time_keys.append(key)

    # Find all keys corresponding to the given exponential key.
    exp_keys = []
    if cdp.exp_type in CPMG_EXP:
        data = cdp.cpmg_frqs
    else:
        data = cdp.spin_lock_nu1
    for key in data:
        if data[key] == exp_key:
            exp_keys.append(key)

    # The common key.
    common_key = []
    for key in time_keys:
        if key in exp_keys:
            common_key.append(key)

    # Sanity checks.
    if len(common_key) == 0:
        raise RelaxError("No intensity key could be found for the CPMG frequency or R1rho spin-lock field strength of %s and relaxation time period of %s seconds." % (exp_key, relax_time))
    if len(common_key) != 1:
        raise RelaxError("More than one intensity key %s found for the CPMG frequency or R1rho spin-lock field strength of %s and relaxation time period of %s seconds." % (common_key, exp_key, relax_time))

    # Return the unique key.
    return common_key[0]


def loop_all_data():
    """Generator method for looping over the spectrometer frequency, dispersion points, and relaxation times.

    @return:    The spectrometer frequency, dispersion point data (either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz), and the relaxation times.
    @rtype:     float, float, float
    """

    # First loop over the spectrometer frequencies.
    for frq in loop_spectrometer():
        # Then the dispersion points.
        for point in loop_dispersion_point():
            # Finally the relaxation times.
            for time in cdp.relax_time_list:
                # Return all data.
                yield frq, point, time


def loop_dispersion_point():
    """Generator method for looping over all dispersion points (either spin-lock field or nu_CPMG points).

    @return:    Either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz.
    @rtype:     float
    """

    # CPMG type data.
    if cdp.exp_type in CPMG_EXP:
        fields = unique_elements(cdp.cpmg_frqs_list)
    elif cdp.exp_type in R1RHO_EXP:
        fields = unique_elements(cdp.spin_lock_nu1.values())
    else:
        raise RelaxError("The experiment type '%s' is unknown." % cdp.exp_type)
    fields.sort()

    # Yield each unique field strength or frequency.
    for field in fields:
        yield field


def loop_exp_curve():
    """Generator method looping over the exponential curves, yielding the index and key pair.

    @return:    The index of the exponential curve and the floating point number key used in the R2eff and I0 spin data structures.
    @rtype:     int and float
    """

    # Loop over each exponential curve.
    for i in range(cdp.dispersion_points):
        # The experiment specific key.
        if cdp.exp_type in CPMG_EXP:
            key = cdp.cpmg_frqs_list[i]
        else:
            key = cdp.spin_lock_nu1_list[i]

        # Yield the data.
        yield i, key


def loop_spectrometer():
    """Generator method for looping over all spectrometer field data.

    @return:    The field strength in Hz.
    @rtype:     float
    """

    # The number of spectrometer field strengths.
    field_count = 1
    fields = [None]
    if hasattr(cdp, 'frq'):
        field_count = count_unique_elements(cdp.frq.values())
        fields = unique_elements(cdp.frq.values())
        fields.sort()

    # Yield each unique spectrometer field strength.
    for field in fields:
        yield field


def relax_time(time=0.0, spectrum_id=None):
    """Set the relaxation time period associated with a given spectrum.

    @keyword time:          The time, in seconds, of the relaxation period.
    @type time:             float
    @keyword spectrum_id:   The spectrum identification string.
    @type spectrum_id:      str
    """

    # Test if the spectrum id exists.
    if spectrum_id not in cdp.spectrum_ids:
        raise RelaxNoSpectraError(spectrum_id)

    # Initialise the global relaxation time data structures if needed.
    if not hasattr(cdp, 'relax_times'):
        cdp.relax_times = {}
    if not hasattr(cdp, 'relax_time_list'):
        cdp.relax_time_list = []

    # Add the time, converting to a float if needed.
    cdp.relax_times[spectrum_id] = float(time)

    # The unique time points.
    if cdp.relax_times[spectrum_id] not in cdp.relax_time_list:
        cdp.relax_time_list.append(cdp.relax_times[spectrum_id])
    cdp.relax_time_list.sort()

    # Update the exponential time point count.
    cdp.num_time_pts = len(cdp.relax_time_list)

    # Printout.
    print("Setting the '%s' spectrum relaxation time period to %s s." % (spectrum_id, cdp.relax_times[spectrum_id]))


def return_cpmg_frqs(ref_flag=True):
    """Return the list of nu_CPMG frequencies.

    @keyword ref_flag:  A flag which if False will cause the reference spectrum frequency of None to be removed from the list.
    @type ref_flag:     bool
    @return:            The list of nu_CPMG frequencies in Hz.
    @rtype:             list of float
    """

    # Initialise.
    cpmg_frqs = []

    # Loop over the frequencies.
    for frq in cdp.cpmg_frqs_list:
        if frq == None and not ref_flag:
            continue

        # Add the frequency.
        cpmg_frqs.append(frq)

    # Return the new list.
    return cpmg_frqs


def return_intensity(spin=None, frq=None, point=None, time=None, ref=False):
    """Return the peak intensity corresponding to the given field strength and dispersion point.

    The corresponding reference intensity can be returned if the ref flag is set.  This assumes that the data is of the fixed relaxation time period type.


    @keyword spin:  The spin container object.
    @type spin:     SpinContainer instance
    @keyword frq:   The spectrometer frequency.
    @type frq:      float
    @keyword point: The dispersion point data (either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz).
    @type point:    float
    @keyword time:  The relaxation time period.
    @type time:     float
    @keyword ref:   A flag which if True will cause the corresponding reference intensity to be returned instead.
    @type ref:      bool
    """

    # Checks.
    if ref and cdp.exp_type not in FIXED_TIME_EXP:
        raise RelaxError("The reference peak intensity does not exist for the variable relaxation time period experiment types.")

    # The key.
    if ref:
        key = return_key(frq=frq, point=None, time=time)
    else:
        key = return_key(frq=frq, point=point, time=time)

    # Return the intensity.
    return spin.intensities[key]


def return_r2eff_arrays(spins=None, spin_ids=None, fields=None, field_count=None, sim_index=None):
    """Return numpy arrays of the R2eff/R1rho values and errors.

    @keyword spins:         The list of spin containers in the cluster.
    @type spins:            list of SpinContainer instances
    @keyword spin_ids:      The list of spin IDs for the cluster.
    @type spin_ids:         list of str
    @keyword fields:        The list of spectrometer field strengths.
    @type fields:           list of float
    @keyword field_count:   The number of spectrometer field strengths.  This may not be equal to the length of the fields list as the user may not have set the field strength.
    @type field_count:      int
    @keyword sim_index:     The index of the simulation to return the data of.  This should be None if the normal data is required.
    @type sim_index:        None or int
    @return:                The numpy array structures of the R2eff/R1rho values, errors and missing data.  For each structure, the first dimension corresponds to the spins of a spin block, the second to the spectrometer field strength, and the third is the dispersion points.
    @rtype:                 numpy rank-3 float array, numpy rank-3 float array, numpy rank-3 int array
    """

    # The spin count.
    spin_num = len(spins)

    # Initialise the data structures for the target function (errors are set to one to avoid divide by zero for missing data in the chi-squared function).
    values = zeros((spin_num, field_count, cdp.dispersion_points), float64)
    errors = ones((spin_num, field_count, cdp.dispersion_points), float64)
    missing = ones((spin_num, field_count, cdp.dispersion_points), int32)

    # Pack the R2eff/R1rho data.
    data_flag = False
    for spin_index in range(spin_num):
        # Alias the spin.
        spin = spins[spin_index]

        # No data.
        if not hasattr(spin, 'r2eff'):
            continue
        data_flag = True

        # The keys.
        keys = list(spin.r2eff.keys())

        # Loop over the R2eff data.
        for key in keys:
            # Reference in the fixed time experiments.
            if cdp.exp_type in FIXED_TIME_EXP:
                if cdp.exp_type in CPMG_EXP and cdp.cpmg_frqs[key] == None:
                    continue
                if cdp.exp_type in R1RHO_EXP and cdp.spin_lock_nu1[key] == None:
                    continue

            # The indices.
            disp_pt_index = 0
            if cdp.exp_type in CPMG_EXP:
                disp_pt_index = cdp.cpmg_frqs_list.index(cdp.cpmg_frqs[key])
            elif cdp.exp_type in R1RHO_EXP:
                disp_pt_index = cdp.spin_lock_nu1_list.index(cdp.spin_lock_nu1[key])
            if cdp.exp_type in FIXED_TIME_EXP:
                disp_pt_index -= 1
            field_index = 0
            if hasattr(cdp, 'frq'):
                field_index = fields.index(cdp.frq[key])

            # The values.
            if sim_index == None:
                values[spin_index, field_index, disp_pt_index] = spin.r2eff[key]
            else:
                values[spin_index, field_index, disp_pt_index] = spin.r2eff_sim[key][sim_index]

            # The errors.
            errors[spin_index, field_index, disp_pt_index] = spin.r2eff_err[key]

            # Flip the missing flag to off.
            missing[spin_index, field_index, disp_pt_index] = 0

    # No R2eff/R1rho data for the spin cluster.
    if not data_flag:
        raise RelaxError("No R2eff/R1rho data could be found for the spin cluster %s." % spin_ids)

    # Return the structures.
    return values, errors, missing


def return_key(frq=None, point=None, time=None):
    """Return the key corresponding to the spectrometer frequency, dispersion point, and relaxation time.

    @keyword frq:   The spectrometer frequency.
    @type frq:      float
    @keyword point: The dispersion point data (either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz).
    @type point:    float
    @keyword time:  The relaxation time period.
    @type time:     float
    @return:        The key corresponding to the spectrometer frequency, dispersion point, and relaxation time.
    @rtype:         str
    """

    # The dispersion data.
    if cdp.exp_type in CPMG_EXP:
        disp_data = cdp.cpmg_frqs
    else:
        disp_data = cdp.spin_lock_nu1

    # Loop over all spectrum IDs, returning the matching ID.
    for id in cdp.spectrum_ids:
        if cdp.frq[id] == frq and disp_data[id] == point and cdp.relax_times[id] == time:
            return id

    # Should not be here.
    raise RelaxError("No key could be found corresponding to the spectrometer frequency %s, dispersion point %s and relaxation time %s." % (frq, point, time))


def return_spin_lock_nu1(ref_flag=True):
    """Return the list of spin-lock field strengths.

    @keyword ref_flag:  A flag which if False will cause the reference spectrum frequency of None to be removed from the list.
    @type ref_flag:     bool
    @return:            The list of spin-lock field strengths in Hz.
    @rtype:             list of float
    """

    # Initialise.
    nu1 = []

    # Loop over the frequencies.
    for frq in cdp.spin_lock_nu1_list:
        if frq == None and not ref_flag:
            continue

        # Add the frequency.
        nu1.append(frq)

    # Return the new list.
    return nu1


def spin_lock_field(spectrum_id=None, field=None):
    """Set the spin-lock field strength (nu1) for the given spectrum.

    @keyword spectrum_id:   The spectrum ID string.
    @type spectrum_id:      str
    @keyword field:         The spin-lock field strength (nu1) in Hz.
    @type field:            int or float
    """

    # Test if the spectrum ID exists.
    if spectrum_id not in cdp.spectrum_ids:
        raise RelaxNoSpectraError(spectrum_id)

    # Initialise the global nu1 data structures if needed.
    if not hasattr(cdp, 'spin_lock_nu1'):
        cdp.spin_lock_nu1 = {}
    if not hasattr(cdp, 'spin_lock_nu1_list'):
        cdp.spin_lock_nu1_list = []

    # Add the frequency, converting to a float if needed.
    cdp.spin_lock_nu1[spectrum_id] = float(field)

    # The unique curves for the R2eff fitting (R1rho).
    if cdp.spin_lock_nu1[spectrum_id] not in cdp.spin_lock_nu1_list:
        cdp.spin_lock_nu1_list.append(cdp.spin_lock_nu1[spectrum_id])
    cdp.spin_lock_nu1_list.sort()

    # Update the exponential curve count (skipping the reference if present).
    cdp.dispersion_points = len(cdp.spin_lock_nu1_list)
    if None in cdp.spin_lock_nu1_list:
        cdp.dispersion_points -= 1

    # Printout.
    print("Setting the '%s' spectrum spin-lock field strength to %s kHz." % (spectrum_id, cdp.spin_lock_nu1[spectrum_id]/1000.0))
