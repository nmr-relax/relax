###############################################################################
#                                                                             #
# Copyright (C) 2004-2014 Edward d'Auvergne                                   #
# Copyright (C) 2009 Sebastien Morin                                          #
# Copyright (C) 2013-2014 Troels E. Linnet                                    #
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
"""Module for handling relaxation dispersion data within the relax data store.

Ordering of data
================

The dispersion data model is based on the following concepts, in order of importance:

    - 'exp', the experiment type,
    - 'spin', the spins of the cluster,
    - 'frq', the spectrometer frequency (if multiple field data is present),
    - 'offset', the spin-lock offsets,
    - 'point', the dispersion point (nu_CPMG value or spin-lock nu1 field strength),
    - 'time', the relaxation time point (if exponential curve data has been collected).


Indices
=======

The data structures used in this module consist of many different index types which follow the data ordering above.  These are abbreviated as:

    - Ei or ei:  The index for each experiment type.
    - Si or si:  The index for each spin of the spin cluster.
    - Mi or mi:  The index for each magnetic field strength.
    - Oi or oi:  The index for each spin-lock offset.  In the case of CPMG-type data, this index is always zero.
    - Di or di:  The index for each dispersion point (either the spin-lock field strength or the nu_CPMG frequency).
    - Ti or ti:  The index for each dispersion point (either the spin-lock field strength or the nu_CPMG frequency).
"""

# Python module imports.
from math import cos, pi, sin, sqrt
from numpy import array, float64, int32, ones, zeros
from os import F_OK, access
from os.path import expanduser
from random import gauss
from re import search
import sys
from warnings import warn

# relax module imports.
from lib.errors import RelaxError, RelaxNoSpectraError, RelaxNoSpinError, RelaxSpinTypeError
from lib.float import isNaN
from lib.io import extract_data, get_file_path, open_write_file, strip, write_data
from lib.nmr import frequency_to_ppm, frequency_to_ppm_from_rad, frequency_to_rad_per_s, rotating_frame_params
from lib.physical_constants import g1H, return_gyromagnetic_ratio
from lib.sequence import read_spin_data, write_spin_data
from lib.software.grace import write_xy_data, write_xy_header, script_grace2images
from lib.warnings import RelaxWarning, RelaxNoSpinWarning
from pipe_control import pipes
from pipe_control.mol_res_spin import check_mol_res_spin_data, exists_mol_res_spin_data, generate_spin_id_unique, generate_spin_string, return_spin, spin_loop
from pipe_control.result_files import add_result_file
from pipe_control.selection import desel_spin
from pipe_control.sequence import return_attached_protons
from pipe_control.spectrum import add_spectrum_id
from pipe_control.spectrometer import check_frequency, get_frequency
from pipe_control import value
import specific_analyses
from specific_analyses.relax_disp.checks import check_exp_type, check_interpolate_offset_cpmg_model, check_mixed_curve_types
from specific_analyses.relax_disp.variables import EXP_TYPE_CPMG_DQ, EXP_TYPE_CPMG_MQ, EXP_TYPE_CPMG_PROTON_MQ, EXP_TYPE_CPMG_PROTON_SQ, EXP_TYPE_CPMG_SQ, EXP_TYPE_CPMG_ZQ, EXP_TYPE_DESC_CPMG_DQ, EXP_TYPE_DESC_CPMG_MQ, EXP_TYPE_DESC_CPMG_PROTON_MQ, EXP_TYPE_DESC_CPMG_PROTON_SQ, EXP_TYPE_DESC_CPMG_SQ, EXP_TYPE_DESC_CPMG_ZQ, EXP_TYPE_DESC_R1RHO, EXP_TYPE_LIST, EXP_TYPE_LIST_CPMG, EXP_TYPE_LIST_R1RHO, EXP_TYPE_R1RHO, MODEL_B14, MODEL_B14_FULL, MODEL_DPL94, MODEL_LIST_MMQ, MODEL_LIST_NUMERIC_CPMG, MODEL_LIST_R1RHO, MODEL_LIST_R1RHO_FULL, MODEL_LIST_R1RHO_FIT_R1, MODEL_LIST_R1RHO_W_R1, MODEL_MP05, MODEL_NS_R1RHO_2SITE, MODEL_PARAMS, MODEL_R2EFF, MODEL_TAP03, MODEL_TP02, PARAMS_R20
from stat import S_IRWXU, S_IRGRP, S_IROTH
from os import chmod, sep


# Module variables.
R20_KEY_FORMAT = "%s - %.8f MHz"

# Plotting variables.
Y_AXIS_R2_EFF = "r2_eff"
Y_AXIS_R2_R1RHO = "r2_r1rho"

X_AXIS_DISP = "disp"
X_AXIS_W_EFF = "w_eff"
X_AXIS_THETA = "theta"

INTERPOLATE_DISP = "disp"
INTERPOLATE_OFFSET = "offset"

# Default hardcoded colours (one colour for each magnetic field strength).
COLOUR_ORDER = [4, 15, 2, 13, 11, 1, 3, 5, 6, 7, 8, 9, 10, 12, 14] * 1000


def average_intensity(spin=None, exp_type=None, frq=None, offset=None, point=None, time=None, sim_index=None, error=False):
    """Return the average peak intensity for the spectrometer frequency, dispersion point, and relaxation time.

    This is for handling replicate peak intensity data.


    @keyword spin:      The spin container to average the peak intensities for.
    @type spin:         SpinContainer instance
    @keyword exp_type:  The experiment type.
    @type exp_type:     str
    @keyword frq:       The spectrometer frequency.
    @type frq:          float
    @keyword offset:    The spin-lock or hard pulse offset.
    @type offset:       float
    @keyword point:     The dispersion point data (either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz).
    @type point:        float
    @keyword time:      The relaxation time period.
    @type time:         float
    @keyword sim_index: The simulation index.  This should be None for the measured intensity values.
    @type sim_index:    None or int
    @keyword error:     A flag which if True will average and return the peak intensity errors.
    @type error:        bool
    @return:            The average peak intensity value.
    @rtype:             float
    """

    # The keys.
    int_keys = find_intensity_keys(exp_type=exp_type, frq=frq, offset=offset, point=point, time=time)

    # Initialise.
    intensity = 0.0

    # Loop over the replicates.
    for i in range(len(int_keys)):
        # Simulation intensity data.
        if sim_index != None:
            # Error checking.
            if not int_keys[i] in spin.peak_intensity_sim:
                raise RelaxError("The peak intensity simulation data is missing the key '%s'." % int_keys[i])

            # Sum.
            intensity += spin.peak_intensity_sim[int_keys[i]][sim_index]

        # Error intensity data.
        if error:
            # Error checking.
            if not int_keys[i] in spin.peak_intensity_err:
                raise RelaxError("The peak intensity errors are missing the key '%s'." % int_keys[i])

            # Sum.
            intensity += spin.peak_intensity_err[int_keys[i]]**2

        # Normal intensity data.
        else:
            # Error checking.
            if not int_keys[i] in spin.peak_intensity:
                raise RelaxError("The peak intensity data is missing the key '%s'." % int_keys[i])

            # Sum.
            intensity += spin.peak_intensity[int_keys[i]]

    # Average.
    if error:
        intensity = sqrt(intensity / len(int_keys))
    else:
        intensity /= len(int_keys)

    # Return the value.
    return intensity


def calc_rotating_frame_params(spin=None, spin_id=None, fields=None, verbosity=0):
    """Calculates and rotating frame parameters, calculated from:
    - The spectrometer frequency.
    - The spin-lock or hard pulse offset.
    - The dispersion point data (the spin-lock field strength in Hz).

    The return will be for each spin,
    - Rotating frame tilt angle ( theta = arctan(w_1 / Omega) ) [rad]
    - The average resonance offset in the rotating frame ( Domega = w_{pop_ave} - w_rf  ) [rad/s]
    - Effective field in rotating frame ( w_eff = sqrt( Omega^2 + w_1^2 ) ) [rad/s]

    Calculations are mentioned in the U{manual<http://www.nmr-relax.com/manual/Dispersion_model_summary.html>}

    @keyword spin:      The spin system specific data container
    @type spin:         SpinContainer instance
    @keyword spin_id:   The spin ID string.
    @type spin_id:      None or str
    @keyword fields:    The spin-lock field strengths to use instead of the user loaded values - to enable interpolation.  The dimensions are {Ei, Mi}.
    @type fields:       rank-2 list of floats
    @keyword verbosity: A flag specifying to print calculations.
    @type verbosity:    int
    @return:            List with dict() of theta, Domega, w_eff and list of dict() keys.
    @rtype:             List of dict() 
    """

    # If the spin is not selected, return None
    if not spin.select:
        return None, None, None, None

    # If the spin does not have isotope, return None
    if not hasattr(spin, 'isotope'):
        return None, None, None, None

    # Get the field count
    field_count = count_frq()

    # Check the experiment type
    if not has_r1rho_exp_type():
        raise RelaxError("The experiment type is not of R1rho type.")

    # Get the spin_lock_field points
    if fields == None:
        spin_lock_nu1 = return_spin_lock_nu1(ref_flag=False)
    else:
        spin_lock_nu1 = fields

    # The offset and R1 data.
    offsets, spin_lock_fields_inter, chemical_shifts, tilt_angles, Delta_omega, w_eff = return_offset_data(spins=[spin], spin_ids=[spin_id], field_count=field_count, fields=spin_lock_nu1)
        
    # Loop over the index of spins, then exp_type, frq, offset
    if verbosity:
        print("Printing the following")    
        print("exp_type spin_id frq offset{ppm} offsets[ei][si][mi][oi]{rad/s} ei mi oi si di cur_spin.chemical_shift{ppm} chemical_shifts[ei][si][mi]{rad/s} spin_lock_nu1{Hz} tilt_angles[ei][si][mi][oi]{rad} av_res_offset[ei][si][mi][oi]{rad/s}")

    si = 0
    theta_spin_dic = dict()
    Domega_spin_dic = dict()
    w_eff_spin_dic = dict()
    dic_key_list = []

    for exp_type, frq, offset, ei, mi, oi in loop_exp_frq_offset(return_indices=True):
        # Loop over the dispersion points.
        spin_lock_fields = spin_lock_nu1[ei][mi][oi]
        for di in range(len(spin_lock_fields)):
            if verbosity:
                print("%-8s %-10s %11.1f %8.4f %12.5f %i  %i  %i  %i  %i %7.3f %12.5f %12.5f %12.5f %12.5f"%(exp_type, spin_id, frq, offset, offsets[ei][si][mi][oi], ei, mi, oi, si, di, spin.chemical_shift, chemical_shifts[ei][si][mi], spin_lock_fields[di], tilt_angles[ei][si][mi][oi][di], Delta_omega[ei][si][mi][oi][di]))
            dic_key = return_param_key_from_data(exp_type=exp_type, frq=frq, offset=offset, point=spin_lock_fields[di])
            dic_key_list.append(dic_key) 
            theta_spin_dic["%s"%(dic_key)] = tilt_angles[ei][si][mi][oi][di]
            Domega_spin_dic["%s"%(dic_key)] = Delta_omega[ei][si][mi][oi][di]
            w_eff_spin_dic["%s"%(dic_key)] = w_eff[ei][si][mi][oi][di]

    # Return the dic and list of keys
    return [theta_spin_dic, Domega_spin_dic, w_eff_spin_dic, dic_key_list]


def count_exp():
    """Count the number of experiments present.

    @return:    The experiment count
    @rtype:     int
    """

    # The normal count variable.
    return len(cdp.exp_type_list)


def count_frq():
    """Count the number of spectrometer frequencies present.

    @return:    The spectrometer frequency count
    @rtype:     int
    """

    # Handle missing frequency data.
    if not hasattr(cdp, 'spectrometer_frq'):
        return 1

    # The normal count variable.
    return cdp.spectrometer_frq_count


def count_relax_times(exp_type=None, frq=None, offset=None, point=None, ei=None):
    """Count the number of relaxation times present.

    @keyword exp_type:          The experiment type.
    @type exp_type:             str
    @keyword frq:               The spectrometer frequency in Hz.
    @type frq:                  float
    @keyword offset:            The spin-lock or hard pulse offset value in ppm.
    @type offset:               None or float
    @keyword point:             The dispersion point data (either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz).
    @type point:                float
    @keyword ei:                The experiment type index.
    @type ei:                   str
    @return:                    The relaxation time count for the given experiment.
    @rtype:                     int
    """

    # Loop over the times.
    count = 0
    for time in loop_time(exp_type=exp_type, frq=frq, offset=offset, point=point):
        # Find a matching experiment ID.
        found = False
        for id in cdp.exp_type.keys():
            # Skip non-matching experiments.
            if cdp.exp_type[id] != cdp.exp_type_list[ei]:
                continue

            # Found.
            found = True
            break

        # No data.
        if not found:
            continue

        # A new time.
        count += 1

    # Return the count.
    return count


def count_spins(spins=None):
    """Count the number of selected spins in the spin cluster."""

    # Count the selected spins.
    spin_num = 0
    for spin in spins:
        if spin.select:
            spin_num += 1

    # Return the count.
    return spin_num


def cpmg_setup(spectrum_id=None, cpmg_frq=None, ncyc_even=True):
    """Set the CPMG frequency associated with a given spectrum.

    @keyword spectrum_id:   The spectrum identification string.
    @type spectrum_id:      str
    @keyword cpmg_frq:      The frequency, in Hz, of the CPMG pulse train.
    @type cpmg_frq:         float
    @keyword ncyc_even:     A flag which if True means that the number of CPMG blocks must be even.  This is pulse sequence dependant.
    @type ncyc_even:        bool
    """

    # Test if the spectrum id exists.
    if spectrum_id not in cdp.spectrum_ids:
        raise RelaxNoSpectraError(spectrum_id)

    # Initialise the global data structures if needed.
    if not hasattr(cdp, 'cpmg_frqs'):
        cdp.cpmg_frqs = {}
    if not hasattr(cdp, 'cpmg_frqs_list'):
        cdp.cpmg_frqs_list = []
    if not hasattr(cdp, 'ncyc_even'):
        cdp.ncyc_even = {}

    # Add the frequency at the correct position, converting to a float if needed.
    if cpmg_frq == None:
        cdp.cpmg_frqs[spectrum_id] = cpmg_frq
    else:
        cdp.cpmg_frqs[spectrum_id] = float(cpmg_frq)

    # The unique curves for the R2eff fitting (CPMG).
    if cdp.cpmg_frqs[spectrum_id] not in cdp.cpmg_frqs_list:
        cdp.cpmg_frqs_list.append(cdp.cpmg_frqs[spectrum_id])

    # Sort the list (handling None for Python 3).
    flag = False
    if None in cdp.cpmg_frqs_list:
        cdp.cpmg_frqs_list.pop(cdp.cpmg_frqs_list.index(None))
        flag = True
    cdp.cpmg_frqs_list.sort()
    if flag:
        cdp.cpmg_frqs_list.insert(0, None)

    # Update the exponential curve count (skipping the reference if present).
    cdp.dispersion_points = len(cdp.cpmg_frqs_list)
    if None in cdp.cpmg_frqs_list:
        cdp.dispersion_points -= 1

    # Add the ncyc flag.
    cdp.ncyc_even[spectrum_id] = ncyc_even

    # Printout.
    print("The spectrum ID '%s' CPMG frequency is set to %s Hz." % (spectrum_id, cdp.cpmg_frqs[spectrum_id]))
    print("The spectrum ID '%s' even number of CPMG blocks flag is set to %s." % (spectrum_id, cdp.ncyc_even[spectrum_id]))


def decompose_r20_key(key=None):
    """Decompose the unique R20 key into the experiment type and spectrometer frequency.

    @keyword key:   The unique R20 key.
    @type key:      str
    @return:        The experiment and the spectrometer frequency in Hz.
    @rtype:         str, float
    """

    # Loop over the experiments and frequencies until the matching key is found.
    for exp_type, frq in loop_exp_frq():
        if key == generate_r20_key(exp_type=exp_type, frq=frq):
            return exp_type, frq


def find_intensity_keys(exp_type=None, frq=None, offset=None, point=None, time=None, raise_error=True):
    """Return the key corresponding to the spectrometer frequency, dispersion point, and relaxation time.

    @keyword exp_type:      The experiment type.
    @type exp_type:         str
    @keyword frq:           The spectrometer frequency.
    @type frq:              float
    @keyword offset:        The optional offset value for off-resonance R1rho-type data.
    @type offset:           None or float
    @keyword point:         The dispersion point data (either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz).
    @type point:            float
    @keyword time:          The relaxation time period.
    @type time:             float
    @keyword raise_error:   A flag which if True will cause a RelaxError to be raised if no keys could be found.
    @type raise_error:      bool
    @return:                The keys corresponding to the spectrometer frequency, dispersion point, and relaxation time.
    @rtype:                 list of str
    """

    # Check.
    if exp_type == None:
        raise RelaxError("The experiment type has not been supplied.")

    # Catch NaNs.
    if isNaN(point):
        point = None

    # The dispersion data.
    if exp_type in EXP_TYPE_LIST_CPMG:
        disp_data = cdp.cpmg_frqs
    else:
        disp_data = cdp.spin_lock_nu1

    # Loop over all spectrum IDs, returning the matching ID.
    ids = []
    for id in cdp.exp_type.keys():
        # Skip non-matching experiments.
        if cdp.exp_type[id] != exp_type:
            continue

        # Skip non-matching spectrometer frequencies.
        if hasattr(cdp, 'spectrometer_frq') and cdp.spectrometer_frq[id] != frq:
            continue

        # Skip non-matching offsets.
        if offset != None and hasattr(cdp, 'spin_lock_offset') and cdp.spin_lock_offset[id] != offset:
            continue

        # Skip non-matching dispersion points.
        if disp_data[id] != point:
            continue

        # The reference point, so checking the time is pointless (and can fail as specifying the time should not be necessary).
        if point == None or isNaN(point):
            ids.append(id)

        # Matching time.
        elif time == None:
            ids.append(id)
        elif cdp.relax_times[id] == time:
            ids.append(id)

    # Check for missing IDs.
    if raise_error and len(ids) == 0:
        if point == None or isNaN(point):
            raise RelaxError("No reference intensity data could be found corresponding to the spectrometer frequency of %s MHz and relaxation time of %s s." % (frq*1e-6, time))
        else:
            raise RelaxError("No intensity data could be found corresponding to the spectrometer frequency of %s MHz, dispersion point of %s and relaxation time of %s s." % (frq*1e-6, point, time))

    # Return the IDs.
    return ids


def generate_r20_key(exp_type=None, frq=None):
    """Generate the unique R20 key from the experiment type and spectrometer frequency.

    @keyword exp_type:  The experiment type.
    @type exp_type:     str
    @keyword frq:       The spectrometer frequency in Hz.
    @type frq:          float
    @return:            The unique R20 key.
    @rtype:             str
    """

    # Generate and return the unique key.
    return R20_KEY_FORMAT % (exp_type, frq/1e6)


def get_curve_type(id=None):
    """Return the unique curve type.

    @keyword id:    The spectrum ID.  If not supplied, then all data will be assumed.
    @type id:       str
    @return:        The curve type - either 'fixed time' or 'exponential'.
    @rtype:         str
    """

    # All data.
    if id == None:
        # Data checks.
        check_mixed_curve_types()

        # Determine the curve type.
        curve_type = 'fixed time'
        if has_exponential_exp_type():
            curve_type = 'exponential'

    # A specific ID.
    else:
        # Determine the curve type.
        curve_type = 'exponential'
        exp_type = cdp.exp_type[id]
        frq = cdp.spectrometer_frq[id]
        if count_relax_times(exp_type = exp_type, frq = frq, ei = cdp.exp_type_list.index(cdp.exp_type[id])) == 1:
            curve_type = 'fixed time'

    # Return the type.
    return curve_type


def get_exp_type(id=None):
    """Return the experiment type for the given ID.

    @keyword id:    The spectrum ID.
    @type id:       str
    @return:        The experiment type corresponding to the ID.
    @rtype:         str
    """

    # Data check.
    check_exp_type(id=id)

    # Return the type.
    return cdp.exp_type[id]


def has_cpmg_exp_type():
    """Determine if the current data pipe contains CPMG experiment types.

    @return:    True if CPMG experiment types exist, False otherwise.
    @rtype:     bool
    """

    # No experiment types set.
    if not hasattr(cdp, 'exp_type'):
        return False

    # Loop over all experiment types.
    for exp_type in cdp.exp_type_list:
        if exp_type in EXP_TYPE_LIST_CPMG:
            return True

    # No CPMG experiment types.
    return False


def has_disp_data(spins=None, spin_ids=None, exp_type=None, frq=None, offset=None, point=None):
    """Determine if dispersion data exists for the given data combination.

    @keyword spins:     The list of spin containers in the cluster.
    @type spins:        list of SpinContainer instances
    @keyword spin_ids:  The list of spin IDs for the cluster.
    @type spin_ids:     list of str
    @keyword exp_type:  The experiment type.
    @type exp_type:     str
    @keyword frq:       The spectrometer frequency.
    @type frq:          float
    @keyword offset:    For R1rho-type data, the spin-lock offset value in ppm.
    @type offset:       None or float
    @keyword point:     The dispersion point data (either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz).
    @type point:        float
    @return:            True if dispersion data exists, False otherwise.
    @rtype:             bool
    """

    # Skip reference spectra.
    if point == None:
        return False

    # The key.
    key = return_param_key_from_data(exp_type=exp_type, frq=frq, offset=offset, point=point)

    # Loop over the spins.
    for si in range(len(spins)):
        # Alias the correct spin.
        current_spin = spins[si]
        if exp_type in [EXP_TYPE_CPMG_PROTON_SQ, EXP_TYPE_CPMG_PROTON_MQ]:
            current_spin = return_attached_protons(spin_ids[si])[0]

        # The data is present.
        if key in current_spin.r2eff.keys():
            return True

    # No data.
    return False


def has_exponential_exp_type():
    """Determine if the current data pipe contains exponential curves.

    @return:    True if spectral data for exponential curves exist, False otherwise.
    @rtype:     bool
    """

    # No experiment types set.
    if not hasattr(cdp, 'exp_type'):
        return False

    # Loop over all spectra IDs.
    for id in cdp.exp_type.keys():
        if get_curve_type(id) == 'exponential':
            return True

    # No exponential data.
    return False


def has_fixed_time_exp_type():
    """Determine if the current data pipe contains fixed time data.

    @return:    True if spectral data for fixed time data exists, False otherwise.
    @rtype:     bool
    """

    # No experiment types set.
    if not hasattr(cdp, 'exp_type'):
        return False

    # Loop over all experiment types.
    for id in cdp.exp_type.keys():
        if get_curve_type(id) == 'fixed time':
            return True

    # No exponential data.
    return False


def has_proton_mmq_cpmg():
    """Determine if the current data pipe contains either proton SQ or MQ (MMQ) CPMG data.

    This is only for the MMQ models.


    @return:    True if either proton SQ or MQ CPMG data exists, False otherwise.
    @rtype:     bool
    """

    # 1H MMQ data exists.
    if has_proton_sq_cpmg():
        return True
    if has_proton_mq_cpmg():
        return True

    # No 1H MMQ CPMG data.
    return False


def has_proton_mq_cpmg():
    """Determine if the current data pipe contains proton MQ CPMG data.

    This is only for the MMQ models.


    @return:    True if proton MQ CPMG data exists, False otherwise.
    @rtype:     bool
    """

    # Proton MQ CPMG data is present.
    if EXP_TYPE_CPMG_PROTON_MQ in cdp.exp_type_list:
        return True

    # No 1H MQ CPMG data.
    return False


def has_proton_sq_cpmg():
    """Determine if the current data pipe contains proton SQ CPMG data.

    This is only for the MMQ models.


    @return:    True if proton SQ CPMG data exists, False otherwise.
    @rtype:     bool
    """

    # Proton SQ CPMG data is present.
    if EXP_TYPE_CPMG_PROTON_SQ in cdp.exp_type_list:
        return True

    # No 1H SQ CPMG data.
    return False


