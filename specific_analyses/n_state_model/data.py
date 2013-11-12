###############################################################################
#                                                                             #
# Copyright (C) 2007-2013 Edward d'Auvergne                                   #
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

# Package docstring.
"""Module for handling base data of the N-state model or structural ensemble analysis."""

# Python module imports.
from math import pi, sqrt
from numpy import array, float64
from numpy.linalg import norm
from warnings import warn

# relax module imports.
from lib.check_types import is_float
from lib.errors import RelaxError, RelaxNoValueError, RelaxSpinTypeError
from lib.physical_constants import dipolar_constant, g1H, return_gyromagnetic_ratio
from lib.warnings import RelaxWarning
from pipe_control import align_tensor
from pipe_control.interatomic import interatomic_loop
from pipe_control.mol_res_spin import return_spin, spin_loop


def base_data_types():
    """Determine all the base data types.

    The base data types can include::
        - 'rdc', residual dipolar couplings.
        - 'pcs', pseudo-contact shifts.
        - 'noesy', NOE restraints.
        - 'tensor', alignment tensors.

    @return:    A list of all the base data types.
    @rtype:     list of str
    """

    # Array of data types.
    list = []

    # RDC search.
    for interatom in interatomic_loop():
        if hasattr(interatom, 'rdc'):
            list.append('rdc')
            break

    # PCS search.
    for spin in spin_loop():
        if hasattr(spin, 'pcs'):
            list.append('pcs')
            break

    # Alignment tensor search.
    if not ('rdc' in list or 'pcs' in list) and hasattr(cdp, 'align_tensors'):
        list.append('tensor')

    # NOESY data search.
    if hasattr(cdp, 'noe_restraints'):
        list.append('noesy')

    # No data is present.
    if not list:
        raise RelaxError("Neither RDC, PCS, NOESY nor alignment tensor data is present.")

    # Return the list.
    return list


def calc_ave_dist(atom1, atom2, exp=1):
    """Calculate the average distances.

    The formula used is::

                  _N_
              / 1 \                  \ 1/exp
        <r> = | -  > |p1i - p2i|^exp |
              \ N /__                /
                   i

    where i are the members of the ensemble, N is the total number of structural models, and p1
    and p2 at the two atom positions.


    @param atom1:   The atom identification string of the first atom.
    @type atom1:    str
    @param atom2:   The atom identification string of the second atom.
    @type atom2:    str
    @keyword exp:   The exponent used for the averaging, e.g. 1 for linear averaging and -6 for
                    r^-6 NOE averaging.
    @type exp:      int
    @return:        The average distance between the two atoms.
    @rtype:         float
    """

    # Get the spin containers.
    spin1 = return_spin(atom1)
    spin2 = return_spin(atom2)

    # Loop over each model.
    num_models = len(spin1.pos)
    ave_dist = 0.0
    for i in range(num_models):
        # Distance to the minus sixth power.
        dist = norm(spin1.pos[i] - spin2.pos[i])
        ave_dist = ave_dist + dist**(exp)

    # Average.
    ave_dist = ave_dist / num_models

    # The exponent.
    ave_dist = ave_dist**(1.0/exp)

    # Return the average distance.
    return ave_dist


def check_rdcs(interatom, spin1, spin2):
    """Check if the RDCs for the given interatomic data container should be used.

    @param interatom:   The interatomic data container.
    @type interatom:    InteratomContainer instance
    @param spin1:       The first spin container.
    @type spin1:        SpinContainer instance
    @param spin2:       The second spin container.
    @type spin2:        SpinContainer instance
    @return:            True if the RDCs should be used, False otherwise.
    """

    # Skip deselected interatomic data containers.
    if not interatom.select:
        return False

    # Skip deselected spins.
    # FIXME:  These checks could be fatal in the future if a user has good RDCs and one of the two spins are deselected!
    if not spin1.select or not spin2.select:
        return False

    # Only use interatomic data containers with RDC data.
    if not hasattr(interatom, 'rdc'):
        return False

    # Only use interatomic data containers with RDC and J coupling data.
    if opt_uses_j_couplings() and not hasattr(interatom, 'j_coupling'):
        return False

    # RDC data exists but the interatomic vectors are missing?
    if not hasattr(interatom, 'vector'):
        # Throw a warning.
        warn(RelaxWarning("RDC data exists but the interatomic vectors are missing, skipping the spin pair '%s' and '%s'." % (interatom.spin_id1, interatom.spin_id2)))

        # Jump to the next spin.
        return False

    # Skip non-Me pseudo-atoms for the first spin.
    if hasattr(spin1, 'members') and len(spin1.members) != 3:
        warn(RelaxWarning("Only methyl group pseudo atoms are supported due to their fast rotation, skipping the spin pair '%s' and '%s'." % (interatom.spin_id1, interatom.spin_id2)))
        return False

    # Skip non-Me pseudo-atoms for the second spin.
    if hasattr(spin2, 'members') and len(spin2.members) != 3:
        warn(RelaxWarning("Only methyl group pseudo atoms are supported due to their fast rotation, skipping the spin pair '%s' and '%s'." % (interatom.spin_id1, interatom.spin_id2)))
        return False

    # Checks.
    if not hasattr(spin1, 'isotope'):
        raise RelaxSpinTypeError(interatom.spin_id1)
    if not hasattr(spin2, 'isotope'):
        raise RelaxSpinTypeError(interatom.spin_id2)
    if not hasattr(interatom, 'r'):
        raise RelaxNoValueError("averaged interatomic distance")

    # Everything is ok.
    return True


