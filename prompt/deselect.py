###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004, 2008 Edward d'Auvergne                            #
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

# relax module imports.
import help
from generic_fns import selection
from relax_errors import RelaxBoolError, RelaxNoneIntError, RelaxNoneStrError, RelaxStrError


class Deselect:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for deselecting spins."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def all(self):
        """Function for deselecting all spins.

        Examples
        ~~~~~~~~

        To deselect all spins, simply type:

        relax> deselect.all()
        """

        # Function intro test.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "deselect.all()"
            print text

        # Execute the functional code.
        selection.desel_all()


    def read(self, file=None, dir=None, mol_name_col=None, res_num_col=0, res_name_col=None, spin_num_col=None, spin_name_col=None, sep=None, change_all=False):
        """Function for deselecting the spins contained in a file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        file:  The name of the file containing the list of spins to deselect.

        dir:  The directory where the file is located.

        mol_name_col:  The molecule name column (this defaults to no column).

        res_num_col:  The residue number column (the default is 0, i.e. the first column).

        res_name_col:  The residue name column (this defaults to no column).

        spin_num_col:  The spin number column (this defaults to no column).

        spin_name_col:  The spin name column (this defaults to no column).

        sep:  The column separator (the default is white space).

        change_all:  A flag specifying if all other spins should be changed.


        Description
        ~~~~~~~~~~~

        Empty lines and lines beginning with a hash are ignored.

        The 'change_all' flag argument default is False meaning that all spins currently either
        selected or deselected will remain that way.  Setting the argument to True will cause all
        spins not specified in the file to be selected.


        Examples
        ~~~~~~~~

        To deselect all overlapped residues listed with residue numbers in the first column of the
        file 'unresolved', type:

        relax> deselect.read('unresolved')
        relax> deselect.read(file='unresolved')

        To deselect the spins in the second column of the relaxation data file 'r1.600' while
        selecting all other spins, for example type:

        relax> deselect.read('r1.600', change_all=True, spin_num_col=1)
        relax> deselect.read(file='r1.600', change_all=True, spin_num_col=1)
        """

        # Function intro test.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "deselect.read("
            text = text + "file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", mol_name_col=" + `mol_name_col`
            text = text + ", res_num_col=" + `res_num_col`
            text = text + ", res_name_col=" + `res_name_col`
            text = text + ", spin_num_col=" + `spin_num_col`
            text = text + ", spin_name_col=" + `spin_name_col`
            text = text + ", sep=" + `sep`
            text = text + ", change_all=" + `change_all` + ")"
            print text

        # File name.
        if type(file) != str:
            raise RelaxStrError, ('file name', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # Molecule name column.
        if mol_name_col != None and type(mol_name_col) != int:
            raise RelaxNoneIntError, ('molecule name column', mol_name_col)

        # Residue number column.
        if res_num_col != None and type(res_num_col) != int:
            raise RelaxNoneIntError, ('residue number column', res_num_col)

        # Residue name column.
        if res_name_col != None and type(res_name_col) != int:
            raise RelaxNoneIntError, ('residue name column', res_name_col)

        # Spin number column.
        if spin_num_col != None and type(spin_num_col) != int:
            raise RelaxNoneIntError, ('spin number column', spin_num_col)

        # Spin name column.
        if spin_name_col != None and type(spin_name_col) != int:
            raise RelaxNoneIntError, ('spin name column', spin_name_col)

        # Column separator.
        if sep != None and type(sep) != str:
            raise RelaxNoneStrError, ('column separator', sep)

        # Change all flag.
        if type(change_all) != bool:
            raise RelaxBoolError, ('change_all', change_all)

        # Execute the functional code.
        selection.desel_read(file=file, dir=dir, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, sep=sep, change_all=change_all)


    def spin(self, spin_id=None, change_all=False):
        """Function for deselecting specific spins.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        spin_id:  The spin identification string.

        change_all:  A flag specifying if all other spins should be changed.


        Description
        ~~~~~~~~~~~

        The 'change_all' flag argument default is False meaning that all spins currently either
        selected or deselected will remain that way.  Setting the argument to True will cause all
        spins not specified by 'spin_id' to be selected.


        Examples
        ~~~~~~~~

        To deselect all glycines and alanines, type:

        relax> deselect.spin(spin_id=':GLY|:ALA')

        To deselect residue 12 MET type:

        relax> deselect.spin(':12')
        relax> deselect.spin(spin_id=':12')
        relax> deselect.spin(spin_id=':12&:MET')
        """

        # Function intro test.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "deselect.spin("
            text = text + "spin_id=" + `spin_id`
            text = text + ", change_all=" + `change_all` + ")"
            print text

        # Spin identification string.
        if spin_id != None and type(spin_id) != str:
            raise RelaxNoneStrError, ('Spin identification string', spin_id)

        # Change all flag.
        if type(change_all) != bool:
            raise RelaxBoolError, ('change_all', change_all)

        # Execute the functional code.
        selection.desel_spin(spin_id=spin_id, change_all=change_all)


    def reverse(self):
        """Function for the reversal of the spin selection.

        Examples
        ~~~~~~~~

        To deselect all currently selected spins and select those which are deselected type:

        relax> deselect.reverse()
        """

        # Function intro test.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "deselect.reverse()"
            print text

        # Execute the functional code.
        selection.reverse()