def has_r1rho_exp_type():
    """Determine if the current data pipe contains R1rho experiment types.

    @return:    True if R1rho experiment types exist, False otherwise.
    @rtype:     bool
    """

    # No experiment types set.
    if not hasattr(cdp, 'exp_type'):
        return False

    # Loop over all experiment types.
    for exp_type in cdp.exp_type_list:
        if exp_type in EXP_TYPE_LIST_R1RHO:
            return True

    # No CPMG experiment types.
    return False


def insignificance(level=0.0):
    """Deselect all spins with insignificant dispersion profiles.

    @keyword level: The R2eff/R1rho value in rad/s by which to judge insignificance.  If the maximum difference between two points on all dispersion curves for a spin is less than this value, that spin will be deselected.
    @type level:    float
    """

    # Nothing to do.
    if level == 0.0:
        return

    # Number of spectrometer fields.
    fields = [None]
    field_count = 1
    if hasattr(cdp, 'spectrometer_frq_count'):
        fields = cdp.spectrometer_frq_list
        field_count = cdp.spectrometer_frq_count

    # Loop over all spins.
    for spin, spin_id in spin_loop(return_id=True, skip_desel=True):
        # Nothing to do (the R2eff model has no dispersion curves).
        if spin.model == 'R2eff':
            continue

        # Get all the data.
        try:
            values, errors, missing, frqs, frqs_H, exp_types, relax_times = return_r2eff_arrays(spins=[spin], spin_ids=[spin_id], fields=fields, field_count=field_count)

        # No R2eff data, so skip the rest.
        except RelaxError:
            continue

        # The flag.
        desel = True

        # Loop over the experiments, magnetic fields, and offsets.
        max_diff = 0.0
        for exp_type, frq, offset, ei, mi, oi in loop_exp_frq_offset(return_indices=True):
            # No data.
            if not len(values[ei][0][mi][oi]):
                continue

            # The difference.
            diff = values[ei][0][mi][oi].max() - values[ei][0][mi][oi].min()

            # Significance detected.
            if diff > level:
                desel = False

            # Store the maximum for the deselection printout.
            if diff > max_diff:
                max_diff = diff

        # Deselect the spin.
        if desel:
            # Printout.
            print("Deselecting spin '%s', the maximum dispersion curve difference for all curves is %s rad/s." % (spin_id, max_diff))

            # Deselection.
            desel_spin(spin_id)


def interpolate_disp(spin=None, spin_id=None, si=None, num_points=None, extend_hz=None):
    """Interpolate function for 2D Grace plotting function for the dispersion curves.

    @keyword spin:          The specific spin data container.
    @type spin:             SpinContainer instance.
    @keyword spin_id:       The spin ID string.
    @type spin_id:          str
    @keyword si:            The index of the given spin in the cluster.
    @type si:               int
    @keyword num_points:    The number of points to generate the interpolated fitted curves with.
    @type num_points:       int
    @keyword extend_hz:     How far to extend the interpolated fitted curves to (in Hz).
    @type extend_hz:        float
    @return:                The interpolated_flag, list of back calculated R2eff/R1rho values in rad/s {Ei, Si, Mi, Oi, Di}, list of interpolated frequencies for cpmg_frqs in Hz {Ei, Si, Mi, Oi, Di}, interpolated spin-lock offsets in rad/s {Ei, Si, Mi, Oi}, list of interpolated spin-lock field strength frequencies for spin_lock_nu1_new in Hz {Ei, Si, Mi, Oi, Di}, chemical shifts in rad/s {Ei, Si, Mi}, interpolated rotating frame tilt angles theta {Ei, Si, Mi, Oi, Di}, interpolated average resonance offset in the rotating frame Omega in rad/s {Ei, Si, Mi, Oi, Di} and the interpolated effective field in rotating frame w_eff in rad/s {Ei, Si, Mi, Oi, Di}.
    @rtype:                 boolean, rank-4 list of numpy rank-1 float arrays, rank-4 list of numpy rank-1 float arrays, rank-3 list of numpy rank-1 float arrays, rank-4 list of numpy rank-1 float arrays, rank-2 list of numpy rank-1 float arrays, rank-4 list of numpy rank-1 float arrays, rank-4 list of numpy rank-1 float arrays, rank-4 list of numpy rank-1 float arrays
    """
    # Set the flag.
    interpolated_flag = True

    # Initialise some structures.
    cpmg_frqs_new = None
    spin_lock_nu1_new = None

    # Interpolate the CPMG frequencies (numeric models).
    if spin.model in MODEL_LIST_NUMERIC_CPMG or spin.model in [MODEL_B14, MODEL_B14_FULL]:
        cpmg_frqs = return_cpmg_frqs(ref_flag=False)
        relax_times = return_relax_times()
        if cpmg_frqs != None and len(cpmg_frqs[0][0]):
            cpmg_frqs_new = []
            for ei in range(len(cpmg_frqs)):
                # Add a new dimension.
                cpmg_frqs_new.append([])

                # Then loop over the spectrometer frequencies.
                for mi in range(len(cpmg_frqs[ei])):
                    # Add a new dimension.
                    cpmg_frqs_new[ei].append([])

                    # Finally the offsets.
                    for oi in range(len(cpmg_frqs[ei][mi])):
                        # Add a new dimension.
                        cpmg_frqs_new[ei][mi].append([])

                        # No data.
                        if not len(cpmg_frqs[ei][mi][oi]):
                            continue

                        # The minimum frequency unit.
                        min_frq = 1.0 / relax_times[ei][mi]
                        max_frq = max(cpmg_frqs[ei][mi][oi]) + round(extend_hz / min_frq) * min_frq
                        num_points = int(round(max_frq / min_frq))

                        # Interpolate (adding the extended amount to the end).
                        for di in range(num_points):
                            point = (di + 1) * min_frq
                            cpmg_frqs_new[ei][mi][oi].append(point)

                        # Convert to a numpy array.
                        cpmg_frqs_new[ei][mi][oi] = array(cpmg_frqs_new[ei][mi][oi], float64)

    # Interpolate the CPMG frequencies (analytic models).
    else:
        cpmg_frqs = return_cpmg_frqs(ref_flag=False)
        if cpmg_frqs != None and len(cpmg_frqs[0][0]):
            cpmg_frqs_new = []
            for ei in range(len(cpmg_frqs)):
                # Add a new dimension.
                cpmg_frqs_new.append([])

                # Then loop over the spectrometer frequencies.
                for mi in range(len(cpmg_frqs[ei])):
                    # Add a new dimension.
                    cpmg_frqs_new[ei].append([])

                    # Finally the offsets.
                    for oi in range(len(cpmg_frqs[ei][mi])):
                        # Add a new dimension.
                        cpmg_frqs_new[ei][mi].append([])

                        # No data.
                        if not len(cpmg_frqs[ei][mi][oi]):
                            continue

                        # Interpolate (adding the extended amount to the end).
                        for di in range(num_points):
                            point = (di + 1) * (max(cpmg_frqs[ei][mi][oi])+extend_hz) / num_points
                            cpmg_frqs_new[ei][mi][oi].append(point)

                        # Convert to a numpy array.
                        cpmg_frqs_new[ei][mi][oi] = array(cpmg_frqs_new[ei][mi][oi], float64)

    # Interpolate the spin-lock field strengths.
    spin_lock_nu1 = return_spin_lock_nu1(ref_flag=False)

    if spin_lock_nu1 != None and len(spin_lock_nu1[0][0][0]):
        spin_lock_nu1_new = []
        for ei in range(len(spin_lock_nu1)):
            # Add a new dimension.
            spin_lock_nu1_new.append([])

            # Then loop over the spectrometer frequencies.
            for mi in range(len(spin_lock_nu1[ei])):
                # Add a new dimension.
                spin_lock_nu1_new[ei].append([])

                # Finally the offsets.
                for oi in range(len(spin_lock_nu1[ei][mi])):
                    # Add a new dimension.
                    spin_lock_nu1_new[ei][mi].append([])

                    # No data.
                    if not len(spin_lock_nu1[ei][mi][oi]):
                        continue

                    # Interpolate (adding the extended amount to the end).
                    for di in range(num_points):
                        point = (di + 1) * (max(spin_lock_nu1[ei][mi][oi])+extend_hz) / num_points
                        spin_lock_nu1_new[ei][mi][oi].append(point)

                    # Convert to a numpy array.
                    spin_lock_nu1_new[ei][mi][oi] = array(spin_lock_nu1_new[ei][mi][oi], float64)

    # Number of spectrometer fields.
    fields = [None]
    field_count = 1
    if hasattr(cdp, 'spectrometer_frq_count'):
        fields = cdp.spectrometer_frq_list
        field_count = cdp.spectrometer_frq_count

    # The offset data.
    if spin.model in MODEL_LIST_R1RHO_FULL and has_r1rho_exp_type():
        offsets, spin_lock_fields_inter, chemical_shifts, tilt_angles, Delta_omega, w_eff = return_offset_data(spins=[spin], spin_ids=[spin_id], field_count=field_count, fields=spin_lock_nu1_new)
    else:
        offsets, spin_lock_fields_inter, chemical_shifts, tilt_angles, Delta_omega, w_eff = return_offset_data(spins=[spin], spin_ids=[spin_id], field_count=field_count, fields=cpmg_frqs_new)

    if spin.model == MODEL_R2EFF:
        back_calc = None
    else:
        # Back calculate R2eff data for the second sets of plots.
        back_calc = specific_analyses.relax_disp.optimisation.back_calc_r2eff(spin=spin, spin_id=spin_id, cpmg_frqs=cpmg_frqs_new, spin_lock_nu1=spin_lock_nu1_new)

    return interpolated_flag, back_calc, cpmg_frqs_new, offsets, spin_lock_fields_inter, chemical_shifts, tilt_angles, Delta_omega, w_eff


def interpolate_offset(spin=None, spin_id=None, si=None, num_points=None, extend_ppm=None):
    """Interpolate function for 2D Grace plotting function for the dispersion curves, interpolating through spin-lock offset in rad/s.

    @keyword spin:          The specific spin data container.
    @type spin:             SpinContainer instance.
    @keyword spin_id:       The spin ID string.
    @type spin_id:          str
    @keyword si:            The index of the given spin in the cluster.
    @type si:               int
    @keyword num_points:    The number of points to generate the interpolated fitted curves with.
    @type num_points:       int
    @keyword extend_ppm:    How far to extend the interpolated fitted curves to in offset ppm.
    @type extend_ppm:       float
    @return:                The interpolated_flag, list of back calculated R2eff/R1rho values in rad/s {Ei, Si, Mi, Oi, Di}, list of interpolated frequencies for cpmg_frqs in Hz {Ei, Si, Mi, Oi, Di}, interpolated spin-lock offsets in rad/s {Ei, Si, Mi, Oi}, list of interpolated spin-lock field strength frequencies for spin_lock_nu1_new in Hz {Ei, Si, Mi, Oi, Di}, chemical shifts in rad/s {Ei, Si, Mi}, interpolated rotating frame tilt angles theta {Ei, Si, Mi, Oi, Di}, interpolated average resonance offset in the rotating frame Omega in rad/s {Ei, Si, Mi, Oi, Di} and the interpolated effective field in rotating frame w_eff in rad/s {Ei, Si, Mi, Oi, Di}.
    @rtype:                 boolean, rank-4 list of numpy rank-1 float arrays, rank-4 list of numpy rank-1 float arrays, rank-3 list of numpy rank-1 float arrays, rank-4 list of numpy rank-1 float arrays, rank-2 list of numpy rank-1 float arrays, rank-4 list of numpy rank-1 float arrays, rank-4 list of numpy rank-1 float arrays, rank-4 list of numpy rank-1 float arrays
    """

    # Set the flag.
    interpolated_flag = True

    # Initialise some structures.
    spin_lock_offset_new = []

    # Get the spin-lock field strengths.
    spin_lock_nu1 = return_spin_lock_nu1(ref_flag=False)

    # Get the current minimum and maximum spin_lock_offset
    if not hasattr(cdp, 'spin_lock_offset'):
        min_offset = 0
        max_offset = 0

    else:
        min_offset = min(cdp.spin_lock_offset_list)
        max_offset = max(cdp.spin_lock_offset_list)

    if spin_lock_nu1 != None and len(spin_lock_nu1[0][0][0]):
        for ei in range(len(spin_lock_nu1)):
            # Add a new dimension for ei.
            spin_lock_offset_new.append([])

            # Add a new dimension for si.
            spin_lock_offset_new[ei].append([])

            # Then loop over the spectrometer frequencies.
            for mi in range(len(spin_lock_nu1[ei])):
                # Add a new dimension for mi.
                spin_lock_offset_new[ei][0].append([])

                # Interpolate (adding the extended amount to the end).
                for oi in range(num_points+1):
                    offset_point = oi * (max_offset+extend_ppm) / num_points
                    spin_lock_offset_new[ei][0][mi].append(offset_point)

                # Convert to a numpy array.
                spin_lock_offset_new[ei][0][mi] = array(spin_lock_offset_new[ei][0][mi], float64)

    # Number of spectrometer fields.
    fields = [None]
    field_count = 1
    if hasattr(cdp, 'spectrometer_frq_count'):
        fields = cdp.spectrometer_frq_list
        field_count = cdp.spectrometer_frq_count

    # The offset data.
    offsets, spin_lock_fields_inter, chemical_shifts, tilt_angles, Delta_omega, w_eff = return_offset_data(spins=[spin], spin_ids=[spin_id], field_count=field_count, spin_lock_offset=spin_lock_offset_new, fields=spin_lock_nu1)

    if spin.model == MODEL_R2EFF:
        back_calc = None
    else:
        # Back calculate R2eff data for the second sets of plots.
        back_calc = specific_analyses.relax_disp.optimisation.back_calc_r2eff(spin=spin, spin_id=spin_id, spin_lock_offset=spin_lock_offset_new, spin_lock_nu1=spin_lock_fields_inter)

    # cpmg_frqs are not interpolated.
    cpmg_frqs_new = None

    return interpolated_flag, back_calc, cpmg_frqs_new, offsets, spin_lock_fields_inter, chemical_shifts, tilt_angles, Delta_omega, w_eff


def is_cpmg_exp_type(id=None):
    """Determine if the given spectrum ID corresponds to a CPMG experiment type.

    @keyword id:    The spectrum ID string.
    @type id:       str
    @return:        True if the spectrum ID corresponds to a CPMG experiment type, False otherwise.
    @rtype:         bool
    """

    # No experiment type set.
    if not hasattr(cdp, 'exp_type') or id not in cdp.exp_type:
        return False

    # CPMG experiment type.
    if cdp.exp_type[id] in EXP_TYPE_LIST_CPMG:
        return True

    # Not a CPMG experiment type.
    return False


def is_r1rho_exp_type(id=None):
    """Determine if the given spectrum ID corresponds to a R1rho experiment type.

    @keyword id:    The spectrum ID string.
    @type id:       str
    @return:        True if the spectrum ID corresponds to a R1rho experiment type, False otherwise.
    @rtype:         bool
    """

    # No experiment type set.
    if not hasattr(cdp, 'exp_type') or id not in cdp.exp_type:
        return False

    # R1rho experiment type.
    if cdp.exp_type[id] in EXP_TYPE_LIST_R1RHO:
        return True

    # Not a R1rho experiment type.
    return False


def loop_cluster(skip_desel=True):
    """Loop over the spin groupings for one model applied to multiple spins.

    @keyword skip_desel:    A flag which if True will cause deselected spins or spin clusters to be skipped.
    @type skip_desel:       bool
    @return:                The list of spin IDs per block will be yielded.
    @rtype:                 list of str
    """

    # No clustering, so loop over the sequence.
    if not hasattr(cdp, 'clustering'):
        for spin, spin_id in spin_loop(return_id=True, skip_desel=skip_desel):
            # Skip protons for MMQ data.
            if hasattr(spin, 'model') and spin.model in MODEL_LIST_MMQ and spin.isotope == '1H':
                continue

            # Return the spin ID as a list.
            yield [spin_id]

    # Loop over the clustering.
    else:
        # The clusters.
        for key in cdp.clustering.keys():
            # Skip the free spins.
            if key == 'free spins':
                continue

            # Create the spin ID lists.
            spin_id_list = []
            for spin_id in cdp.clustering[key]:
                # Skip deselected spins.
                spin = return_spin(spin_id)
                if skip_desel and not spin.select:
                    continue

                # Skip protons for MMQ data.
                if hasattr(spin, 'model') and spin.model in MODEL_LIST_MMQ and spin.isotope == '1H':
                    continue

                # Add the spin ID.
                spin_id_list.append(spin_id)

            # Yield the cluster.
            yield spin_id_list

        # The free spins.
        for spin_id in cdp.clustering['free spins']:
            # Skip deselected spins.
            spin = return_spin(spin_id)
            if skip_desel and not spin.select:
                continue

            # Skip protons for MMQ data.
            if hasattr(spin, 'model') and spin.model in MODEL_LIST_MMQ and spin.isotope == '1H':
                continue

            # Yield each spin individually.
            yield [spin_id]


def loop_exp(return_indices=False):
    """Generator method for looping over all experiment types.

    @keyword return_indices:    A flag which if True will cause the experiment type index to be returned as well.
    @type return_indices:       bool
    @return:                    The experiment type, and the index if asked.
    @rtype:                     str, (int)
    """

    # Initialise the index.
    ei = -1

    # Loop over the experiment types.
    for exp_type in cdp.exp_type_list:
        # Increment the index.
        ei += 1

        # Yield each unique experiment type.
        if return_indices:
            yield exp_type, ei
        else:
            yield exp_type


def loop_exp_frq(return_indices=False):
    """Generator method for looping over the exp and frq data.
    
    These are the experiment types and spectrometer frequencies.


    @keyword return_indices:    A flag which if True will cause the experiment type and spectrometer frequency indices to be returned as well.
    @type return_indices:       bool
    @return:                    The experiment type and spectrometer frequency in Hz, and the indices if asked.
    @rtype:                     str, float, (int, int)
    """

    # First loop over the experiment types.
    for exp_type, ei in loop_exp(return_indices=True):
        # Then loop over the spectrometer frequencies.
        for frq, mi in loop_frq(return_indices=True):
            # Yield the data.
            if return_indices:
                yield exp_type, frq, ei, mi
            else:
                yield exp_type, frq


def loop_exp_frq_offset(return_indices=False):
    """Generator method for looping over the exp, frq, and offset data.
    
    These are the experiment types, spectrometer frequencies and spin-lock offset data.


    @keyword return_indices:    A flag which if True will cause the experiment type, spectrometer frequency and spin-lock offset indices to be returned as well.
    @type return_indices:       bool
    @return:                    The experiment type, spectrometer frequency in Hz and spin-lock offset data, and the indices if asked.
    @rtype:                     str, float, float, (int, int, int)
    """

    # First loop over the experiment types.
    for exp_type, ei in loop_exp(return_indices=True):
        # Then loop over the spectrometer frequencies.
        for frq, mi in loop_frq(return_indices=True):
            # And finally the offset data.
            for offset, oi in loop_offset(exp_type=exp_type, frq=frq, return_indices=True):
                # Yield the data.
                if return_indices:
                    yield exp_type, frq, offset, ei, mi, oi
                else:
                    yield exp_type, frq, offset


def loop_exp_frq_offset_point(return_indices=False):
    """Generator method for looping over the exp, frq, offset, and point data.
    
    These are the experiment types, spectrometer frequencies, spin-lock offset data,  and dispersion points.


    @keyword return_indices:    A flag which if True will cause the experiment type, spectrometer frequency, spin-lock offset and dispersion point indices to be returned as well.
    @type return_indices:       bool
    @return:                    The experiment type, spectrometer frequency in Hz, spin-lock offset data and dispersion point data (either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz), and the indices if asked.
    @rtype:                     str, float, float, float, (int, int, int, int)
    """

    # First loop over the experiment types.
    for exp_type, ei in loop_exp(return_indices=True):
        # Then loop over the spectrometer frequencies.
        for frq, mi in loop_frq(return_indices=True):
            # Then loop over the offset data.
            for offset, oi in loop_offset(exp_type=exp_type, frq=frq, return_indices=True):
                # And finally the dispersion points.
                for point, di in loop_point(exp_type=exp_type, frq=frq, offset=offset, return_indices=True):
                    # Yield the data.
                    if return_indices:
                        yield exp_type, frq, offset, point, ei, mi, oi, di
                    else:
                        yield exp_type, frq, offset, point


def loop_exp_frq_offset_point_time(return_indices=False):
    """Generator method for looping over the exp, frq, offset, and point data.
    
    These are the experiment types, spectrometer frequencies, spin-lock offset data,  and dispersion points.


    @keyword return_indices:    A flag which if True will cause the experiment type, spectrometer frequency, spin-lock offset and dispersion point indices to be returned as well.
    @type return_indices:       bool
    @return:                    The experiment type, spectrometer frequency in Hz, spin-lock offset data and dispersion point data (either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz), and the indices if asked.
    @rtype:                     str, float, float, float, (int, int, int, int)
    """

    # First loop over the experiment types.
    for exp_type, ei in loop_exp(return_indices=True):
        # Then loop over the spectrometer frequencies.
        for frq, mi in loop_frq(return_indices=True):
            # Then loop over the offset data.
            for offset, oi in loop_offset(exp_type=exp_type, frq=frq, return_indices=True):
                # Then the dispersion points.
                for point, di in loop_point(exp_type=exp_type, frq=frq, offset=offset, return_indices=True):
                    # Finally the relaxation times.
                    for time, ti in loop_time(exp_type=exp_type, frq=frq, offset=offset, point=point, return_indices=True):
                        # Yield the data.
                        if return_indices:
                            yield exp_type, frq, offset, point, time, ei, mi, oi, di, ti
                        else:
                            yield exp_type, frq, offset, point, time


def loop_exp_frq_point(return_indices=False):
    """Generator method for looping over the exp, frq, and point data.
    
    These are the experiment types, spectrometer frequencies and dispersion points.


    @keyword return_indices:    A flag which if True will cause the experiment type, spectrometer frequency and dispersion point indices to be returned as well.
    @type return_indices:       bool
    @return:                    The experiment type, spectrometer frequency in Hz and dispersion point data (either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz), and the indices if asked.
    @rtype:                     str, float, float, (int, int, int)
    """

    # First loop over the experiment types.
    for exp_type, ei in loop_exp(return_indices=True):
        # Then loop over the spectrometer frequencies.
        for frq, mi in loop_frq(return_indices=True):
            # And finally the dispersion points.
            for point, di in loop_point(exp_type=exp_type, frq=frq, offset=0.0, return_indices=True):
                # Yield the data.
                if return_indices:
                    yield exp_type, frq, point, ei, mi, di
                else:
                    yield exp_type, frq, point


def loop_exp_frq_point_time(return_indices=False):
    """Generator method for looping over the exp, frq, point, and time data.
    
    These are the experiment types, spectrometer frequencies, dispersion points, and relaxation times.


    @keyword return_indices:    A flag which if True will cause the experiment type, spectrometer frequency, dispersion point, and relaxation time indices to be returned as well.
    @type return_indices:       bool
    @return:                    The experiment type, spectrometer frequency in Hz, dispersion point data (either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz), the relaxation time, and the indices if asked.
    @rtype:                     str, float, float, float, (int, int, int, int)
    """

    # First loop over the experiment types.
    for exp_type, ei in loop_exp(return_indices=True):
        # Then the spectrometer frequencies.
        for frq, mi in loop_frq(return_indices=True):
            # Then the dispersion points.
            for point, di in loop_point(exp_type=exp_type, frq=frq, offset=0.0, return_indices=True):
                # Finally the relaxation times.
                for time, ti in loop_time(exp_type=exp_type, frq=frq, point=point, return_indices=True):
                    # Yield all data.
                    if return_indices:
                        yield exp_type, frq, point, time, ei, mi, di, ti
                    else:
                        yield exp_type, frq, point, time


def loop_frq(return_indices=False):
    """Generator method for looping over all spectrometer frequencies.

    @keyword return_indices:    A flag which if True will cause the spectrometer frequency index to be returned as well.
    @type return_indices:       bool
    @return:                    The spectrometer frequency in Hz, and the index if asked.
    @rtype:                     float, (int)
    """

    # Handle missing frequency data.
    frqs = [None]
    if hasattr(cdp, 'spectrometer_frq_list'):
        frqs = cdp.spectrometer_frq_list

    # Initialise the index.
    mi = -1

    # Loop over the spectrometer frequencies.
    for field in frqs:
        # Increment the index.
        mi += 1

        # Yield each unique spectrometer field strength.
        if return_indices:
            yield field, mi
        else:
            yield field


