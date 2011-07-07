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
"""Module containing the 'deselect' user function class."""
__docformat__ = 'plaintext'

# Python module imports.
from select import boolean_doc

# relax module imports.
from base_class import User_fn_class, _build_doc
import arg_check
from generic_fns import selection


class Deselect(User_fn_class):
    """Class for deselecting spins."""

    def all(self):
        # Function intro test.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "deselect.all()"
            print(text)

        # Execute the functional code.
        selection.desel_all()

    # The function doc info.
    all._doc_title = "Deselect all spins."
    all._doc_desc = """
        This will deselect all spins, irregardless of their current state.
        """
    all._doc_examples = """
        To deselect all spins, simply type:

        relax> deselect.all()
        """
    _build_doc(all)


    def read(self, file=None, dir=None, spin_id_col=None, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None, sep=None, spin_id=None, boolean='AND', change_all=False):
        # Function intro test.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "deselect.read("
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
        selection.desel_read(file=file, dir=dir, spin_id_col=spin_id_col, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, sep=sep, spin_id=spin_id, boolean=boolean, change_all=change_all)

    # The function doc info.
    read._doc_title = "Deselect the spins contained in a file."
    read._doc_title_short = "Deselect spins from file."
    read._doc_args = [
        ["file", "The name of the file containing the list of spins to deselect."],
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
        The spin system can be identified in the file using two different formats.  The first is the spin ID string column which can include the molecule name, the residue name and number, and the spin name and number.  Alternatively the molecule name, residue number, residue name, spin number and/or spin name columns can be supplied allowing this information to be in separate columns.  Note that the numbering of columns starts at one.  The spin ID string can be used to restrict the reading to certain spin types, for example only 15N spins when only residue information is in the file.

        Empty lines and lines beginning with a hash are ignored.

        The 'change all' flag default is False meaning that all spins currently either selected or deselected will remain that way.  Setting this to True will cause all spins not specified in the file to be selected.
        """
    read._doc_examples = """
        To deselect all overlapped residues listed with residue numbers in the first column of the
        file 'unresolved', type one of:

        relax> deselect.read('unresolved', res_num_col=1)
        relax> deselect.read(file='unresolved', res_num_col=1)

        To deselect the spins in the second column of the relaxation data file 'r1.600' while
        selecting all other spins, for example type:

        relax> deselect.read('r1.600', spin_num_col=2, change_all=True)
        relax> deselect.read(file='r1.600', spin_num_col=2, change_all=True)
        """
    read._doc_additional = [boolean_doc]
    _build_doc(read)


    def reverse(self, spin_id=None):
        # Function intro test.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "deselect.reverse("
            text = text + "spin_id=" + repr(spin_id) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(spin_id, 'spin ID string', can_be_none=True)

        # Execute the functional code.
        selection.reverse(spin_id=spin_id)

    # The function doc info.
    reverse._doc_title = "Reversal of the spin selection for the given spins."
    reverse._doc_title_short = "Reversal of spin selection."
    reverse._doc_args = [
        ["spin_id", "The spin ID string."]
    ]
    reverse._doc_desc = """
        By supplying the spin ID string, a subset of spins can have their selection status reversed.
        """
    reverse._doc_examples = """
        To deselect all currently selected spins and select those which are deselected type:

        relax> deselect.reverse()
        """
    _build_doc(reverse)


    def spin(self, spin_id=None, change_all=False):
        # Function intro test.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "deselect.spin("
            text = text + "spin_id=" + repr(spin_id)
            text = text + ", change_all=" + repr(change_all) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(spin_id, 'spin ID string', can_be_none=True)
        arg_check.is_bool(change_all, 'change all')

        # Execute the functional code.
        selection.desel_spin(spin_id=spin_id, change_all=change_all)

    # The function doc info.
    spin._doc_title = "Deselect specific spins."
    spin._doc_args = [
        ["spin_id", "The spin ID string."],
        ["change_all", "A flag specifying if all other spins should be changed."]
    ]
    spin._doc_desc = """
        The 'change all' flag default is False meaning that all spins currently either selected or deselected will remain that way.  Setting this to True will cause all spins not specified by the spin ID string to be selected.
        """
    spin._doc_examples = """
        To deselect all glycines and alanines, type:

        relax> deselect.spin(spin_id=':GLY|:ALA')

        To deselect residue 12 MET type:

        relax> deselect.spin(':12')
        relax> deselect.spin(spin_id=':12')
        relax> deselect.spin(spin_id=':12&:MET')
        """
    _build_doc(spin)
