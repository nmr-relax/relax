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
"""Module containing the special objects for auto-generating the user functions and classes."""

# relax module imports.
from prompt.base_class import _strip_lead
from prompt.help import relax_class_help


class Class_container(object):
    """The container for created the user function class objects."""

    def __init__(self, name, desc):
        """Set up the container.

        @param name:    The name of the user function class.
        @type name:     str
        @param desc:    The description to be presented by the help system.
        @type desc:     str
        """

        # Store the args.
        self._name = name

        # Build the relax help system string.
        self.__relax_help__ = desc
        self.__relax_help__ += "\n%s" % relax_class_help

        # Add a description to the help string.
        if hasattr(self, '__description__'):
            self.__relax_help__ += "\n\n%s" % _strip_lead(self.__description__)


    def __repr__(self):
        """Replacement function for displaying an instance of this user function class."""

        # Return a description.
        return "<The %s user function class object>" % self._name