def loop_frq_offset(exp_type=None, return_indices=False):
    """Generator method for looping over the spectrometer frequencies and dispersion points.

    @keyword exp_type:          The experiment type.
    @type exp_type:             str
    @keyword return_indices:    A flag which if True will cause the spectrometer frequency and dispersion point indices to be returned as well.
    @type return_indices:       bool
    @return:                    The spectrometer frequency in Hz and dispersion point data (either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz).
    @rtype:                     float, float, (int, int)
    """

    # Checks.
    if exp_type == None:
        raise RelaxError("The experiment type must be supplied.")

    # First loop over the spectrometer frequencies.
    for frq, mi in loop_frq(return_indices=True):
        # Then the offset points.
        for offset, oi in loop_offset(exp_type=exp_type, frq=frq, return_indices=True):
            # Yield the data.
            if return_indices:
                yield frq, offset, mi, oi
            else:
                yield frq, offset


def loop_frq_point(exp_type=None, return_indices=False):
    """Generator method for looping over the spectrometer frequencies and dispersion points.

    @keyword exp_type:          The experiment type.
    @type exp_type:             str
    @keyword return_indices:    A flag which if True will cause the spectrometer frequency and dispersion point indices to be returned as well.
    @type return_indices:       bool
    @return:                    The spectrometer frequency in Hz and dispersion point data (either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz).
    @rtype:                     float, float, (int, int)
    """

    # First loop over the spectrometer frequencies.
    for frq, mi in loop_frq(return_indices=True):
        # Then the dispersion points.
        for point, di in loop_point(exp_type=exp_type, frq=frq, offset=0.0, return_indices=True):
            # Yield the data.
            if return_indices:
                yield frq, point, mi, di
            else:
                yield frq, point


def loop_frq_offset_point_key(exp_type=None):
    """Generator method for looping over the spectrometer frequencies, spin-lock offsets and dispersion points (returning the key).

    @keyword exp_type:  The experiment type.
    @type exp_type:     str
    @return:            The key corresponding to the spectrometer frequency, offset and dispersion point.
    @rtype:             str
    """

    # First loop over the spectrometer frequencies, offsets and dispersion points.
    for frq, offset, point in loop_frq_offset_point(return_indices=True):
        # Generate and yield the key.
        yield return_param_key_from_data(exp_type=exp_type, frq=frq, offset=offset, point=point)


def loop_frq_point_time(exp_type=None, return_indices=False):
    """Generator method for looping over the spectrometer frequencies, dispersion points, and relaxation times.

    @keyword exp_type:          The experiment type.
    @type exp_type:             str
    @keyword return_indices:    A flag which if True will cause the spectrometer frequency, dispersion point, and relaxation time indices to be returned as well.
    @type return_indices:       bool
    @return:                    The spectrometer frequency in Hz, dispersion point data (either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz), and the relaxation time.
    @rtype:                     float, float, float
    """

    # First loop over the spectrometer frequencies.
    for frq, mi in loop_frq(return_indices=True):
        # Then the dispersion points.
        for point, di in loop_point(exp_type=exp_type, frq=frq, offset=0.0, return_indices=True):
            # Finally the relaxation times.
            for time, ti in loop_time(exp_type=exp_type, frq=frq, point=point, return_indices=True):
                # Yield all data.
                if return_indices:
                    yield frq, point, time, mi, di, ti
                else:
                    yield frq, point, time


def loop_offset(exp_type=None, frq=None, return_indices=False):
    """Generator method for looping over the spin-lock offset values.

    @keyword exp_type:          The experiment type.
    @type exp_type:             str
    @keyword frq:               The spectrometer frequency.
    @type frq:                  float
    @keyword return_indices:    A flag which if True will cause the offset index to be returned as well.
    @type return_indices:       bool
    @return:                    The spin-lock offset value and the index if asked.
    @rtype:                     float, (int)
    """

    # Checks.
    if exp_type == None:
        raise RelaxError("The experiment type must be supplied.")
    if frq == None:
        raise RelaxError("The spectrometer frequency must be supplied.")

    # Initialise the index.
    oi = -1

    # CPMG-type data.
    if exp_type in EXP_TYPE_LIST_CPMG:
        # Yield a single set of dummy values until hard pulse offset handling is implemented.
        yield 0.0, 0

    # R1rho-type data.
    if exp_type in EXP_TYPE_LIST_R1RHO:
        # No offsets set.
        if not hasattr(cdp, 'spin_lock_offset_list'):
            yield 0.0, 0

        # Loop over the offset data.
        else:
            for offset in cdp.spin_lock_offset_list:
                # Find a matching experiment ID.
                found = False
                for id in cdp.exp_type.keys():
                    # Skip non-matching experiments.
                    if cdp.exp_type[id] != exp_type:
                        continue

                    # Skip non-matching spectrometer frequencies.
                    if hasattr(cdp, 'spectrometer_frq') and cdp.spectrometer_frq[id] != frq:
                        continue

                    # Skip non-matching offsets.
                    if cdp.spin_lock_offset[id] != offset:
                        continue

                    # Found.
                    found = True
                    break

                # No data.
                if not found:
                    continue

                # Increment the index.
                oi += 1

                # Yield each unique field strength or frequency.
                if return_indices:
                    yield offset, oi
                else:
                    yield offset


def loop_offset_point(exp_type=None, frq=None, skip_ref=True, return_indices=False):
    """Generator method for looping over the offsets and dispersion points.

    @keyword exp_type:          The experiment type.
    @type exp_type:             str
    @keyword frq:               The spectrometer frequency.
    @type frq:                  float
    @keyword skip_ref:          A flag which if True will cause the reference point to be skipped.
    @type skip_ref:             bool
    @keyword return_indices:    A flag which if True will cause the offset and dispersion point indices to be returned as well.
    @type return_indices:       bool
    @return:                    The offsets in ppm and the dispersion point data (either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz), and the index if asked.
    @rtype:                     float, float, (int, int)
    """

    # First loop over the offsets.
    for offset, oi in loop_offset(exp_type=exp_type, frq=frq, return_indices=True):
        # Then the dispersion points.
        for point, di in loop_point(exp_type=exp_type, frq=frq, offset=offset, return_indices=True):
            # Yield all data.
            if return_indices:
                yield offset, point, oi, di
            else:
                yield offset, point


def loop_point(exp_type=None, frq=None, offset=None, time=None, skip_ref=True, return_indices=False):
    """Generator method for looping over the dispersion points.

    @keyword exp_type:          The experiment type.
    @type exp_type:             str
    @keyword frq:               The spectrometer frequency.
    @type frq:                  float
    @keyword offset:            The spin-lock or hard pulse offset value in ppm.
    @type offset:               None or float
    @keyword time:              The relaxation time period.
    @type time:                 float
    @keyword skip_ref:          A flag which if True will cause the reference point to be skipped.
    @type skip_ref:             bool
    @keyword return_indices:    A flag which if True will cause the experiment type index to be returned as well.
    @type return_indices:       bool
    @return:                    Dispersion point data for the given indices (either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz), and the index if asked.
    @rtype:                     float, (int)
    """

    # Checks.
    if exp_type == None:
        raise RelaxError("The experiment type must be supplied.")
    if frq == None:
        raise RelaxError("The spectrometer frequency must be supplied.")
    if offset == None:
        raise RelaxError("The offset must be supplied.")

    # Assemble the dispersion data.
    ref_flag = not skip_ref
    if exp_type in EXP_TYPE_LIST_CPMG:
        fields = return_cpmg_frqs_single(exp_type=exp_type, frq=frq, offset=offset, time=time, ref_flag=ref_flag)
    elif exp_type in EXP_TYPE_LIST_R1RHO:
        fields = return_spin_lock_nu1_single(exp_type=exp_type, frq=frq, offset=offset, ref_flag=ref_flag)
    else:
        raise RelaxError("The experiment type '%s' is unknown." % exp_type)

    # Initialise the index.
    di = -1

    # Loop over the field data.
    for field in fields:
        # Skip the reference (the None value will be converted to the numpy nan value).
        if skip_ref and isNaN(field):
            continue

        # Increment the index.
        di += 1

        # Yield each unique field strength or frequency.
        if return_indices:
            yield field, di
        else:
            yield field


def loop_spectrum_ids(exp_type=None, frq=None, offset=None, point=None, time=None):
    """Generator method for selectively looping over the spectrum IDs.

    @keyword exp_type:  The experiment type.
    @type exp_type:     str
    @keyword frq:       The spectrometer frequency.
    @type frq:          float
    @keyword offset:    For R1rho-type data, the spin-lock offset value in ppm.
    @type offset:       None or float
    @keyword point:     The dispersion point data (either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz).
    @type point:        float
    @keyword time:      The relaxation time period.
    @type time:         float
    @return:            The spectrum ID.
    @rtype:             str
    """

    # Loop over all spectrum IDs.
    for id in cdp.spectrum_ids:
        # Experiment type filter.
        if exp_type != None:
            # No experiment type set.
            if not hasattr(cdp, 'exp_type') or id not in cdp.exp_type:
                continue

            # No match.
            if cdp.exp_type[id] != exp_type:
                continue

        # The frequency filter.
        if frq != None:
            # No frequency data set.
            if not hasattr(cdp, 'spectrometer_frq') or id not in cdp.spectrometer_frq:
                continue

            # No match.
            if cdp.spectrometer_frq[id] != frq:
                continue

        # The dispersion point filter.
        if point != None:
            # No experiment type set.
            if not hasattr(cdp, 'exp_type') or id not in cdp.exp_type:
                continue

            # The experiment type.
            exp_type = cdp.exp_type[id]

            # The CPMG dispersion data.
            if exp_type in EXP_TYPE_LIST_CPMG:
                # No dispersion point data set.
                if not hasattr(cdp, 'cpmg_frqs') or id not in cdp.cpmg_frqs:
                    continue

                # Alias the structure
                disp_data = cdp.cpmg_frqs

            # The R1rho dispersion data.
            else:
                # No dispersion point data set.
                if not hasattr(cdp, 'spin_lock_nu1') or id not in cdp.spin_lock_nu1:
                    continue

                # Alias the structure
                disp_data = cdp.spin_lock_nu1

            # No match.
            if disp_data[id] != point:
                continue

        # The time filter.
        if time != None:
            # No time data set.
            if not hasattr(cdp, 'relax_times') or id not in cdp.relax_times:
                continue

            # No match.
            if cdp.relax_times[id] != time:
                continue

        # Yield the Id.
        yield id


def loop_time(exp_type=None, frq=None, offset=None, point=None, return_indices=False):
    """Generator method for looping over the relaxation times.

    @keyword exp_type:          The experiment type.
    @type exp_type:             str
    @keyword frq:               The spectrometer frequency in Hz.
    @type frq:                  float
    @keyword offset:            The spin-lock or hard pulse offset value in ppm.
    @type offset:               None or float
    @keyword point:             The dispersion point data (either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz).
    @type point:                float
    @keyword return_indices:    A flag which if True will cause the relaxation time index to be returned as well.
    @type return_indices:       bool
    @return:                    The relaxation time.
    @rtype:                     float
    """

    # Initialise the index.
    ti = -1

    # Loop over the time points.
    if hasattr(cdp, 'relax_time_list'):
        for time in cdp.relax_time_list:
            # Find a matching experiment ID.
            found = False
            for id in cdp.exp_type.keys():
                # Skip non-matching experiments.
                if exp_type != None and cdp.exp_type[id] != exp_type:
                    continue

                # Skip non-matching spectrometer frequencies.
                if frq != None and hasattr(cdp, 'spectrometer_frq') and cdp.spectrometer_frq[id] != frq:
                    continue

                # Skip non-matching offsets.
                if offset != None and hasattr(cdp, 'spin_lock_offset') and cdp.spin_lock_offset[id] != offset:
                    continue

                # The dispersion point filter.
                if point != None:
                    # No experiment type set.
                    if not hasattr(cdp, 'exp_type') or id not in cdp.exp_type:
                        continue

                    # The experiment type.
                    exp_type = cdp.exp_type[id]

                    # The CPMG dispersion data.
                    if exp_type in EXP_TYPE_LIST_CPMG:
                        # No dispersion point data set.
                        if hasattr(cdp, 'cpmg_frqs') and cdp.cpmg_frqs[id] != point:
                            continue

                    # The R1rho data
                    if exp_type in EXP_TYPE_R1RHO:
                        if hasattr(cdp, 'spin_lock_nu1') and cdp.spin_lock_nu1[id] != point:
                            continue

                if time != cdp.relax_times[id]:
                    continue

                # Found.
                found = True
                break

            # No data.
            if not found:
                continue

            # Increment the index.
            ti += 1

            # Yield each unique relaxation time.
            if return_indices:
                yield time, ti
            else:
                yield time

    # No times set.
    else:
        if return_indices:
            yield None, None
        else:
            yield None


def num_exp_types():
    """Count the number of experiment types present.

    @return:    The number of experiment types.
    @rtype:     int
    """

    # The count.
    count = len(cdp.exp_type_list)

    # Return the count.
    return count


def pack_back_calc_r2eff(spin=None, spin_id=None, si=None, back_calc=None, proton_mmq_flag=False):
    """Store the back calculated R2eff data for the given spin.

    @keyword spin:              The spin data container to store the data in.
    @type spin:                 SpinContainer instance
    @keyword spin_id:           The spin ID string.
    @type spin_id:              str
    @keyword si:                The index of the given spin in the cluster.
    @type si:                   int
    @keyword back_calc:         The back calculated data.  The first index corresponds to the experiment type, the second is the spin of the cluster, the third is the magnetic field strength, and the fourth is the dispersion point.
    @type back_calc:            list of lists of lists of lists of float
    @keyword proton_mmq_flag:   The flag specifying if proton SQ or MQ CPMG data exists for the spin.
    @type proton_mmq_flag:      bool
    """

    # Get the attached proton.
    proton = None
    if proton_mmq_flag:
        proton = return_attached_protons(spin_id)[0]

    # Loop over the R2eff data.
    for exp_type, frq, offset, point, ei, mi, oi, di in loop_exp_frq_offset_point(return_indices=True):
        # The R2eff key.
        key = return_param_key_from_data(exp_type=exp_type, frq=frq, offset=offset, point=point)

        # Alias the correct spin.
        current_spin = spin
        if exp_type in [EXP_TYPE_CPMG_PROTON_SQ, EXP_TYPE_CPMG_PROTON_MQ]:
            current_spin = proton

        # Missing data.
        if not hasattr(current_spin, 'r2eff') or key not in current_spin.r2eff.keys():
            continue

        # Initialise.
        if not hasattr(current_spin, 'r2eff_bc'):
            current_spin.r2eff_bc = {}

        # Store the back-calculated data.
        current_spin.r2eff_bc[key] = back_calc[ei][si][mi][oi][di]


def plot_disp_curves(dir=None, y_axis=Y_AXIS_R2_EFF, x_axis=X_AXIS_DISP, num_points=1000, extend_hz=500.0, extend_ppm=500.0, interpolate=INTERPOLATE_DISP, force=False):
    """Custom 2D Grace plotting function for the dispersion curves.

    One file will be created per spin system.

    A python "grace to PNG/EPS/SVG..." conversion script is created at the end

    @keyword dir:           The optional directory to place the file into.
    @type dir:              str
    @keyword y_axis:        String flag to tell which data on Y axis to plot for.  Option can be either "%s" which plot 'r2eff' for CPMG experiments or 'r1rho' for R1rho experiments or option can be "%s", which for R1rho experiments plot R2 = R1rho / sin^2(theta) - R_1 / tan^2(theta) = (R1rho - R_1 * cos^2(theta) ) / sin^2(theta).
    @type y_axis:           str
    @keyword x_axis:        String flag to tell which data on X axis to plot for.  Option can be either "%s" which plot 'CPMG frequency (Hz)' for CPMG experiments or 'Spin-lock field strength (Hz)' for R1rho experiments or option can be either "%s" or "%s" for R1rho experiments, which plot 'Effective field in rotating frame (rad/s)' or 'Rotating frame tilt angle theta (rad)'.
    @type x_axis:           str
    @keyword num_points:    The number of points to generate the interpolated fitted curves with.
    @type num_points:       int
    @keyword extend_hz:     How far to extend the interpolated fitted curves to, when interpolating over CPMG frequency or spin-lock field strength (in Hz).
    @type extend_hz:        float
    @keyword extend_ppm:    How far to extend the interpolated fitted curves to, when interpolating over spin-lock offset (in ppm).
    @type extend_ppm:       float
    @keyword interpolate:   How to interpolate the fitted curves.  Either by option "%s" which interpolate CPMG frequency or spin-lock field strength, or by option "%s" which interpole over spin-lock offset.
    @type interpolate:      float
    @param force:           Boolean argument which if True causes the files to be overwritten if it already exists.
    @type force:            bool
    """%(Y_AXIS_R2_EFF, Y_AXIS_R2_R1RHO, X_AXIS_DISP, X_AXIS_W_EFF, X_AXIS_THETA, INTERPOLATE_DISP, INTERPOLATE_OFFSET)

    # Checks.
    pipes.test()
    check_mol_res_spin_data()

    # Check if interpolating against offset for CPMG models.
    # This is currently not implemented, and will raise an error.
    check_interpolate_offset_cpmg_model(interpolate=interpolate)

    # 1H MMQ flag.
    proton_mmq_flag = has_proton_mmq_cpmg()

    # Determine file name:
    file_name_ini = return_grace_file_name_ini(y_axis=y_axis, x_axis=x_axis, interpolate=interpolate)

    # Plot dispersion curves.
    plot_disp_curves_to_file(file_name_ini=file_name_ini, dir=dir, y_axis=y_axis, x_axis=x_axis, interpolate=interpolate, num_points=num_points, extend_hz=extend_hz, extend_ppm=extend_ppm, force=force, proton_mmq_flag=proton_mmq_flag)

    # Write a python "grace to PNG/EPS/SVG..." conversion script.
    # Open the file for writing.
    file_name = "grace2images.py"
    file_path = get_file_path(file_name, dir)

    # Prevent to write the file multiple times.
    if access(file_path, F_OK) and not force:
        pass

    else:
        file = open_write_file(file_name, dir, force)

        # Write the file.
        script_grace2images(file=file)

        # Close the batch script, then make it executable (expanding any ~ characters).
        file.close()
        if dir:
            dir = expanduser(dir)
            chmod(dir + sep + file_name, S_IRWXU|S_IRGRP|S_IROTH)
        else:
            file_name = expanduser(file_name)
            chmod(file_name, S_IRWXU|S_IRGRP|S_IROTH)


def plot_disp_curves_to_file(file_name_ini=None, dir=None, y_axis=None, x_axis=None, interpolate=None, num_points=None, extend_hz=None, extend_ppm=None, force=None, proton_mmq_flag=None):
    """Custom 2D Grace plotting function for the dispersion curves, interpolating theta through spin-lock offset rather than spin-lock field strength.

    One file will be created per spin system.

    @keyword file_name_ini:     The first part of the file_name.
    @type file_name_ini:        str
    @keyword dir:               The optional directory to place the file into.
    @type dir:                  str
    @keyword y_axis:            String flag to tell which data on Y axis to plot for.  Option can be either "%s" which plot 'r2eff' for CPMG experiments or 'r1rho' for R1rho experiments or option can be "%s", which for R1rho experiments plot R2 = R1rho / sin^2(theta) - R_1 / tan^2(theta) = (R1rho - R_1 * cos^2(theta) ) / sin^2(theta).
    @type y_axis:               str
    @keyword x_axis:            String flag to tell which data on X axis to plot for.  Option can be either "%s" which plot 'CPMG frequency (Hz)' for CPMG experiments or 'Spin-lock field strength (Hz)' for R1rho experiments or option can be either "%s" or "%s" for R1rho experiments, which plot 'Effective field in rotating frame (rad/s)' or 'Rotating frame tilt angle theta (rad)'.
    @type x_axis:               str
    @keyword interpolate:       How to interpolate the fitted curves.  Either by option "%s" which interpolate CPMG frequency or spin-lock field strength, or by option "%s" which interpole over spin-lock offset.
    @type interpolate:          float
    @keyword num_points:        The number of points to generate the interpolated fitted curves with.
    @type num_points:           int
    @keyword extend_hz:         How far to extend the interpolated fitted curves to, when interpolating over CPMG frequency or spin-lock field strength (in Hz).
    @type extend_hz:            float
    @keyword extend_ppm:        How far to extend the interpolated fitted curves to, when interpolating over spin-lock offset (in ppm).
    @type extend_ppm:           float
    @param force:               Boolean argument which if True causes the files to be overwritten if it already exists.
    @type force:                bool
    @keyword proton_mmq_flag:   The flag specifying if proton SQ or MQ CPMG data exists for the spin.
    @type proton_mmq_flag:      bool
    """%(Y_AXIS_R2_EFF, Y_AXIS_R2_R1RHO, X_AXIS_DISP, X_AXIS_W_EFF, X_AXIS_THETA, INTERPOLATE_DISP, INTERPOLATE_OFFSET)

    # Loop over each spin. Initialise spin counter.
    si = 0
    for spin, mol_name, res_num, res_name, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
        # Skip protons for MMQ data.
        if spin.model in MODEL_LIST_MMQ and spin.isotope == '1H':
            continue

        # Initialise some data structures.
        data = []
        set_labels = []
        x_err_flag = False
        y_err_flag = False
        axis_labels = []
        set_colours = []
        x_axis_type_zero = []
        symbols = []
        symbol_sizes = []
        linetype = []
        linestyle = []

        # Set up the interpolated curve data structures.
        interpolated_flag = False

        # The unique file name.
        file_name = "%s%s.agr" % (file_name_ini, spin_id.replace('#', '_').replace(':', '_').replace('@', '_'))

        if interpolate == INTERPOLATE_DISP:
            # Interpolate through disp points.
            interpolated_flag, back_calc, cpmg_frqs_new, offsets_inter, spin_lock_nu1_new, chemical_shifts, tilt_angles_inter, Delta_omega_inter, w_eff_inter = interpolate_disp(spin=spin, spin_id=spin_id, si=si, num_points=num_points, extend_hz=extend_hz)

        elif interpolate == INTERPOLATE_OFFSET:
            # Interpolate through disp points.
            interpolated_flag, back_calc, cpmg_frqs_new, offsets_inter, spin_lock_nu1_new, chemical_shifts, tilt_angles_inter, Delta_omega_inter, w_eff_inter = interpolate_offset(spin=spin, spin_id=spin_id, si=si, num_points=num_points, extend_ppm=extend_ppm)

        # Do not interpolate, if model is R2eff.
        if spin.model == MODEL_R2EFF:
            interpolated_flag = False

        # Open the file for writing.
        file_path = get_file_path(file_name, dir)
        file = open_write_file(file_name, dir, force)

        # Get the attached proton.
        proton = None
        if proton_mmq_flag:
            proton = return_attached_protons(spin_id)[0]

        # Loop over each experiment type.
        graph_index = 0
        for exp_type, ei in loop_exp(return_indices=True):
            # Update the structures.
            data.append([])
            set_labels.append([])
            set_colours.append([])
            x_axis_type_zero.append([])
            symbols.append([])
            symbol_sizes.append([])
            linetype.append([])
            linestyle.append([])

            # Alias the correct spin.
            current_spin = spin
            if exp_type in [EXP_TYPE_CPMG_PROTON_SQ, EXP_TYPE_CPMG_PROTON_MQ]:
                current_spin = proton

            # Loop over the spectrometer frequencies and offsets.
            if interpolate == INTERPOLATE_DISP:
                err, data, set_labels, set_colours, x_axis_type_zero, symbols, symbol_sizes, linetype, linestyle, axis_labels = return_grace_data_vs_disp(y_axis=y_axis, x_axis=x_axis, interpolate=interpolate, exp_type=exp_type, ei=ei, current_spin=current_spin, spin_id=spin_id, si=si, back_calc=back_calc, cpmg_frqs_new=cpmg_frqs_new, spin_lock_nu1_new=spin_lock_nu1_new, chemical_shifts=chemical_shifts, offsets_inter=offsets_inter, tilt_angles_inter=tilt_angles_inter, Delta_omega_inter=Delta_omega_inter, w_eff_inter=w_eff_inter, interpolated_flag=interpolated_flag, graph_index=graph_index, data=data, set_labels=set_labels, set_colours=set_colours, x_axis_type_zero=x_axis_type_zero, symbols=symbols, symbol_sizes=symbol_sizes, linetype=linetype, linestyle=linestyle, axis_labels=axis_labels)

            elif interpolate == INTERPOLATE_OFFSET:
                err, data, set_labels, set_colours, x_axis_type_zero, symbols, symbol_sizes, linetype, linestyle, axis_labels = return_grace_data_vs_offset(y_axis=y_axis, x_axis=x_axis, interpolate=interpolate, exp_type=exp_type, ei=ei, current_spin=current_spin, spin_id=spin_id, si=si, back_calc=back_calc, cpmg_frqs_new=cpmg_frqs_new, spin_lock_nu1_new=spin_lock_nu1_new, chemical_shifts=chemical_shifts, offsets_inter=offsets_inter, tilt_angles_inter=tilt_angles_inter, Delta_omega_inter=Delta_omega_inter, w_eff_inter=w_eff_inter, interpolated_flag=interpolated_flag, graph_index=graph_index, data=data, set_labels=set_labels, set_colours=set_colours, x_axis_type_zero=x_axis_type_zero, symbols=symbols, symbol_sizes=symbol_sizes, linetype=linetype, linestyle=linestyle, axis_labels=axis_labels)

            # Increment the graph index.
            graph_index += 1

        # Remove all NaN values.
        for i in range(len(data)):
            for j in range(len(data[i])):
                for k in range(len(data[i][j])):
                    for l in range(len(data[i][j][k])):
                        if isNaN(data[i][j][k][l]):
                            data[i][j][k][l] = 0.0

        # Write the header.
        spin_string = generate_spin_string(spin=spin, mol_name=mol_name, res_num=res_num, res_name=res_name)
        title = "Relaxation dispersion plot for: %s"%(spin_string)
        if interpolate == INTERPOLATE_DISP:
            subtitle = "Interpolated through Spin-lock field strength \\xw\\B\\s1\\N"
        elif interpolate == INTERPOLATE_OFFSET:
            subtitle = "Interpolated through Spin-lock offset \\xw\\B\\srf\\N"

        graph_num = len(data)
        sets = []
        legend = []
        for gi in range(len(data)):
            sets.append(len(data[gi]))
            legend.append(False)
        legend[0] = True
        write_xy_header(file=file, title=title, subtitle=subtitle, graph_num=graph_num, sets=sets, set_names=set_labels, set_colours=set_colours, x_axis_type_zero=x_axis_type_zero, symbols=symbols, symbol_sizes=symbol_sizes, linetype=linetype, linestyle=linestyle, axis_labels=axis_labels, legend=legend, legend_box_fill_pattern=[0]*graph_num, legend_char_size=[0.8]*graph_num)

        # Write the data.
        graph_type = 'xy'
        if err:
            graph_type = 'xydy'
        write_xy_data(data, file=file, graph_type=graph_type)

        # Close the file.
        file.close()

        # Add the file to the results file list.
        add_result_file(type='grace', label='Grace', file=file_path)


