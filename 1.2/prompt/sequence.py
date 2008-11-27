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


class Sequence:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for manipulating sequence data."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def add(self, run=None, res_num=None, res_name=None, select=1):
        """Function for adding a residue onto the sequence.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        res_num:  The residue number.

        res_name:  The name of the residue.

        select:  A flag specifying if the residue should be selected.


        Description
        ~~~~~~~~~~~

        Using this function a new sequence can be generated without having to load the sequence from
        a file.  However if the sequence already exists, the new residue will be added to the end.
        The same residue number cannot be used more than once.


        Examples
        ~~~~~~~~

        The following sequence of commands will generate the sequence 1 ALA, 2 GLY, 3 LYS and assign
        it to the run 'm3':

        relax> run = 'm3'
        relax> sequence.add(run, 1, 'ALA')
        relax> sequence.add(run, 2, 'GLY')
        relax> sequence.add(run, 3, 'LYS')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "sequence.add("
            text = text + "run=" + `run`
            text = text + ", res_num=" + `res_num`
            text = text + ", res_name=" + `res_name`
            text = text + ", select=" + `select` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Residue number.
        if type(res_num) != int:
            raise RelaxIntError, ('residue number', res_num)

        # Residue name.
        if type(res_name) != str:
            raise RelaxStrError, ('residue name', res_name)

        # Select flag.
        if type(select) != int or (select != 0 and select != 1):
            raise RelaxBinError, ('select', select)

        # Execute the functional code.
        self.__relax__.generic.sequence.add(run=run, res_num=res_num, res_name=res_name, select=select)


    def copy(self, run1=None, run2=None):
        """Function for copying the sequence from run1 to run2.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run1:  The name of the run to copy the sequence from.

        run2:  The name of the run to copy the sequence to.


        Description
        ~~~~~~~~~~~

        This function will copy the sequence from 'run1' to 'run2'.  'run1' must contain sequence
        information, while 'run2' must have no sequence loaded.


        Examples
        ~~~~~~~~

        To copy the sequence from the run 'm1' to the run 'm2', type:

        relax> sequence.copy('m1', 'm2')
        relax> sequence.copy(run1='m1', run2='m2')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "sequence.copy("
            text = text + "run1=" + `run1`
            text = text + ", run2=" + `run2` + ")"
            print text

        # The run1 argument.
        if type(run1) != str:
            raise RelaxStrError, ('run1', run1)

        # The run2 argument.
        if type(run2) != str:
            raise RelaxStrError, ('run2', run2)

        # Execute the functional code.
        self.__relax__.generic.sequence.copy(run1=run1, run2=run2)


    def delete(self, run=None):
        """Function for deleting the sequence.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.


        Description
        ~~~~~~~~~~~

        This function has the same effect as using the 'delete' function to delete all residue
        specific data.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "sequence.delete("
            text = text + "run=" + `run` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Execute the functional code.
        self.__relax__.generic.sequence.delete(run=run)


    def display(self, run=None):
        """Function for displaying the sequence.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "sequence.display("
            text = text + "run=" + `run` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Execute the functional code.
        self.__relax__.generic.sequence.display(run=run)


    def read(self, run=None, file=None, dir=None, num_col=0, name_col=1, sep=None):
        """Function for reading sequence data.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        file:  The name of the file containing the sequence data.

        dir:  The directory where the file is located.

        num_col:  The residue number column (the default is 0, ie the first column).

        name_col:  The residue name column (the default is 1).

        sep:  The column separator (the default is white space).


        Description
        ~~~~~~~~~~~

        If no directory is given, the file will be assumed to be in the current working directory.


        Examples
        ~~~~~~~~

        The following commands will read the sequence data out of a file called 'seq' where the
        residue numbers and names are in the first and second columns respectively and assign it to
        the run 'm1'.

        relax> sequence.read('m1', 'seq')
        relax> sequence.read('m1', 'seq', num_col=0, name_col=1)
        relax> sequence.read(run='m1', file='seq', num_col=0, name_col=1, sep=None)


        The following commands will read the sequence out of the file 'noe.out' which also contains
        the NOE values.

        relax> sequence.read('m1', 'noe.out')
        relax> sequence.read('m1', 'noe.out', num_col=0, name_col=1)
        relax> sequence.read(run='m1', file='noe.out', num_col=0, name_col=1)


        The following commands will read the sequence out of the file 'noe.600.out' where the
        residue numbers are in the second column, the names are in the sixth column and the columns
        are separated by commas and assign it to the run 'm5'.

        relax> sequence.read('m5', 'noe.600.out', num_col=1, name_col=5, sep=',')
        relax> sequence.read(run='m5', file='noe.600.out', num_col=1, name_col=5, sep=',')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "sequence.read("
            text = text + "run=" + `run`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", num_col=" + `num_col`
            text = text + ", name_col=" + `name_col`
            text = text + ", sep=" + `sep` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # The file name.
        if type(file) != str:
            raise RelaxStrError, ('file name', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # Number column.
        if type(num_col) != int:
            raise RelaxIntError, ('residue number column', num_col)

        # Name column.
        if type(name_col) != int:
            raise RelaxIntError, ('residue name column', name_col)

        # Column separator.
        if sep != None and type(sep) != str:
            raise RelaxNoneStrError, ('column separator', sep)

        # Execute the functional code.
        self.__relax__.generic.sequence.read(run=run, file=file, dir=dir, num_col=num_col, name_col=name_col, sep=sep)


    def sort(self, run=None):
        """Function for numerically sorting the sequence by residue number.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "sequence.sort("
            text = text + "run=" + `run` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Execute the functional code.
        self.__relax__.generic.sequence.sort(run=run)


    def write(self, run=None, file=None, dir=None, force=0):
        """Function for writing the sequence to a file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        file:  The name of the file.

        dir:  The directory name.

        force:  A flag which, if set to 1, will cause the file to be overwritten.


        Description
        ~~~~~~~~~~~

        If no directory name is given, the file will be placed in the current working directory.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "sequence.write("
            text = text + "run=" + `run`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", force=" + `force` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # File.
        if type(file) != str:
            raise RelaxStrError, ('file name', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # The force flag.
        if type(force) != int or (force != 0 and force != 1):
            raise RelaxBinError, ('force flag', force)

        # Execute the functional code.
        self.__relax__.generic.sequence.write(run=run, file=file, dir=dir, force=force)
