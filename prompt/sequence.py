###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004, 2007-2008 Edward d'Auvergne                       #
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

# Module docstring.
"""Module containing the 'sequence' user function class."""
__docformat__ = 'plaintext'

# Python module imports.
import sys

# relax module imports.
import help
from generic_fns import sequence
from relax_errors import RelaxError, RelaxBoolError, RelaxNoneIntError, RelaxNoneStrError, RelaxStrError


class Sequence:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for manipulating sequence data."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def copy(self, pipe_from=None, pipe_to=None):
        """Copy the molecule, residue, and spin sequence data from one data pipe to another.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        pipe_from:  The name of the data pipe to copy the sequence data from.

        pipe_to:  The name of the data pipe to copy the sequence data to.


        Description
        ~~~~~~~~~~~

        This function will copy the sequence data between data pipes.  The destination data pipe
        must not contain any sequence data.  If the pipe_from or pipe_to arguments are not
        supplied, then both will default to the current data pipe (hence giving one argument is
        essential).


        Examples
        ~~~~~~~~

        To copy the sequence from the data pipe 'm1' to the current data pipe, type:

        relax> sequence.copy('m1')
        relax> sequence.copy(pipe_from='m1')


        To copy the sequence from the current data pipe to the data pipe 'm9', type:

        relax> sequence.copy(pipe_to='m9')


        To copy the sequence from the data pipe 'm1' to 'm2', type:

        relax> sequence.copy('m1', 'm2')
        relax> sequence.copy(pipe_from='m1', pipe_to='m2')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "sequence.copy("
            text = text + "pipe_from=" + repr(pipe_from)
            text = text + ", pipe_to=" + repr(pipe_to) + ")"
            print(text)

        # The pipe_from argument.
        if pipe_from != None and type(pipe_from) != str:
            raise RelaxNoneStrError('pipe from', pipe_from)

        # The pipe_to argument.
        if pipe_to != None and type(pipe_to) != str:
            raise RelaxNoneStrError('pipe to', pipe_to)

        # Both pipe arguments cannot be None.
        if pipe_from == None and pipe_to == None:
            raise RelaxError("The pipe_from and pipe_to arguments cannot both be set to None.")

        # Execute the functional code.
        sequence.copy(pipe_from=pipe_from, pipe_to=pipe_to)


    def display(self, sep=None, mol_name_flag=True, res_num_flag=True, res_name_flag=True, spin_num_flag=True, spin_name_flag=True):
        """Function for displaying sequences of molecules, residues, and/or spins.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        sep:  The column separator (the default of None corresponds to white space).

        mol_name_flag:  A flag whic if True will cause the molecule name column to be shown.

        res_num_flag:  A flag whic if True will cause the residue number column to be shown.

        res_name_flag:  A flag whic if True will cause the residue name column to be shown.

        spin_num_flag:  A flag whic if True will cause the spin number column to be shown.

        spin_name_flag:  A flag whic if True will cause the spin name column to be shown.

        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "sequence.display("
            text = text + "sep=" + repr(sep)
            text = text + ", mol_name_flag=" + repr(mol_name_flag)
            text = text + ", res_num_flag=" + repr(res_num_flag)
            text = text + ", res_name_flag=" + repr(res_name_flag)
            text = text + ", spin_num_flag=" + repr(spin_num_flag)
            text = text + ", spin_name_flag=" + repr(spin_name_flag) + ")"
            print(text)

        # Column separator.
        if sep != None and type(sep) != str:
            raise RelaxNoneStrError('column separator', sep)

        # Molecule name flag.
        if type(mol_name_flag) != bool:
            raise RelaxBoolError('molecule name flag', mol_name_flag)

        # Residue number flag.
        if type(res_num_flag) != bool:
            raise RelaxBoolError('residue number flag', res_num_flag)

        # Residue name flag.
        if type(res_name_flag) != bool:
            raise RelaxBoolError('residue name flag', res_name_flag)

        # Spin number flag.
        if type(spin_num_flag) != bool:
            raise RelaxBoolError('spin number flag', spin_num_flag)

        # Spin name flag.
        if type(spin_name_flag) != bool:
            raise RelaxBoolError('spin name flag', spin_name_flag)

        # Execute the functional code.
        sequence.display(sep=sep, mol_name_flag=mol_name_flag, res_num_flag=res_num_flag, res_name_flag=res_name_flag, spin_num_flag=spin_num_flag, spin_name_flag=spin_name_flag)


    def read(self, file=None, dir=None, mol_name_col=None, res_num_col=0, res_name_col=1, spin_num_col=None, spin_name_col=None, sep=None):
        """Function for reading sequences of molecules, residues, and spins.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        file:  The name of the file containing the sequence data.

        dir:  The directory where the file is located.

        mol_name_col:  The molecule name column (this defaults to no column).

        res_num_col:  The residue number column (the default is 0, i.e. the first column).

        res_name_col:  The residue name column (the default is 1, i.e. the second column).

        spin_num_col:  The spin number column (this defaults to no column).

        spin_name_col:  The spin name column (this defaults to no column).

        sep:  The column separator (the default is white space).


        Description
        ~~~~~~~~~~~

        If no directory is given, the file will be assumed to be in the current working directory.


        Examples
        ~~~~~~~~

        The following commands will read the sequence data out of a file called 'seq' where the
        residue numbers and names are in the first and second columns respectively:

        relax> sequence.read('seq')
        relax> sequence.read('seq', num_col=0, name_col=1)
        relax> sequence.read(file='seq', num_col=0, name_col=1, sep=None)


        The following commands will read the residue sequence out of the file 'noe.out' which also
        contains the NOE values:

        relax> sequence.read('noe.out')
        relax> sequence.read('noe.out', num_col=0, name_col=1)
        relax> sequence.read(file='noe.out', num_col=0, name_col=1)


        The following commands will read the sequence out of the file 'noe.600.out' where the
        residue numbers are in the second column, the names are in the sixth column and the columns
        are separated by commas:

        relax> sequence.read('noe.600.out', num_col=1, name_col=5, sep=',')
        relax> sequence.read(file='noe.600.out', num_col=1, name_col=5, sep=',')


        The following commands will read the RNA residues and atoms (including C2, C5, C6, C8, N1,
        and N3) from the file '500.NOE', where the residue number, residue name, spin number, and
        spin name are in the first to fourth columns respectively:

        relax> sequence.read('500.NOE', spin_num_col=2, spin_name_col=3)
        relax> sequence.read('500.NOE', num_col=0, name_col=1, spin_num_col=2, spin_name_col=3)
        relax> sequence.read(file='500.NOE', spin_num_col=2, spin_name_col=3)
        relax> sequence.read(file='500.NOE', num_col=0, name_col=1, spin_num_col=2, spin_name_col=3)
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "sequence.read("
            text = text + "file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", mol_name_col=" + repr(mol_name_col)
            text = text + ", res_num_col=" + repr(res_num_col)
            text = text + ", res_name_col=" + repr(res_name_col)
            text = text + ", spin_num_col=" + repr(spin_num_col)
            text = text + ", spin_name_col=" + repr(spin_name_col)
            text = text + ", sep=" + repr(sep) + ")"
            print(text)

        # The file name.
        if type(file) != str:
            raise RelaxStrError('file name', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError('directory name', dir)

        # Molecule name column.
        if mol_name_col != None and type(mol_name_col) != int:
            raise RelaxNoneIntError('molecule name column', mol_name_col)

        # Residue number column.
        if res_name_col != None and type(res_num_col) != int:
            raise RelaxNoneIntError('residue number column', res_num_col)

        # Residue name column.
        if res_name_col != None and type(res_name_col) != int:
            raise RelaxNoneIntError('residue name column', res_name_col)

        # Spin number column.
        if spin_num_col != None and type(spin_num_col) != int:
            raise RelaxNoneIntError('spin number column', spin_num_col)

        # Spin name column.
        if spin_name_col != None and type(spin_name_col) != int:
            raise RelaxNoneIntError('spin name column', spin_name_col)

        # Column separator.
        if sep != None and type(sep) != str:
            raise RelaxNoneStrError('column separator', sep)

        # Execute the functional code.
        sequence.read(file=file, dir=dir, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, sep=sep)


    def write(self, file, dir=None, sep=None, mol_name_flag=False, res_num_flag=False, res_name_flag=False, spin_num_flag=False, spin_name_flag=False, force=False):
        """Write the molecule, residue, and spin sequence to a file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        file:  The name of the file.

        dir:  The directory name.

        sep:  The column separator (the default of None corresponds to white space).

        mol_name_flag:  A flag whic if True will cause the molecule name column to be shown.

        res_num_flag:  A flag whic if True will cause the residue number column to be shown.

        res_name_flag:  A flag whic if True will cause the residue name column to be shown.

        spin_num_flag:  A flag whic if True will cause the spin number column to be shown.

        spin_name_flag:  A flag whic if True will cause the spin name column to be shown.

        force:  A flag which if True will cause the file to be overwritten.


        Description
        ~~~~~~~~~~~

        If no directory name is given, the file will be placed in the current working directory.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "sequence.write("
            text = text + "file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", sep=" + repr(sep)
            text = text + ", mol_name_flag=" + repr(mol_name_flag)
            text = text + ", res_num_flag=" + repr(res_num_flag)
            text = text + ", res_name_flag=" + repr(res_name_flag)
            text = text + ", spin_num_flag=" + repr(spin_num_flag)
            text = text + ", spin_name_flag=" + repr(spin_name_flag)
            text = text + ", force=" + repr(force) + ")"
            print(text)

        # File.
        if type(file) != str:
            raise RelaxStrError('file name', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError('directory name', dir)

        # Column separator.
        if sep != None and type(sep) != str:
            raise RelaxNoneStrError('column separator', sep)

        # Molecule name flag.
        if type(mol_name_flag) != bool:
            raise RelaxBoolError('molecule name flag', mol_name_flag)

        # Residue number flag.
        if type(res_num_flag) != bool:
            raise RelaxBoolError('residue number flag', res_num_flag)

        # Residue name flag.
        if type(res_name_flag) != bool:
            raise RelaxBoolError('residue name flag', res_name_flag)

        # Spin number flag.
        if type(spin_num_flag) != bool:
            raise RelaxBoolError('spin number flag', spin_num_flag)

        # Spin name flag.
        if type(spin_name_flag) != bool:
            raise RelaxBoolError('spin name flag', spin_name_flag)

        # The force flag.
        if type(force) != bool:
            raise RelaxBoolError('force flag', force)

        # Execute the functional code.
        sequence.write(file=file, dir=dir, sep=sep, mol_name_flag=mol_name_flag, res_num_flag=res_num_flag, res_name_flag=res_name_flag, spin_num_flag=spin_num_flag, spin_name_flag=spin_name_flag, force=force)