def plot_exp_curves(file=None, dir=None, force=None, norm=None):
    """Custom 2D Grace plotting function for the exponential curves.

    @keyword file:          The name of the Grace file to create.
    @type file:             str
    @keyword dir:           The optional directory to place the file into.
    @type dir:              str
    @param force:           Boolean argument which if True causes the file to be overwritten if it already exists.
    @type force:            bool
    @keyword norm:          The normalisation flag which if set to True will cause all graphs to be normalised to a starting value of 1.
    @type norm:             bool
    """

    # Test if the current pipe exists.
    pipes.test()

    # Test if the sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Open the file for writing.
    file_path = get_file_path(file, dir)
    file = open_write_file(file, dir, force)

    # Initialise some data structures.
    data = []
    set_labels = []
    x_err_flag = False
    y_err_flag = False

    # 1H MMQ flag.
    proton_mmq_flag = has_proton_mmq_cpmg()

    # Loop over the spectrometer frequencies.
    graph_index = 0
    err = False
    for exp_type, frq, offset, ei, mi, oi in loop_exp_frq_offset(return_indices=True):
        # Loop over the dispersion points.
        for point, di in loop_point(exp_type=exp_type, frq=frq, offset=offset, return_indices=True):
            # Create a new graph.
            data.append([])

            # Loop over each spin.
            for spin, id in spin_loop(return_id=True, skip_desel=True):
                # Skip protons for MMQ data.
                if spin.model in MODEL_LIST_MMQ and spin.isotope == '1H':
                    continue

                # No data present.
                if not hasattr(spin, 'peak_intensity'):
                    continue

                # Get the attached proton.
                proton = None
                if proton_mmq_flag:
                    proton = return_attached_protons(spin_id)[0]

                # Alias the correct spin.
                current_spin = spin
                if exp_type in [EXP_TYPE_CPMG_PROTON_SQ, EXP_TYPE_CPMG_PROTON_MQ]:
                    current_spin = proton

                # Append a new set structure and set the name to the spin ID.
                data[graph_index].append([])
                if graph_index == 0:
                    set_labels.append("Spin %s" % id)

                # Loop over the relaxation time periods.
                for time in loop_time(exp_type=exp_type, frq=frq, offset=offset, point=point):
                    # The key.
                    keys = find_intensity_keys(exp_type=exp_type, frq=frq, offset=offset, point=point, time=time)

                    # Loop over each key.
                    for key in keys:
                        # No key present.
                        if key not in current_spin.peak_intensity:
                            continue

                        # Add the data.
                        if hasattr(current_spin, 'peak_intensity_err'):
                            data[graph_index][-1].append([time, current_spin.peak_intensity[key], spin.peak_intensity_err[key]])
                            err = True
                        else:
                            data[graph_index][-1].append([time, current_spin.peak_intensity[key]])

            # Increment the frq index.
            graph_index += 1

    # The axis labels.
    axis_labels = ['Relaxation time period (s)', 'Peak intensities']

    # Write the header.
    graph_num = len(data)
    sets = []
    for gi in range(graph_num):
        sets.append(len(data[gi]))
    write_xy_header(file=file, graph_num=graph_num, sets=sets, set_names=[set_labels]*graph_num, axis_labels=[axis_labels]*graph_num, norm=[norm]*graph_num)

    # Write the data.
    graph_type = 'xy'
    if err:
        graph_type = 'xydy'
    write_xy_data(data, file=file, graph_type=graph_type, norm=[norm]*graph_num)

    # Close the file.
    file.close()

    # Add the file to the results file list.
    add_result_file(type='grace', label='Grace', file=file_path)


def r20_from_min_r2eff(force=True, verbosity=1):
    """Set the R20 values to the minimum R2eff values.

    For a 2 field cpmg experiment with model CR72, that would drop number of uniform grid search point from gridNr^5 to gridNr^3.
    For standard 21 grid Nr, it would make the grid search 441 times faster. 

    @keyword force:         A flag forcing the overwriting of current values.
    @type force:            bool
    @keyword verbosity:     A flag specifying to print the setting of values.
    @type verbosity:        int
    """

    # Number of spectrometer fields.
    fields = [None]
    field_count = 1
    if hasattr(cdp, 'spectrometer_frq_count'):
        fields = cdp.spectrometer_frq_list
        field_count = cdp.spectrometer_frq_count

    # Loop over all spins.
    for spin, spin_id in spin_loop(return_id=True, skip_desel=True):
        # Nothing to do (the R2eff model has no dispersion curves).
        if spin.model == MODEL_R2EFF:
            print("The spin model is %s. The %s model has no dispersion curves, so will not set the grid values."%(spin.model, spin.model))
            continue

        # Get all the data.
        try:
            values, errors, missing, frqs, frqs_H, exp_types, relax_times = return_r2eff_arrays(spins=[spin], spin_ids=[spin_id], fields=fields, field_count=field_count)

        # No R2eff data, so skip the rest.
        except RelaxError:
            continue

        # Loop over the experiments, magnetic fields, and offsets.
        for exp_type, frq, offset, ei, mi, oi in loop_exp_frq_offset(return_indices=True):
            # No data.
            if not len(values[ei][0][mi][oi]):
                continue

            # The minimum
            min_val = values[ei][0][mi][oi].min()

            # Loop over the parameters for the current model
            for param in MODEL_PARAMS[spin.model]:
                # Check if the param is r2
                if param in PARAMS_R20:
                    # Set the value
                    value.set(val=min_val, param=param, index=mi, spin_id=spin_id, force=force)
                    if verbosity:
                        print("For %s, frq=%3.1f, offset=%3.1f, for grid search setting initial %s=%3.2f for spin: %s"%(exp_type, frq/1E6, offset, param, min_val, spin_id))


def r2eff_read(id=None, file=None, dir=None, disp_frq=None, offset=None, spin_id_col=None, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None, data_col=None, error_col=None, sep=None):
    """Read R2eff/R1rho values directly from a file whereby each row corresponds to a different spin.

    @keyword id:            The experiment ID string to associate the data with.
    @type id:               str
    @keyword file:          The name of the file to open.
    @type file:             str
    @keyword dir:           The directory containing the file (defaults to the current directory if None).
    @type dir:              str or None
    @keyword disp_frq:      For CPMG-type data, the frequency of the CPMG pulse train.  For R1rho-type data, the spin-lock field strength (nu1).  The units must be Hertz.
    @type disp_frq:         float
    @keyword offset:        For R1rho-type data, the spin-lock offset value in ppm.
    @type offset:           None or float
    @keyword spin_id_col:   The column containing the spin ID strings.  If supplied, the mol_name_col, res_name_col, res_num_col, spin_name_col, and spin_num_col arguments must be none.
    @type spin_id_col:      int or None
    @keyword mol_name_col:  The column containing the molecule name information.  If supplied, spin_id_col must be None.
    @type mol_name_col:     int or None
    @keyword res_name_col:  The column containing the residue name information.  If supplied, spin_id_col must be None.
    @type res_name_col:     int or None
    @keyword res_num_col:   The column containing the residue number information.  If supplied, spin_id_col must be None.
    @type res_num_col:      int or None
    @keyword spin_name_col: The column containing the spin name information.  If supplied, spin_id_col must be None.
    @type spin_name_col:    int or None
    @keyword spin_num_col:  The column containing the spin number information.  If supplied, spin_id_col must be None.
    @type spin_num_col:     int or None
    @keyword data_col:      The column containing the R2eff/R1rho data in Hz.
    @type data_col:         int or None
    @keyword error_col:     The column containing the R2eff/R1rho errors.
    @type error_col:        int or None
    @keyword sep:           The column separator which, if None, defaults to whitespace.
    @type sep:              str or None
    """

    # Data checks.
    pipes.test()
    check_mol_res_spin_data()
    check_frequency(id=id)
    check_exp_type(id=id)

    # Store the spectrum ID.
    add_spectrum_id(id)

    # Get the metadata.
    frq = get_frequency(id=id)
    exp_type = get_exp_type(id=id)

    # Loop over the data.
    data_flag = False
    mol_names = []
    res_nums = []
    res_names = []
    spin_nums = []
    spin_names = []
    values = []
    errors = []
    for data in read_spin_data(file=file, dir=dir, spin_id_col=spin_id_col, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, data_col=data_col, error_col=error_col, sep=sep):
        # Unpack.
        if data_col and error_col:
            mol_name, res_num, res_name, spin_num, spin_name, value, error = data
        elif data_col:
            mol_name, res_num, res_name, spin_num, spin_name, value = data
            error = None
        else:
            mol_name, res_num, res_name, spin_num, spin_name, error = data
            value = None

        # Test the error value (cannot be 0.0).
        if error == 0.0:
            raise RelaxError("An invalid error value of zero has been encountered.")

        # Get the corresponding spin container.
        spin_id = generate_spin_id_unique(mol_name=mol_name, res_num=res_num, res_name=res_name, spin_num=spin_num, spin_name=spin_name)
        spin = return_spin(spin_id)
        if spin == None:
            warn(RelaxNoSpinWarning(spin_id))
            continue

        # The dispersion point key.
        point_key = return_param_key_from_data(exp_type=exp_type, frq=frq, offset=offset, point=disp_frq)

        # Store the R2eff data.
        if data_col:
            # Initialise if necessary.
            if not hasattr(spin, 'r2eff'):
                spin.r2eff = {}

            # Store.
            spin.r2eff[point_key] = value

        # Store the R2eff error.
        if error_col:
            # Initialise if necessary.
            if not hasattr(spin, 'r2eff_err'):
                spin.r2eff_err = {}

            # Store.
            spin.r2eff_err[point_key] = error

        # Data added.
        data_flag = True

        # Append the data for printout.
        mol_names.append(mol_name)
        res_nums.append(res_num)
        res_names.append(res_name)
        spin_nums.append(spin_num)
        spin_names.append(spin_name)
        values.append(value)
        errors.append(error)

    # Print out.
    write_spin_data(file=sys.stdout, mol_names=mol_names, res_nums=res_nums, res_names=res_names, spin_nums=spin_nums, spin_names=spin_names, data=values, data_name='R2eff', error=errors, error_name='R2eff_error')

    # Update the global structures.
    if data_flag:
        # Set the dispersion point frequency.
        if exp_type in EXP_TYPE_LIST_CPMG:
            cpmg_setup(spectrum_id=id, cpmg_frq=disp_frq)
        else:
            spin_lock_field(spectrum_id=id, field=disp_frq)


def r2eff_read_spin(id=None, spin_id=None, file=None, dir=None, disp_point_col=None, offset_col=None, data_col=None, error_col=None, sep=None):
    """Read R2eff/R1rho values from file whereby each row is a different dispersion point.

    @keyword id:                The experiment ID string to associate the data with.  This will be modified to include the dispersion point data as "%s_%s" % (id, disp_point).
    @type id:                   str
    @keyword spin_id:           The spin ID string.
    @type spin_id:              str
    @keyword file:              The name of the file to open.
    @type file:                 str
    @keyword dir:               The directory containing the file (defaults to the current directory if None).
    @type dir:                  str or None
    @keyword disp_point_col:    The column containing the dispersion point information.  For CPMG-type data, this is the frequency of the CPMG pulse train.  For R1rho-type data, this is the spin-lock field strength (nu1).  The units must be Hertz.
    @type disp_point_col:       int
    @keyword offset_col:        This is for R1rho data - the dispersion point column can be substituted for the offset values in Hertz.
    @type offset_col:           None or int
    @keyword data_col:          The column containing the R2eff/R1rho data in Hz.
    @type data_col:             int
    @keyword error_col:         The column containing the R2eff/R1rho errors.
    @type error_col:            int
    @keyword sep:               The column separator which, if None, defaults to whitespace.
    @type sep:                  str or None
    """

    # Data checks.
    pipes.test()
    check_mol_res_spin_data()

    # Get the spin.
    spin = return_spin(spin_id)
    if spin == None:
        raise RelaxNoSpinError(spin_id)

    # Extract the data from the file, removing comments and blank lines.
    file_data = extract_data(file, dir, sep=sep)
    file_data = strip(file_data)

    # Loop over the data.
    data = []
    new_ids = []
    for line in file_data:
        # Invalid columns.
        if disp_point_col != None and disp_point_col > len(line):
            warn(RelaxWarning("The data %s is invalid, no dispersion point column can be found." % line))
            continue
        if offset_col != None and offset_col > len(line):
            warn(RelaxWarning("The data %s is invalid, no offset column can be found." % line))
            continue
        if data_col > len(line):
            warn(RelaxWarning("The R2eff/R1rho data %s is invalid, no data column can be found." % line))
            continue
        if error_col > len(line):
            warn(RelaxWarning("The R2eff/R1rho data %s is invalid, no error column can be found." % line))
            continue

        # Unpack.
        if disp_point_col != None:
            ref_data = line[disp_point_col-1]
        elif offset_col != None:
            ref_data = line[offset_col-1]
        value = line[data_col-1]
        error = line[error_col-1]

        # Convert and check the dispersion point or offset.
        try:
            ref_data = float(ref_data)
        except ValueError:
            if disp_point_col != None:
                warn(RelaxWarning("The dispersion point data of the line %s is invalid." % line))
            elif offset_col != None:
                warn(RelaxWarning("The offset data of the line %s is invalid." % line))
            continue

        # Convert and check the value.
        if value == 'None':
            value = None
        if value != None:
            try:
                value = float(value)
            except ValueError:
                warn(RelaxWarning("The R2eff/R1rho value of the line %s is invalid." % line))
                continue

        # Convert and check the error.
        if error == 'None':
            error = None
        if error != None:
            try:
                error = float(error)
            except ValueError:
                warn(RelaxWarning("The R2eff/R1rho error of the line %s is invalid." % line))
                continue

        # Test the error value (cannot be 0.0).
        if error == 0.0:
            raise RelaxError("An invalid error value of zero has been encountered.")

        # Find the matching spectrum ID.
        new_id = None
        for spectrum_id in cdp.spectrum_ids:
            # Skip IDs which don't start with the base ID.
            if not search("^%s"%id, spectrum_id):
                continue

            # Find a close enough dispersion point (to one decimal place to allow for user truncation).
            if disp_point_col != None:
                if hasattr(cdp, 'cpmg_frqs') and spectrum_id in cdp.cpmg_frqs:
                    if abs(ref_data - cdp.cpmg_frqs[spectrum_id]) < 0.1:
                        new_id = spectrum_id
                        break
                if hasattr(cdp, 'spin_lock_nu1') and spectrum_id in cdp.spin_lock_nu1:
                    if abs(ref_data - cdp.spin_lock_nu1[spectrum_id]) < 0.1:
                        new_id = spectrum_id
                        break

            # Find a close enough offset (to one decimal place to allow for user truncation).
            elif offset_col != None:
                if hasattr(cdp, 'spin_lock_offset') and spectrum_id in cdp.spin_lock_offset:
                    # The sign to multiply offsets by.
                    sign = 1.0
                    if spin.isotope == '15N':
                        sign = -1.0

                    # Convert the data.
                    data_new = sign * frequency_to_ppm(frq=ref_data, B0=cdp.spectrometer_frq[spectrum_id], isotope=spin.isotope)

                    # Store the ID.
                    if abs(data_new - cdp.spin_lock_offset[spectrum_id]) < 0.1:
                        new_id = spectrum_id
                        break

        # No match.
        if new_id == None:
            if disp_point_col != None:
                raise RelaxError("The experiment ID corresponding to the base ID '%s' and the dispersion point '%s' could not be found." % (id, ref_data))
            if offset_col != None:
                raise RelaxError("The experiment ID corresponding to the base ID '%s' and the offset '%s' could not be found." % (id, data_new))

        # Add the ID to the list.
        new_ids.append(new_id)

        # Data checks.
        check_frequency(id=new_id)
        check_exp_type(id=new_id)

        # Store the spectrum ID.
        add_spectrum_id(new_id)

        # Get the metadata.
        frq = get_frequency(id=new_id)
        exp_type = get_exp_type(id=new_id)

        # The dispersion point key.
        if disp_point_col != None:
            disp_point = ref_data
            offset = 0.0
        elif offset_col != None:
            disp_point = cdp.spin_lock_nu1[new_id]
            offset = data_new
        point_key = return_param_key_from_data(exp_type=exp_type, frq=frq, offset=offset, point=disp_point)

        # Store the R2eff data.
        if data_col:
            # Initialise if necessary.
            if not hasattr(spin, 'r2eff'):
                spin.r2eff = {}

            # Store.
            spin.r2eff[point_key] = value

        # Store the R2eff error.
        if error_col:
            # Initialise if necessary.
            if not hasattr(spin, 'r2eff_err'):
                spin.r2eff_err = {}

            # Store.
            spin.r2eff_err[point_key] = error

        # Append the data for printout.
        if disp_point_col != None:
            data.append(["%-40s" % point_key, "%20.15f" % disp_point, "%20.15f" % value, "%20.15f" % error])
        else:
            data.append(["%-40s" % point_key, "%20.15f" % offset, "%20.15f" % value, "%20.15f" % error])

        # Data added.
        data_flag = True

    # No data, so fail hard!
    if not len(data):
        raise RelaxError("No R2eff/R1rho data could be extracted.")

    # Print out.
    print("The following R2eff/R1rho data has been loaded into the relax data store:\n")
    if disp_point_col != None:
        write_data(out=sys.stdout, headings=["R2eff_key", "Disp_point", "R2eff", "R2eff_error"], data=data)
    else:
        write_data(out=sys.stdout, headings=["R2eff_key", "Offset (ppm)", "R2eff", "R2eff_error"], data=data)


