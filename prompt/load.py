from generic_functions import Generic_functions


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
        self.relax_data = x.relax_data
        self.sequence = x.sequence


class Macro_class(Generic_functions):
    def __init__(self, relax):
        """Class containing macros for loading data."""

        self.relax = relax


    def relax_data(self, ri_label=None, frq_label=None, frq=None, file_name=None, num_col=0, name_col=1, data_col=2, error_col=3, sep=None):
        """Macro for loading R1, R2, or NOE relaxation data.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        ri_label:  The relaxation data type, ie 'R1', 'R2', or 'NOE'.

        frq_label:  The field strength in MHz, ie '600'.  This string can be anything as long as 
        data collected at the same field strength have the same label.

        frq:  The spectrometer frequency in Hz.

        file_name:  The name of the file containing the relaxation data.

        num_col:  The residue number column (the default is 0, ie the first column).

        name_col:  The residue name column (the default is 1).

        data_col:  The relaxation data column (the default is 2).

        error_col:  The experimental error column (the default is 3).

        sep:  The column separator (the default is white space).


        Examples
        ~~~~~~~~

        The following commands will load the NOE relaxation data collected at 600 MHz out of a file
        called 'noe.600.out' where the residue numbers, residue names, data, errors are in the
        first, second, third, and forth columns respectively.

        relax> load.relax_data('NOE', '600', 599.7 * 1e6, 'noe.600.out')
        relax> load.relax_data(ri_label='NOE', frq_label='600', frq=600.0 * 1e6,
                               file_name='noe.600.out')


        The following commands will load the R2 data out of the file 'r2.out' where the residue
        numbers, residue names, data, errors are in the second, third, fifth, and sixth columns
        respectively.  The columns are separated by commas.

        relax> load.relax_data('R2', '800 MHz', 8.0 * 1e8, 'r2.out', 1, 2, 4, 5, ',')
        relax> load.relax_data(ri_label='R2', frq_label='800 MHz', frq=8.0*1e8, file_name='r2.out',
                               num_col=1, name_col=2, data_col=4, error_col=5, sep=',')


        The following commands will load the R1 data out of the file 'r1.out' where the columns are
        separated by the symbol '%'

        relax> load.relax_data('R1', '300', 300.1 * 1e6, 'r1.out', sep='%')
        """

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = self.relax.interpreter.macro_prompt + "load.relax_data("
            text = text + "ri_label=" + `ri_label`
            text = text + ", frq_label=" + `frq_label`
            text = text + ", frq=" + `frq`
            text = text + ", file_name=" + `file_name`
            text = text + ", num_col=" + `num_col`
            text = text + ", name_col=" + `name_col`
            text = text + ", data_col=" + `data_col`
            text = text + ", error_col=" + `error_col`
            text = text + ", sep=" + `sep` + ")\n"
            print text

        # Relaxation data type.
        if not ri_label or type(ri_label) != str:
            print "The relaxation label 'ri_label' has not been supplied correctly."
            return

        # Frequency label.
        elif type(frq_label) != str:
            print "The frequency label 'frq_label' has not been supplied correctly."
            return

        # Frequency.
        elif type(frq) != float:
            print "The frequency argument 'frq' should be a floating point number."
            return

        # The file name.
        elif not file_name:
            print "No file has been specified."
            return
        elif type(file_name) != str:
            print "The file name should be a string."
            return

        # The columns.
        elif type(num_col) != int or type(name_col) != int or type(data_col) != int or type(error_col) != int:
            print "The column arguments 'num_col', 'name_col', 'data_col', and 'error_col' should be integers."
            return

        # Column separator.
        elif sep != None and type(sep) != str:
            print "The column separator argument 'sep' should be either a string or None."
            return

        # Execute the functional code.
        self.relax.load.relax_data(ri_label=ri_label, frq_label=frq_label, frq=frq, file_name=file_name, num_col=num_col, name_col=name_col, data_col=data_col, error_col=error_col, sep=sep)


    def sequence(self, file_name=None, num_col=0, name_col=1, sep=None):
        """Macro for loading sequence data.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        file_name:  The name of the file containing the sequence data.

        num_col:  The residue number column (the default is 0, ie the first column).

        name_col:  The residue name column (the default is 1).

        sep:  The column separator (the default is white space).


        Examples
        ~~~~~~~~

        The following commands will load the sequence data out of a file called 'seq' where the
        residue numbers and names are in the first and second columns respectively.

        relax> load.sequence('seq')
        relax> load.sequence('seq', 0, 1)
        relax> load.sequence('seq', 0, 1, None)
        relax> load.sequence('seq', num_col=0, name_col=1)
        relax> load.sequence(file_name='seq', num_col=0, name_col=1, seq=None)


        The following commands will load the sequence out of the file 'noe.out' which also contains
        the NOE values.

        relax> load.sequence('noe.out')
        relax> load.sequence('noe.out', 0, 1)


        The following commands will load the sequence out of the file 'noe.600.out' where the
        residue numbers are in the second column, the names are in the sixth column and the columns
        are separated by commas.

        relax> load.sequence('noe.600.out', 1, 5, ',')
        relax> load.sequence(file_name='noe.600.out', num_col=1, name_col=5, seq=',')
        """

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = self.relax.interpreter.macro_prompt + "load.sequence("
            text = text + "file_name=" + `file_name`
            text = text + ", num_col=" + `num_col`
            text = text + ", name_col=" + `name_col`
            text = text + ", sep=" + `sep` + ")\n"
            print text

        # The file name.
        if not file_name:
            print "No file is specified."
            return
        elif type(file_name) != str:
            print "The file name should be a string."
            return

        # The columns.
        elif type(num_col) != int or type(name_col) != int:
            print "The residue number and name column arguments 'num_col' and 'name_col' should be integers."
            return

        # Column separator.
        elif sep != None and type(sep) != str:
            print "The column separator argument 'sep' should be either a string or None."
            return

        # Execute the functional code.
        self.relax.load.sequence(file_name=file_name, num_col=num_col, name_col=name_col, sep=sep)
