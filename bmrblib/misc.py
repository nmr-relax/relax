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
"""Functions for manipulating NMR-STAR dictionary data."""


def no_missing(data, name):
    """Check that there are no None values in the data.

    @param data:    The data to check.
    @type data:     anything
    @param name:    The name associated with the data.
    @type name:     str
    """

    # Init.
    missing = False

    # List data.
    if isinstance(data, list):
        # Loop over the data.
        for i in range(len(data)):
            if data[i] == None or data[i] == 'None':
                missing = True

    # None.
    if data == None:
        missing = True

    # Fail.
    if missing:
        raise NameError("Data is missing from the " + name + '.')


def translate(data):
    """Translate all None values into the '?' string.

    @param data:    The data to translate.
    @type data:     anything
    """

    # List data.
    if isinstance(data, list):
        # Loop over the data.
        new_data = []
        for i in range(len(data)):
            if data[i] == None or data[i] == 'None':
                new_data.append('?')
            else:
                new_data.append(str(data[i]))

    # None.
    elif data == None:
        new_data = '?'

    # Otherwise don't do anything (except convert to string).
    else:
        new_data = str(data)

    # Return the translated result.
    return new_data