def randomise_R1(spin=None, ri_id=None, N=None):
    """Randomise the R1 data for the given spin for use in the Monte Carlo simulations.

    @keyword spin:      The spin container to randomise the data for.
    @type spin:         SpinContainer instance
    @keyword ri_id:     The relaxation data ID string.
    @type ri_id:        str
    @keyword N:         The number of randomisations to perform.
    @type N:            int
    """

    # The data already exists.
    if hasattr(spin, 'ri_data_sim') and ri_id in spin.ri_data_sim:
        return

    # Initialise the structure.
    if not hasattr(spin, 'ri_data_sim'):
        spin.ri_data_sim = {}
    spin.ri_data_sim[ri_id] = []

    # Randomise.
    for i in range(N):
        spin.ri_data_sim[ri_id].append(gauss(spin.ri_data[ri_id], spin.ri_data_err[ri_id]))


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
    @return:            The list of nu_CPMG frequencies in Hz.  It has the dimensions {Ei, Mi, Oi}.
    @rtype:             rank-2 list of numpy rank-1 float64 arrays
    """

    # No data.
    if not hasattr(cdp, 'cpmg_frqs_list'):
        return None

    # Initialise.
    cpmg_frqs = []

    # First loop over the experiment types.
    for exp_type, ei in loop_exp(return_indices=True):
        # Add a new dimension.
        cpmg_frqs.append([])

        # Then loop over the spectrometer frequencies.
        for frq, mi in loop_frq(return_indices=True):
            # Add a new dimension.
            cpmg_frqs[ei].append([])

            # Loop over the offsets.
            for offset, oi in loop_offset(exp_type=exp_type, frq=frq, return_indices=True):
                # Add a new dimension.
                cpmg_frqs[ei][mi].append([])

                # Loop over the fields.
                for point in cdp.cpmg_frqs_list:
                    # Skip reference points.
                    if (not ref_flag) and point == None:
                        continue

                    # Find a matching experiment ID.
                    found = False
                    for id in cdp.exp_type.keys():
                        # Skip non-matching experiments.
                        if cdp.exp_type[id] != exp_type:
                            continue

                        # Skip non-matching spectrometer frequencies.
                        if hasattr(cdp, 'spectrometer_frq') and cdp.spectrometer_frq[id] != frq:
                            continue

                        # Skip non-matching points.
                        if cdp.cpmg_frqs[id] != point:
                            continue

                        # Found.
                        found = True
                        break

                    # No data.
                    if not found:
                        continue

                    # Add the data.
                    cpmg_frqs[ei][mi][oi].append(point)

                # Convert to a numpy array.
                cpmg_frqs[ei][mi][oi] = array(cpmg_frqs[ei][mi][oi], float64)

    # Return the data.
    return cpmg_frqs


def return_cpmg_frqs_single(exp_type=None, frq=None, offset=None, time=None, ref_flag=True):
    """Return the list of nu_CPMG frequencies.

    @keyword exp_type:  The experiment type.
    @type exp_type:     str
    @keyword frq:       The spectrometer frequency in Hz.
    @type frq:          float
    @keyword offset:    The hard pulse offset, if desired.
    @type offset:       None or float
    @keyword time:      The relaxation time period.
    @type time:         float
    @keyword ref_flag:  A flag which if False will cause the reference spectrum frequency of None to be removed from the list.
    @type ref_flag:     bool
    @return:            The list of nu_CPMG frequencies in Hz.
    @rtype:             numpy rank-1 float64 array
    """

    # No data.
    if not hasattr(cdp, 'cpmg_frqs_list'):
        return None

    # Initialise.
    cpmg_frqs = []

    # Loop over the points.
    for point in cdp.cpmg_frqs_list:
        # Skip reference points.
        if (not ref_flag) and point == None:
            continue

        # Find a matching experiment ID.
        found = False
        for id in cdp.exp_type.keys():
            # Skip non-matching experiments.
            if cdp.exp_type[id] != exp_type:
                continue

            # Skip non-matching spectrometer frequencies.
            if hasattr(cdp, 'spectrometer_frq') and cdp.spectrometer_frq[id] != frq:
                continue

            # Skip non-matching offsets.
            if offset != None and hasattr(cdp, 'spin_lock_offset') and cdp.spin_lock_offset[id] != offset:
                continue

            # Skip non-matching time points.
            if time != None and hasattr(cdp, 'relax_times') and cdp.relax_times[id] != time:
                continue

            # Skip non-matching points.
            if cdp.cpmg_frqs[id] != point:
                continue

            # Found.
            found = True
            break

        # No data.
        if not found:
            continue

        # Add the data.
        cpmg_frqs.append(point)

    # Return the data as a numpy array.
    return array(cpmg_frqs, float64)


def return_grace_data_vs_disp(y_axis=None, x_axis=None, interpolate=None, exp_type=None, ei=None, current_spin=None, spin_id=None, si=None, back_calc=None, cpmg_frqs_new=None, spin_lock_nu1_new=None, chemical_shifts=None, offsets_inter=None, tilt_angles_inter=None, Delta_omega_inter=None, w_eff_inter=None, interpolated_flag=None, graph_index=None, data=None, set_labels=None, set_colours=None, x_axis_type_zero=None, symbols=None, symbol_sizes=None, linetype=None, linestyle=None, axis_labels=None):
    """Return data in lists for 2D Grace plotting function, to prepate plotting R1rho R2 as function of effective field in rotating frame w_eff.

    @keyword y_axis:                    String flag to tell which data on Y axis to plot for.  Option can be either "%s" which plot 'r2eff' for CPMG experiments or 'r1rho' for R1rho experiments or option can be "%s", which for R1rho experiments plot R2 = R1rho / sin^2(theta) - R_1 / tan^2(theta) = (R1rho - R_1 * cos^2(theta) ) / sin^2(theta).
    @type y_axis:                       str
    @keyword x_axis:                    String flag to tell which data on X axis to plot for.  Option can be either "%s" which plot 'CPMG frequency (Hz)' for CPMG experiments or 'Spin-lock field strength (Hz)' for R1rho experiments or option can be either "%s" or "%s" for R1rho experiments, which plot 'Effective field in rotating frame (rad/s)' or 'Rotating frame tilt angle theta (rad)'.
    @type x_axis:                       str
    @keyword interpolate:               How to interpolate the fitted curves.  Either by option "%s" which interpolate CPMG frequency or spin-lock field strength, or by option "%s" which interpole over spin-lock offset.
    @type interpolate:                  float
    @keyword exp_type:                  The experiment type.
    @type exp_type:                     str
    @keyword ei:                        The experiment type index.
    @type ei:                           int
    @keyword current_spin:              The specific spin data container.
    @type current_spin:                 SpinContainer instance.
    @keyword spin_id:                   The spin ID string.
    @type spin_id:                      str
    @keyword si:                        The index of the given spin in the cluster.
    @type si:                           int
    @keyword back_calc:                 The back calculated data.  The first index corresponds to the experiment type, the second is the spin of the cluster, the third is the magnetic field strength, and the fourth is the dispersion point.
    @type back_calc:                    list of lists of lists of lists of float
    @keyword cpmg_frqs_new:             The interpolated CPMG frequencies in Hertz.  The dimensions are {Ei, Mi, Oi}.
    @type cpmg_frqs_new:                rank-3 list of floats
    @keyword spin_lock_nu1_new:         The interpolated spin-lock field strengths in Hertz.  The dimensions are {Ei, Mi, Oi}.
    @type spin_lock_nu1_new:            rank-3 list of floats
    @keyword chemical_shifts:           The chemical shifts in rad/s {Ei, Si, Mi}
    @type chemical_shifts:              rank-3 list of floats
    @keyword offsets_inter:             Interpolated spin-lock offsets in rad/s {Ei, Si, Mi, Oi}
    @type offsets_inter:                rank-3 list of numpy rank-1 float arrays
    @keyword tilt_angles_inter:         The interpolated rotating frame tilt angles {Ei, Si, Mi, Oi, Di}
    @type tilt_angles_inter:            rank-5 list of floats
    @keyword Delta_omega_inter:         The interpolated average resonance offset in the rotating frame in rad/s {Ei, Si, Mi, Oi, Di}
    @type Delta_omega_inter:            rank-5 list of floats
    @keyword w_eff_inter:               The interpolated effective field in rotating frame in rad/s {Ei, Si, Mi, Oi, Di}.
    @type w_eff_inter:                  rank-5 list of floats
    @keyword interpolated_flag:         Flag telling if the graph should be interpolated.
    @type interpolated_flag:            bool
    @keyword graph_index:               Graph index for xmgrace.
    @type graph_index:                  int
    @keyword data:                      The 4D structure of numerical data to graph (see docstring).
    @type data:                         list of lists of lists of float
    @keyword set_labels:                Data labels to be used per experiment.
    @type set_labels:                   list of list of strings
    @keyword set_colours:               The colours for each graph data set Gx.Sy.  The first dimension is the graph, the second is the set.
    @type set_colours:                  None or list of list of int
    @keyword x_axis_type_zero:          The flags specifying if the X-axis should be placed at zero.
    @type x_axis_type_zero:             list of lists of bool
    @keyword symbols:                   The symbol style for each graph data set Gx.Sy.  The first dimension is the graph, the second is the set.
    @type symbols:                      list of list of int
    @keyword symbol_sizes:              The symbol size for each graph data set Gx.Sy.  The first dimension is the graph, the second is the set.
    @type symbol_sizes:                 list of list of int
    @keyword linetype:                  The line type for each graph data set Gx.Sy.  The first dimension is the graph, the second is the set.
    @type linetype:                     list of list of int
    @keyword linestyle:                 The line style for each graph data set Gx.Sy.  The first dimension is the graph, the second is the set.
    @type linestyle:                    list of list of int
    @keyword axis_labels:               The labels for the axes (in the [X, Y] list format).  The first dimension is the graph.
    @type axis_labels:                  list of list of str
    @return:                            The xy graph or xydy error graph, the 4D structure of numerical data to grace graph, the names associated with each graph data set Gx.Sy, the colours for each graph data set Gx.Sy, flags specifying if the X-axis should be placed at zero, the symbol style for each graph data set Gx.Sy, the symbol size for each graph data set Gx.Sy, the line type for each graph data set Gx.Sy, the line style for each graph data set Gx.Sy, the labels for the axes (in the [X, Y] list format).
    @rtype:                             boolean, list of lists of lists of float, list of list of str, list of list of int, list of lists of bool, list of list of int, list of list of int, list of list of int, list of list of int, list of list of str
    """%(Y_AXIS_R2_EFF, Y_AXIS_R2_R1RHO, X_AXIS_DISP, X_AXIS_W_EFF, X_AXIS_THETA, INTERPOLATE_DISP, INTERPOLATE_OFFSET)

    set_index = 0
    err = False
    colour_index = 0

    # Return r1.
    field_count = cdp.spectrometer_frq_count
    r1 = return_r1_data(spins=[current_spin], spin_ids=[spin_id], field_count=field_count)
    r1_err = return_r1_err_data(spins=[current_spin], spin_ids=[spin_id], field_count=field_count)

    # Add the recorded data points.
    data_type = "data"
    for frq, offset, mi, oi in loop_frq_offset(exp_type=exp_type, return_indices=True):
        # Add a new set for the data at each frequency and offset.
        data[graph_index].append([])

        # Return data label plotting info.
        label, symbols_int, symbol_sizes_float, linetype_int, linestyle_int = return_x_y_data_labels_settings(data_type=data_type, y_axis=y_axis, exp_type=exp_type, frq=frq, offset=offset, interpolated_flag=interpolated_flag)

        # Save settings.
        set_labels[ei].append(label)
        symbols[graph_index].append(symbols_int)
        symbol_sizes[graph_index].append(symbol_sizes_float)
        linetype[graph_index].append(linetype_int)
        linestyle[graph_index].append(linestyle_int)

        # The other settings.
        set_colours[graph_index].append(COLOUR_ORDER[colour_index])
        x_axis_type_zero[graph_index].append(True)

        # Loop over the dispersion points.
        for point, di in loop_point(exp_type=exp_type, frq=frq, offset=offset, return_indices=True):
            # The data key.
            key = return_param_key_from_data(exp_type=exp_type, frq=frq, offset=offset, point=point)

            # No data present.
            if key not in current_spin.r2eff:
                continue

            # Convert offset to rad/s from ppm.
            if hasattr(current_spin, 'isotope'):
                offset_rad = frequency_to_rad_per_s(frq=offset, B0=frq, isotope=current_spin.isotope)
            else:
                offset_rad = 0.0

            # Convert spin-lock field strength from Hz to rad/s.
            omega1 = point * 2.0 * pi

            # Return the rotating frame parameters.
            Delta_omega, theta, w_eff = rotating_frame_params(chemical_shift=chemical_shifts[ei][si][mi], spin_lock_offset=offset_rad, omega1=omega1)

            # Return the x and y point.
            x_point, y_point, err, y_err_point = return_grace_x_y_point(data_type=data_type, x_axis=x_axis, y_axis=y_axis, interpolate=interpolate, data_key=key, spin=current_spin, point=point, r1=r1[si][mi], r1_err=r1_err[si][mi], w_eff=w_eff, theta=theta, err=err)

            # Add the data.
            data[graph_index][set_index].append([x_point, y_point])

            # Handle the errors.
            if err:
                data[graph_index][set_index][-1].append(y_err_point)

        # Increment the graph set index.
        set_index += 1
        colour_index += 1

    # Add the back calculated data.
    colour_index = 0
    data_type = "back_calculated"
    for frq, offset, mi, oi in loop_frq_offset(exp_type=exp_type, return_indices=True):
        # Add a new set for the data at each frequency and offset.
        data[graph_index].append([])

        # Return data label plotting info.
        label, symbols_int, symbol_sizes_float, linetype_int, linestyle_int = return_x_y_data_labels_settings(data_type=data_type, y_axis=y_axis, exp_type=exp_type, frq=frq, offset=offset, interpolated_flag=interpolated_flag)

        # Save settings.
        set_labels[ei].append(label)
        symbols[graph_index].append(symbols_int)
        symbol_sizes[graph_index].append(symbol_sizes_float)
        linetype[graph_index].append(linetype_int)
        linestyle[graph_index].append(linestyle_int)

        # The other settings.
        set_colours[graph_index].append(COLOUR_ORDER[colour_index])
        x_axis_type_zero[graph_index].append(True)

        # Loop over the dispersion points.
        for point, di in loop_point(exp_type=exp_type, frq=frq, offset=offset, return_indices=True):
            # The data key.
            key = return_param_key_from_data(exp_type=exp_type, frq=frq, offset=offset, point=point)

            # No data present.
            if not hasattr(current_spin, 'r2eff_bc') or key not in current_spin.r2eff_bc:
                continue

            # Convert offset to rad/s from ppm.
            offset_rad = frequency_to_rad_per_s(frq=offset, B0=frq, isotope=current_spin.isotope)

            # Convert spin-lock field strength from Hz to rad/s.
            omega1 = point * 2.0 * pi

            # Return the rotating frame parameters.
            Delta_omega, theta, w_eff = rotating_frame_params(chemical_shift=chemical_shifts[ei][si][mi], spin_lock_offset=offset_rad, omega1=omega1)

            # Return the x and y point.
            x_point, y_point, err, y_err_point = return_grace_x_y_point(data_type=data_type, x_axis=x_axis, y_axis=y_axis, interpolate=interpolate, data_key=key, spin=current_spin, point=point, r1=r1[si][mi], r1_err=r1_err[si][mi], w_eff=w_eff, theta=theta, err=err)

            # Add the data.
            data[graph_index][set_index].append([x_point, y_point])

            # Handle the errors.
            if err:
                data[graph_index][set_index][-1].append(None)

        # Increment the graph set index.
        set_index += 1
        colour_index += 1

    # Add the interpolated back calculated data.
    data_type = "interpolated"
    if interpolated_flag:
        colour_index = 0
        for frq, offset, mi, oi in loop_frq_offset(exp_type=exp_type, return_indices=True):
            # Add a new set for the data at each frequency and offset.
            data[graph_index].append([])

            # Return data label plotting info.
            label, symbols_int, symbol_sizes_float, linetype_int, linestyle_int = return_x_y_data_labels_settings(spin=current_spin, data_type=data_type, y_axis=y_axis, exp_type=exp_type, frq=frq, offset=offset, interpolated_flag=interpolated_flag)

            # Save settings.
            set_labels[ei].append(label)
            symbols[graph_index].append(symbols_int)
            symbol_sizes[graph_index].append(symbol_sizes_float)
            linetype[graph_index].append(linetype_int)
            linestyle[graph_index].append(linestyle_int)

            # The other settings.
            set_colours[graph_index].append(COLOUR_ORDER[colour_index])
            x_axis_type_zero[graph_index].append(True)

            # Loop over the dispersion points.
            for di, r2eff in enumerate(back_calc[ei][si][mi][oi]):
                # Skip invalid points (values of 1e100).
                if r2eff > 1e50:
                    continue

                # The X point.
                if exp_type in EXP_TYPE_LIST_CPMG:
                    point = cpmg_frqs_new[ei][mi][oi][di]
                else:
                    point = spin_lock_nu1_new[ei][mi][oi][di]

                theta = tilt_angles_inter[ei][si][mi][oi][di]
                w_eff = w_eff_inter[ei][si][mi][oi][di]

                # Return the x and y point.
                x_point, y_point, err, y_err_point = return_grace_x_y_point(data_type=data_type, x_axis=x_axis, y_axis=y_axis, interpolate=interpolate, data_key=key, spin=current_spin, back_calc=r2eff, point=point, r1=r1[si][mi], r1_err=r1_err[si][mi], w_eff=w_eff, theta=theta, err=err)

                # Add the data.
                data[graph_index][set_index].append([x_point, y_point])

                # Handle the errors.
                if err:
                    data[graph_index][set_index][-1].append(None)

            # Increment the graph set index.
            set_index += 1
            colour_index += 1

    # Add the residuals for statistical comparison.
    colour_index = 0
    data_type = "residual"
    for frq, offset, mi, oi in loop_frq_offset(exp_type=exp_type, return_indices=True):
        # Add a new set for the data at each frequency and offset.
        data[graph_index].append([])

        # Return data label plotting info.
        label, symbols_int, symbol_sizes_float, linetype_int, linestyle_int = return_x_y_data_labels_settings(spin=current_spin, data_type=data_type, y_axis=y_axis, exp_type=exp_type, frq=frq, offset=offset, interpolated_flag=interpolated_flag)

        # Save settings.
        set_labels[ei].append(label)
        symbols[graph_index].append(symbols_int)
        symbol_sizes[graph_index].append(symbol_sizes_float)
        linetype[graph_index].append(linetype_int)
        linestyle[graph_index].append(linestyle_int)

        # The other settings.
        set_colours[graph_index].append(COLOUR_ORDER[colour_index])
        x_axis_type_zero[graph_index].append(True)

        # Loop over the dispersion points.
        for point, di in loop_point(exp_type=exp_type, frq=frq, offset=offset, return_indices=True):
            # The data key.
            key = return_param_key_from_data(exp_type=exp_type, frq=frq, offset=offset, point=point)

            # No data present.
            if key not in current_spin.r2eff or not hasattr(current_spin, 'r2eff_bc') or key not in current_spin.r2eff_bc:
                continue

            # Convert offset to rad/s from ppm.
            offset_rad = frequency_to_rad_per_s(frq=offset, B0=frq, isotope=current_spin.isotope)

            # Convert spin-lock field strength from Hz to rad/s.
            omega1 = point * 2.0 * pi

            # Return the rotating frame parameters.
            Delta_omega, theta, w_eff = rotating_frame_params(chemical_shift=chemical_shifts[ei][si][mi], spin_lock_offset=offset_rad, omega1=omega1)

            # Return the x and y point.
            x_point, y_point, err, y_err_point = return_grace_x_y_point(data_type=data_type, y_axis=y_axis, x_axis=x_axis, interpolate=interpolate, data_key=key, spin=current_spin, point=point, r1=r1[si][mi], r1_err=r1_err[si][mi], w_eff=w_eff, theta=theta, err=err)

            # Add the data.
            data[graph_index][set_index].append([x_point, y_point])

            # Handle the errors.
            if err:
                data[graph_index][set_index][-1].append(y_err_point)

        # Increment the graph set index.
        set_index += 1
        colour_index += 1

    # The axis labels.
    x_axis_label, y_axis_label = return_grace_x_y_axis_labels(y_axis=y_axis, x_axis=x_axis, exp_type=exp_type, interpolate=interpolate)
    axis_labels.append([x_axis_label, y_axis_label])

    return err, data, set_labels, set_colours, x_axis_type_zero, symbols, symbol_sizes, linetype, linestyle, axis_labels


def return_grace_data_vs_offset(y_axis=None, x_axis=None, interpolate=None, exp_type=None, ei=None, current_spin=None, spin_id=None, si=None, back_calc=None, cpmg_frqs_new=None, spin_lock_nu1_new=None, chemical_shifts=None, offsets_inter=None, tilt_angles_inter=None, Delta_omega_inter=None, w_eff_inter=None, interpolated_flag=None, graph_index=None, data=None, set_labels=None, set_colours=None, x_axis_type_zero=None, symbols=None, symbol_sizes=None, linetype=None, linestyle=None, axis_labels=None):
    """Return data in lists for 2D Grace plotting function, to prepate plotting R1rho R2 as function of effective field in rotating frame w_eff.

    @keyword y_axis:                    String flag to tell which data on Y axis to plot for.  Option can be either "%s" which plot 'r2eff' for CPMG experiments or 'r1rho' for R1rho experiments or option can be "%s", which for R1rho experiments plot R2 = R1rho / sin^2(theta) - R_1 / tan^2(theta) = (R1rho - R_1 * cos^2(theta) ) / sin^2(theta).
    @type y_axis:                       str
    @keyword x_axis:                    String flag to tell which data on X axis to plot for.  Option can be either "%s" which plot 'CPMG frequency (Hz)' for CPMG experiments or 'Spin-lock field strength (Hz)' for R1rho experiments or option can be either "%s" or "%s" for R1rho experiments, which plot 'Effective field in rotating frame (rad/s)' or 'Rotating frame tilt angle theta (rad)'.
    @type x_axis:                       str
    @keyword interpolate:               How to interpolate the fitted curves.  Either by option "%s" which interpolate CPMG frequency or spin-lock field strength, or by option "%s" which interpole over spin-lock offset.
    @type interpolate:                  float
    @keyword exp_type:                  The experiment type.
    @type exp_type:                     str
    @keyword ei:                        The experiment type index.
    @type ei:                           int
    @keyword current_spin:              The specific spin data container.
    @type current_spin:                 SpinContainer instance.
    @keyword spin_id:                   The spin ID string.
    @type spin_id:                      str
    @keyword si:                        The index of the given spin in the cluster.
    @type si:                           int
    @keyword back_calc:                 The back calculated data.  The first index corresponds to the experiment type, the second is the spin of the cluster, the third is the magnetic field strength, and the fourth is the dispersion point.
    @type back_calc:                    list of lists of lists of lists of float
    @keyword cpmg_frqs_new:             The interpolated CPMG frequencies in Hertz.  The dimensions are {Ei, Mi, Oi}.
    @type cpmg_frqs_new:                rank-3 list of floats
    @keyword spin_lock_nu1_new:         The interpolated spin-lock field strengths in Hertz.  The dimensions are {Ei, Mi, Oi}.
    @type spin_lock_nu1_new:            rank-3 list of floats
    @keyword chemical_shifts:           The chemical shifts in rad/s {Ei, Si, Mi}
    @type chemical_shifts:              rank-3 list of floats
    @keyword offsets_inter:             Interpolated spin-lock offsets in rad/s {Ei, Si, Mi, Oi}
    @type offsets_inter:                rank-3 list of numpy rank-1 float arrays
    @keyword tilt_angles_inter:         The interpolated rotating frame tilt angles {Ei, Si, Mi, Oi, Di}
    @type tilt_angles_inter:            rank-5 list of floats
    @keyword Delta_omega_inter:         The interpolated average resonance offset in the rotating frame in rad/s {Ei, Si, Mi, Oi, Di}
    @type Delta_omega_inter:            rank-5 list of floats
    @keyword w_eff_inter:               The interpolated effective field in rotating frame in rad/s {Ei, Si, Mi, Oi, Di}.
    @type w_eff_inter:                  rank-5 list of floats
    @keyword interpolated_flag:         Flag telling if the graph should be interpolated.
    @type interpolated_flag:            bool
    @keyword graph_index:               Graph index for xmgrace.
    @type graph_index:                  int
    @keyword data:                      The 4D structure of numerical data to graph (see docstring).
    @type data:                         list of lists of lists of float
    @keyword set_labels:                Data labels to be used per experiment.
    @type set_labels:                   list of list of strings
    @keyword set_colours:               The colours for each graph data set Gx.Sy.  The first dimension is the graph, the second is the set.
    @type set_colours:                  None or list of list of int
    @keyword x_axis_type_zero:          The flags specifying if the X-axis should be placed at zero.
    @type x_axis_type_zero:             list of lists of bool
    @keyword symbols:                   The symbol style for each graph data set Gx.Sy.  The first dimension is the graph, the second is the set.
    @type symbols:                      list of list of int
    @keyword symbol_sizes:              The symbol size for each graph data set Gx.Sy.  The first dimension is the graph, the second is the set.
    @type symbol_sizes:                 list of list of int
    @keyword linetype:                  The line type for each graph data set Gx.Sy.  The first dimension is the graph, the second is the set.
    @type linetype:                     list of list of int
    @keyword linestyle:                 The line style for each graph data set Gx.Sy.  The first dimension is the graph, the second is the set.
    @type linestyle:                    list of list of int
    @keyword axis_labels:               The labels for the axes (in the [X, Y] list format).  The first dimension is the graph.
    @type axis_labels:                  list of list of str
    @return:                            The xy graph or xydy error graph, the 4D structure of numerical data to grace graph, the names associated with each graph data set Gx.Sy, the colours for each graph data set Gx.Sy, flags specifying if the X-axis should be placed at zero, the symbol style for each graph data set Gx.Sy, the symbol size for each graph data set Gx.Sy, the line type for each graph data set Gx.Sy, the line style for each graph data set Gx.Sy, the labels for the axes (in the [X, Y] list format).
    @rtype:                             boolean, list of lists of lists of float, list of list of str, list of list of int, list of lists of bool, list of list of int, list of list of int, list of list of int, list of list of int, list of list of str
    """%(Y_AXIS_R2_EFF, Y_AXIS_R2_R1RHO, X_AXIS_DISP, X_AXIS_W_EFF, X_AXIS_THETA, INTERPOLATE_DISP, INTERPOLATE_OFFSET)

    set_index = 0
    err = False
    colour_index = 0

    # Return r1.
    field_count = cdp.spectrometer_frq_count
    r1 = return_r1_data(spins=[current_spin], spin_ids=[spin_id], field_count=field_count)
    r1_err = return_r1_err_data(spins=[current_spin], spin_ids=[spin_id], field_count=field_count)

    # Add the recorded data points.
    data_type = "data"
    for frq, mi in loop_frq(return_indices=True):
        # Loop over the all the dispersion points.
        for di, point in enumerate(spin_lock_nu1_new[ei][mi][0]):
            # Add a new set for the data at each frequency and offset.
            data[graph_index].append([])

            # Return data label plotting info.
            label, symbols_int, symbol_sizes_float, linetype_int, linestyle_int = return_x_y_data_labels_settings(data_type=data_type, y_axis=y_axis, exp_type=exp_type, frq=frq, point=point, interpolated_flag=interpolated_flag)

            # Save settings.
            set_labels[ei].append(label)
            symbols[graph_index].append(symbols_int)
            symbol_sizes[graph_index].append(symbol_sizes_float)
            linetype[graph_index].append(linetype_int)
            linestyle[graph_index].append(linestyle_int)

            # The other settings.
            set_colours[graph_index].append(COLOUR_ORDER[colour_index])
            x_axis_type_zero[graph_index].append(True)

            # Loop over the spin_lock offsets.
            for offset, oi in loop_offset(exp_type=exp_type, frq=frq, return_indices=True):
                # The data key.
                key = return_param_key_from_data(exp_type=exp_type, frq=frq, offset=offset, point=point)

                # No data present.
                if key not in current_spin.r2eff:
                    continue

                # Convert offset to rad/s from ppm.
                if hasattr(current_spin, 'isotope'):
                    offset_rad = frequency_to_rad_per_s(frq=offset, B0=frq, isotope=current_spin.isotope)
                else:
                    offset_rad = 0.0

                # Convert spin-lock field strength from Hz to rad/s.
                omega1 = point * 2.0 * pi

                # Return the rotating frame parameters.
                Delta_omega, theta, w_eff = rotating_frame_params(chemical_shift=chemical_shifts[ei][si][mi], spin_lock_offset=offset_rad, omega1=omega1)

                # Return the x and y point.
                x_point, y_point, err, y_err_point = return_grace_x_y_point(data_type=data_type, x_axis=x_axis, y_axis=y_axis, interpolate=interpolate, data_key=key, spin=current_spin, offset=offset, r1=r1[si][mi], r1_err=r1_err[si][mi], w_eff=w_eff, theta=theta, err=err)

                # Add the data.
                data[graph_index][set_index].append([x_point, y_point])

                # Handle the errors.
                if err:
                    data[graph_index][set_index][-1].append(y_err_point)

            # Increment the graph set index.
            set_index += 1
            colour_index += 1

    # Add the back calculated data.
    colour_index = 0
    data_type = "back_calculated"
    for frq, mi in loop_frq(return_indices=True):
        # Loop over the all the dispersion points.
        for di, point in enumerate(spin_lock_nu1_new[ei][mi][0]):
            # Add a new set for the data at each frequency and offset.
            data[graph_index].append([])

            # Return data label plotting info.
            label, symbols_int, symbol_sizes_float, linetype_int, linestyle_int = return_x_y_data_labels_settings(data_type=data_type, y_axis=y_axis, exp_type=exp_type, frq=frq, point=point, interpolated_flag=interpolated_flag)

            # Save settings.
            set_labels[ei].append(label)
            symbols[graph_index].append(symbols_int)
            symbol_sizes[graph_index].append(symbol_sizes_float)
            linetype[graph_index].append(linetype_int)
            linestyle[graph_index].append(linestyle_int)

            # The other settings.
            set_colours[graph_index].append(COLOUR_ORDER[colour_index])
            x_axis_type_zero[graph_index].append(True)

            # Loop over the spin_lock offsets.
            for offset, oi in loop_offset(exp_type=exp_type, frq=frq, return_indices=True):
                # The data key.
                key = return_param_key_from_data(exp_type=exp_type, frq=frq, offset=offset, point=point)

                # No data present.
                if not hasattr(current_spin, 'r2eff_bc') or key not in current_spin.r2eff_bc:
                    continue

                # Convert offset to rad/s from ppm.
                offset_rad = frequency_to_rad_per_s(frq=offset, B0=frq, isotope=current_spin.isotope)

                # Convert spin-lock field strength from Hz to rad/s.
                omega1 = point * 2.0 * pi

                # Return the rotating frame parameters.
                Delta_omega, theta, w_eff = rotating_frame_params(chemical_shift=chemical_shifts[ei][si][mi], spin_lock_offset=offset_rad, omega1=omega1)

                # Return the x and y point.
                x_point, y_point, err, y_err_point = return_grace_x_y_point(data_type=data_type, x_axis=x_axis, y_axis=y_axis, interpolate=interpolate, data_key=key, spin=current_spin, offset=offset, r1=r1[si][mi], r1_err=r1_err[si][mi], w_eff=w_eff, theta=theta, err=err)

                # Add the data.
                data[graph_index][set_index].append([x_point, y_point])

                # Handle the errors.
                if err:
                    data[graph_index][set_index][-1].append(None)

            # Increment the graph set index.
            set_index += 1
            colour_index += 1

    # Add the interpolated back calculated data.
    data_type = "interpolated"
    if interpolated_flag:
        colour_index = 0
        for frq, mi in loop_frq(return_indices=True):
            # Loop over the all the dispersion points.
            for di, point in enumerate(spin_lock_nu1_new[ei][mi][0]):
                # Add a new set for the data at each frequency and dispersion points.
                data[graph_index].append([])

                # Return data label plotting info.
                label, symbols_int, symbol_sizes_float, linetype_int, linestyle_int = return_x_y_data_labels_settings(spin=current_spin, data_type=data_type, y_axis=y_axis, exp_type=exp_type, frq=frq, point=point, interpolated_flag=interpolated_flag)

                # Save settings.
                set_labels[ei].append(label)
                symbols[graph_index].append(symbols_int)
                symbol_sizes[graph_index].append(symbol_sizes_float)
                linetype[graph_index].append(linetype_int)
                linestyle[graph_index].append(linestyle_int)

                # The other settings.
                set_colours[graph_index].append(COLOUR_ORDER[colour_index])
                x_axis_type_zero[graph_index].append(True)

                # Loop over the offsets.
                for oi, r2eff_arr in enumerate(back_calc[ei][si][mi]):
                    # Assign r2eff
                    r2eff = r2eff_arr[di]

                    # Skip invalid points (values of 1e100).
                    if r2eff > 1e50:
                        continue

                    # The X point.
                    if exp_type in EXP_TYPE_LIST_CPMG:
                        offset = None
                        theta = None
                        w_eff = None

                    else:
                        theta = tilt_angles_inter[ei][si][mi][oi][di]
                        w_eff = w_eff_inter[ei][si][mi][oi][di]
                        offset = frequency_to_ppm_from_rad(frq=offsets_inter[ei][si][mi][oi], B0=frq, isotope=current_spin.isotope)

                    # Return the x and y point.
                    x_point, y_point, err, y_err_point = return_grace_x_y_point(data_type=data_type, x_axis=x_axis, y_axis=y_axis, interpolate=interpolate, data_key=key, spin=current_spin, back_calc=r2eff, offset=offset, r1=r1[si][mi], r1_err=r1_err[si][mi], w_eff=w_eff, theta=theta, err=err)

                    # Add the data.
                    data[graph_index][set_index].append([x_point, y_point])

                    # Handle the errors.
                    if err:
                        data[graph_index][set_index][-1].append(None)

                # Increment the graph set index.
                set_index += 1
                colour_index += 1

    # Add the residuals for statistical comparison.
    colour_index = 0
    data_type = "residual"
    for frq, mi in loop_frq(return_indices=True):
        # Loop over the all the dispersion points.
        for di, point in enumerate(spin_lock_nu1_new[ei][mi][0]):
            # Add a new set for the data at each frequency and offset.
            data[graph_index].append([])

            # Return data label plotting info.
            label, symbols_int, symbol_sizes_float, linetype_int, linestyle_int = return_x_y_data_labels_settings(spin=current_spin, data_type=data_type, y_axis=y_axis, exp_type=exp_type, frq=frq, point=point, interpolated_flag=interpolated_flag)

            # Save settings.
            set_labels[ei].append(label)
            symbols[graph_index].append(symbols_int)
            symbol_sizes[graph_index].append(symbol_sizes_float)
            linetype[graph_index].append(linetype_int)
            linestyle[graph_index].append(linestyle_int)

            # The other settings.
            set_colours[graph_index].append(COLOUR_ORDER[colour_index])
            x_axis_type_zero[graph_index].append(True)

            # Loop over the spin_lock offsets.
            for offset, oi in loop_offset(exp_type=exp_type, frq=frq, return_indices=True):
                # The data key.
                key = return_param_key_from_data(exp_type=exp_type, frq=frq, offset=offset, point=point)

                # No data present.
                if key not in current_spin.r2eff or not hasattr(current_spin, 'r2eff_bc') or key not in current_spin.r2eff_bc:
                    continue

                # Convert offset to rad/s from ppm.
                offset_rad = frequency_to_rad_per_s(frq=offset, B0=frq, isotope=current_spin.isotope)

                # Convert spin-lock field strength from Hz to rad/s.
                omega1 = point * 2.0 * pi

                # Return the rotating frame parameters.
                Delta_omega, theta, w_eff = rotating_frame_params(chemical_shift=chemical_shifts[ei][si][mi], spin_lock_offset=offset_rad, omega1=omega1)

                # Return the x and y point.
                x_point, y_point, err, y_err_point = return_grace_x_y_point(data_type=data_type, y_axis=y_axis, x_axis=x_axis, interpolate=interpolate, data_key=key, spin=current_spin, offset=offset, r1=r1[si][mi], r1_err=r1_err[si][mi], w_eff=w_eff, theta=theta, err=err)

                # Add the data.
                data[graph_index][set_index].append([x_point, y_point])

                # Handle the errors.
                if err:
                    data[graph_index][set_index][-1].append(y_err_point)

            # Increment the graph set index.
            set_index += 1
            colour_index += 1

    # The axis labels.
    x_axis_label, y_axis_label = return_grace_x_y_axis_labels(y_axis=y_axis, x_axis=x_axis, exp_type=exp_type, interpolate=interpolate)
    axis_labels.append([x_axis_label, y_axis_label])

    return err, data, set_labels, set_colours, x_axis_type_zero, symbols, symbol_sizes, linetype, linestyle, axis_labels


def return_grace_file_name_ini(y_axis=None, x_axis=None, interpolate=None):
    """Return the initial part of the file name for the xmgrace plot files.

    @keyword y_axis:        String flag to tell which data on Y axis to plot for.  Option can be either "%s" which plot 'r2eff' for CPMG experiments or 'r1rho' for R1rho experiments or option can be "%s", which for R1rho experiments plot R2 = R1rho / sin^2(theta) - R_1 / tan^2(theta) = (R1rho - R_1 * cos^2(theta) ) / sin^2(theta).
    @type y_axis:           str
    @keyword x_axis:        String flag to tell which data on X axis to plot for.  Option can be either "%s" which plot 'CPMG frequency (Hz)' for CPMG experiments or 'Spin-lock field strength (Hz)' for R1rho experiments or option can be either "%s" or "%s" for R1rho experiments, which plot 'Effective field in rotating frame (rad/s)' or 'Rotating frame tilt angle theta (rad)'.
    @type x_axis:           str
    @keyword interpolate:   How to interpolate the fitted curves.  Either by option "%s" which interpolate CPMG frequency or spin-lock field strength, or by option "%s" which interpole over spin-lock offset.
    @type interpolate:      float
    @return:                The X-axis label for grace plotting, yhe Y-axis label for grace plotting
    @rtype:                 str, str
    """%(Y_AXIS_R2_EFF, Y_AXIS_R2_R1RHO, X_AXIS_DISP, X_AXIS_W_EFF, X_AXIS_THETA, INTERPOLATE_DISP, INTERPOLATE_OFFSET)

    if y_axis == Y_AXIS_R2_EFF and x_axis == X_AXIS_DISP and interpolate == INTERPOLATE_DISP:
        file_name_ini = "disp"

    # Special file name for R2_R1RHO data.
    elif has_r1rho_exp_type() and y_axis == Y_AXIS_R2_EFF and x_axis != X_AXIS_DISP:
        file_name_ini = "%s_vs_%s_inter_%s"%("r1rho", x_axis, interpolate)

    elif has_cpmg_exp_type() and y_axis == Y_AXIS_R2_R1RHO:
        file_name_ini = "%s_vs_%s_inter_%s"%("r2", x_axis, interpolate)

    else:
        file_name_ini = "%s_vs_%s_inter_%s"%(y_axis, x_axis, interpolate)

    # Return axis labels
    return file_name_ini


def return_grace_x_y_axis_labels(y_axis=None, x_axis=None, exp_type=None, interpolate=None):
    """Return the X and Y labels and plot settings, according to selected axis to plot for.

    @keyword y_axis:        String flag to tell which data on Y axis to plot for.  Option can be either "%s" which plot 'r2eff' for CPMG experiments or 'r1rho' for R1rho experiments or option can be "%s", which for R1rho experiments plot R2 = R1rho / sin^2(theta) - R_1 / tan^2(theta) = (R1rho - R_1 * cos^2(theta) ) / sin^2(theta).
    @type y_axis:           str
    @keyword x_axis:        String flag to tell which data on X axis to plot for.  Option can be either "%s" which plot 'CPMG frequency (Hz)' for CPMG experiments or 'Spin-lock field strength (Hz)' for R1rho experiments or option can be either "%s" or "%s" for R1rho experiments, which plot 'Effective field in rotating frame (rad/s)' or 'Rotating frame tilt angle theta (rad)'.
    @type x_axis:           str
    @keyword interpolate:   How to interpolate the fitted curves.  Either by option "%s" which interpolate CPMG frequency or spin-lock field strength, or by option "%s" which interpole over spin-lock offset.
    @type interpolate:      float
    @return:                The X-axis label for grace plotting, yhe Y-axis label for grace plotting
    @rtype:                 str, str
    """%(Y_AXIS_R2_EFF, Y_AXIS_R2_R1RHO, X_AXIS_DISP, X_AXIS_W_EFF, X_AXIS_THETA, INTERPOLATE_DISP, INTERPOLATE_OFFSET)

    # If x_axis is with dispersion points.
    if x_axis == X_AXIS_DISP:
        if interpolate == INTERPOLATE_DISP:
            if exp_type in EXP_TYPE_LIST_CPMG:
                # Set x_label.
                x_label = "\\qCPMG pulse train frequency \\xn\\B\\sCPMG\\N\\Q (Hz)"

            elif exp_type in EXP_TYPE_LIST_R1RHO:
                # Set x_label.
                x_label = "\\qSpin-lock field strength \\xn\\B\\s1\\N\\Q (Hz)"

        elif interpolate == INTERPOLATE_OFFSET:
                x_label = "\\qSpin-lock offset \\Q (ppm)"

    # If x_axis is effective field w_eff.
    elif x_axis == X_AXIS_W_EFF:
        # Set x_label.
        x_label = "\\qEffective field in rotating frame \\xw\\B\\seff\\N\\Q (rad.s\\S-1\\N)"

    # If x_axis is angle theta.
    elif x_axis == X_AXIS_THETA:
        # Set x_label.
        x_label = "\\qRotating frame tilt angle \\xq\\B\\Q (rad)"

    # If plotting either CPMG R2eff or R1rho.
    if y_axis == Y_AXIS_R2_EFF:
        if exp_type in EXP_TYPE_LIST_CPMG:
            # Set y_label.
            y_label = "%s - \\qR\\s2,eff\\N\\Q (rad.s\\S-1\\N)"%exp_type

        elif exp_type in EXP_TYPE_LIST_R1RHO:
            # Set y_label.
            y_label = "%s - \\qR\\s1\\xr\\B\\N\\Q (rad.s\\S-1\\N)"%exp_type

    # If plotting special R1rho R2 values.
    # R_2 = R1rho / sin^2(theta) - R_1 / tan^2(theta) = (R1rho - R_1 * cos^2(theta) ) / sin^2(theta).
    elif y_axis == Y_AXIS_R2_R1RHO:
        if exp_type in EXP_TYPE_LIST_CPMG:
            # Set y_label.
            y_label = "%s - \\qR\\s2\\N\\Q (rad.s\\S-1\\N)"%exp_type

        elif exp_type in EXP_TYPE_LIST_R1RHO:
            # Set y_label.
            y_label = "%s - \\qR\\s2\\N\\Q (rad.s\\S-1\\N)"%exp_type

    # Return axis labels
    return x_label, y_label


def return_x_y_data_labels_settings(spin=None, data_type=None, y_axis=None, exp_type=None, frq=None, offset=None, point=None, interpolated_flag=None):
    """Return the X and Y labels and plot settings, according to selected axis to plot for.

    @keyword spin:              The specific spin data container.
    @type spin:                 SpinContainer instance
    @keyword data_type:         String flag to tell which data type to return for.  Option can be either "data", "back_calculated", "interpolated" or "residual".
    @type data_type:            str
    @keyword exp_type:          The experiment type.
    @type exp_type:             str
    @keyword y_axis:            String flag to tell which data on Y axis to plot for.  Option can be either "%s" which plot 'r2eff' for CPMG experiments or 'r1rho' for R1rho experiments or option can be "%s", which for R1rho experiments plot R2 = R1rho / sin^2(theta) - R_1 / tan^2(theta) = (R1rho - R_1 * cos^2(theta) ) / sin^2(theta).
    @type y_axis:               str
    @keyword frq:               The spectrometer frequency in Hz.
    @type frq:                  float
    @keyword offset:            The spin-lock offset.
    @type offset:               None or float
    @keyword point:             The Spin-lock field strength (Hz).
    @type point:                float
    @keyword interpolated_flag: Flag telling if the graph should be interpolated.
    @type interpolated_flag:    bool
    @return:                    The data label, the data symbol, the data symbol size, the data line type, the data line style.
    @rtype:                     str, int, float, int, int
    """

    # If plotting either CPMG R2eff or R1rho.
    if y_axis == Y_AXIS_R2_EFF:
        if exp_type in EXP_TYPE_LIST_CPMG:
            # Set y_label.
            r_string = "R\\s2eff\\N"

        elif exp_type in EXP_TYPE_LIST_R1RHO:
            # Set y_label.
            r_string = "R\\s1\\xr\\B\\N"

    # If plotting special R1rho R2 values.
    # R_2 = R1rho / sin^2(theta) - R_1 / tan^2(theta) = (R1rho - R_1 * cos^2(theta) ) / sin^2(theta).
    elif y_axis == Y_AXIS_R2_R1RHO:
        if exp_type in EXP_TYPE_LIST_CPMG:
            # Set y_label.
            r_string = "R\\s2\\N"

        elif exp_type in EXP_TYPE_LIST_R1RHO:
            # Set y_label.
            r_string = "R\\s2\\N"

    # Determine unit string.
    if offset != None and frq != None:
        u_string = " (%.1f MHz, %.3f ppm)" % (frq / 1e6, offset)
    elif point != None and frq != None:
        u_string = " (%.1f MHz, %.3f Hz)" % (frq / 1e6, point)
    elif frq != None:
        u_string = " (%.1f MHz)" % (frq / 1e6)
    elif offset != None:
        u_string = " (%.3f ppm)" % (offset)
    elif point != None:
        u_string = " (%.3f Hz)" % (point)

    if data_type == "data":
        # Add a new label.
        label = r_string
        label += u_string

        # Set graph settings for data type.
        symbols_int = 1
        symbol_sizes_float = 0.45
        linetype_int = 0
        linestyle_int = 0

    elif data_type == "back_calculated":
        # Add a new label.
        label = "Back calculated %s"%(r_string)
        label += u_string

        # Set graph settings for data type.
        symbols_int = 4
        symbol_sizes_float = 0.45
        linetype_int = 1
        linestyle_int = 0

        if interpolated_flag:
            linestyle_int = 2
        else:
            linestyle_int = 1

    elif data_type == "interpolated":
        # Add a new label.
        label = "%s interpolated curve"%(r_string)
        label += u_string

        # Set graph settings for data type.
        if spin.model in MODEL_LIST_NUMERIC_CPMG:
            symbols_int =8
        else:
            symbols_int = 0

        symbol_sizes_float = 0.20
        linetype_int = 1
        linestyle_int = 1

    elif data_type == "residual":
        # Add a new label.
        label = "Residuals"
        label += u_string

        # Set graph settings for data type.
        symbols_int = 9
        symbol_sizes_float = 0.45
        linetype_int = 1
        linestyle_int = 3

    return label, symbols_int, symbol_sizes_float, linetype_int, linestyle_int


def return_grace_x_y_point(data_type=None, y_axis=None, x_axis=None, interpolate=None, data_key=None, spin=None, back_calc=None, offset=None, point=None, r1=None, r1_err=None, w_eff=None, theta=None, err=False):
    """Return the X and Y data point, according to selected axis to plot for.

    @keyword data_type:     String flag to tell which data type to return for.  Option can be either "data", "back_calculated", "interpolated" or "residual".
    @type data_type:        str
    @keyword y_axis:        String flag to tell which data on Y axis to plot for.  Option can be either "%s" which plot 'r2eff' for CPMG experiments or 'r1rho' for R1rho experiments or option can be "%s", which for R1rho experiments plot R2 = R1rho / sin^2(theta) - R_1 / tan^2(theta) = (R1rho - R_1 * cos^2(theta) ) / sin^2(theta).
    @type y_axis:           str
    @keyword x_axis:        String flag to tell which data on X axis to plot for.  Option can be either "%s" which plot 'CPMG frequency (Hz)' for CPMG experiments or 'Spin-lock field strength (Hz)' for R1rho experiments or option can be either "%s" or "%s" for R1rho experiments, which plot 'Effective field in rotating frame (rad/s)' or 'Rotating frame tilt angle theta (rad)'.
    @type x_axis:           str
    @keyword interpolate:   How to interpolate the fitted curves.  Either by option "%s" which interpolate CPMG frequency or spin-lock field strength, or by option "%s" which interpole over spin-lock offset.
    @type interpolate:      float
    @keyword data_key:      The unique data key.
    @type data_key:         str
    @keyword spin:          The specific spin data container.
    @type spin:             SpinContainer instance.
    @keyword back_calc:     The back calculated of CPMG R2eff value, or R1rho value.
    @type back_calc:        float
    @keyword offset:        The spin-lock offset.
    @type offset:           None or float
    @keyword point:         The CPMG pulse train frequency (Hz) or Spin-lock field strength (Hz).
    @type point:            float
    @keyword r1:            The R1 relaxation data point.
    @type r1:               float
    @keyword r1_err:        error for R1 relaxation data point.
    @type r1_err:           float
    @keyword w_eff:         The effective field in rotating frame (rad/s).
    @type w_eff:            float
    @keyword theta:         The rotating frame tilt angle theta (rad).
    @type theta:            float
    @keyword err:           The flag for xy graph or xydy error graph.
    @type err:              boolean
    @return:                The X-point, the Y-point, the flag for xy graph or xydy error graph, the Y-error value.
    @rtype:                 float, float, boolean, float
    """%(Y_AXIS_R2_EFF, Y_AXIS_R2_R1RHO, X_AXIS_DISP, X_AXIS_W_EFF, X_AXIS_THETA, INTERPOLATE_DISP, INTERPOLATE_OFFSET)

    # Start setting y_err_point to none.
    y_err_point = None

    if x_axis == X_AXIS_DISP:
        if interpolate == INTERPOLATE_DISP:
            # Set x_point.
            x_point = point

        elif interpolate == INTERPOLATE_OFFSET:
            # Set x_point.
            x_point = offset

    elif x_axis == X_AXIS_W_EFF:
        # Set x_point.
        x_point = w_eff

    elif x_axis == X_AXIS_THETA:
        # Set x_point.
        x_point = theta

    # Determine which data to return.
    if data_type == "data":
        # Determine y data type.
        if y_axis == Y_AXIS_R2_EFF:
            # Set y_point.
            y_point = spin.r2eff[data_key]

            # Add the error.
            if hasattr(spin, 'r2eff_err') and data_key in spin.r2eff_err:
                err = True
                y_err_point = spin.r2eff_err[data_key]

        elif y_axis == Y_AXIS_R2_R1RHO:
            # R_2 = R1rho / sin^2(theta) - R_1 / tan^2(theta) = (R1rho - R_1 * cos^2(theta) ) / sin^2(theta)
            y_point = ( spin.r2eff[data_key] - r1*cos(theta)**2 ) / sin(theta)**2

            # Add the error.
            if hasattr(spin, 'r2eff_err') and data_key in spin.r2eff_err:
                err = True
                y_err_point = ( spin.r2eff_err[data_key] - r1_err*cos(theta)**2 ) / sin(theta)**2

    elif data_type == "back_calculated":
        # Determine y data type.
        if y_axis == Y_AXIS_R2_EFF:
            # Set y_point.
            y_point = spin.r2eff_bc[data_key]

        elif y_axis == Y_AXIS_R2_R1RHO:
            # R_2 = R1rho / sin^2(theta) - R_1 / tan^2(theta) = (R1rho - R_1 * cos^2(theta) ) / sin^2(theta)
            y_point = ( spin.r2eff_bc[data_key] - r1*cos(theta)**2 ) / sin(theta)**2

    elif data_type == "interpolated":
        # Determine y data type.
        if y_axis == Y_AXIS_R2_EFF:
            # Set y_point.
            y_point = back_calc

        elif y_axis == Y_AXIS_R2_R1RHO:
            # R_2 = R1rho / sin^2(theta) - R_1 / tan^2(theta) = (R1rho - R_1 * cos^2(theta) ) / sin^2(theta)
            y_point = ( back_calc - r1*cos(theta)**2 ) / sin(theta)**2

    elif data_type == "residual":
        # Determine y data type.
        if y_axis == Y_AXIS_R2_EFF:
            # Set y_point.
            y_point_data = spin.r2eff[data_key]
            y_point_bc = spin.r2eff_bc[data_key]

            # Calculate residual.
            y_point = y_point_data - y_point_bc
            y_err_point = spin.r2eff_err[data_key]

        elif y_axis == Y_AXIS_R2_R1RHO:
            # R_2 = R1rho / sin^2(theta) - R_1 / tan^2(theta) = (R1rho - R_1 * cos^2(theta) ) / sin^2(theta)
            y_point_data = ( spin.r2eff[data_key] - r1*cos(theta)**2 ) / sin(theta)**2
            y_point_bc = ( spin.r2eff_bc[data_key] - r1*cos(theta)**2 ) / sin(theta)**2

            # Calculate residual.
            y_point = y_point_data - y_point_bc
            y_err_point = ( spin.r2eff_err[data_key] - r1_err*cos(theta)**2 ) / sin(theta)**2

    return x_point, y_point, err, y_err_point


def return_index_from_disp_point(value, exp_type=None):
    """Convert the dispersion point data into the corresponding index.

    @param value:       The dispersion point data (either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz).
    @type value:        float
    @keyword exp_type:  The experiment type.
    @type exp_type:     str
    @return:            The corresponding index.
    @rtype:             int
    """

    # Check.
    if exp_type == None:
        raise RelaxError("The experiment type has not been supplied.")

    # Initialise.
    index = 0
    ref_correction = False

    # CPMG-type experiments.
    if exp_type in EXP_TYPE_LIST_CPMG:
        index = cdp.cpmg_frqs_list.index(value)
        if None in cdp.cpmg_frqs_list:
            ref_correction = True

    # R1rho-type experiments.
    elif exp_type in EXP_TYPE_LIST_R1RHO:
        index = cdp.spin_lock_nu1_list.index(value)
        if None in cdp.spin_lock_nu1_list:
            ref_correction = True

    # Remove the reference point (always at index 0).
    for id in loop_spectrum_ids(exp_type=exp_type):
        if ref_correction and get_curve_type(id) == 'fixed time':
            index -= 1
            break

    # Return the index.
    return index


def return_index_from_exp_type(exp_type=None):
    """Convert the experiment type into the corresponding index.

    @keyword exp_type:  The experiment type.
    @type exp_type:     str
    @return:            The corresponding index.
    @rtype:             int
    """

    # Check.
    if exp_type == None:
        raise RelaxError("The experiment type has not been supplied.")

    # Return the index.
    if exp_type in cdp.exp_type_list:
        return cdp.exp_type_list.index(exp_type)

    # The number of experiments.
    num = len(cdp.exp_type_list)


def return_index_from_frq(value):
    """Convert the dispersion point data into the corresponding index.

    @param value:   The spectrometer frequency in Hz.
    @type value:    float
    @return:        The corresponding index.
    @rtype:         int
    """

    # No frequency present.
    if value == None:
        return 0

    # Return the index.
    return cdp.spectrometer_frq_list.index(value)


def return_index_from_disp_point_key(key, exp_type=None):
    """Convert the dispersion point key into the corresponding index.

    @keyword exp_type:  The experiment type.
    @type exp_type:     str
    @param key:         The dispersion point or R2eff/R1rho key.
    @type key:          str
    @return:            The corresponding index.
    @rtype:             int
    """

    # Check.
    if exp_type == None:
        raise RelaxError("The experiment type has not been supplied.")

    # CPMG-type experiments.
    if exp_type in EXP_TYPE_LIST_CPMG:
        return return_index_from_disp_point(cdp.cpmg_frqs[key], exp_type=exp_type)

    # R1rho-type experiments.
    elif exp_type in EXP_TYPE_LIST_R1RHO:
        return return_index_from_disp_point(cdp.spin_lock_nu1[key], exp_type=exp_type)


def return_key_from_di(mi=None, di=None):
    """Convert the dispersion point index into the corresponding key.

    @keyword mi:    The spectrometer frequency index.
    @type mi:       int
    @keyword di:    The dispersion point or R2eff/R1rho index.
    @type di:       int
    @return:        The corresponding key.
    @rtype:         str
    """

    # Insert the reference point (always at index 0).
    if has_fixed_time_exp_type():
        di += 1

    # The frequency.
    frq = return_value_from_frq_index(mi)

    # CPMG data.
    if exp_type in EXP_TYPE_LIST_CPMG:
        point = cdp.cpmg_frqs_list[di]
        points = cdp.cpmg_frqs

    # R1rho data.
    else:
        point = cdp.spin_lock_nu1_list[di]
        points = cdp.spin_lock_nu1

    # Find the keys matching the dispersion point.
    key_list = []
    all_keys = points.keys()
    for key in all_keys:
        if points[key] == point:
            key_list.append(key)

    # Return the key.
    return key


def return_offset_data(spins=None, spin_ids=None, field_count=None, spin_lock_offset=None, fields=None):
    """Return numpy arrays of the chemical shifts, offsets and tilt angles.

    Indices
    =======

    The data structures consist of many different index types.  These are:

        - Ei:  The index for each experiment type.
        - Si:  The index for each spin of the spin cluster.
        - Mi:  The index for each magnetic field strength.
        - Oi:  The index for each spin-lock offset.  In the case of CPMG-type data, this index is always zero.
        - Di:  The index for each dispersion point (either the spin-lock field strength or the nu_CPMG frequency).


    @keyword spins:             The list of spin containers in the cluster.
    @type spins:                list of SpinContainer instances
    @keyword spin_ids:          The list of spin IDs for the cluster.
    @type spin_ids:             list of str
    @keyword field_count:       The number of spectrometer field strengths.  This may not be equal to the length of the fields list as the user may not have set the field strength.
    @type field_count:          int
    @keyword spin_lock_offset:  The spin-lock offsets to use instead of the user loaded values - to enable interpolation.
    @type spin_lock_offset:     list of lists of numpy rank-1 float arrays
    @keyword fields:            The spin-lock field strengths to use instead of the user loaded values - to enable interpolation.  The dimensions are {Ei, Mi}.
    @type fields:               rank-2 list of floats
    @return:                    interpolated spin-lock offsets in rad/s {Ei, Si, Mi, Oi}, interpolated spin-lock field strength frequencies in Hz {Ei, Si, Mi, Oi, Di}, the chemical shifts in rad/s {Ei, Si, Mi}, the interpolated rotating frame tilt angles {Ei, Si, Mi, Oi, Di}, interpolated average resonance offset in the rotating frame in rad/s {Ei, Si, Mi, Oi, Di} and the interpolated effective field in rotating frame in rad/s {Ei, Si, Mi, Oi, Di}.
    @rtype:                     rank-3 list of numpy rank-1 float arrays, rank-4 list of numpy rank-1 float arrays, rank-2 list of numpy rank-1 float arrays, rank-4 list of numpy rank-1 float arrays, rank-4 list of numpy rank-1 float arrays, rank-4 list of numpy rank-1 float arrays
    """

    # The counts.
    exp_num = num_exp_types()
    spin_num = 0
    for spin in spins:
        if spin.select:
            spin_num += 1

    # Initialise the data structures for the target function.
    fields_orig = fields
    shifts = []
    offsets = []
    spin_lock_fields_inter = []
    tilt_angles = []
    Domega = []
    w_e = []

    for exp_type, ei in loop_exp(return_indices=True):
        shifts.append([])
        offsets.append([])
        spin_lock_fields_inter.append([])
        tilt_angles.append([])
        Domega.append([])
        w_e.append([])
        for si in range(spin_num):
            shifts[ei].append([])
            offsets[ei].append([])
            tilt_angles[ei].append([])
            Domega[ei].append([])
            w_e[ei].append([])
            for frq, mi in loop_frq(return_indices=True):
                shifts[ei][si].append(None)
                offsets[ei][si].append([])
                spin_lock_fields_inter[ei].append([])
                tilt_angles[ei][si].append([])
                Domega[ei][si].append([])
                w_e[ei][si].append([])
                # Enable possible interpolation of spin-lock offset.
                if spin_lock_offset != None:
                    for oi, offset in enumerate(spin_lock_offset[ei][si][mi]):
                        offsets[ei][si][mi].append(None)
                        spin_lock_fields_inter[ei][mi].append([])
                        tilt_angles[ei][si][mi].append([])
                        Domega[ei][si][mi].append([])
                        w_e[ei][si][mi].append([])
                else:
                    for offset, oi in loop_offset(exp_type=exp_type, frq=frq, return_indices=True):
                        offsets[ei][si][mi].append(None)
                        spin_lock_fields_inter[ei][mi].append([])
                        tilt_angles[ei][si][mi].append([])
                        Domega[ei][si][mi].append([])
                        w_e[ei][si][mi].append([])

    # Assemble the data.
    data_flag = False
    si = 0
    for spin_index in range(len(spins)):
        # Skip deselected spins.
        if not spins[spin_index].select:
            continue

        # Alias the spin.
        spin = spins[spin_index]
        spin_id = spin_ids[spin_index]

        # No data.
        shift = 0.0
        if hasattr(spin, 'chemical_shift'):
            shift = spin.chemical_shift
        elif has_r1rho_exp_type():
            warn(RelaxWarning("The chemical shift for the spin '%s' cannot be found.  Be careful, it is being set to 0.0 ppm so offset calculations will probably be wrong!" % spin_id))

        # Loop over the experiments and spectrometer frequencies.
        data_flag = True
        for exp_type, frq, ei, mi in loop_exp_frq(return_indices=True):
            # The R1rho and off-resonance R1rho flag.
            r1rho_flag = False
            if exp_type in EXP_TYPE_LIST_R1RHO:
                r1rho_flag = True
            r1rho_off_flag = False
            if exp_type in [MODEL_DPL94, MODEL_TP02, MODEL_TAP03, MODEL_MP05, MODEL_NS_R1RHO_2SITE]:
                r1rho_off_flag = True

            # Make sure offset data exists for off-resonance R1rho-type experiments.
            if r1rho_off_flag and not hasattr(cdp, 'spin_lock_offset'):
                raise RelaxError("The spin-lock offsets have not been set.")

            # Convert the shift from ppm to rad/s and store it.
            if hasattr(spin, 'isotope'):
                shifts[ei][si][mi] = frequency_to_rad_per_s(frq=shift, B0=frq, isotope=spin.isotope)
            else:
                shifts[ei][si][mi] = shift

            # Enable possible interpolation of spin-lock offset.
            if spin_lock_offset != None:
                for oi, offset in enumerate(spin_lock_offset[ei][si][mi]):
                    # Assign spin-lock fields to all loaded fields.
                    fields = [x for x in cdp.spin_lock_nu1_list if x!=None]

                    # Save the fields to list.
                    spin_lock_fields_inter[ei][mi][oi] = fields

                    # Find a matching experiment ID.
                    found = False
                    for id in cdp.exp_type.keys():
                        # Skip non-matching experiments.
                        if cdp.exp_type[id] != exp_type:
                            continue

                        # Skip non-matching spectrometer frequencies.
                        if hasattr(cdp, 'spectrometer_frq') and cdp.spectrometer_frq[id] != frq:
                            continue

                        # Found.
                        found = True
                        break

                    # No data.
                    if not found:
                        continue

                    # Store the offset in rad/s from ppm.  Only once and using the first key.
                    if offsets[ei][si][mi][oi] == None:
                        if r1rho_flag and hasattr(cdp, 'spin_lock_offset') and hasattr(spin, 'isotope'):
                            offsets[ei][si][mi][oi] = frequency_to_rad_per_s(frq=offset, B0=frq, isotope=spin.isotope)
                        else:
                            offsets[ei][si][mi][oi] = 0.0

                    # Loop over the dispersion points.
                    for di in range(len(fields)):
                        # Alias the point.
                        point = fields[di]

                        # Skip reference spectra.
                        if point == None:
                            continue

                        # Convert spin-lock field strength from Hz to rad/s.
                        omega1 = point * 2.0 * pi

                        # Return the rotating frame parameters.
                        Delta_omega, theta, w_eff = rotating_frame_params(chemical_shift=shifts[ei][si][mi], spin_lock_offset=offsets[ei][si][mi][oi], omega1=omega1)

                        # Assign the data to lists.
                        Domega[ei][si][mi][oi].append(Delta_omega)
                        tilt_angles[ei][si][mi][oi].append(theta)
                        w_e[ei][si][mi][oi].append(w_eff)


            else:
                # Loop over offset.
                for offset, oi in loop_offset(exp_type=exp_type, frq=frq, return_indices=True):
                    # The spin-lock data.
                    if fields_orig != None:
                        fields = fields_orig[ei][mi][oi]
                    else:
                        if not r1rho_flag:
                            fields = return_cpmg_frqs_single(exp_type=exp_type, frq=frq, offset=offset, ref_flag=False)
                        else:
                            fields = return_spin_lock_nu1_single(exp_type=exp_type, frq=frq, offset=offset, ref_flag=False)

                    # Save the fields to list.
                    spin_lock_fields_inter[ei][mi][oi] = fields

                    # Find a matching experiment ID.
                    found = False
                    for id in cdp.exp_type.keys():
                        # Skip non-matching experiments.
                        if cdp.exp_type[id] != exp_type:
                            continue

                        # Skip non-matching spectrometer frequencies.
                        if hasattr(cdp, 'spectrometer_frq') and cdp.spectrometer_frq[id] != frq:
                            continue

                        # Skip non-matching offsets.
                        if r1rho_flag and hasattr(cdp, 'spin_lock_offset') and cdp.spin_lock_offset[id] != offset:
                            continue

                        # Found.
                        found = True
                        break

                    # No data.
                    if not found:
                        continue

                    # Store the offset in rad/s.  Only once and using the first key.
                    if offsets[ei][si][mi][oi] == None:
                        if r1rho_flag and hasattr(cdp, 'spin_lock_offset') and hasattr(spin, 'isotope'):
                            offsets[ei][si][mi][oi] = frequency_to_rad_per_s(frq=cdp.spin_lock_offset[id], B0=frq, isotope=spin.isotope)
                        else:
                            offsets[ei][si][mi][oi] = 0.0

                    # Loop over the dispersion points.
                    for di in range(len(fields)):
                        # Alias the point.
                        point = fields[di]

                        # Skip reference spectra.
                        if point == None:
                            continue

                        # Convert spin-lock field strength from Hz to rad/s.
                        omega1 = point * 2.0 * pi

                        # Return the rotating frame parameters.
                        Delta_omega, theta, w_eff = rotating_frame_params(chemical_shift=shifts[ei][si][mi], spin_lock_offset=offsets[ei][si][mi][oi], omega1=omega1)

                        # Assign the data to lists.
                        Domega[ei][si][mi][oi].append(Delta_omega)
                        tilt_angles[ei][si][mi][oi].append(theta)
                        w_e[ei][si][mi][oi].append(w_eff)

        # Increment the spin index.
        si += 1

    # No shift data for the spin cluster.
    if not data_flag:
        return None, None, None

    # Convert to numpy arrays.
    #for ei in range(exp_num):
    #    for si in range(spin_num):
    #        for mi in range(field_count):
    #            theta[ei][si][mi] = array(theta[ei][si][mi], float64)

    # Return the structures.
    return offsets, spin_lock_fields_inter, shifts, tilt_angles, Domega, w_e


def return_param_key_from_data(exp_type=None, frq=0.0, offset=0.0, point=0.0):
    """Generate the unique key from the spectrometer frequency and dispersion point.

    @keyword exp_type:  The experiment type.
    @type exp_type:     str
    @keyword frq:       The spectrometer frequency in Hz.
    @type frq:          float
    @keyword offset:    The optional offset value for off-resonance R1rho-type data.
    @type offset:       None or float
    @keyword point:     The dispersion point data (either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz).
    @type point:        float
    @return:            The unique key.
    @rtype:             str
    """

    # Convert the experiment type.
    if exp_type == None:
        raise RelaxError("The experiment type must be supplied.")
    exp_type = exp_type.replace(' ', '_').lower()

    # Convert None values.
    if frq == None:
        frq = 0.0
    if offset == None:
        offset = 0.0
    if point == None:
        point = 0.0

    # Generate the unique key.
    key = "%s_%.8f_%.3f_%.3f" % (exp_type, frq/1e6, offset, point)

    # Return the unique key.
    return key


def return_r1_data(spins=None, spin_ids=None, field_count=None, sim_index=None):
    """Return the R1 data structures for off-resonance R1rho experiments.

    @keyword spins:         The list of spin containers in the cluster.
    @type spins:            list of SpinContainer instances
    @keyword spin_ids:      The list of spin IDs for the cluster.
    @type spin_ids:         list of str
    @keyword field_count:   The number of spectrometer field strengths.  This may not be equal to the length of the fields list as the user may not have set the field strength.
    @type field_count:      int
    @keyword sim_index:     The index of the simulation to return the R1 data of.  This should be None if the normal data is required.
    @type sim_index:        None or int
    @return:                The R1 relaxation data.
    @rtype:                 numpy rank-2 float array
    """

    # The spin count.
    spin_num = count_spins(spins)

    # Initialise the data structure.
    r1 = -ones((spin_num, field_count), float64)

    # Set testing flags.
    flags = [False]*field_count

    # Check for the presence of data.
    if not hasattr(cdp, 'ri_ids') and spins[0].model not in  MODEL_LIST_R1RHO_FIT_R1:
        warn_text = "No R1 relaxation data has been loaded.  Setting it to 0.0.  This is essential for the proper handling of offsets in off-resonance R1rho experiments."
        error_text = "No R1 relaxation data has been loaded.  This is essential for the proper handling of offsets in off-resonance R1rho experiments."
        if has_r1rho_exp_type():
            # For all R1rho models using R1, raise an error, if R1 has not been loaded.
            if spins[0].model in MODEL_LIST_R1RHO_W_R1:
                raise RelaxError(error_text)

            # For all models not listed in R1rho models, raise a warning, and set 0.0 as value.
            else:
                warn(RelaxWarning(warn_text))
                r1 = 0.0 * r1

        # For all non-R1rho experiments, return 0.0.
        else:
            r1 = 0.0 * r1

        # Return the data.
        return r1

    # For all R1rho models fitting R1.
    elif spins[0].model in MODEL_LIST_R1RHO_FIT_R1:
        # Spin loop.
        for si in range(spin_num):
            # Assign spin:
            spin = spins[si]

            # Loop over exp type and frq.
            for exp_type, frq, ei, mi in loop_exp_frq(return_indices=True):
                # Assign key
                r20_key = generate_r20_key(exp_type=exp_type, frq=frq)

                # If no data is available.
                if len(spin.r1_fit) == 0:
                    r1[si, mi] = None

                else:
                    r1[si, mi] = spin.r1_fit[r20_key]

                # Flip the flag.
                flags[mi] = True

    else:
        # Loop over the Rx IDs.
        for ri_id in cdp.ri_ids:
            # Only use R1 data.
            if cdp.ri_type[ri_id] != 'R1':
                continue

            # The frequency.
            frq = cdp.spectrometer_frq[ri_id]
            mi = return_index_from_frq(frq)

            # Flip the flag.
            flags[mi] = True

            # Spin loop.
            for si in range(spin_num):
                # FIXME:  This is a kludge - the data randomisation needs to be incorporated into the dispersion base_data_loop() method and the standard Monte Carlo simulation pathway used.
                # Randomise the R1 data, when required.
                if sim_index != None and (not hasattr(spins[si], 'ri_data_sim') or ri_id not in spins[si].ri_data_sim):
                    randomise_R1(spin=spins[si], ri_id=ri_id, N=cdp.sim_number)

                # Store the data.
                if sim_index != None:
                    r1[si, mi] = spins[si].ri_data_sim[ri_id][sim_index]
                else:
                    r1[si, mi] = spins[si].ri_data[ri_id]

    # Check the data to prevent user mistakes.
    for mi in range(field_count):
        # The frequency.
        frq = return_value_from_frq_index(mi=mi)

        # Check for R1 data for this frequency.
        if not flags[mi]:
            raise RelaxError("R1 data for the %.1f MHz field strength cannot be found." % (frq/1e6))

        # Check the spin data.
        for si in range(spin_num):
            if r1[si, mi] == -1.0:
                raise RelaxError("R1 data for the '%s' spin at %.1f MHz field strength cannot be found." % (spin_ids[si], frq/1e6))

    # Return the data.
    return r1


def return_r1_err_data(spins=None, spin_ids=None, field_count=None, sim_index=None):
    """Return the R1 error data structures for off-resonance R1rho experiments.

    @keyword spins:         The list of spin containers in the cluster.
    @type spins:            list of SpinContainer instances
    @keyword spin_ids:      The list of spin IDs for the cluster.
    @type spin_ids:         list of str
    @keyword field_count:   The number of spectrometer field strengths.  This may not be equal to the length of the fields list as the user may not have set the field strength.
    @type field_count:      int
    @keyword sim_index:     The index of the simulation to return the R1 data of.  This should be None if the normal data is required.
    @type sim_index:        None or int
    @return:                The R1 relaxation error data.
    @rtype:                 numpy rank-2 float array
    """

    # The spin count.
    spin_num = count_spins(spins)

    # Initialise the data structure.
    r1_err = -ones((spin_num, field_count), float64)

    # Set testing flags.
    flags = [False]*field_count

    # Check for the presence of data.
    if not hasattr(cdp, 'ri_ids') and spins[0].model not in  MODEL_LIST_R1RHO_FIT_R1:
        warn_text = "No R1 relaxation data has been loaded.  Setting it to 0.0.  This is essential for the proper handling of offsets in off-resonance R1rho experiments."
        error_text = "No R1 relaxation data has been loaded.  This is essential for the proper handling of offsets in off-resonance R1rho experiments."
        if has_r1rho_exp_type():
            # For all R1rho models using R1, raise an error, if R1 has not been loaded.
            if spins[0].model in MODEL_LIST_R1RHO_W_R1:
                raise RelaxError(error_text)

            # For all models not listed in R1rho models, raise a warning, and set 0.0 as value.
            else:
                warn(RelaxWarning(warn_text))
                r1_err = 0.0 * r1_err

        # For all non-R1rho experiments, return 0.0.
        else:
            r1_err = 0.0 * r1_err

        # Return the data.
        return r1_err

    # For all R1rho models fitting R1.
    elif spins[0].model in MODEL_LIST_R1RHO_FIT_R1:
        # Spin loop.
        for si in range(spin_num):
            # Assign spin:
            spin = spins[si]

            # Loop over exp type and frq.
            for exp_type, frq, ei, mi in loop_exp_frq(return_indices=True):
                # Assign key
                r20_key = generate_r20_key(exp_type=exp_type, frq=frq)

                # If no Monte-Carlo simulations has been performed, there will be no error.
                if not hasattr(spin, 'r1_fit_err'):
                    r1_err[si, mi] = None

                else:
                    r1_err[si, mi] = spin.r1_fit_err[r20_key]

                # Flip the flag.
                flags[mi] = True

    else:
        # Loop over the Rx IDs.
        for ri_id in cdp.ri_ids:
            # Only use R1 data.
            if cdp.ri_type[ri_id] != 'R1':
                continue

            # The frequency.
            frq = cdp.spectrometer_frq[ri_id]
            mi = return_index_from_frq(frq)

            # Flip the flag.
            flags[mi] = True

            # Spin loop.
            for si in range(spin_num):
                # FIXME:  This is a kludge - the data randomisation needs to be incorporated into the dispersion base_data_loop() method and the standard Monte Carlo simulation pathway used.
                # Randomise the R1 data, when required.
                if sim_index != None and (not hasattr(spins[si], 'ri_data_sim') or ri_id not in spins[si].ri_data_sim):
                    randomise_R1(spin=spins[si], ri_id=ri_id, N=cdp.sim_number)

                # Store the data.
                if sim_index != None:
                    r1_err[si, mi] = spins[si].ri_data_err_sim[ri_id][sim_index]
                else:
                    r1_err[si, mi] = spins[si].ri_data_err[ri_id]

    # Check the data to prevent user mistakes.
    for mi in range(field_count):
        # The frequency.
        frq = return_value_from_frq_index(mi=mi)

        # Check for R1 data for this frequency.
        if not flags[mi]:
            raise RelaxError("R1 data for the %.1f MHz field strength cannot be found." % (frq/1e6))

        # Check the spin data.
        for si in range(spin_num):
            if r1_err[si, mi] == -1.0:
                raise RelaxError("R1 data for the '%s' spin at %.1f MHz field strength cannot be found." % (spin_ids[si], frq/1e6))

    # Return the data.
    return r1_err


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
    @return:                The numpy array structures of the R2eff/R1rho values, errors, missing data, and corresponding Larmor frequencies.  For each structure, the first dimension corresponds to the experiment types, the second the spins of a spin block, the third to the spectrometer field strength, and the fourth is the dispersion points.  For the Larmor frequency structure, the fourth dimension is omitted.  For R1rho-type data, an offset dimension is inserted between the spectrometer field strength and the dispersion points.
    @rtype:                 lists of numpy float arrays, lists of numpy float arrays, lists of numpy float arrays, numpy rank-2 int array
    """

    # The counts.
    exp_num = num_exp_types()
    spin_num = count_spins(spins)

    # 1H MMQ flag.
    proton_mmq_flag = has_proton_mmq_cpmg()

    # Initialise the data structures for the target function.
    exp_types = []
    values = []
    errors = []
    missing = []
    frqs = []
    frqs_H = []
    relax_times = []
    for exp_type, ei in loop_exp(return_indices=True):
        values.append([])
        errors.append([])
        missing.append([])
        frqs.append([])
        frqs_H.append([])
        relax_times.append([])
        for si in range(spin_num):
            values[ei].append([])
            errors[ei].append([])
            missing[ei].append([])
            frqs[ei].append([])
            frqs_H[ei].append([])
            for frq, mi in loop_frq(return_indices=True):
                values[ei][si].append([])
                errors[ei][si].append([])
                missing[ei][si].append([])
                frqs[ei][si].append(0.0)
                frqs_H[ei][si].append(0.0)
                for offset, oi in loop_offset(exp_type=exp_type, frq=frq, return_indices=True):
                    values[ei][si][mi].append([])
                    errors[ei][si][mi].append([])
                    missing[ei][si][mi].append([])
        for mi in range(field_count):
            relax_times[ei].append(None)

    # Pack the R2eff/R1rho data.
    data_flag = False
    si = 0
    for spin_index in range(len(spins)):
        # Skip deselected spins.
        if not spins[spin_index].select:
            continue

        # Alias the spin.
        spin = spins[spin_index]
        spin_id = spin_ids[spin_index]

        # Get the attached proton.
        proton = None
        if proton_mmq_flag:
            # Get all protons.
            proton_spins = return_attached_protons(spin_id)

            # Only one allowed.
            if len(proton_spins) > 1:
                raise RelaxError("Only one attached proton is supported for the MMQ-type models.")

            # Missing proton.
            if not len(proton_spins):
                raise RelaxError("No proton attached to the spin '%s' could be found.  This is required for the MMQ-type models." % spin_id)

            # Alias the single proton.
            proton = proton_spins[0]

        # No data.
        if not hasattr(spin, 'r2eff') and not hasattr(proton, 'r2eff'):
            continue
        data_flag = True

        # No isotope information.
        if not hasattr(spin, 'isotope'):
            raise RelaxSpinTypeError(spin_id=spin_ids[si])

        # Loop over the R2eff data.
        for exp_type, frq, offset, point, ei, mi, oi, di in loop_exp_frq_offset_point(return_indices=True):

            # Alias the correct spin.
            current_spin = spin
            if exp_type in [EXP_TYPE_CPMG_PROTON_SQ, EXP_TYPE_CPMG_PROTON_MQ]:
                current_spin = proton

            # Add the experiment type.
            if exp_type not in exp_types:
                exp_types.append(exp_type)

            # The key.
            key = return_param_key_from_data(exp_type=exp_type, frq=frq, offset=offset, point=point)
            if mi == 0:
                fact = 60.83831274541046
            else:
                fact = 81.11775032721394
            
            # The Larmor frequency for this spin (and that of an attached proton for the MMQ models) and field strength (in MHz*2pi to speed up the ppm to rad/s conversion).
            if frq != None:
                frqs[ei][si][mi] = 2.0 * pi * frq / g1H * return_gyromagnetic_ratio(spin.isotope) * 1e-6
                frqs_H[ei][si][mi] = 2.0 * pi * frq * 1e-6

            # Missing data.
            if key not in current_spin.r2eff.keys():
                values[ei][si][mi][oi].append(0.0)
                errors[ei][si][mi][oi].append(1.0)
                missing[ei][si][mi][oi].append(1)
                continue
            else:
                missing[ei][si][mi][oi].append(0)

            # The values.
            if sim_index == None:
                values[ei][si][mi][oi].append(current_spin.r2eff[key])
            else:
                values[ei][si][mi][oi].append(current_spin.r2eff_sim[sim_index][key])

            # The errors.
            errors[ei][si][mi][oi].append(current_spin.r2eff_err[key])

            # The relaxation times.
            for id in cdp.spectrum_ids:
                # Non-matching data.
                if cdp.spectrometer_frq[id] != frq:
                    continue
                if cdp.exp_type[id] != exp_type:
                    continue
                if exp_type in EXP_TYPE_LIST_CPMG:
                    if id not in cdp.cpmg_frqs.keys() or cdp.cpmg_frqs[id] != point:
                        continue
                else:
                    if id not in cdp.spin_lock_nu1.keys() or  cdp.spin_lock_nu1[id] != point:
                        continue

                # Found.
                relax_time = cdp.relax_times[id]
                break

            # Check the value if already set.
            if relax_times[ei][mi] != None:
                if relax_times[ei][mi] != relax_time:
                    raise RelaxError("The relaxation times do not match for all experiments.")
                continue

            # Store the time.
            relax_times[ei][mi] = relax_time

        # Increment the spin index.
        si += 1

    # No R2eff/R1rho data for the spin cluster.
    if not data_flag:
        raise RelaxError("No R2eff/R1rho data could be found for the spin cluster %s." % spin_ids)

    # Convert to numpy arrays.
    relax_times = array(relax_times, float64)
    for exp_type, ei in loop_exp(return_indices=True):
        for si in range(spin_num):
            for frq, mi in loop_frq(return_indices=True):
                for offset, oi in loop_offset(exp_type=exp_type, frq=frq, return_indices=True):
                    values[ei][si][mi][oi] = array(values[ei][si][mi][oi], float64)
                    errors[ei][si][mi][oi] = array(errors[ei][si][mi][oi], float64)
                    missing[ei][si][mi][oi] = array(missing[ei][si][mi][oi], int32)

    # Return the structures.
    return values, errors, missing, frqs, frqs_H, exp_types, relax_times


