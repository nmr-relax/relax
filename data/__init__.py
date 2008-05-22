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

# Module docstring.
"""Package containing the relax data storage object."""


# Python module imports.
from re import match

# relax module imports.
from pipe_container import PipeContainer
from relax_errors import RelaxPipeError


__all__ = [ 'data_classes',
            'diff_tensor',
            'diff_tensor_auto_objects',
            'main' ]


class Relax_data_store(dict):
    """The relax data storage object."""

    # The current data pipe.
    current_pipe = None

    # Class variable for storing the class instance.
    instance = None

    def __new__(self, *args, **kargs): 
        """Replacement function for implementing the singleton design pattern."""

        # First initialisation.
        if self.instance is None:
            self.instance = dict.__new__(self, *args, **kargs)

        # Already initialised, so return the instance.
        return self.instance

    
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
            if match("^_", name) or name in dict.__dict__ or name == 'add' or name == 'instance':
                continue
            text = text + "  %s: %s\n" % (name, `getattr(self, name)`)

        # Methods.
        text = text + "\n"
        text = text + "Methods:\n"
        text = text + "  __reset__, Reset the relax data storage object back to its initial state\n"
        text = text + "  add, Add a new data pipe container.\n"


        # dict methods.
        text = text + "\n"
        text = text + "Inherited dictionary methods:\n"
        for name in dir(dict):
            if match("^_", name):
                continue
            text = text + "  %s\n" % name
        return text


    def __reset__(self):
        """Delete all the data from the relax data storage object.

        This method is to make the current single instance of the Data object identical to a newly
        created instance of Data, hence resetting the relax program state.
        """

        # Loop over the keys of self.__dict__ and delete the corresponding object.
        for key in self.__dict__.keys():
            # Delete the object.
            del self.__dict__[key]

        # Remove all items from the dictionary.
        self.clear()


    def add(self, pipe_name, pipe_type):
        """Method for adding a new data pipe container to the dictionary.

        This method should be used rather than importing the PipeContainer class and using the
        statement 'D[pipe] = PipeContainer()', where D is the relax data storage object and pipe is
        the name of the data pipe.

        @param pipe:    The name of the new data pipe.
        @type pipe:     str
        """

        # Test if the pipe already exists.
        if pipe_name in self.keys():
            raise RelaxPipeError, pipe_name

        # Create a new container.
        self[pipe_name] = PipeContainer()

        # Add the data pipe type string to the container.
        self[pipe_name].pipe_type = pipe_type

        # Change the current data pipe.
        self.current_pipe = pipe_name
