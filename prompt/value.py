###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004 Edward d'Auvergne                                  #
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

import sys

import message


class Shell:
    def __init__(self, relax):
        """The class accessible to the interpreter.

        The purpose of this class is to hide the variables and functions found within the namespace
        of the main class, found below, except for those required for interactive use.  This is an
        abstraction layer designed to avoid user confusion as none of the main class data structures
        are accessible.  For more flexibility use the main class directly.
        """

        # Load the main class into the namespace of this __init__ function.
        x = Main(relax)

        # Place references to the interactive functions within the namespace of this class.
        self.load = x.load
        self.set = x.set

        # __repr__.
        self.__repr__ = message.main_class


class Main:
    def __init__(self, relax):
        """Class containing functions for the setting up of data structures."""

        self.relax = relax


    def load(self, type=None, file_name=None, num_col=0, name_col=1, data_col=2, error_col=3, sep=None):
        """Function for loading data structure values from file.

        Incomplete and broken code (and should probably be placed under the 'load' function class).
        """

        raise NameError, "Broken code."

        # Arguments
        if not type:
            raise RelaxNoneError, 'data type'
        else:
            self.type = type
        if not file_name:
            raise RelaxNoneError, 'file name'
        else:
            self.file_name = file_name
        self.num_col = num_col
        self.name_col = name_col
        self.data_col = data_col
        self.error_col = error_col
        self.sep = sep

        # Test if sequence data is loaded.
        try:
            self.relax.data.res
        except AttributeError:
            raise RelaxSequenceError

        # Initialise the type specific data.
        if not self.init_data():
            return

        # Extract the data from the file.
        file_data = self.relax.file_ops.extract_data(self.file_name)

        # Do nothing if the file does not exist.
        if not file_data:
            raise RelaxError, "No sequence data loaded."

        # Strip data.
        file_data = self.relax.file_ops.strip(file_data)

        # Create the data.
        self.data = self.create_data(file_data)


    def set(self, run=None, data_type=None, val=None, err=None):
        """Function for setting data structure values.

        Keyword arguments
        ~~~~~~~~~~~~~~~~~

        run:  The run to assign the values to.

        data_type:  The data type.  This argument should be a string.

        val:  The value.

        err:  The error.


        Data type
        ~~~~~~~~~

        The following types are currently supported:
        _________________________________________________________________
        |                         |                                     |
        | Type                    | Pattern                             |
        |-------------------------|-------------------------------------|
        |                         |                                     |
        | Bond length             | '[Bb]ond[ -_][Ll]ength'             |
        |                         |                                     |
        | CSA                     | '[Cc][Ss][Aa]'                      |
        |-------------------------|-------------------------------------|
        """

        # Function intro text.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "value.set("
            text = text + "run=" + `run`
            text = text + ", data_type=" + `data_type`
            text = text + ", val=" + `val`
            text = text + ", err=" + `err` + ")"
            print text

        # The run name.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Data type.
        elif data_type == None:
            raise RelaxNoneError, 'data type'
        elif type(data_type) != str:
            raise RelaxStrError, ('data type', data_type)

        # Value.
        elif val == None:
            raise RelaxNoneError, 'value'
        elif type(val) != float:
            raise RelaxFloatError, ('value', val)

        # Error.
        elif err != None:
            if type(err) != float:
                raise RelaxNoneFloatError, ('error', err)

        # Execute the functional code.
        self.relax.generic.value.set(run=run, data_type=data_type, val=val, err=err)