def return_relax_times():
    """Return the list of relaxation times.

    @return:    The list of relaxation times in s.
    @rtype:     numpy rank-2 float64 array
    """

    # No data.
    if not hasattr(cdp, 'relax_times'):
        return None

    # Initialise.
    relax_times = zeros((count_exp(), count_frq()), float64)

    # Loop over the experiment types.
    for exp_type, frq, point, time, ei, mi, di, ti in loop_exp_frq_point_time(return_indices=True):
        # Fetch all of the matching intensity keys.
        keys = find_intensity_keys(exp_type=exp_type, frq=frq, point=point, time=time, raise_error=False)

        # No data.
        if not len(keys):
            continue

        # Add the data.
        relax_times[ei][mi] = cdp.relax_times[keys[0]]

    # Return the data.
    return relax_times


def return_spin_lock_nu1(ref_flag=True):
    """Return the list of spin-lock field strengths.

    @keyword ref_flag:  A flag which if False will cause the reference spectrum frequency of None to be removed from the list.
    @type ref_flag:     bool
    @return:            The list of spin-lock field strengths in Hz.  It has the dimensions {Ei, Mi, Oi}.
    @rtype:             rank-2 list of numpy rank-1 float64 arrays
    """

    # No data.
    if not hasattr(cdp, 'spin_lock_nu1_list'):
        return None

    # Initialise.
    nu1 = []

    # First loop over the experiment types.
    for exp_type, ei in loop_exp(return_indices=True):
        # Add a new dimension.
        nu1.append([])

        # Then loop over the spectrometer frequencies.
        for frq, mi in loop_frq(return_indices=True):
            # Add a new dimension.
            nu1[ei].append([])

            # Loop over the offsets.
            for offset, oi in loop_offset(exp_type=exp_type, frq=frq, return_indices=True):
                # Add a new dimension.
                nu1[ei][mi].append([])

                # Loop over the fields.
                for point in cdp.spin_lock_nu1_list:
                    # Skip reference points.
                    if (not ref_flag) and point == None:
                        continue

                    # Find a matching experiment ID.
                    found = False
                    for id in cdp.exp_type.keys():
                        # Skip non-matching experiments.
                        if cdp.exp_type[id] != exp_type:
                            continue

                        # Skip non-matching spectrometer frequencies.
                        if hasattr(cdp, 'spectrometer_frq') and cdp.spectrometer_frq[id] != frq:
                            continue

                        # Skip non-matching offsets.
                        if offset != None and hasattr(cdp, 'spin_lock_offset') and cdp.spin_lock_offset[id] != offset:
                            continue

                        # Skip non-matching points.
                        if cdp.spin_lock_nu1[id] != point:
                            continue

                        # Found.
                        found = True
                        break

                    # No data.
                    if not found:
                        continue

                    # Add the data.
                    nu1[ei][mi][oi].append(point)

                # Convert to a numpy array.
                nu1[ei][mi][oi] = array(nu1[ei][mi][oi], float64)

    # Return the data.
    return nu1


