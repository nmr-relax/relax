from re import match

from generic_functions import generic_functions
from select_res import select_res


class skin:
    def __init__(self, relax):
        """The class accessible to the interpreter.

        The purpose of this class is to hide the variables and functions found within the namespace
        of the macro class, found below, except for those required for interactive use.  This is an
        abstraction layer designed to avoid user confusion as none of the macro class data
        structures are accessible.  For more flexibility use the macro class directly.
        """

        # Load the macro class into the namespace of this __init__ function.
        x = macro_class(relax)

        # Place references to the interactive functions within the namespace of this skin class.
        self.load = x.load
        self.set = x.set


class macro_class(generic_functions, select_res):
    def __init__(self, relax):
        """Base class containing functions for the setting up of data structures."""

        self.relax = relax


    def load(self, type=None, file_name=None, num_col=0, name_col=1, data_col=2, error_col=3, sep=None):
        """Macro for loading data structure values from file."""

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


    def init_data(self, data):
        """Function for initialisation of the data type."""

        # Bond length.
        if match('[Bb]ond[ -_][Ll]ength', self.type):
            try:
                self.relax.data.bond_length
            except AttributeError:
                self.relax.data.bond_length = self.create_data(data)
            else:
                print "The bond lengths have already been specified."
                print "To reset the values, delete the original data (self.relax.data.bond_length)."

        # CSA.
        elif match('[Cc][Ss][Aa]', self.type):
            try:
                self.relax.data.csa
            except AttributeError:
                self.relax.data.csa = self.create_data(data)
            else:
                print "The CSA values have already been specified."
                print "To reset the values, delete the original data (self.self.x.data.csa)."

        # Bad type.
        else:
            print "The type '" + self.type + "' is not supported."


    def set(self, type=None, val=None, err=0.0, sel=[]):
        """Macro for setting data structure values."""

        # Arguments.
        if not type:
            print "The data type string has not been supplied."
            return
        else:
            self.type = type
        if not val:
            print "No value has been given."
            return
        else:
            self.val = val
        self.err = err
        self.sel = sel

        # Test if sequence data is loaded.
        try:
            self.relax.data.seq
        except AttributeError:
            print "Sequence data has to be loaded first."
            return

        # Set fixed values to specific residues.
        if len(self.sel) > 0:
            self.indecies = self.select_residues()
            if not self.indecies:
                return
            for index in self.indecies:
                self.data[index][0] = self.val
                self.data[index][1] = self.err


        # Set one value to all residues.
        else:
            # Create a temporary data structure.
            temp = []
            for i in range(len(self.relax.data.seq)):
                temp.append([self.relax.data.seq[i][0], self.relax.data.seq[i][1], self.val, self.err])

            # Initialise the type specific data.
            self.init_data(temp)
