###############################################################################
#                                                                             #
# Copyright (C) 2007-2008 Edward d'Auvergne                                   #
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

# relax module imports.
from data import Data as relax_data_store
from relax_errors import RelaxError, RelaxNoPipeError, RelaxSpinSelectDisallowError
from selection import parse_token, residue_loop, return_residue, return_spin, return_single_spin_info, spin_loop, tokenise


# Module doc.
"""Functions for manipulating the spin information content in the relax data storage singleton.

This touches part of the molecule-residue-spin data structure.
"""


def name_spin(spin_id=None, name=None):
    """Name the spins.

    @param spin_id:     The spin identification string.
    @type spin_id:      str
    @param name:        The new spin name.
    @type name:         str
    """

    # Rename the spin.
    for spin in spin_loop(spin_id):
        spin.name = name


def number_spin(spin_id=None, number=None):
    """Number the spins.

    @param spin_id:     The spin identification string.
    @type spin_id:      str
    @param number:      The new spin number.
    @type number:       int
    """

    # Catch multiple renumberings!
    i = 0
    for spin in spin_loop(spin_id):
        i = i + 1

    # Fail if multiple spins are numbered.
    if i > 1:
        raise RelaxError, "The numbering of multiple spins is disallowed, as each spin requires a unique number."

    # Rename the spin.
    for spin in spin_loop(spin_id):
        spin.num = number
