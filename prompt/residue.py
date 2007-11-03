###############################################################################
#                                                                             #
# Copyright (C) 2007 Edward d'Auvergne                                        #
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

# Python module imports.
import sys
from string import replace

# relax module imports.
import help
from generic_fns import residue
from generic_fns.selection import id_string_doc
from relax_errors import RelaxBinError, RelaxIntError, RelaxNoneStrError, RelaxStrError


class Residue:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for manipulating the residue data."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


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


    def create(self, res_num=None, res_name=None):
        """Function for creating a new residue.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        res_num:  The residue number.

        res_name:  The name of the residue.


        Description
        ~~~~~~~~~~~

        Using this function a new sequence can be generated without using the sequence user
        functions.  However if the sequence already exists, the new residue will be added to the end
        of the residue list (the residue numbers of this list need not be sequential).  The same
        residue number cannot be used more than once.  A corresponding single spin system will be
        created for this residue.  The spin system number and name or additional spin systems can be
        added later if desired.


        Examples
        ~~~~~~~~

        The following sequence of commands will generate the sequence 1 ALA, 2 GLY, 3 LYS:

        relax> residue.create(1, 'ALA')
        relax> residue.create(2, 'GLY')
        relax> residue.create(3, 'LYS')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "residue.create("
            text = text + ", res_num=" + `res_num`
            text = text + ", res_name=" + `res_name` + ")"
            print text

        # Residue number.
        if type(res_num) != int:
            raise RelaxIntError, ('residue number', res_num)

        # Residue name.
        if type(res_name) != str:
            raise RelaxStrError, ('residue name', res_name)

        # Execute the functional code.
        residue.create(res_num=res_num, res_name=res_name)


    def delete(self, res_id=None):
        """Function for deleting residues.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        res_id:  The residue identifier string.


        Description
        ~~~~~~~~~~~

        This function can be used to delete a single or sets of residues.  See the identification
        string documentation below for more information.  If spin system/atom ids are included a
        RelaxError will be raised.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "residue.delete("
            text = text + "res_id=" + `res_id` + ")"
            print text

        # The residue identifier argument.
        if type(res_id) != str:
            raise RelaxStrError, ('residue identifier', res_id)

        # Execute the functional code.
        residue.delete(res_id=res_id)


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


    # Docstring modification.
    #########################

    # Indent the identification string documentation.
    #id_string_doc = replace(id_string_doc, '\n', '\n' + 8*' ')

    # Delete function.
    delete.__doc__ = delete.__doc__ + "\n\n" + id_string_doc + "\n"
