###############################################################################
#                                                                             #
# Copyright (C) 2009 Edward d'Auvergne                                        #
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
"""Module containing read/write functions for miscellaneous BMRB NMR-STAR saveframes."""

# relax module imports.
from version import version, get_revision


def write_relax(star):
    """Generate the Software saveframe records for relax.

    @param star:        The NMR-STAR dictionary object.
    @type star:         NMR_STAR instance
    """

    # The relax version.
    ver = version
    if ver == 'repository checkout':
        # Get the SVN revision.
        rev = get_revision()

        # Change the version string.
        if rev:
            ver = version + " r" + rev

    # The relax info.
    star.software.add(name='relax', version=ver, vendor_name='The relax development team', vendor_eaddress='http://nmr-relax.com', task='data processing')
