###############################################################################
#                                                                             #
# Copyright (C) 2007-2008 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax.  If not, see <http://www.gnu.org/licenses/>.              #
#                                                                             #
###############################################################################

# Module docstring.
"""Module containing the Prototype base class for the molecule-residue-spin containers."""


# Python module imports.
from copy import deepcopy
from re import search


class Prototype(object):
    """Base class implementing the prototype design pattern."""

    def __deepcopy__(self, memo):
        """Replacement deepcopy method."""

        # Make a new object.
        new_obj = self.__class__.__new__(self.__class__)

        # Loop over all objects in self and make deepcopies of them.
        for name in dir(self):
            # Skip all names begining with '__'.
            if search('^__', name):
                continue

            # Skip the class methods.
            if name in list(self.__class__.__dict__.keys()):
                continue

            # Get the object.
            value = getattr(self, name)

            # Replace the object with a deepcopy of it.
            setattr(new_obj, name, deepcopy(value, memo))

        # Return the new object.
        return new_obj


    def __clone__(self):
        """Prototype method which returns a deepcopy of the object."""

        # Make a new object.
        return deepcopy(self)
