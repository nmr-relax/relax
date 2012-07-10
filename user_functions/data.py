###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
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
"""Module containing the user function data singleton which stores all of the data."""

# Python module imports.
from re import search
from relax_errors import RelaxError
from string import split

# relax module imports.
from relax_errors import RelaxError
from user_functions.objects import Class_container, Table, Uf_container


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
            self._uf = {}
            self._class_names = []
            self._classes = {}

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
        self._classes[name] = Class_container()

        # Alphabetically sort the names.
        self._class_names.sort()

        # Return the object.
        return self._classes[name]


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
        if search('\.', name):
            # Split up the name.
            class_name, fn_name = split(name, '.')

            # Check for the class name.
            if class_name not in self._class_names:
                raise RelaxError("The user function class '%s' has not been set up yet." % class_name)

        # Store the name and initialise a new object.
        self._uf_names.append(name)
        self._uf[name] = Uf_container()

        # Alphabetically sort the names.
        self._uf_names.sort()

        # Return the object.
        return self._uf[name]


    def class_loop(self):
        """Iterator method for looping over the user function classes.

        @return:    The class name and data container.
        @rtype:     tuple of str and Class_container instance
        """

        # Loop over the classes.
        for i in range(len(self._class_names)):
            yield self._class_names[i], self._classes[self._class_names[i]]


    def get_class(self, name):
        """Return the user function class data object corresponding to the given name.

        @param name:    The name of the user function class.
        @type name:     str
        @return:        The class data container.
        @rtype:         Class_container instance
        """

        # Return the object.
        return self._classes[name]


    def get_uf(self, name):
        """Return the user function data object corresponding to the given name.

        @param name:    The name of the user function.
        @type name:     str
        @return:        The user function data container.
        @rtype:         Uf_container instance
        """

        # Return the object.
        return self._uf[name]


    def uf_loop(self, uf_class=None):
        """Iterator method for looping over the user functions.

        @keyword uf_class:  If given, restrict the iterator to a user function class.
        @type uf_class:     str or None
        @return:            The user function name and data container.
        @rtype:             tuple of str and Uf_container instance
        """

        # Loop over the user functions.
        for i in range(len(self._uf_names)):
            # Restriction.
            if uf_class and not search("^%s\." % uf_class, self._uf_names[i]):
                continue

            yield self._uf_names[i], self._uf[self._uf_names[i]]


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



class Uf_tables(object):
    """The data singleton holding all of the description tables."""

    # Class variable for storing the class instance (for the singleton).
    _instance = None

    def __new__(self, *args, **kargs):
        """Replacement method for implementing the singleton design pattern."""

        # First instantiation.
        if self._instance is None:
            # Instantiate.
            self._instance = object.__new__(self, *args, **kargs)

            # Initialise a number of class variables.
            self._tables = {}
            self._labels = []

        # Already instantiated, so return the instance.
        return self._instance


    def add_table(self, label=None, caption=None, caption_short=None, spacing=True, longtable=False):
        """Add a new table to the object.

        @keyword label:         The unique label of the table.  This is used to identify tables, and is also used in the table referencing in the LaTeX compilation of the user manual.
        @type label:            str
        @keyword caption:       The caption for the table.
        @type caption:          str
        @keyword caption_short: The optional short caption for the table, used in the LaTeX user manual list of tables section for example.
        @type caption_short:    str
        @keyword spacing:       A flag which if True will cause empty rows to be placed between elements.
        @type spacing:          bool
        @keyword longtable:     A special LaTeX flag which if True will cause the longtables package to be used to spread a table across multiple pages.  This should only be used for tables that do not fit on a single page.
        @type longtable:        bool
        @return:                The table object.
        @rtype:                 user_functions.objects.Table instance
        """

        # Check that the label is supplied.
        if label == None:
            raise RelaxError("The table label must be supplied.")

        # Check if the table already exists.
        if label in self._labels:
            raise RelaxError("The table with label '%s' has already been set up." % label)

        # Store the label and initialise a new object.
        self._labels.append(label)
        self._tables[label] = Table(label=label, caption=caption, caption_short=caption_short, spacing=spacing, longtable=longtable)

        # Return the table.
        return self._tables[label]


    def get_table(self, label):
        """Return the table matching the given label.

        @param label:   The unique label of the table.
        @type label:    str
        @return:        The table data container.
        @rtype:         user_functions.objects.Table instance
        """

        # Check the label.
        if label not in self._tables.keys():
            raise RelaxError("The table with label '%s' does not exist." % label)

        # Return the table.
        return self._tables[label]
