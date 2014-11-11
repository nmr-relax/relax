###############################################################################
#                                                                             #
# Copyright (C) 2009-2014 Edward d'Auvergne                                   #
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
"""Module for handling the frame order data in the relax data store."""

# relax module imports.
from lib.errors import RelaxError
from pipe_control.interatomic import interatomic_loop
from pipe_control.mol_res_spin import spin_loop


def base_data_types():
    """Determine all the base data types.

    The base data types can include::
        - 'rdc', residual dipolar couplings.
        - 'pcs', pseudo-contact shifts.

    @return:    A list of all the base data types.
    @rtype:     list of str
    """

    # Array of data types.
    list = []

    # RDC search.
    for interatom in interatomic_loop(selection1=domain_moving()):
        if hasattr(interatom, 'rdc'):
            list.append('rdc')
            break

    # PCS search.
    for spin in spin_loop(selection=domain_moving()):
        if hasattr(spin, 'pcs'):
            list.append('pcs')
            break

    # No data is present.
    if not list:
        raise RelaxError("Neither RDCs nor PCSs are present.")

    # Return the list.
    return list


def domain_moving():
    """Return the spin ID string corresponding to the moving domain.

    @return:    The spin ID string defining the moving domain.
    @rtype:     str
    """

    # Check that the domain is defined.
    if not hasattr(cdp, 'domain'):
        raise RelaxError("No domains have been defined.  Please use the domain user function.")

    # Only support for 2 domains.
    if len(cdp.domain) > 2:
        raise RelaxError("Only two domains are supported in the frame order analysis.")

    # Reference domain not set yet, so return nothing.
    if not hasattr(cdp, 'ref_domain'):
        return None

    # Loop over the domains.
    for id in cdp.domain:
        # Reference domain.
        if id == cdp.ref_domain:
            continue

        # Return the ID.
        return cdp.domain[id]


def pivot_fixed():
    """Determine if the pivot is fixed or not.

    @return:    The answer to the question.
    @rtype:     bool
    """

    # A pivot point is not supported by the model.
    if cdp.model in ['rigid']:
        return True

    # The PCS is loaded.
    if 'pcs' in base_data_types():
        # The fixed flag is not set.
        if hasattr(cdp, 'pivot_fixed') and not cdp.pivot_fixed:
            return False

    # The point is fixed.
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


def translation_fixed():
    """Is the translation of the average domain position fixed?

    @return:    The answer to the question.
    @rtype:     bool
    """

    # PCS data must be present.
    if 'pcs' in base_data_types():
        # The fixed flag is not set.
        if hasattr(cdp, 'ave_pos_translation') and cdp.ave_pos_translation:
            return False

    # Default to being fixed.
    return True
