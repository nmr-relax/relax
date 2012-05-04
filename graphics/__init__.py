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

# Package docstring.
"""The relax graphics package."""

# Python module imports.
from os import sep
from string import split


def fetch_icon(icon, size='16x16'):
    """Return the path to the specified icon.

    The icon code consists of two parts separated by the '.' character.  These are:

        - The first part corresponds to the icon type, and can either be 'relax' or 'oxygen'.
        - The second part is the icon name, as a path.  The directories and files are separated by '.' characters.  So for the 'actions/dialog-close.png' icon, the second part would be 'actions.dialog-close'.

    To specify the 'graphics/oxygen_icons/16x16/actions/document-open.png' icon, the icon code string would therefore be 'oxygen.actions.document-open'.

    @param icon:    The special icon code.
    @type icon:     str
    @keyword size:  The icon size to fetch.
    @type size:     str
    @return:        The icon path, for example 'oxygen_icons/16x16/actions/document-open.png'.
    @rtype:         str
    """

    # Initialise the path.
    path = 'graphics' + sep

    # Split up the icon code.
    elements = split(icon, '.')

    # The icon type.
    if elements[0] == 'relax':
        path += 'relax_icons' + sep
    elif elements[0] == 'oxygen':
        path += 'oxygen_icons' + sep
    else:
        raise RelaxError("The icon type '%s' is unknown." % elements[0])

    # The icon size.
    path += size + sep

    # The subdirectory.
    if len(elements) == 3:
        path += elements[1] + sep

    # The file.
    path += "%s.png" % elements[-1]

    # Return the path.
    return path
