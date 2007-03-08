###############################################################################
#                                                                             #
# Copyright (C) 2003-2004, 2006-2007 Edward d'Auvergne                        #
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
from re import match
from types import DictType


__all__ = [ 'data_classes',
            'diff_tensor',
            'diff_tensor_auto_objects',
            'main' ]


class Data(DictType):
    """The relax data storage object."""

    # Singleton initialisation, the reference to the single instance of this class.
    __instance = None


    def __init__(self):
        pass


    def __new__(self, *args, **kargs):
        """Method for implementing the singleton design pattern.

        If no other class instance currently exists, create a new instance of this class.  Otherwise
        return the class instance.  See http://en.wikipedia.org/wiki/Singleton_pattern for a
        description of this design pattern.
        """

        # Create a new instance if none exists.
        if self.__instance is None:
            self.__instance = DictType.__new__(self, *args, **kargs)

        # Return the class instance.
        return self.__instance


    def __repr__(self):
        """The string representation of the object.

        Rather than using the standard Python conventions (either the string representation of the
        value or the "<...desc...>" notation), a rich-formatted description of the object is given.
        """

        # Intro text.
        text = "The relax data storage object.\n"

        # The data pipes.
        text = text + "\n"
        text = text + "Data pipes:\n"
        pipes = self.keys()
        if pipes:
            for pipe in pipes:
                text = text + "  %s\n" % `pipe`
        else:
            text = text + "  None\n"

        # Objects.
        text = text + "\n"
        text = text + "Objects:\n"
        for name in dir(self):
            if match("^_", name):
                continue
            if name in DictType.__dict__:
                continue
            text = text + "  %s, %s\n" % (name, `type(getattr(self, name))`)

        # DictType methods.
        text = text + "\n"
        text = text + "Dictionary type methods:\n"
        for name in dir(DictType):
            if match("^_", name):
                continue
            text = text + "  %s, %s\n" % (name, `type(getattr(self, name))`)
        return text


    def __reset__(self):
        """Delete all the data from the relax data storage object.

        This method is to make the current single instance of the Data object identical to a newly
        created instance of Data, hence resetting the relax program state.
        """

        # Get the keys of self.__dict__.
        keys = self.__dict__.keys()

        # Loop over the keys and delete the corresponding object.
        for key in keys:
            # Delete the object.
            del self.__dict__[key]

        # Rerun the __init__() method.
        self.__init__()
