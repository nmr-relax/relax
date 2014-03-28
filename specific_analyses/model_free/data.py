###############################################################################
#                                                                             #
# Copyright (C) 2007-2014 Edward d'Auvergne                                   #
# Copyright (C) 2007 Gary S Thompson (https://gna.org/users/varioustoxins)    #
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
"""The Lipari-Szabo model-free analysis base data functions."""


# Python module imports.
from re import search

# relax module imports.
from lib.errors import RelaxError


def compare_objects(object_from, object_to, pipe_from, pipe_to):
    """Compare the contents of the two objects and raise RelaxErrors if they are not the same.

    @param object_from: The first object.
    @type object_from:  any object
    @param object_to:   The second object.
    @type object_to:    any object
    @param pipe_from:   The name of the data pipe containing the first object.
    @type pipe_from:    str
    @param pipe_to:     The name of the data pipe containing the second object.
    @type pipe_to:      str
    """

    # Loop over the modifiable objects.
    for data_name in dir(object_from):
        # Skip special objects (starting with _, or in the original class and base class namespaces).
        if search('^_', data_name) or data_name in list(object_from.__class__.__dict__.keys()) or (hasattr(object_from.__class__, '__bases__') and len(object_from.__class__.__bases__) and data_name in list(object_from.__class__.__bases__[0].__dict__.keys())):
            continue

        # Skip some more special objects.
        if data_name in ['structural_data']:
            continue

        # Get the original object.
        data_from = None
        if hasattr(object_from, data_name):
            data_from = getattr(object_from, data_name)

        # Get the target object.
        if data_from and not hasattr(object_to, data_name):
            raise RelaxError("The structural object " + repr(data_name) + " of the " + repr(pipe_from) + " data pipe is not located in the " + repr(pipe_to) + " data pipe.")
        elif data_from:
            data_to = getattr(object_to, data_name)
        else:
            continue

        # The data must match!
        if data_from != data_to:
            raise RelaxError("The object " + repr(data_name) + " is not consistent between the pipes " + repr(pipe_from) + " and " + repr(pipe_to) + ".")
