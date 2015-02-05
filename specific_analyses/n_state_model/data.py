###############################################################################
#                                                                             #
# Copyright (C) 2007-2015 Edward d'Auvergne                                   #
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
"""The N-state model or structural ensemble analysis base data handling."""

# Python module imports.
from numpy.linalg import norm

# relax module imports.
from lib.check_types import is_float
from lib.errors import RelaxError
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
                for id in spin.pcs:
                    if is_float(spin.pcs[id]):
                        n = n + 1

    # Interatomic data loop.
    for interatom in interatomic_loop():
        # RDC data (skipping array elements set to None).
        if 'rdc' in data_types:
            if hasattr(interatom, 'rdc'):
                for id in interatom.rdc:
                    if is_float(interatom.rdc[id]):
                        n = n + 1

    # Alignment tensors.
    if 'tensor' in data_types:
        n = n + 5*len(cdp.align_tensors)

    # Return the value.
    return n


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
