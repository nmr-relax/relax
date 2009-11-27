###############################################################################
#                                                                             #
# Copyright (C) 2003-2005 Edward d'Auvergne                                   #
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


class Csa_data:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for manipulating CST and CSEA csa data."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def copy(self, run1=None, run2=None, csa_label=None):
        """Function for copying csa data from run1 to run2.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run1:  The name of the run to copy the sequence from.

        run2:  The name of the run to copy the sequence to.

        csa_label:  The csa data type, ie 'CST' or 'CSEA'.



        Description
        ~~~~~~~~~~~

        This function will copy csa data from 'run1' to 'run2'.  If csa_label is not given
	then all csa data will be copied, otherwise only a specific data set will be copied.


        Examples
        ~~~~~~~~

        To copy all csa data from run 'm1' to run 'm9', type one of:

        relax> csa_data.copy('m1', 'm9')
        relax> csa_data.copy(run1='m1', run2='m9')
        relax> csa_data.copy('m1', 'm9', None)
        relax> csa_data.copy(run1='m1', run2='m9', csa_label=None)

        To copy only the CST csa data from 'm3' to 'm6', type one of:

        relax> csa_data.copy('m3', 'm6', 'CST')
        relax> csa_data.copy(run1='m3', run2='m6', csa_label='CST')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "csa_data.copy("
            text = text + "run1=" + `run1`
            text = text + ", run2=" + `run2`
            text = text + ", csa_label=" + `csa_label` + ")"
            print text

        # The run1 argument.
        if type(run1) != str:
            raise RelaxStrError, ('run1', run1)

        # The run2 argument.
        if type(run2) != str:
            raise RelaxStrError, ('run2', run2)

        # Relaxation data type.
        if csa_label != None and type(csa_label) != str:
            raise RelaxNoneStrError, ('csa label', csa_label)

        # Execute the functional code.
        self.__relax__.specific.csa_data.copy(run1=run1, run2=run2, csa_label=csa_label)


    def delete(self, run=None, csa_label=None):
        """Function for deleting the csa data corresponding to csa_label.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        csa_label:  The csa data type, ie 'CST' or 'CSEA'.


        Examples
        ~~~~~~~~

        To delete the csa data corresponding to csa_label='CST', and the run 'm4', type:

        relax> csa_data.delete('m4', 'CST')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "csa_data.delete("
            text = text + "run=" + `run`
            text = text + ", csa_label=" + `csa_label` + ")"
            print text

        # The run name.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Relaxation data type.
        if type(csa_label) != str:
            raise RelaxStrError, ('csa label', csa_label)

        # Execute the functional code.
        self.__relax__.specific.csa_data.delete(run=run, csa_label=csa_label)


    def display(self, run=None, csa_label=None):
        """Function for displaying the csa data corresponding to csa_label.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        csa_label:  The csa data type, ie 'CST' or 'CSEA'.


        Examples
        ~~~~~~~~

        To display the CST csa data from the run 'm4', type

        relax> csa_data.display('m4', 'CST')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "csa_data.display("
            text = text + "run=" + `run`
            text = text + ", csa_label=" + `csa_label` + ")"
            print text

        # The run name.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Relaxation data type.
        if type(csa_label) != str:
            raise RelaxStrError, ('csa label', csa_label)

        # Execute the functional code.
        self.__relax__.specific.csa_data.display(run=run, csa_label=csa_label)


    def read(self, run=None, csa_label=None, file=None, dir=None, num_col=0, name_col=1, data_ax_col=2, data_by_col=3, data_cz_col=4, sep=None):
        """Function for reading CST or CSEA csa data from a file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        csa_label:  The relaxation data type, ie 'CST' or 'CSEA'.

        file:  The name of the file containing the csa data.

        dir:  The directory where the file is located.

        num_col:  The residue number column (the default is 0, ie the first column).

        name_col:  The residue name column (the default is 1).

        data_ax_col:  The csa data column 1 (the default is 2).

        data_by_col:  The csa data column 2 (the default is 3).
	
        data_cz_col:  The csa data column 3 (the default is 4).

        sep:  The column separator (the default is white space).


        Description
        ~~~~~~~~~~~

        The frequency label argument can be anything as long as data collected at the same field
        strength have the same label.


        Examples
        ~~~~~~~~

        The following commands will read the CSA1 csa data collected out of a file
        called 'csa1.out' where the residue numbers, residue names, csa data are in the
        first, second, third, forth and fifth columns respectively.

        relax> csa_data.read('m1', 'CST', 'csa1.out')
        relax> csa_data.read('m1', csa_label='CST', file='csa1.out')


        The following commands will read the CSEA data out of the file 'csa2.out' where the residue
        numbers, residue names, data, errors are in the second, third, fifth, sixth and seventh columns
        respectively.  The columns are separated by commas.

        relax> csa_data.read('m1', 'CSEA', 'csa2.out', 1, 2, 4, 5, 6, ',')
        relax> csa_data.read('m1', csa_label='CSA2', file='csa2.out', num_col=1, name_col=2, data_col1=4,
			       data_col2=5, data_col3=6, sep=',')


        The following commands will read the CSEA data out of the file 'csa1.out' where the columns are
        separated by the symbol '%'

        relax> csa_data.read('m1', 'R1', 'r1.out', sep='%')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "csa_data.read("
            text = text + "run=" + `run`
            text = text + ", csa_label=" + `csa_label`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", num_col=" + `num_col`
            text = text + ", name_col=" + `name_col`
            text = text + ", data_ax_col=" + `data_ax_col`
            text = text + ", data_by_col=" + `data_by_col`
            text = text + ", data_cz_col=" + `data_cz_col`
            text = text + ", sep=" + `sep` + ")"
            print text

        # The run name.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Relaxation data type.
        if type(csa_label) != str:
            raise RelaxStrError, ('csa label', csa_label)

        # The file name.
        if type(file) != str:
            raise RelaxStrError, ('file', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # The number column.
        if type(num_col) != int:
            raise RelaxIntError, ('residue number column', num_col)

        # The name column.
        if type(name_col) != int:
            raise RelaxIntError, ('residue name column', name_col)

        # The data column 1.
        if type(data_ax_col) != int:
            raise RelaxIntError, ('data ax column', data_ax_col)

        # The data column 2.
        if type(data_by_col) != int:
            raise RelaxIntError, ('data by column', data_by_col)

        # The data column 3.
        if type(data_cz_col) != int:
            raise RelaxIntError, ('data cz column', data_cz_col)

        # Column separator.
        if sep != None and type(sep) != str:
            raise RelaxNoneStrError, ('column separator', sep)

        # Execute the functional code.
        self.__relax__.specific.csa_data.read(run=run, csa_label=csa_label, file=file, dir=dir, num_col=num_col, name_col=name_col, data_ax_col=data_ax_col, data_by_col=data_by_col, data_cz_col=data_cz_col, sep=sep)


    def write(self, run=None, csa_label=None, file=None, dir=None, force=0):
        """Function for writing CST or CSEA csa data to a file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        csa_label:  The csa data type, ie 'CST' or 'CSEA'.

        file:  The name of the file.

        dir:  The directory name.

        force:  A flag which, if set to 1, will cause the file to be overwritten.


        Description
        ~~~~~~~~~~~

        If no directory name is given, the file will be placed in the current working directory.
        The 'csa_label' argument is required for selecting which csa data to write to file.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "csa_data.write("
            text = text + "run=" + `run`
            text = text + ", csa_label=" + `csa_label`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", force=" + `force` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Relaxation data type.
        if type(csa_label) != str:
            raise RelaxStrError, ('csa label', csa_label)

        # File.
        if file != None and type(file) != str:
            raise RelaxNoneStrError, ('file name', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # The force flag.
        if type(force) != int or (force != 0 and force != 1):
            raise RelaxBinError, ('force flag', force)

        # Execute the functional code.
        self.__relax__.specific.csa_data.write(run=run, csa_label=csa_label, file=file, dir=dir, force=force)
