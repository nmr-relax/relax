###############################################################################
#                                                                             #
# Copyright (C) 2003-2004, 2006-2008 Edward d'Auvergne                        #
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

# Python module imports.
from re import search
from numpy import ndarray


# Empty data container.
#######################

class Element(object):
    """Empty data container."""

    def __repr__(self):
        # Header.
        text = "%-25s%-100s\n\n" % ("Data structure", "Value")

        # Data structures.
        for name in dir(self):
            # Skip Element and derived class methods.
            if name in list(Element.__dict__.keys()) or name in list(self.__class__.__dict__.keys()):
                continue

            # Skip special objects.
            if search("^_", name):
                continue

            # Get the object.
            obj = getattr(self, name)

            # Numpy matrices.
            if isinstance(obj, ndarray) and  isinstance(obj[0], ndarray):
                spacer = '\n'
            else:
                spacer = ''

            # Generate the text.
            text = text + "%-25s%s%-100s\n" % (name, spacer, repr(obj))

        # Return the lot.
        return text


    def is_empty(self):
        """Method for testing if the Element container is empty.

        @return:    True if the Element container is empty, False otherwise.
        @rtype:     bool
        """

        # An object has been added to the container.
        for name in dir(self):
            # Skip Element and derived class methods.
            if name in list(Element.__dict__.keys()) or name in list(self.__class__.__dict__.keys()):
                continue

            # Skip special objects.
            if search("^__", name):
                continue

            # An object has been added.
            return False

        # The Element container is empty.
        return True
