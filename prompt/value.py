###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# Relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# Relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################


from re import match

from select_res import Select_res


class Skin:
    def __init__(self, relax):
        """The class accessible to the interpreter.

        The purpose of this class is to hide the variables and functions found within the namespace
        of the macro class, found below, except for those required for interactive use.  This is an
        abstraction layer designed to avoid user confusion as none of the macro class data
        structures are accessible.  For more flexibility use the macro class directly.
        """

        # Load the macro class into the namespace of this __init__ function.
        x = Macro_class(relax)

        # Place references to the interactive functions within the namespace of this skin class.
        self.load = x.load
        self.set = x.set


class Macro_class(Select_res):
    def __init__(self, relax):
        """Class containing macros for the setting up of data structures."""

        self.relax = relax


    def load(self, type=None, file_name=None, num_col=0, name_col=1, data_col=2, error_col=3, sep=None):
        """Macro for loading data structure values from file.

        Incomplete and broken code (and should probably be placed under the 'load' macro class.
        """

        # Arguments
        if not type:
            print "The data type string has not been supplied."
            return
        else:
            self.type = type
        if not file_name:
            print "No file is specified."
            return
        else:
            self.file_name = file_name
        self.num_col = num_col
        self.name_col = name_col
        self.data_col = data_col
        self.error_col = error_col
        self.sep = sep

        # Test if sequence data is loaded.
        try:
            self.relax.data.seq
        except AttributeError:
            print "Sequence data has to be loaded first."
            return

        # Initialise the type specific data.
        if not self.init_data():
            return

        # Extract the data from the file.
        file_data = self.relax.file_ops.extract_data(self.file_name)

        # Do nothing if the file does not exist.
        if not file_data:
            print "No sequence data loaded."
            return

        # Strip data.
        file_data = self.relax.file_ops.strip(file_data)

        # Create the data.
        self.data = self.create_data(file_data)


    def set(self, run=None, data_type=None, val=None, err=None):
        """Macro for setting data structure values.

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

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = self.relax.interpreter.macro_prompt + "value.set("
            text = text + "run=" + `run`
            text = text + ", data_type=" + `data_type`
            text = text + ", val=" + `val`
            text = text + ", err=" + `err` + ")\n"
            print text

        # The run name.
        if type(run) != str:
            print "The run argument must be a string."
            return

        # Data type.
        elif data_type == None:
            print "The data type argument has not been supplied."
            return
        elif type(data_type) != str:
            print "The data type argument must be a string."
            return

        # Value.
        elif val == None:
            print "No value has been given."
            return
        elif type(val) != float:
            print "The value argument must be a floating point number."
            return

        # Error.
        elif err != None:
            if type(err) != float:
                print "The error argument must either be None or be a floating point number."
                return

        # Execute the functional code.
        self.relax.value.set(run=run, data_type=data_type, val=val, err=err)
