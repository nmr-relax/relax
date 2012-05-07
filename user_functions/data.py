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
from relax_errors import RelaxError
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

        # Check if the user function already exists.
        if name in self._class_names:
            raise RelaxError("The user function class %s has already been set up." % name)

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

        # Check if the user function already exists.
        if name in self._uf_names:
            raise RelaxError("The user function %s has already been set up." % name)

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


    def class_loop(self):
        """Iterator method for looping over the user function classes.

        @return:    The class name and data container.
        @rtype:     tuple of str and Class_container instance
        """

        # Loop over the classes.
        for i in range(len(self._class_names)):
            yield self._class_names[i], self._classes[i]


    def get_class(self, name):
        """Return the user function class data object corresponding to the given name.

        @param name:    The name of the user function class.
        @type name:     str
        @return:        The class data container.
        @rtype:         Class_container instance
        """

        # Return the object.
        return self._classes[self._class_names.index(name)]


    def get_uf(self, name):
        """Return the user function data object corresponding to the given name.

        @param name:    The name of the user function.
        @type name:     str
        @return:        The user function data container.
        @rtype:         Uf_container instance
        """

        # Return the object.
        return self._uf[self._uf_names.index(name)]


    def uf_loop(self):
        """Iterator method for looping over the user functions.

        @return:    The user function name and data container.
        @rtype:     tuple of str and Uf_container instance
        """

        # Loop over the user functions.
        for i in range(len(self._uf_names)):
            yield self._uf_names[i], self._uf[i]


    def validate(self):
        """Validate that all of the user functions have been correctly set up."""

        # Loop over the user functions.
        for name, uf in self.uf_loop():
            # Check the title.
            if uf.title == None:
                raise RelaxError("The title of the %s user function has not been specified." % name)

            # Check the backend.
            if uf.backend == None:
                raise RelaxError("The back end of the %s user function has not been specified." % name)
