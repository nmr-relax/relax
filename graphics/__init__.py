###############################################################################
#                                                                             #
# Copyright (C) 2012-2013 Edward d'Auvergne                                   #
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
"""The relax graphics package."""

# Python module imports.
from os import sep

# relax module imports.
from lib.errors import RelaxError
from status import Status; status = Status()

# GUI image and icon paths.
ANALYSIS_IMAGE_PATH = status.install_path + sep + 'graphics' + sep + 'analyses' + sep
IMAGE_PATH = status.install_path + sep + 'graphics' + sep + 'misc' + sep
WIZARD_IMAGE_PATH = status.install_path + sep + 'graphics' + sep + 'wizards' + sep


def fetch_icon(icon=None, size='16x16', format='png'):
    """Return the path to the specified icon.

    The icon code consists of two parts separated by the '.' character.  These are:

        - The first part corresponds to the icon type, and can either be 'relax' or 'oxygen'.
        - The second part is the icon name, as a path.  The directories and files are separated by '.' characters.  So for the 'actions/dialog-close.png' icon, the second part would be 'actions.dialog-close'.

    To specify the 'graphics/oxygen_icons/16x16/actions/document-open.png' icon, the icon code string would therefore be 'oxygen.actions.document-open'.

    @keyword icon:      The special icon code.
    @type icon:         str
    @keyword size:      The icon size to fetch.
    @type size:         str
    @keyword format:    The format of the icon, defaulting to PNG images.  This can be changed to 'eps.gz' for example, or None for no file ending.
    @type format:       str
    @return:            The icon path, for example 'oxygen_icons/16x16/actions/document-open.png'.
    @rtype:             str
    """

    # No icon.
    if icon == None:
        return None

    # Initialise the path.
    path = status.install_path + sep + 'graphics' + sep

    # Split up the icon code.
    elements = icon.split('.')

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
    if format == None:
        path += elements[-1]
    elif format == 'png':
        path += "%s.png" % elements[-1]
    elif format == 'eps.gz':
        path += "%s.eps.gz" % elements[-1]
    else:
        raise RelaxError("The icon format '%s' is unknown." % format)

    # Return the path.
    return path
