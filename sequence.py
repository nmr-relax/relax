class Sequence:
    def __init__(self, relax):
        """Class containing functions specific to amino-acid sequence."""

        self.relax = relax


    def macro_read(self, file_name=None, num_col=0, name_col=1, sep=None, header_lines=1):
        """Macro for loading sequence data.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        file_name:  The name of the file containing the sequence data.

        num_col:  The residue number column (the default is 0, ie the first column).

        name_col:  The residue name column (the default is 1).

        sep:  The column separator (the default is white space).

        header_lines:  The number of lines at the top of the file to skip (the default is 1 line).


        Examples
        ~~~~~~~~

        The following commands will load the sequence data out of a file called 'seq' where the
        residue numbers and names are in the first and second columns respectively.

        relax> load.sequence('seq')
        relax> load.sequence('seq', 0, 1)
        relax> load.sequence('seq', 0, 1, None)
        relax> load.sequence('seq', num_col=0, name_col=1)
        relax> load.sequence(file_name='seq', num_col=0, name_col=1, seq=None, header_lines=1)


        The following commands will load the sequence out of the file 'noe.out' which also contains
        the NOE values.

        relax> load.sequence('noe.out')
        relax> load.sequence('noe.out', 0, 1)


        The following commands will load the sequence out of the file 'noe.600.out' where the
        residue numbers are in the second column, the names are in the sixth column and the columns
        are separated by commas.

        relax> load.sequence('noe.600.out', 1, 5, ',')
        relax> load.sequence(file_name='noe.600.out', num_col=1, name_col=5, seq=',',
                             header_lines=1)
        """

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = self.relax.interpreter.macro_prompt + "load.sequence("
            text = text + "file_name=" + `file_name`
            text = text + ", num_col=" + `num_col`
            text = text + ", name_col=" + `name_col`
            text = text + ", sep=" + `sep`
            text = text + ", header_lines=" + `header_lines` + ")\n"
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

        # Header lines.
        elif type(header_lines) != int:
            print "The number of header lines argument 'header_lines' should be an integer."
            return

        # Execute the functional code.
        self.read(file_name=file_name, num_col=num_col, name_col=name_col, sep=sep, header_lines=header_lines)


    def read(self, file_name=None, num_col=0, name_col=1, sep=None, header_lines=None):
        """Function for loading sequence data."""

        # Test if the sequence data has already been loaded.
        if len(self.relax.data.res):
            print "The sequence data has already been loaded."
            print "To reload, reinitialise all data."
            return

        # Extract the data from the file.
        file_data = self.relax.file_ops.extract_data(file_name)

        # Do nothing if the file does not exist.
        if not file_data:
            print "No sequence data loaded."
            return

        # Remove the header.
        file_data = file_data[header_lines:]

        # Strip data.
        file_data = self.relax.file_ops.strip(file_data)

        # Fill the array self.relax.data.res with data containers and place sequence data into the array.
        for i in range(len(file_data)):
            # Append a data container.
            self.relax.data.res.append(Residue())

            # Get the data.
            try:
                num = int(file_data[i][num_col])
                name = file_data[i][name_col]
                label = file_data[i][num_col] + '_' + file_data[i][name_col]
            except ValueError:
                print "Sequence data is invalid."
                return

            # Insert the data.
            self.relax.data.res[i].num = num
            self.relax.data.res[i].name = name
            self.relax.data.res[i].label = label
            self.relax.data.res[i].select = 1


class Residue:
    def __init__(self):
        """Empty data container."""