def num_data_points():
    """Determine the number of data points used in the model.

    @return:    The number, n, of data points in the model.
    @rtype:     int
    """

    # Determine the data type.
    data_types = base_data_types()

    # Init.
    n = 0

    # Spin loop.
    for spin in spin_loop():
        # Skip deselected spins.
        if not spin.select:
            continue

        # PCS data (skipping array elements set to None).
        if 'pcs' in data_types:
            if hasattr(spin, 'pcs'):
                for pcs in spin.pcs:
                    if isinstance(pcs, float):
                        n = n + 1

    # Interatomic data loop.
    for interatom in interatomic_loop():
        # RDC data (skipping array elements set to None).
        if 'rdc' in data_types:
            if hasattr(interatom, 'rdc'):
                for rdc in interatom.rdc:
                    if isinstance(rdc, float):
                        n = n + 1

    # Alignment tensors.
    if 'tensor' in data_types:
        n = n + 5*len(cdp.align_tensors)

    # Return the value.
    return n


def opt_tensor(tensor):
    """Determine if the given tensor is to be optimised.

    @param tensor:  The alignment tensor to check.
    @type tensor:   AlignmentTensor object.
    @return:        True if the tensor is to be optimised, False otherwise.
    @rtype:         bool
    """

    # Combine all RDC and PCS IDs.
    ids = []
    if hasattr(cdp, 'rdc_ids'):
        ids += cdp.rdc_ids
    if hasattr(cdp, 'pcs_ids'):
        ids += cdp.pcs_ids

    # No RDC or PCS data for the alignment, so skip the tensor as it will not be optimised.
    if tensor.align_id not in ids:
        return False

    # Fixed tensor.
    if tensor.fixed:
        return False

    # The tensor is to be optimised.
    return True


def opt_uses_align_data(align_id=None):
    """Determine if the PCS or RDC data for the given alignment ID is needed for optimisation.

    @keyword align_id:  The optional alignment ID string.
    @type align_id:     str
    @return:            True if alignment data is to be used for optimisation, False otherwise.
    @rtype:             bool
    """

    # No alignment IDs.
    if not hasattr(cdp, 'align_ids'):
        return False

    # Convert the align IDs to an array, or take all IDs.
    if align_id:
        align_ids = [align_id]
    else:
        align_ids = cdp.align_ids

    # Check the PCS and RDC.
    for align_id in align_ids:
        if opt_uses_pcs(align_id) or opt_uses_rdc(align_id):
            return True

    # No alignment data is used for optimisation.
    return False


def opt_uses_j_couplings():
    """Determine of J couplings are needed for optimisation.

    @return:    True if J couplings are required, False otherwise.
    @rtype:     bool
    """

    # Loop over the alignments.
    for align_id in cdp.align_ids:
        for interatom in interatomic_loop():
            if hasattr(interatom, 'rdc_data_types') and align_id in interatom.rdc_data_types and interatom.rdc_data_types[align_id] == 'T':
                return True

    # No J values required.
    return False