def return_spin_lock_nu1_single(exp_type=None, frq=None, offset=None, ref_flag=True):
    """Return the list of spin-lock field strengths.

    @keyword exp_type:  The experiment type.
    @type exp_type:     str
    @keyword frq:       The spectrometer frequency in Hz.
    @type frq:          float
    @keyword offset:    The spin-lock offset.
    @type offset:       None or float
    @keyword ref_flag:  A flag which if False will cause the reference spectrum frequency of None to be removed from the list.
    @type ref_flag:     bool
    @return:            The list of spin-lock field strengths in Hz.
    @rtype:             numpy rank-1 float64 array
    """

    # No data.
    if not hasattr(cdp, 'spin_lock_nu1_list'):
        return None

    # Initialise.
    nu1 = []

    # Loop over the points.
    for point in cdp.spin_lock_nu1_list:
        # Skip reference points.
        if (not ref_flag) and point == None:
            continue

        # Find a matching experiment ID.
        found = False
        for id in cdp.exp_type.keys():
            # Skip non-matching experiments.
            if cdp.exp_type[id] != exp_type:
                continue

            # Skip non-matching spectrometer frequencies.
            if hasattr(cdp, 'spectrometer_frq') and cdp.spectrometer_frq[id] != frq:
                continue

            # Skip non-matching offsets.
            if offset != None and hasattr(cdp, 'spin_lock_offset') and cdp.spin_lock_offset[id] != offset:
                continue

            # Skip non-matching points.
            if cdp.spin_lock_nu1[id] != point:
                continue

            # Found.
            found = True
            break

        # No data.
        if not found:
            continue

        # Add the data.
        nu1.append(point)

    # Return the data as a numpy array.
    return array(nu1, float64)


