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
from numpy.linalg import norm
from warnings import warn

# relax module imports.
from lib.errors import RelaxError, RelaxNoValueError, RelaxSpinTypeError
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
