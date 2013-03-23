###############################################################################
#                                                                             #
# Copyright (C) 2011 Edward d'Auvergne                                        #
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
"""Module containing the structural domain related functions."""


def define(id=None, spin_id=None):
    """Define the domain.

    @keyword id:        The domain ID string.
    @type id:           str
    @keyword spin_id:   The spin ID string for all atoms of the domain.
    @type spin_id:      str
    """

    # Initialise the data structure if needed.
    if not hasattr(cdp, 'domain'):
        cdp.domain = {}

    # Store the domain info.
    cdp.domain[id] = spin_id


def get_domain_ids():
    """Return the list of all domain ID strings.

    @return:        The list of all domain IDs.
    @rtype:         list of str
    """

    # No pipe.
    if cdp == None:
        return []

    # No domain data.
    if not hasattr(cdp, 'domain'):
        return []

    # The domain IDs, sorted.
    ids = sorted(cdp.domain.keys())
    return ids