def return_value_from_frq_index(mi=None):
    """Return the spectrometer frequency corresponding to the frequency index.

    @keyword mi:    The spectrometer frequency index.
    @type mi:       int
    @return:        The spectrometer frequency in Hertz or None if no information is present.
    @rtype:         float
    """

    # No data.
    if not hasattr(cdp, 'spectrometer_frq_list'):
        return None

    # Return the field.
    return cdp.spectrometer_frq_list[mi]


def return_value_from_offset_index(ei=None, mi=None, oi=None):
    """Return the offset corresponding to the offset index.

    @keyword ei:    The experiment type index.
    @type ei:       int
    @keyword mi:    The spectrometer frequency index.
    @type mi:       int
    @keyword oi:    The offset index.
    @type oi:       int
    @return:        The offset in Hertz or None if no information is present.
    @rtype:         float
    """

    # Checks.
    if ei == None:
        raise RelaxError("The experiment type index must be supplied.")
    if mi == None:
        raise RelaxError("The spectrometer frequency index must be supplied.")

    # Initialise the index.
    new_oi = -1

    # The experiment type and frequency.
    exp_type = cdp.exp_type_list[ei]
    frq = return_value_from_frq_index(mi)

    # CPMG-type data.
    if exp_type in EXP_TYPE_LIST_CPMG:
        # Return zero until hard pulse offset handling is implemented.
        return 0.0

    # R1rho-type data.
    if exp_type in EXP_TYPE_LIST_R1RHO:
        # No offsets.
        if not hasattr(cdp, 'spin_lock_offset'):
            return None

        # Loop over the offset data.
        for offset in cdp.spin_lock_offset_list:
            # Increment the index.
            new_oi += 1

            # Find a matching experiment ID.
            found = False
            for id in cdp.exp_type.keys():
                # Skip non-matching experiments.
                if cdp.exp_type[id] != exp_type:
                    continue

                # Skip non-matching spectrometer frequencies.
                if hasattr(cdp, 'spectrometer_frq') and cdp.spectrometer_frq[id] != frq:
                    continue

                # Skip non-matching offsets.
                if new_oi != oi:
                    continue

                # Found.
                found = True
                break

            # No data.
            if not found:
                continue

            # Return the offset.
            return offset


def set_exp_type(spectrum_id=None, exp_type=None):
    """Select the relaxation dispersion experiment type performed.

    @keyword spectrum_id:   The spectrum ID string.
    @type spectrum_id:      str
    @keyword exp:           The relaxation dispersion experiment type.
    @type exp:              str
    """

    # Data checks.
    pipes.test()

    # Add the spectrum ID to the data store if needed.
    add_spectrum_id(spectrum_id)

    # Check the experiment type.
    if exp_type not in EXP_TYPE_LIST:
        raise RelaxError("The relaxation dispersion experiment '%s' is invalid, it must be one of %s." % (exp_type, EXP_TYPE_LIST))

    # Initialise the experiment type data structures if needed.
    if not hasattr(cdp, 'exp_type'):
        cdp.exp_type = {}
    if not hasattr(cdp, 'exp_type_list'):
        cdp.exp_type_list = []

    # Store the value.
    cdp.exp_type[spectrum_id] = exp_type

    # Unique experiments.
    if cdp.exp_type[spectrum_id] not in cdp.exp_type_list:
        cdp.exp_type_list.append(cdp.exp_type[spectrum_id])

    # Printout.
    text = "The spectrum ID '%s' is now set to " % spectrum_id
    if exp_type == EXP_TYPE_CPMG_SQ:
        text += EXP_TYPE_DESC_CPMG_SQ + "."
    elif exp_type == EXP_TYPE_CPMG_MQ:
        text += EXP_TYPE_DESC_CPMG_MQ + "."
    elif exp_type == EXP_TYPE_CPMG_DQ:
        text += EXP_TYPE_DESC_CPMG_DQ + "."
    elif exp_type == EXP_TYPE_CPMG_ZQ:
        text += EXP_TYPE_DESC_CPMG_ZQ + "."
    elif exp_type == EXP_TYPE_CPMG_PROTON_SQ:
        text += EXP_TYPE_DESC_CPMG_PROTON_SQ + "."
    elif exp_type == EXP_TYPE_CPMG_PROTON_MQ:
        text += EXP_TYPE_DESC_CPMG_PROTON_MQ + "."
    elif exp_type == EXP_TYPE_R1RHO:
        text += EXP_TYPE_DESC_R1RHO + "."
    print(text)


def spin_has_frq_data(spin=None, frq=None):
    """Determine if the spin has intensity data for the given spectrometer frequency.

    @keyword spin:      The specific spin data container.
    @type spin:         SpinContainer instance
    @keyword frq:       The spectrometer frequency.
    @type frq:          float
    @return:            True if data for that spectrometer frequency is present, False otherwise.
    @rtype:             bool
    """

    # Loop over the intensity data.
    for key in spin.peak_intensity.keys():
        if key in cdp.spectrometer_frq and cdp.spectrometer_frq[key] == frq:
            return True

    # No data.
    return False


def spin_ids_to_containers(spin_ids):
    """Take the list of spin IDs and return the corresponding spin containers.

    This is useful for handling the data from the model_loop() method.


    @param spin_ids:    The list of spin ID strings.
    @type spin_ids:     list of str
    @return:            The list of spin containers.
    @rtype:             list of SpinContainer instances
    """

    # Loop over the IDs and fetch the container.
    spins = []
    for id in spin_ids:
        spins.append(return_spin(id))

    # Return the containers.
    return spins


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
    if field == None:
        cdp.spin_lock_nu1[spectrum_id] = field
    else:
        cdp.spin_lock_nu1[spectrum_id] = float(field)

    # The unique curves for the R2eff fitting (R1rho).
    if cdp.spin_lock_nu1[spectrum_id] not in cdp.spin_lock_nu1_list:
        cdp.spin_lock_nu1_list.append(cdp.spin_lock_nu1[spectrum_id])

    # Sort the list (handling None for Python 3).
    flag = False
    if None in cdp.spin_lock_nu1_list:
        cdp.spin_lock_nu1_list.pop(cdp.spin_lock_nu1_list.index(None))
        flag = True
    cdp.spin_lock_nu1_list.sort()
    if flag:
        cdp.spin_lock_nu1_list.insert(0, None)

    # Update the exponential curve count (skipping the reference if present).
    cdp.dispersion_points = len(cdp.spin_lock_nu1_list)
    if None in cdp.spin_lock_nu1_list:
        cdp.dispersion_points -= 1

    # Printout.
    if field == None:
        print("The spectrum ID '%s' is set to the reference." % spectrum_id)
    else:
        print("The spectrum ID '%s' spin-lock field strength is set to %s kHz." % (spectrum_id, cdp.spin_lock_nu1[spectrum_id]/1000.0))


def spin_lock_offset(spectrum_id=None, offset=None):
    """Set the spin-lock offset (omega_rf) for the given spectrum.

    @keyword spectrum_id:   The spectrum ID string.
    @type spectrum_id:      str
    @keyword offset:        The spin-lock offset (omega_rf) in ppm.
    @type offset:           int or float
    """

    # Test if the spectrum ID exists.
    if spectrum_id not in cdp.spectrum_ids:
        raise RelaxNoSpectraError(spectrum_id)

    # Initialise the global offset data structures if needed.
    if not hasattr(cdp, 'spin_lock_offset'):
        cdp.spin_lock_offset = {}
    if not hasattr(cdp, 'spin_lock_offset_list'):
        cdp.spin_lock_offset_list = []

    # Add the offset, converting to a float if needed.
    if offset == None:
        raise RelaxError("The offset value must be provided.")
    cdp.spin_lock_offset[spectrum_id] = float(offset)

    # The unique curves for the R2eff fitting (R1rho).
    if cdp.spin_lock_offset[spectrum_id] not in cdp.spin_lock_offset_list:
        cdp.spin_lock_offset_list.append(cdp.spin_lock_offset[spectrum_id])

    # Sort the list.
    cdp.spin_lock_offset_list.sort()

    # Printout.
    print("Setting the '%s' spectrum spin-lock offset to %s ppm." % (spectrum_id, cdp.spin_lock_offset[spectrum_id]))


def write_disp_curves(dir=None, force=None):
    """Write out the dispersion curves to text files.

    One file will be created per spin system.


    @keyword dir:           The optional directory to place the file into.
    @type dir:              str
    @param force:           If True, the files will be overwritten if they already exists.
    @type force:            bool
    """

    # Checks.
    pipes.test()
    check_mol_res_spin_data()

    # The formatting strings.
    format_head = "# %-18s %-20s %-20s %-20s %-20s %-20s\n"
    format = "%-20s %20s %20s %20s %20s %20s\n"

    # 1H MMQ flag.
    proton_mmq_flag = has_proton_mmq_cpmg()

    # Loop over each spin.
    for spin, spin_id in spin_loop(return_id=True, skip_desel=True):
        # Skip protons for MMQ data.
        if spin.model in MODEL_LIST_MMQ and spin.isotope == '1H':
            continue

        # Define writing variables.
        writing_vars = [['disp', ("Experiment_name", "Field_strength_(MHz)", "Disp_point_(Hz)", "R2eff_(measured)", "R2eff_(back_calc)", "R2eff_errors")]]

        # If the model is of R1rho type, then also write as R2eff as function of theta.
        if spin.model in MODEL_LIST_R1RHO_FULL and has_r1rho_exp_type() and hasattr(spin, 'isotope'):
            # Add additonal looping over writing parameters.
            writing_vars.append(['disp_theta', ("Experiment_name", "Field_strength_(MHz)", "Tilt_angle_(rad)", "R2eff_(measured)", "R2eff_(back_calc)", "R2eff_errors")])

        # Loop over writing vars
        for wvar in writing_vars:
            # Get the attached proton.
            proton = None
            if proton_mmq_flag:
                proton = return_attached_protons(spin_id)[0]

            # The unique file name.
            file_name = "%s%s.out" % (wvar[0], spin_id.replace('#', '_').replace(':', '_').replace('@', '_'))

            # Open the file for writing.
            file_path = get_file_path(file_name, dir)
            file = open_write_file(file_name, dir, force)

            # Write a header.
            file.write(format_head % wvar[1])

            # Loop over the dispersion points.
            for exp_type, frq, offset, point, ei, mi, oi, di in loop_exp_frq_offset_point(return_indices=True):
                # Alias the correct spin.
                current_spin = spin
                if exp_type in [EXP_TYPE_CPMG_PROTON_SQ, EXP_TYPE_CPMG_PROTON_MQ]:
                    current_spin = proton

                # The data key.
                key = return_param_key_from_data(exp_type=exp_type, frq=frq, offset=offset, point=point)

                # Format the R2eff data.
                r2eff = "-"
                if hasattr(current_spin, 'r2eff') and  key in current_spin.r2eff:
                    r2eff = "%.15f" % current_spin.r2eff[key]

                # Format the R2eff back calc data.
                r2eff_bc = "-"
                if hasattr(current_spin, 'r2eff_bc') and key in current_spin.r2eff_bc:
                    r2eff_bc = "%.15f" % current_spin.r2eff_bc[key]

                # Format the R2eff errors.
                r2eff_err = "-"
                if hasattr(current_spin, 'r2eff_err') and  key in current_spin.r2eff_err:
                    r2eff_err = "%.15f" % current_spin.r2eff_err[key]

                # Define value to be written.
                if wvar[0] == 'disp_theta':
                    theta_spin_dic, Domega_spin_dic, w_eff_spin_dic, dic_key_list = calc_rotating_frame_params(spin=spin)
                    value = theta_spin_dic[key]
                elif wvar[0] == 'disp_w_eff':
                    theta_spin_dic, Domega_spin_dic, w_eff_spin_dic, dic_key_list = calc_rotating_frame_params(spin=spin)
                    value = w_eff_spin_dic[key]
                # Else use the standard dispersion point data.
                else:
                    value = point

                # Write out the data.
                frq_text = "%.9f" % (frq/1e6)
                value_text = "%.6f" % value
                file.write(format % (repr(exp_type), frq_text, value_text, r2eff, r2eff_bc, r2eff_err))

            # Close the file.
            file.close()

            # Add the file to the results file list.
            add_result_file(type='text', label='Text', file=file_path)
