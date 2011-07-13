###############################################################################
#                                                                             #
# Copyright (C) 2011 Edward d'Auvergne                                        #
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
"""Module implementing the observer design pattern base class."""

# relax module imports.
from relax_errors import RelaxError


class Observer(object):
    """The observer design pattern base class."""

    def __init__(self):
        """Set up the object."""

        # The dictionary of callback methods.
        self._callback = {}


    def notify_observers(self):
        """Notify all observers of the state change."""

        # Loop over the callback methods and execute them.
        for key in self._callback.keys():
            self._callback[key]()


    def register_observer(self, key, method):
        """Register a method to be called when the state changes.

        @param key:     The key to identify the observer's method.
        @type key:      str
        @param method:  The observer's method to be called after a state change.
        @type method:   method
        """

        # Already exists.
        if key in self._callback.keys():
            raise RelaxError("The observer '%s' already exists." % key)

        # Add the method to the dictionary of callbacks.
        self._callback[key] = method


    def unregister_observer(self, key):
        """Unregister the method corresponding to the key.

        @param key:     The key to identify the observer's method.
        @type key:      str
        """

        # Does not exist.
        if key not in self._callback.keys():
            raise RelaxError("The key '%s' does not exist." % key)

        # Remove the method from the dictionary of callbacks.
        self._callback.pop(key)
