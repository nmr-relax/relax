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

import sys


class Sequence:
    def __init__(self, relax):
        """Class containing functions specific to amino-acid sequence."""

        self.relax = relax


    def macro_read(self, file_name=None, num_col=0, name_col=1, sep=None, header_lines=1):
        """Macro for reading sequence data.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        file_name:  The name of the file containing the sequence data.

        num_col:  The residue number column (the default is 0, ie the first column).

        name_col:  The residue name column (the default is 1).

        sep:  The column separator (the default is white space).

        header_lines:  The number of lines at the top of the file to skip (the default is 1 line).


        Examples
        ~~~~~~~~

        The following commands will read the sequence data out of a file called 'seq' where the
        residue numbers and names are in the first and second columns respectively.

        relax> read.sequence('seq')
        relax> read.sequence('seq', 0, 1)
        relax> read.sequence('seq', 0, 1, None)
        relax> read.sequence('seq', num_col=0, name_col=1)
        relax> read.sequence(file_name='seq', num_col=0, name_col=1, seq=None, header_lines=1)


        The following commands will read the sequence out of the file 'noe.out' which also contains
        the NOE values.

        relax> read.sequence('noe.out')
        relax> read.sequence('noe.out', 0, 1)


        The following commands will read the sequence out of the file 'noe.600.out' where the
        residue numbers are in the second column, the names are in the sixth column and the columns
        are separated by commas.

        relax> read.sequence('noe.600.out', 1, 5, ',')
        relax> read.sequence(file_name='noe.600.out', num_col=1, name_col=5, seq=',',
                             header_lines=1)
        """

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = sys.macro_prompt + "read.sequence("
            text = text + "file_name=" + `file_name`
            text = text + ", num_col=" + `num_col`
            text = text + ", name_col=" + `name_col`
            text = text + ", sep=" + `sep`
            text = text + ", header_lines=" + `header_lines` + ")"
            print text

        # The file name.
        if not file_name:
            raise RelaxNoneError, 'file name'
        elif type(file_name) != str:
            raise RelaxStrError, ('file name', file_name)

        # Number column.
        elif type(num_col) != int:
            raise RelaxIntError, ('residue number column', num_col)

        # Name column.
        elif type(name_col) != int:
            raise RelaxIntError, ('residue name column', name_col)

        # Column separator.
        elif sep != None and type(sep) != str:
            raise RelaxNoneStrError, ('column separator', sep)

        # Header lines.
        elif type(header_lines) != int:
            raise RelaxIntError, ('number of header lines', header_lines)

        # Execute the functional code.
        self.read(file_name=file_name, num_col=num_col, name_col=name_col, sep=sep, header_lines=header_lines)


    def read(self, file_name=None, num_col=0, name_col=1, sep=None, header_lines=None):
        """Function for reading sequence data."""

        # Test if the sequence data has already been read.
        if len(self.relax.data.res):
            raise RelaxError, "The sequence data has already been loaded."

        # Extract the data from the file.
        file_data = self.relax.file_ops.extract_data(file_name)

        # Remove the header.
        file_data = file_data[header_lines:]

        # Strip data.
        file_data = self.relax.file_ops.strip(file_data)

        # Do nothing if the file does not exist.
        if not file_data:
            raise RelaxFileEmptyError

        # Test if the sequence data is valid.
        for i in range(len(file_data)):
            try:
                int(file_data[i][num_col])
            except ValueError:
                raise RelaxError, "Sequence data is invalid."

        # Fill the array self.relax.data.res with data containers and place sequence data into the array.
        for i in range(len(file_data)):
            # Append a data container.
            self.relax.data.res.append(Residue())

            # Insert the data.
            self.relax.data.res[i].num = int(file_data[i][num_col])
            self.relax.data.res[i].name = file_data[i][name_col]
            self.relax.data.res[i].label = file_data[i][num_col] + '_' + file_data[i][name_col]
            self.relax.data.res[i].select = 1


class Residue:
    def __init__(self):
        """Empty data container."""
