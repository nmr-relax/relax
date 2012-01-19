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
"""A module of special objects used within the specific function API."""

# relax module imports.
from relax_errors import RelaxError


class Param_list:
    """A special object for handling global and spin parameters."""

    def __init__(self):
        """Set up the class."""

        # Initialise the lists and dictionaries for the parameter info.
        self._names = []
        self._string = {}
        self._defaults = {}
        self._units = {}
        self._desc = {}
        self._grace_string = {}


    def add(self, name, string=None, default=None, units=None, desc=None, grace_string=None):
        """Add a parameter to the list.

        @param name:            The name of the parameter.  This will be used as the variable name.
        @type name:             str
        @keyword string:        The string representation of the parameter.
        @type string:           None or str
        @keyword default:       The default value of the parameter.
        @type default:          anything
        @keyword units:         A string representing the parameters units.
        @type units:            None or str
        @keyword desc:          The text description of the parameter.
        @type desc:             None or str
        @keyword grace_string:  The string used for the axes in Grace plots of the data.
        @type grace_string:     None or str
        """

        # Append the values.
        self._names.append(name)
        self._defaults[name] = default
        self._units[name] = units
        self._desc[name] = desc

        # The parameter string.
        if string:
            self._string[name] = string
        else:
            self._string[name] = name

        # The Grace string.
        if grace_string:
            self._grace_string[name] = grace_string
        else:
            self._grace_string[name] = name


    def contains(self, name):
        """Determine if the given name is within the parameter list.

        @param name:    The name of the parameter to search for.
        @type name:     str
        @return:        True if the parameter is within the list, False otherwise.
        @rtype:         bool
        """

        # Check.
        if name in self._names:
            return True

        # No match.
        return False


    def get_desc(self, name):
        """Return the description of the parameter.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        The description.
        @rtype:         None or str
        """

        # Check.
        if name not in self._names:
            return None

        # Return the description.
        return self._desc[name]


    def get_grace_string(self, name):
        """Return the Grace string for the parameter.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        The Grace string.
        @rtype:         str
        """

        # Check.
        if name not in self._names:
            raise RelaxError("The parameter '%s' does not exist." % name)

        # Return the value.
        return self._grace_string[name]


    def get_units(self, name):
        """Return the units string for the parameter.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        The units string.
        @rtype:         str
        """

        # Check.
        if name not in self._names:
            raise RelaxError("The parameter '%s' does not exist." % name)

        # Return the value.
        return self._units[name]
