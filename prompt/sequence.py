###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004, 2007-2010 Edward d'Auvergne                       #
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

# relax module imports.
from base_class import User_fn_class, _build_doc
import arg_check
from generic_fns import sequence
from relax_errors import RelaxError


class Sequence(User_fn_class):
    """Class for manipulating sequence data."""

    def copy(self, pipe_from=None, pipe_to=None):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "sequence.copy("
            text = text + "pipe_from=" + repr(pipe_from)
            text = text + ", pipe_to=" + repr(pipe_to) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(pipe_from, 'pipe from', can_be_none=True)
        arg_check.is_str(pipe_to, 'pipe to', can_be_none=True)

        # Both pipe arguments cannot be None.
        if pipe_from == None and pipe_to == None:
            raise RelaxError("The pipe_from and pipe_to arguments cannot both be set to None.")

        # Execute the functional code.
        sequence.copy(pipe_from=pipe_from, pipe_to=pipe_to)

    # The function doc info.
    copy._doc_title = "Copy the molecule, residue, and spin sequence data from one data pipe to another."
    copy._doc_title_short = "Sequence data copying."
    copy._doc_args = [
        ["pipe_from", "The name of the data pipe to copy the sequence data from."],
        ["pipe_to", "The name of the data pipe to copy the sequence data to."]
    ]
    copy._doc_desc = """
        This will copy the sequence data between data pipes.  The destination data pipe must not contain any sequence data.  If the source and destination pipes are not specified, then both will default to the current data pipe (hence providing one is essential).
        """
    copy._doc_examples = """
        To copy the sequence from the data pipe 'm1' to the current data pipe, type:

        relax> sequence.copy('m1')
        relax> sequence.copy(pipe_from='m1')


        To copy the sequence from the current data pipe to the data pipe 'm9', type:

        relax> sequence.copy(pipe_to='m9')


        To copy the sequence from the data pipe 'm1' to 'm2', type:

        relax> sequence.copy('m1', 'm2')
        relax> sequence.copy(pipe_from='m1', pipe_to='m2')
        """
    _build_doc(copy)


    def display(self, sep=None, mol_name_flag=True, res_num_flag=True, res_name_flag=True, spin_num_flag=True, spin_name_flag=True):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "sequence.display("
            text = text + "sep=" + repr(sep)
            text = text + ", mol_name_flag=" + repr(mol_name_flag)
            text = text + ", res_num_flag=" + repr(res_num_flag)
            text = text + ", res_name_flag=" + repr(res_name_flag)
            text = text + ", spin_num_flag=" + repr(spin_num_flag)
            text = text + ", spin_name_flag=" + repr(spin_name_flag) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(sep, 'column separator', can_be_none=True)
        arg_check.is_bool(mol_name_flag, 'molecule name flag')
        arg_check.is_bool(res_num_flag, 'residue number flag')
        arg_check.is_bool(res_name_flag, 'residue name flag')
        arg_check.is_bool(spin_num_flag, 'spin number flag')
        arg_check.is_bool(spin_name_flag, 'spin name flag')

        # Execute the functional code.
        sequence.display(sep=sep, mol_name_flag=mol_name_flag, res_num_flag=res_num_flag, res_name_flag=res_name_flag, spin_num_flag=spin_num_flag, spin_name_flag=spin_name_flag)

    # The function doc info.
    display._doc_title = "Display sequences of molecules, residues, and/or spins."
    display._doc_title_short = "Sequence data display."
    display._doc_args = [
        ["sep", "The column separator (the default of None corresponds to white space)."],
        ["mol_name_flag", "A flag whic if True will cause the molecule name column to be shown."],
        ["res_num_flag", "A flag whic if True will cause the residue number column to be shown."],
        ["res_name_flag", "A flag whic if True will cause the residue name column to be shown."],
        ["spin_num_flag", "A flag whic if True will cause the spin number column to be shown."],
        ["spin_name_flag", "A flag whic if True will cause the spin name column to be shown."]
    ]
    _build_doc(display)


    def read(self, file=None, dir=None, spin_id_col=None, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None, sep=None, spin_id=None):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "sequence.read("
            text = text + "file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", spin_id_col=" + repr(spin_id_col)
            text = text + ", mol_name_col=" + repr(mol_name_col)
            text = text + ", res_num_col=" + repr(res_num_col)
            text = text + ", res_name_col=" + repr(res_name_col)
            text = text + ", spin_num_col=" + repr(spin_num_col)
            text = text + ", spin_name_col=" + repr(spin_name_col)
            text = text + ", sep=" + repr(sep)
            text = text + ", spin_id=" + repr(spin_id) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(file, 'file name')
        arg_check.is_str(dir, 'directory name', can_be_none=True)
        arg_check.is_int(spin_id_col, 'spin ID string column', can_be_none=True)
        arg_check.is_int(mol_name_col, 'molecule name column', can_be_none=True)
        arg_check.is_int(res_num_col, 'residue number column', can_be_none=True)
        arg_check.is_int(res_name_col, 'residue name column', can_be_none=True)
        arg_check.is_int(spin_num_col, 'spin number column', can_be_none=True)
        arg_check.is_int(spin_name_col, 'spin name column', can_be_none=True)
        arg_check.is_str(sep, 'column separator', can_be_none=True)
        arg_check.is_str(spin_id, 'spin ID string', can_be_none=True)

        # Execute the functional code.
        sequence.read(file=file, dir=dir, spin_id_col=spin_id_col, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, sep=sep, spin_id=spin_id)

    # The function doc info.
    read._doc_title = "Read the molecule, residue, and spin sequence from a file."
    read._doc_title_short = "Sequence data reading."
    read._doc_args = [
        ["file", "The name of the file containing the sequence data."],
        ["dir", "The directory where the file is located."],
        ["spin_id_col", "The spin ID string column (an alternative to the mol, res, and spin name and number columns)."],
        ["mol_name_col", "The molecule name column (alternative to the spin_id_col)."],
        ["res_num_col", "The residue number column (alternative to the spin_id_col)."],
        ["res_name_col", "The residue name column (alternative to the spin_id_col)."],
        ["spin_num_col", "The spin number column (alternative to the spin_id_col)."],
        ["spin_name_col", "The spin name column (alternative to the spin_id_col)."],
        ["sep", "The column separator (the default is white space)."],
        ["spin_id", "The spin ID string to restrict the loading of data to certain spin subsets."]
    ]
    read._doc_desc = """
        The spin system can be identified in the file using two different formats.  The first is the spin ID string column which can include the molecule name, the residue name and number, and the spin name and number.  Alternatively the molecule name, residue number, residue name, spin number and/or spin name columns can be supplied allowing this information to be in separate columns.  Note that the numbering of columns starts at one.  The spin ID string can be used to restrict the reading to certain spin types, for example only 15N spins when only residue information is in the file.
        """
    read._doc_examples = """
        The following commands will read protein backbone 15N sequence data out of a file called
        'seq' where the residue numbers and names are in the first and second columns respectively:

        relax> sequence.read('seq')
        relax> sequence.read('seq', res_num_col=1, res_name_col=2)
        relax> sequence.read(file='seq', res_num_col=1, res_name_col=2, sep=None)


        The following commands will read the residue sequence out of the file 'noe.out' which also
        contains the NOE values:

        relax> sequence.read('noe.out')
        relax> sequence.read('noe.out', res_num_col=1, res_name_col=2)
        relax> sequence.read(file='noe.out', res_num_col=1, res_name_col=2)


        The following commands will read the sequence out of the file 'noe.600.out' where the
        residue numbers are in the second column, the names are in the sixth column and the columns
        are separated by commas:

        relax> sequence.read('noe.600.out', res_num_col=2, res_name_col=6, sep=',')
        relax> sequence.read(file='noe.600.out', res_num_col=2, res_name_col=6, sep=',')


        The following commands will read the RNA residues and atoms (including C2, C5, C6, C8, N1,
        and N3) from the file '500.NOE', where the residue number, residue name, spin number, and
        spin name are in the first to fourth columns respectively:

        relax> sequence.read('500.NOE', res_num_col=1, res_name_col=2, spin_num_col=3,
                             spin_name_col=4)
        relax> sequence.read(file='500.NOE', res_num_col=1, res_name_col=2, spin_num_col=3,
                             spin_name_col=4)
        """
    _build_doc(read)


    def write(self, file, dir=None, sep=None, mol_name_flag=False, res_num_flag=False, res_name_flag=False, spin_num_flag=False, spin_name_flag=False, force=False):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "sequence.write("
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

        # The argument checks.
        arg_check.is_str(file, 'file name')
        arg_check.is_str(dir, 'directory name', can_be_none=True)
        arg_check.is_str(sep, 'column separator', can_be_none=True)
        arg_check.is_bool(mol_name_flag, 'molecule name flag')
        arg_check.is_bool(res_num_flag, 'residue number flag')
        arg_check.is_bool(res_name_flag, 'residue name flag')
        arg_check.is_bool(spin_num_flag, 'spin number flag')
        arg_check.is_bool(spin_name_flag, 'spin name flag')
        arg_check.is_bool(force, 'force flag')

        # Execute the functional code.
        sequence.write(file=file, dir=dir, sep=sep, mol_name_flag=mol_name_flag, res_num_flag=res_num_flag, res_name_flag=res_name_flag, spin_num_flag=spin_num_flag, spin_name_flag=spin_name_flag, force=force)

    # The function doc info.
    write._doc_title = "Write the molecule, residue, and spin sequence to a file."
    write._doc_title_short = "Sequence data writing."
    write._doc_args = [
        ["file", "The name of the file."],
        ["dir", "The directory name."],
        ["sep", "The column separator (the default of None corresponds to white space)."],
        ["mol_name_flag", "A flag which if True will cause the molecule name column to be shown."],
        ["res_num_flag", "A flag which if True will cause the residue number column to be shown."],
        ["res_name_flag", "A flag which if True will cause the residue name column to be shown."],
        ["spin_num_flag", "A flag which if True will cause the spin number column to be shown."],
        ["spin_name_flag", "A flag which if True will cause the spin name column to be shown."],
        ["force", "A flag which if True will cause the file to be overwritten."]
    ]
    write._doc_desc = """
        Write the sequence data to file.  If no directory name is given, the file will be placed in the current working directory.
        """
    _build_doc(write)
