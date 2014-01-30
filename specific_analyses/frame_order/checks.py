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
"""Module for checks for the frame order analysis."""

# Python module imports.
from warnings import warn

# relax module imports.
from lib.errors import RelaxNoValueError, RelaxSpinTypeError
from lib.warnings import RelaxWarning


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

    # Skip deselected spins.
    if not spin1.select or not spin2.select:
        return False

    # Only use interatomic data containers with RDC data.
    if not hasattr(interatom, 'rdc'):
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
