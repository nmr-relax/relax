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
        self.set = x.set


class Macro_class:
    def __init__(self, relax):
        """Class containing the macro for setting the pdb file."""

        self.relax = relax


    def set(self, path=None, file=None):
        """Macro for setting the pdb file."""

        if not path:
            print "The path has not been set."
        elif not file:
            print "The file has not been set."
        else:
            self.relax.data.pdb_path = path
            self.relax.data.pdb_file = file
            self.relax.data.pdb = path + file

