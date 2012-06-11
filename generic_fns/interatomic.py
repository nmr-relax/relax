###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
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
"""Module for the manipulation of the interatomic data structures in the relax data store."""

# relax module imports.
from generic_fns import pipes
from generic_fns.mol_res_spin import return_spin
from relax_warnings import RelaxNoSpinWarning


def create_interatom(spin_id1=None, spin_id2=None):
    """Create and return the interatomic data container for the two spins.

    @keyword spin_id1:  The spin ID string of the first atom.
    @type spin_id1:     str
    @keyword spin_id2:  The spin ID string of the first atom.
    @type spin_id2:     str
    @return:            The newly created interatomic data container.
    @rtype:             data.interatomic.InteratomContainer instance
    """

    # Check that the spin IDs exist.
    spin = return_spin(spin_id1)
    if spin == None:
        raise RelaxNoSpinWarning(spin_id1)
    spin = return_spin(spin_id2)
    if spin == None:
        raise RelaxNoSpinWarning(spin_id2)

    # Add and return the data.
    return cdp.interatomic.add_item(spin_id1=spin_id1, spin_id2=spin_id2)


def return_interatom(spin_id1=None, spin_id2=None, pipe=None):
    """Return the interatomic data container for the two spins.

    @keyword spin_id1:  The spin ID string of the first atom.
    @type spin_id1:     str
    @keyword spin_id2:  The spin ID string of the first atom.
    @type spin_id2:     str
    @keyword pipe:      The data pipe holding the container.  Defaults to the current data pipe.
    @type pipe:         str or None
    @return:            The interatomic data container, if it exists.
    @rtype:             data.interatomic.InteratomContainer instance or None
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Loop over the data.
    for i in range(len(dp.interatomic)):
        if dp.interatomic[i].id_match(spin_id1, spin_id2):
            return dp.interatomic[i]

    # No container found.
    return None