def opt_uses_pcs(align_id):
    """Determine if the PCS data for the given alignment ID is needed for optimisation.

    @param align_id:    The alignment ID string.
    @type align_id:     str
    @return:            True if the PCS data is to be used for optimisation, False otherwise.
    @rtype:             bool
    """

    # No alignment IDs.
    if not hasattr(cdp, 'pcs_ids'):
        return False

    # No PCS data for the alignment.
    if align_id not in cdp.pcs_ids:
        return False

    # Is the tensor optimised?
    tensor_flag = opt_tensor(align_tensor.get_tensor_object(align_id))

    # Is the paramagnetic position optimised?
    pos_flag = False
    if hasattr(cdp, 'paramag_centre_fixed') and not cdp.paramag_centre_fixed:
        pos_flag = True

    # Are the populations optimised?
    prob_flag = False
    if cdp.model == 'population':
        prob_flag = True

    # Not used.
    if not tensor_flag and not pos_flag and not prob_flag:
        return False

    # The PCS data is to be used for optimisation.
    return True


def opt_uses_rdc(align_id):
    """Determine if the RDC data for the given alignment ID is needed for optimisation.

    @param align_id:    The alignment ID string.
    @type align_id:     str
    @return:            True if the RDC data is to be used for optimisation, False otherwise.
    @rtype:             bool
    """

    # No alignment IDs.
    if not hasattr(cdp, 'rdc_ids'):
        return False

    # No RDC data for the alignment.
    if align_id not in cdp.rdc_ids:
        return False

    # Is the tensor optimised?
    tensor_flag = opt_tensor(align_tensor.get_tensor_object(align_id))

    # Is the paramagnetic position optimised?
    pos_flag = False
    if hasattr(cdp, 'paramag_centre_fixed') and not cdp.paramag_centre_fixed:
        pos_flag = True

    # Are the populations optimised?
    prob_flag = False
    if cdp.model == 'population':
        prob_flag = True

    # Not used.
    if not tensor_flag and not pos_flag and not prob_flag:
        return False

    # The RDC data is to be used for optimisation.
    return True


def return_pcs_data(sim_index=None):
    """Set up the data structures for optimisation using PCSs as base data sets.

    @keyword sim_index: The index of the simulation to optimise.  This should be None if normal optimisation is desired.
    @type sim_index:    None or int
    @return:            The assembled data structures for using PCSs as the base data for optimisation.  These include:
                            - the PCS values.
                            - the unit vectors connecting the paramagnetic centre (the electron spin) to
                            - the PCS weight.
                            - the nuclear spin.
                            - the pseudocontact shift constants.
    @rtype:             tuple of (numpy rank-2 array, numpy rank-2 array, numpy rank-2 array, numpy rank-1 array, numpy rank-1 array)
    """

    # Data setup tests.
    if not hasattr(cdp, 'paramagnetic_centre') and (hasattr(cdp, 'paramag_centre_fixed') and cdp.paramag_centre_fixed):
        raise RelaxError("The paramagnetic centre has not yet been specified.")
    if not hasattr(cdp, 'temperature'):
        raise RelaxError("The experimental temperatures have not been set.")
    if not hasattr(cdp, 'spectrometer_frq'):
        raise RelaxError("The spectrometer frequencies of the experiments have not been set.")

    # Initialise.
    pcs = []
    pcs_err = []
    pcs_weight = []
    temp = []
    frq = []

    # The PCS data.
    for i in range(len(cdp.align_ids)):
        # Alias the ID.
        align_id = cdp.align_ids[i]

        # Skip non-optimised data.
        if not opt_uses_align_data(align_id):
            continue

        # Append empty arrays to the PCS structures.
        pcs.append([])
        pcs_err.append([])
        pcs_weight.append([])

        # Get the temperature for the PCS constant.
        if align_id in cdp.temperature:
            temp.append(cdp.temperature[align_id])

        # The temperature must be given!
        else:
            raise RelaxError("The experimental temperature for the alignment ID '%s' has not been set." % align_id)

        # Get the spectrometer frequency in Tesla units for the PCS constant.
        if align_id in cdp.spectrometer_frq:
            frq.append(cdp.spectrometer_frq[align_id] * 2.0 * pi / g1H)

        # The frequency must be given!
        else:
            raise RelaxError("The spectrometer frequency for the alignment ID '%s' has not been set." % align_id)

        # Spin loop.
        j = 0
        for spin in spin_loop():
            # Skip deselected spins.
            if not spin.select:
                continue

            # Skip spins without PCS data.
            if not hasattr(spin, 'pcs'):
                continue

            # Append the PCSs to the list.
            if align_id in spin.pcs.keys():
                if sim_index != None:
                    pcs[-1].append(spin.pcs_sim[align_id][sim_index])
                else:
                    pcs[-1].append(spin.pcs[align_id])
            else:
                pcs[-1].append(None)

            # Append the PCS errors.
            if hasattr(spin, 'pcs_err') and align_id in spin.pcs_err.keys():
                pcs_err[-1].append(spin.pcs_err[align_id])
            else:
                pcs_err[-1].append(None)

            # Append the weight.
            if hasattr(spin, 'pcs_weight') and align_id in spin.pcs_weight.keys():
                pcs_weight[-1].append(spin.pcs_weight[align_id])
            else:
                pcs_weight[-1].append(1.0)

            # Spin index.
            j = j + 1

    # Convert to numpy objects.
    pcs = array(pcs, float64)
    pcs_err = array(pcs_err, float64)
    pcs_weight = array(pcs_weight, float64)

    # Convert the PCS from ppm to no units.
    pcs = pcs * 1e-6
    pcs_err = pcs_err * 1e-6

    # Return the data structures.
    return pcs, pcs_err, pcs_weight, temp, frq


