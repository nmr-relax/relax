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

import help


class Read:
    def __init__(self, relax):
        """Class containing functions for loading data."""

        # Place relax in the class namespace.
        self.relax = relax

        # Help.
        self.__relax_help__ = help.relax_class_help
        self.__repr__ = help.repr


    def read_results(self, run=None, data_type=None, file='results', dir=None):
        """Function for reading results from a file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        data_type:  The type of data.

        file:  The name of the file to read results from.

        dir:  The directory where the file is located.


        Description
        ~~~~~~~~~~~

        The name of the run can be any string.

        The data_type argument specifies what type of data is to be read and must be one of the
        following:
            'mf' - model-free data.

        If no directory name is given, the results file will be seached for in a directory named
        after the run name.
        """

        # Function intro text.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "read.read_results("
            text = text + "run=" + `run`
            text = text + ", data_type=" + `data_type`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # The data_type argument.
        if type(data_type) != str:
            raise RelaxStrError, ('data_type', data_type)

        # File.
        if type(file) != str:
            raise RelaxStrError, ('file name', file)

        # Directory.
        if dir != None:
            if type(dir) != str:
                raise RelaxNoneStrError, ('directory name', dir)

        # Execute the functional code.
        self.relax.rw.read_results(run=run, data_type=data_type, file=file, dir=dir)


    def relax_data(self, run=None, ri_label=None, frq_label=None, frq=None, file_name=None, num_col=0, name_col=1, data_col=2, error_col=3, sep=None, header_lines=1):
        """Function for reading R1, R2, or NOE relaxation data.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

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

        header_lines:  The number of lines at the top of the file to skip (the default is 1 line).


        Examples
        ~~~~~~~~

        The following commands will read the NOE relaxation data collected at 600 MHz out of a file
        called 'noe.600.out' where the residue numbers, residue names, data, errors are in the
        first, second, third, and forth columns respectively.

        relax> read.relax_data('m1', 'NOE', '600', 599.7 * 1e6, 'noe.600.out')
        relax> read.relax_data('m1', ri_label='NOE', frq_label='600', frq=600.0 * 1e6,
                               file_name='noe.600.out')


        The following commands will read the R2 data out of the file 'r2.out' where the residue
        numbers, residue names, data, errors are in the second, third, fifth, and sixth columns
        respectively.  The columns are separated by commas.

        relax> read.relax_data('m1', 'R2', '800 MHz', 8.0 * 1e8, 'r2.out', 1, 2, 4, 5, ',')
        relax> read.relax_data('m1', ri_label='R2', frq_label='800 MHz', frq=8.0*1e8,
                               file_name='r2.out', num_col=1, name_col=2, data_col=4, error_col=5,
                               sep=',', header_lines=1)


        The following commands will read the R1 data out of the file 'r1.out' where the columns are
        separated by the symbol '%'

        relax> read.relax_data('m1', 'R1', '300', 300.1 * 1e6, 'r1.out', sep='%')
        """

        # Function intro text.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "read.relax_data("
            text = text + "run=" + `run`
            text = text + ", ri_label=" + `ri_label`
            text = text + ", frq_label=" + `frq_label`
            text = text + ", frq=" + `frq`
            text = text + ", file_name=" + `file_name`
            text = text + ", num_col=" + `num_col`
            text = text + ", name_col=" + `name_col`
            text = text + ", data_col=" + `data_col`
            text = text + ", error_col=" + `error_col`
            text = text + ", sep=" + `sep`
            text = text + ", header_lines=" + `header_lines` + ")"
            print text

        # The run name.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Relaxation data type.
        if not ri_label or type(ri_label) != str:
            raise RelaxStrError, ('relaxation label', ri_label)

        # Frequency label.
        elif type(frq_label) != str:
            raise RelaxStrError, ('frequency label', frq_label)

        # Frequency.
        elif type(frq) != float:
            raise RelaxFloatError, ('frequency', frq)

        # The file name.
        elif not file_name:
            raise RelaxNoneError, 'file name'
        elif type(file_name) != str:
            raise RelaxStrError, ('file name', file_name)

        # The number column.
        elif type(num_col) != int:
            raise RelaxIntError, ('residue number column', num_col)

        # The name column.
        elif type(name_col) != int:
            raise RelaxIntError, ('residue name column', name_col)

        # The data column.
        elif type(data_col) != int:
            raise RelaxIntError, ('data column', data_col)

        # The error column.
        elif type(error_col) != int:
            raise RelaxIntError, ('error column', error_col)

        # Column separator.
        elif sep != None and type(sep) != str:
            raise RelaxNoneStrError, ('column separator', sep)

        # Header lines.
        elif type(header_lines) != int:
            raise RelaxIntError, ('number of header lines', header_lines)

        # Execute the functional code.
        self.relax.specific.relax_data.read(run=run, ri_label=ri_label, frq_label=frq_label, frq=frq, file_name=file_name, num_col=num_col, name_col=name_col, data_col=data_col, error_col=error_col, sep=sep, header_lines=header_lines)


    def sequence(self, file_name=None, num_col=0, name_col=1, sep=None, header_lines=1):
        """Function for reading sequence data.

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

        # Function intro text.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "read.sequence("
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
        self.relax.generic.sequence.read(file_name=file_name, num_col=num_col, name_col=name_col, sep=sep, header_lines=header_lines)
