###############################################################################
#                                                                             #
# Copyright (C) 2003-2011 Edward d'Auvergne                                   #
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

# relax module imports.
from base_class import User_fn_class
import arg_check
from generic_fns import selection


boolean_doc = ["Boolean operators", """
The boolean operator can be used to change how spin systems are selected.  The allowed values are: 'OR', 'NOR', 'AND', 'NAND', 'XOR', 'XNOR'.  The following table details how the selections will occur for the different boolean operators.
__________________________________________________________
|                    |   |   |   |   |   |   |   |   |   |
| Spin system        | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|____________________|___|___|___|___|___|___|___|___|___|
|                    |   |   |   |   |   |   |   |   |   |
| Original selection | 0 | 1 | 1 | 1 | 1 | 0 | 1 | 0 | 1 |
|                    |   |   |   |   |   |   |   |   |   |
| New selection      | 0 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 |
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
"""]


class Select(User_fn_class):
    """Class for selecting spins."""

    def all(self):
        # Function intro test.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "select.all()"
            print(text)

        # Execute the functional code.
        selection.sel_all()

    # The function doc info.
    all._doc_title = "Select all spins."
    all._doc_desc = """
        This will select all spins, irregardless of their current state.
        """
    all._doc_examples = """
        To select all spins, simply type:

        relax> select.all()
        """
    _build_doc(all)


    def read(self, file=None, dir=None, spin_id_col=None, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None, sep=None, spin_id=None, boolean='OR', change_all=False):
        # Function intro test.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "select.read("
            text = text + "file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", spin_id_col=" + repr(spin_id_col)
            text = text + ", mol_name_col=" + repr(mol_name_col)
            text = text + ", res_num_col=" + repr(res_num_col)
            text = text + ", res_name_col=" + repr(res_name_col)
            text = text + ", spin_num_col=" + repr(spin_num_col)
            text = text + ", spin_name_col=" + repr(spin_name_col)
            text = text + ", sep=" + repr(sep)
            text = text + ", spin_id=" + repr(spin_id)
            text = text + ", boolean=" + repr(boolean)
            text = text + ", change_all=" + repr(change_all) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str_or_inst(file, 'file name')
        arg_check.is_str(dir, 'directory name', can_be_none=True)
        arg_check.is_int(spin_id_col, 'spin ID string column', can_be_none=True)
        arg_check.is_int(mol_name_col, 'molecule name column', can_be_none=True)
        arg_check.is_int(res_num_col, 'residue number column', can_be_none=True)
        arg_check.is_int(res_name_col, 'residue name column', can_be_none=True)
        arg_check.is_int(spin_num_col, 'spin number column', can_be_none=True)
        arg_check.is_int(spin_name_col, 'spin name column', can_be_none=True)
        arg_check.is_str(sep, 'column separator', can_be_none=True)
        arg_check.is_str(spin_id, 'spin ID string', can_be_none=True)
        arg_check.is_str(boolean, 'boolean operator')
        arg_check.is_bool(change_all, 'change all')

        # Execute the functional code.
        selection.sel_read(file=file, dir=dir, spin_id_col=spin_id_col, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, sep=sep, spin_id=spin_id, boolean=boolean, change_all=change_all)

    # The function doc info.
    read._doc_title = "Select the spins contained in a file."
    read._doc_args = [
        ["file", "The name of the file containing the list of spins to select."],
        ["dir", "The directory where the file is located."],
        ["spin_id_col", "The spin ID string column (an alternative to the mol, res, and spin name and number columns)."],
        ["mol_name_col", "The molecule name column (alternative to the spin_id_col)."],
        ["res_num_col", "The residue number column (alternative to the spin_id_col)."],
        ["res_name_col", "The residue name column (alternative to the spin_id_col)."],
        ["spin_num_col", "The spin number column (alternative to the spin_id_col)."],
        ["spin_name_col", "The spin name column (alternative to the spin_id_col)."],
        ["data_col", "The RDC data column."],
        ["error_col", "The experimental error column."],
        ["sep", "The column separator (the default is white space)."],
        ["spin_id", "The spin ID string to restrict the loading of data to certain spin subsets."],
        ["boolean", "The boolean operator specifying how spins should be selected."],
        ["change_all", "A flag specifying if all other spins should be changed."]
    ]
    read._doc_desc = """
        The spin system can be identified in the file using two different formats.  The first is the spin ID string column which can include the molecule name, the residue name and number, and the spin name and number.  Alternatively the mol_name_col, res_num_col, res_name_col, spin_num_col, and/or spin_name_col arguments can be supplied allowing this information to be in separate columns.  Note that the numbering of columns starts at one.  The spin_id argument can be used to restrict the reading to certain spin types, for example only 15N spins when only residue information is in the file.

        Empty lines and lines beginning with a hash are ignored.

        The 'change_all' flag argument default is False meaning that all spins currently either selected or deselected will remain that way.  Setting the argument to True will cause all spins not specified in the file to be deselected.
        """
    read._doc_examples = """
        To select all residues listed with residue numbers in the first column of the file
        'isolated_peaks', type one of:

        relax> select.read('isolated_peaks', res_num_col=1)
        relax> select.read(file='isolated_peaks', res_num_col=1)

        To select the spins in the second column of the relaxation data file 'r1.600' while
        deselecting all other spins, for example type:

        relax> select.read('r1.600', spin_num_col=2, change_all=True)
        relax> select.read(file='r1.600', spin_num_col=2, change_all=True)
        """
    read._doc_additional = [boolean_doc]
    _build_doc(read)


    def reverse(self, spin_id=None):
        # Function intro test.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "select.reverse("
            text = text + "spin_id=" + repr(spin_id) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(spin_id, 'spin identification string', can_be_none=True)

        # Execute the functional code.
        selection.reverse(spin_id=spin_id)

    # The function doc info.
    reverse._doc_title = "Reversal of the spin selection for the given spins."
    reverse._doc_args = [
        ["spin_id", "The spin identification string."]
    ]
    reverse._doc_desc = """
        By supplying the spin_id argument, a subset of spin can have their selection status reversed.
        """
    reverse._doc_examples = """
        To select all currently deselected spins and deselect those which are selected type:

        relax> select.reverse()
        """
    _build_doc(reverse)


    def spin(self, spin_id=None, boolean='OR', change_all=False):
        # Function intro test.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "select.spin("
            text = text + "spin_id=" + repr(spin_id)
            text = text + ", boolean=" + repr(boolean)
            text = text + ", change_all=" + repr(change_all) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(spin_id, 'spin identification string', can_be_none=True)
        arg_check.is_str(boolean, 'boolean operator')
        arg_check.is_bool(change_all, 'change all')

        # Execute the functional code.
        selection.sel_spin(spin_id=spin_id, boolean=boolean, change_all=change_all)

    # The function doc info.
    spin._doc_title = "Select specific spins."
    spin._doc_args = [
        ["spin_id", "The spin identification string."],
        ["boolean", "The boolean operator specifying how spins should be selected."],
        ["change_all", "A flag specifying if all other spins should be changed."]
    ]
    spin._doc_desc = """
        The 'change_all' flag argument default is False meaning that all spins currently either selected or deselected will remain that way.  Setting the argument to True will cause all spins not specified by 'spin_id' to be selected.
        """
    spin._doc_examples = """
        To select only glycines and alanines, assuming they have been loaded with the names GLY and
        ALA, type one of:

        relax> select.spin(spin_id=':GLY|:ALA')

        To select residue 5 CYS in addition to the currently selected residues, type one of:

        relax> select.spin(':5')
        relax> select.spin(':5&:CYS')
        relax> select.spin(spin_id=':5&:CYS')
        """
    spin._doc_additional = [boolean_doc]
    _build_doc(spin)
