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
"""Module containing the user function data singleton which stores all of the data."""

# Python module imports.
from re import search
from string import split

# relax module imports.
from relax_errors import RelaxError
from user_functions.objects import Class_container, Uf_container


class Uf_info(object):
    """The user function data singleton class."""

    # Class variable for storing the class instance (for the singleton).
    _instance = None

    def __new__(self, *args, **kargs):
        """Replacement method for implementing the singleton design pattern."""

        # First instantiation.
        if self._instance is None:
            # Instantiate.
            self._instance = object.__new__(self, *args, **kargs)

            # Initialise a number of class variables.
            self._uf_names = []
            self._uf = []
            self._class_names = []
            self._classes = []

        # Already instantiated, so return the instance.
        return self._instance


    def add_class(self, name):
        """Add a new user function class.

        @param name:    The name of the user function class.
        @type name:     str
        @return:        The user function class data object.
        @rtype:         user_functions.objects.Class_container instance
        """

        # Store the name and initialise a new object.
        self._class_names.append(name)
        self._classes.append(Class_container())

        # Return the object.
        return self._classes[-1]


    def add_uf(self, name):
        """Add the user function to the object.

        @param name:    The name of the user function.
        @type name:     str
        @return:        The user function data object.
        @rtype:         user_functions.objects.Uf_container instance
        """

        # First check if the user function class has been set up.
        if search('.', name):
            # Split up the name.
            class_name, fn_name = split(name, '.')

            # Check for the class name.
            if class_name not in self._class_names:
                raise RelaxError("The user function class '%s' has not been set up yet." % class_name)

        # Store the name and initialise a new object.
        self._uf_names.append(name)
        self._uf.append(Uf_container())

        # Return the object.
        return self._uf[-1]
