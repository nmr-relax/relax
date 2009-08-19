###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004, 2006, 2008 Edward d'Auvergne                      #
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
"""Module containing the 'select' user function class."""
__docformat__ = 'plaintext'

# Python module imports.
import sys

# relax module imports.
import help
from generic_fns import selection
from relax_errors import RelaxBoolError, RelaxNoneIntError, RelaxNoneStrError, RelaxStrError


class Select:
    __boolean_doc = """
        Boolean operators
        ~~~~~~~~~~~~~~~~~

        The 'boolean' keyword argument can be used to change how spin systems are selected.  The
        allowed values are: 'OR', 'NOR', 'AND', 'NAND', 'XOR', 'XNOR'.  The following table details
        how the selections will occur for the different boolean operators.
        __________________________________________________________
        |                    |   |   |   |   |   |   |   |   |   |
        | Spin system        | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
        |____________________|___|___|___|___|___|___|___|___|___|
        |                    |   |   |   |   |   |   |   |   |   |
        | Original selection | 0 | 1 | 1 | 1 | 1 | 0 | 1 | 0 | 1 |
        |                    |   |   |   |   |   |   |   |   |   |
        | New selection      | 0 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 |
        |____________________|___|___|___|___|___|___|___|___|___|
        |                    |   |   |   |   |   |   |   |   |   |
        | OR                 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 1 |
        |                    |   |   |   |   |   |   |   |   |   |
        | NOR                | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
        |                    |   |   |   |   |   |   |   |   |   |
        | AND                | 0 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 0 |
        |                    |   |   |   |   |   |   |   |   |   |
        | NAND               | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 1 |
        |                    |   |   |   |   |   |   |   |   |   |
        | XOR                | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 1 |
        |                    |   |   |   |   |   |   |   |   |   |
        | XNOR               | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 1 | 0 |
        |____________________|___|___|___|___|___|___|___|___|___|
    """


    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for selecting spins."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def all(self):
        """Function for selecting all spins.

        Examples
        ~~~~~~~~

        To select all spins, simply type:

        relax> select.all()
        """

        # Function intro test.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "select.all()"
            print(text)

        # Execute the functional code.
        selection.sel_all()


    def read(self, file=None, dir=None, mol_name_col=None, res_num_col=0, res_name_col=None, spin_num_col=None, spin_name_col=None, sep=None, boolean='OR', change_all=False):
        """Function for selecting the spins contained in a file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        file:  The name of the file containing the list of spins to select.

        dir:  The directory where the file is located.

        mol_name_col:  The molecule name column (this defaults to no column).

        res_num_col:  The residue number column (the default is 0, i.e. the first column).

        res_name_col:  The residue name column (this defaults to no column).

        spin_num_col:  The spin number column (this defaults to no column).

        spin_name_col:  The spin name column (this defaults to no column).

        sep:  The column separator (the default is white space).

        boolean:  The boolean operator specifying how spins should be selected.

        change_all:  A flag specifying if all other spins should be changed.


        Description
        ~~~~~~~~~~~

        Empty lines and lines beginning with a hash are ignored.

        The 'change_all' flag argument default is False meaning that all spins currently either
        selected or deselected will remain that way.  Setting the argument to True will cause all
        spins not specified in the file to be deselected.


        Examples
        ~~~~~~~~

        To select all residues listed with residue numbers in the first column of the file
        'isolated_peaks', type one of:

        relax> select.read('isolated_peaks')
        relax> select.read(file='isolated_peaks')

        To select the spins in the second column of the relaxation data file 'r1.600' while
        deselecting all other spins, for example type:

        relax> select.read('r1.600', res_num_col=None, spin_num_col=1, change_all=True)
        relax> select.read(file='r1.600', res_num_col=None, spin_num_col=1, change_all=True)
        """

        # Function intro test.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "select.read("
            text = text + "file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", mol_name_col=" + repr(mol_name_col)
            text = text + ", res_num_col=" + repr(res_num_col)
            text = text + ", res_name_col=" + repr(res_name_col)
            text = text + ", spin_num_col=" + repr(spin_num_col)
            text = text + ", spin_name_col=" + repr(spin_name_col)
            text = text + ", sep=" + repr(sep)
            text = text + ", boolean=" + repr(boolean)
            text = text + ", change_all=" + repr(change_all) + ")"
            print(text)

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

        # Boolean operator.
        if type(boolean) != str:
            raise RelaxStrError, ('boolean operator', boolean)

        # Change all flag.
        if type(change_all) != bool:
            raise RelaxBoolError, ('change_all', change_all)

        # Execute the functional code.
        selection.sel_read(file=file, dir=dir, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, sep=sep, boolean=boolean, change_all=change_all)


    def reverse(self, spin_id=None):
        """Function for the reversal of the spin selection for the given spins.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        spin_id:  The spin identification string.


        Description
        ~~~~~~~~~~~

        By supplying the spin_id argument, a subset of spin can have their selection status
        reversed.


        Examples
        ~~~~~~~~

        To select all currently deselected spins and deselect those which are selected type:

        relax> select.reverse()
        """

        # Function intro test.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "select.reverse("
            text = text + "spin_id=" + repr(spin_id) + ")"
            print(text)

        # Spin identification string.
        if spin_id != None and type(spin_id) != str:
            raise RelaxNoneStrError, ('Spin identification string', spin_id)

        # Execute the functional code.
        reverse(selection=selection)


    def spin(self, spin_id=None, boolean='OR', change_all=False):
        """Function for selecting specific spins.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        spin_id:  The spin identification string.

        boolean:  The boolean operator specifying how spins should be selected.

        change_all:  A flag specifying if all other spins should be changed.


        Description
        ~~~~~~~~~~~

        The 'change_all' flag argument default is False meaning that all spins currently either
        selected or deselected will remain that way.  Setting the argument to True will cause all
        spins not specified by 'spin_id' to be selected.


        Examples
        ~~~~~~~~

        To select only glycines and alanines, assuming they have been loaded with the names GLY and
        ALA, type one of:

        relax> select.spin(spin_id=':GLY|:ALA')

        To select residue 5 CYS in addition to the currently selected residues, type one of:

        relax> select.spin(':5')
        relax> select.spin(':5&:CYS')
        relax> select.spin(spin_id=':5&:CYS')
        """

        # Function intro test.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "select.spin("
            text = text + "spin_id=" + repr(spin_id)
            text = text + ", boolean=" + repr(boolean)
            text = text + ", change_all=" + repr(change_all) + ")"
            print(text)

        # Spin identification string.
        if spin_id != None and type(spin_id) != str:
            raise RelaxNoneStrError, ('Spin identification string', spin_id)

        # Boolean operator.
        if type(boolean) != str:
            raise RelaxStrError, ('boolean operator', boolean)

        # Change all flag.
        if type(change_all) != bool:
            raise RelaxBoolError, ('change_all', change_all)

        # Execute the functional code.
        selection.sel_spin(spin_id=spin_id, boolean=boolean, change_all=change_all)



    # Docstring modification.
    #########################

    # Read function.
    read.__doc__ = read.__doc__ + "\n\n" + __boolean_doc + "\n"