def return_rdc_data(sim_index=None):
    """Set up the data structures for optimisation using RDCs as base data sets.

    @keyword sim_index: The index of the simulation to optimise.  This should be None if normal optimisation is desired.
    @type sim_index:    None or int
    @return:            The assembled data structures for using RDCs as the base data for optimisation.  These include:
                            - rdc, the RDC values.
                            - rdc_err, the RDC errors.
                            - rdc_weight, the RDC weights.
                            - vectors, the interatomic vectors.
                            - rdc_const, the dipolar constants.
                            - absolute, the absolute value flags (as 1's and 0's).
                            - T_flags, the flags for T = J+D type data (as 1's and 0's).
                            - j_couplings, the J coupling values if the RDC data type is set to T = J+D.
    @rtype:             tuple of (numpy rank-2 array, numpy rank-2 array, numpy rank-2 array, numpy rank-3 array, numpy rank-2 array, numpy rank-2 array)
    """

    # Initialise.
    rdc = []
    rdc_err = []
    rdc_weight = []
    unit_vect = []
    rdc_const = []
    absolute = []
    T_flags = []
    j_couplings = []

    # The unit vectors, RDC constants, and J couplings.
    for interatom in interatomic_loop():
        # Get the spins.
        spin1 = return_spin(interatom.spin_id1)
        spin2 = return_spin(interatom.spin_id2)

        # RDC checks.
        if not check_rdcs(interatom, spin1, spin2):
            continue

        # Add the vectors.
        if is_float(interatom.vector[0]):
            unit_vect.append([interatom.vector])
        else:
            unit_vect.append(interatom.vector)

        # Gyromagnetic ratios.
        g1 = return_gyromagnetic_ratio(spin1.isotope)
        g2 = return_gyromagnetic_ratio(spin2.isotope)

        # Calculate the RDC dipolar constant (in Hertz, and the 3 comes from the alignment tensor), and append it to the list.
        rdc_const.append(3.0/(2.0*pi) * dipolar_constant(g1, g2, interatom.r))

        # Store the J coupling.
        if opt_uses_j_couplings():
            j_couplings.append(interatom.j_coupling)

    # Fix the unit vector data structure.
    num = None
    for rdc_index in range(len(unit_vect)):
        # Number of vectors.
        if num == None:
            if unit_vect[rdc_index] != None:
                num = len(unit_vect[rdc_index])
            continue

        # Check.
        if unit_vect[rdc_index] != None and len(unit_vect[rdc_index]) != num:
            raise RelaxError("The number of interatomic vectors for all no match:\n%s" % unit_vect)

    # Missing unit vectors.
    if num == None:
        raise RelaxError("No interatomic vectors could be found.")

    # Update None entries.
    for i in range(len(unit_vect)):
        if unit_vect[i] == None:
            unit_vect[i] = [[None, None, None]]*num

    # The RDC data.
    for i in range(len(cdp.align_ids)):
        # Alias the ID.
        align_id = cdp.align_ids[i]

        # Skip non-optimised data.
        if not opt_uses_align_data(align_id):
            continue

        # Append empty arrays to the RDC structures.
        rdc.append([])
        rdc_err.append([])
        rdc_weight.append([])
        absolute.append([])
        T_flags.append([])

        # Interatom loop.
        for interatom in interatomic_loop():
            # Get the spins.
            spin1 = return_spin(interatom.spin_id1)
            spin2 = return_spin(interatom.spin_id2)

            # Skip deselected spins.
            if not spin1.select or not spin2.select:
                continue

            # Only use interatomic data containers with RDC and vector data.
            if not hasattr(interatom, 'rdc') or not hasattr(interatom, 'vector'):
                continue

            # T-type data.
            if align_id in interatom.rdc_data_types and interatom.rdc_data_types[align_id] == 'T':
                T_flags[-1].append(True)
            else:
                T_flags[-1].append(False)

            # Check for J couplings if the RDC data type is T = J+D.
            if T_flags[-1][-1] and not hasattr(interatom, 'j_coupling'):
                continue

            # Defaults of None.
            value = None
            error = None

            # Pseudo-atom set up.
            if (hasattr(spin1, 'members') or hasattr(spin2, 'members')) and align_id in interatom.rdc.keys():
                # Skip non-Me groups.
                if (hasattr(spin1, 'members') and len(spin1.members) != 3) or (hasattr(spin2, 'members') and len(spin2.members) != 3):
                    continue

                # The RDC for the Me-pseudo spin where:
                #     <D> = -1/3 Dpar.
                # See Verdier, et al., JMR, 2003, 163, 353-359.
                if sim_index != None:
                    value = -3.0 * interatom.rdc_sim[align_id][sim_index]
                else:
                    value = -3.0 * interatom.rdc[align_id]

                # The error.
                if hasattr(interatom, 'rdc_err') and align_id in interatom.rdc_err.keys():
                    # T values.
                    if T_flags[-1][-1]:
                        error = -3.0 * sqrt(interatom.rdc_err[align_id]**2 + interatom.j_coupling_err**2)

                    # D values.
                    else:
                        error = -3.0 * interatom.rdc_err[align_id]

            # Normal set up.
            elif align_id in interatom.rdc.keys():
                # The RDC.
                if sim_index != None:
                    value = interatom.rdc_sim[align_id][sim_index]
                else:
                    value = interatom.rdc[align_id]

                # The error.
                if hasattr(interatom, 'rdc_err') and align_id in interatom.rdc_err.keys():
                    # T values.
                    if T_flags[-1][-1]:
                        error = sqrt(interatom.rdc_err[align_id]**2 + interatom.j_coupling_err**2)

                    # D values.
                    else:
                        error = interatom.rdc_err[align_id]

            # Append the RDCs to the list.
            rdc[-1].append(value)

            # Append the RDC errors.
            rdc_err[-1].append(error)

            # Append the weight.
            if hasattr(interatom, 'rdc_weight') and align_id in interatom.rdc_weight.keys():
                rdc_weight[-1].append(interatom.rdc_weight[align_id])
            else:
                rdc_weight[-1].append(1.0)

            # Append the absolute value flag.
            if hasattr(interatom, 'absolute_rdc') and align_id in interatom.absolute_rdc.keys():
                absolute[-1].append(interatom.absolute_rdc[align_id])
            else:
                absolute[-1].append(False)

    # Convert to numpy objects.
    rdc = array(rdc, float64)
    rdc_err = array(rdc_err, float64)
    rdc_weight = array(rdc_weight, float64)
    unit_vect = array(unit_vect, float64)
    rdc_const = array(rdc_const, float64)
    absolute = array(absolute, float64)
    T_flags = array(T_flags, float64)
    if opt_uses_j_couplings():
        j_couplings = array(j_couplings, float64)
    else:
        j_couplings = None

    # Return the data structures.
    return rdc, rdc_err, rdc_weight, unit_vect, rdc_const, absolute, T_flags, j_couplings


def tensor_loop(red=False):
    """Generator method for looping over the full or reduced tensors.

    @keyword red:   A flag which if True causes the reduced tensors to be returned, and if False
                    the full tensors are returned.
    @type red:      bool
    @return:        The tensor index and the tensor.
    @rtype:         (int, AlignTensorData instance)
    """

    # Number of tensor pairs.
    n = len(cdp.align_tensors.reduction)

    # Alias.
    data = cdp.align_tensors
    list = data.reduction

    # Full or reduced index.
    if red:
        index = 1
    else:
        index = 0

    # Loop over the reduction list.
    for i in range(n):
        yield i, data[list[i][index]]
