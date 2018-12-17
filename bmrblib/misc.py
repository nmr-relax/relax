#############################################################################
#                                                                           #
# The BMRB library.                                                         #
#                                                                           #
# Copyright (C) 2009-2015 Edward d'Auvergne                                 #
#                                                                           #
# This program is free software: you can redistribute it and/or modify      #
# it under the terms of the GNU General Public License as published by      #
# the Free Software Foundation, either version 3 of the License, or         #
# (at your option) any later version.                                       #
#                                                                           #
# This program is distributed in the hope that it will be useful,           #
# but WITHOUT ANY WARRANTY; without even the implied warranty of            #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
# GNU General Public License for more details.                              #
#                                                                           #
# You should have received a copy of the GNU General Public License         #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                           #
#############################################################################

# Module docstring.
"""Functions for manipulating NMR-STAR dictionary data.

This file is part of the U{BMRB library<https://gna.org/projects/bmrblib>}.
"""

# Python module imports.
from numpy import ndarray
from warnings import warn


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
    if data is None:
        missing = True

    # Fail.
    if missing:
        raise NameError("Data is missing from the " + name + '.')


def translate(data, format='str', reverse=False):
    """Translate all values back-and-forth between Python structures and NMR-STAR strings.

    @param data:        The data to translate.
    @type data:         anything
    @keyword format:    The format to convert to.  This can be 'str', 'int', or 'float'.
    @type format:       str
    """

    # From Python to NMR-STAR.
    if not reverse:
        # List data (including numpy arrays).
        if isinstance(data, list) or isinstance(data, ndarray):
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

        # Otherwise normal conversion.
        else:
            new_data = str(data)

    # The data is None.
    elif data == None:
        new_data = None

    # From NMR-STAR to Python.
    else:
        # Conversion function.
        if format == 'str':
            convert = str
        elif format == 'int':
            convert = int
        elif format == 'float':
            convert = float

        # List data.
        if isinstance(data, list):
            # Loop over the data.
            new_data = []
            for i in range(len(data)):
                if data[i] in ['?', '.']:
                    new_data.append(None)
                else:
                    new_data.append(convert(data[i]))

        # None.
        elif data in ['?', '.']:
            new_data = None

        # Otherwise normal conversion.
        else:
            new_data = convert(data)

    # Return the translated result.
    return new_data
