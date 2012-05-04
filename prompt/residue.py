###############################################################################
#                                                                             #
# Copyright (C) 2007-2012 Edward d'Auvergne                                   #
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
"""Module containing the 'residue' user function class."""
__docformat__ = 'plaintext'

# relax module imports.
from base_class import User_fn_class, _build_doc
import arg_check
from generic_fns.mol_res_spin import copy_residue, create_residue, delete_residue, display_residue, id_string_doc, name_residue, number_residue
from status import Status; status = Status()


class Residue(User_fn_class):
    """Class for manipulating the residue data."""

    def copy(self, pipe_from=None, res_from=None, pipe_to=None, res_to=None):
        # Function intro text.
        if status.prompt_intro:
            text = status.ps3 + "residue.copy("
            text = text + "pipe_from=" + repr(pipe_from)
            text = text + ", res_from=" + repr(res_from)
            text = text + ", pipe_to=" + repr(pipe_to)
            text = text + ", res_to=" + repr(res_to) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(pipe_from, 'pipe from', can_be_none=True)
        arg_check.is_str(res_from, 'residue from')
        arg_check.is_str(pipe_to, 'pipe to', can_be_none=True)
        arg_check.is_str(res_to, 'residue to', can_be_none=True)

        # Execute the functional code.
        copy_residue(pipe_from=pipe_from, res_from=res_from, pipe_to=pipe_to, res_to=res_to)

    # The function doc info.
    copy._doc_title = "Copy all data associated with a residue."
    copy._doc_title_short = "Residue copying."
    copy._doc_args = [
        ["pipe_from", "The data pipe containing the residue from which the data will be copied.  This defaults to the current data pipe."],
        ["res_from", "The residue ID string of the residue to copy the data from."],
        ["pipe_to", "The data pipe to copy the data to.  This defaults to the current data pipe."],
        ["res_to", "The residue ID string of the residue to copy the data to."]]
    copy._doc_desc = """
        This will copy all the data associated with the identified residue to the new, non-existent residue.  The new residue cannot currently exist.
        """
    copy._doc_examples = """
        To copy the residue data from residue 1 to the new residue 2, type:

        relax> residue.copy(res_from=':1', res_to=':2')


        To copy residue 1 of the molecule 'Old mol' to residue 5 of the molecule 'New mol', type:

        relax> residue.copy(res_from='#Old mol:1', res_to='#New mol:5')


        To copy the residue data of residue 1 from the data pipe 'm1' to 'm2', assuming the current
        data pipe is 'm1', type:

        relax> residue.copy(res_from=':1', pipe_to='m2')
        relax> residue.copy(pipe_from='m1', res_from=':1', pipe_to='m2', res_to=':1')
        """
    _build_doc(copy)


    def create(self, res_num=None, res_name=None, mol_name=None):
        # Function intro text.
        if status.prompt_intro:
            text = status.ps3 + "residue.create("
            text = text + "res_num=" + repr(res_num)
            text = text + ", res_name=" + repr(res_name)
            text = text + ", mol_name=" + repr(mol_name) + ")"
            print(text)

        # The argument checks.
        arg_check.is_int(res_num, 'residue number')
        arg_check.is_str(res_name, 'residue name', can_be_none=True)
        arg_check.is_str(mol_name, 'molecule name', can_be_none=True)

        # Execute the functional code.
        create_residue(res_num=res_num, res_name=res_name, mol_name=mol_name)

    # The function doc info.
    create._doc_title = "Create a new residue."
    create._doc_title_short = "Residue creation."
    create._doc_args = [
        ["res_num", "The residue number."],
        ["res_name", "The name of the residue."],
        ["mol_name", "The name of the molecule to add the residue to."]]
    create._doc_desc = """
        Using this, a new sequence can be generated without using the sequence user functions.  However if the sequence already exists, the new residue will be added to the end of the residue list (the residue numbers of this list need not be sequential).  The same residue number cannot be used more than once.  A corresponding single spin system will be created for this residue.  The spin system number and name or additional spin systems can be added later if desired.
        """
    create._doc_examples = """
        The following sequence of commands will generate the sequence 1 ALA, 2 GLY, 3 LYS:

        relax> residue.create(1, 'ALA')
        relax> residue.create(2, 'GLY')
        relax> residue.create(3, 'LYS')
        """
    _build_doc(create)


    def delete(self, res_id=None):
        # Function intro text.
        if status.prompt_intro:
            text = status.ps3 + "residue.delete("
            text = text + "res_id=" + repr(res_id) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(res_id, 'residue ID string')

        # Execute the functional code.
        delete_residue(res_id=res_id)

    # The function doc info.
    delete._doc_title = "Delete residues from the current data pipe."
    delete._doc_title_short = "Residue deletion."
    delete._doc_args = [
        ["res_id", "The residue ID string."]]
    delete._doc_desc = """
        This can be used to delete a single or sets of residues.  See the ID string documentation for more information.  If spin system/atom ids are included a RelaxError will be raised.
        """
    delete._doc_additional = [id_string_doc]
    _build_doc(delete)


    def display(self, res_id=None):
        # Function intro text.
        if status.prompt_intro:
            text = status.ps3 + "residue.display("
            text = text + "res_id=" + repr(res_id) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(res_id, 'residue ID string', can_be_none=True)

        # Execute the functional code.
        display_residue(res_id=res_id)

    # The function doc info.
    display._doc_title = "Display information about the residue(s)."
    display._doc_args = [
        ["res_id", "The residue ID string."]]
    display._doc_additional = [id_string_doc]
    _build_doc(display)


    def name(self, res_id=None, name=None, force=False):
        # Function intro text.
        if status.prompt_intro:
            text = status.ps3 + "residue.name("
            text = text + "res_id=" + repr(res_id)
            text = text + ", name=" + repr(name)
            text = text + ", force=" + repr(force) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(res_id, 'residue ID string')
        arg_check.is_str(name, 'new residue name')
        arg_check.is_bool(force, 'force flag')

        # Execute the functional code.
        name_residue(res_id=res_id, name=name, force=force)

    # The function doc info.
    name._doc_title = "Name the residues."
    name._doc_title_short = "Residue naming."
    name._doc_args = [
        ["res_id", "The residue ID string corresponding to one or more residues."],
        ["name", "The new name."],
        ["force", "A flag which if True will cause the residue to be renamed."]]
    name._doc_desc = """
        This simply allows residues to be named (or renamed).
        """
    name._doc_examples = """
        The following sequence of commands will rename the sequence {1 ALA, 2 GLY, 3 LYS} to {1 XXX,
        2 XXX, 3 XXX}:

        relax> residue.name(':1', 'XXX', force=True)
        relax> residue.name(':2', 'XXX', force=True)
        relax> residue.name(':3', 'XXX', force=True)

        Alternatively:

        relax> residue.name(':1,2,3', 'XXX', force=True)
        """
    name._doc_additional = [id_string_doc]
    _build_doc(name)


    def number(self, res_id=None, number=None, force=False):
        # Function intro text.
        if status.prompt_intro:
            text = status.ps3 + "residue.number("
            text = text + "res_id=" + repr(res_id)
            text = text + ", number=" + repr(number)
            text = text + ", force=" + repr(force) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(res_id, 'residue ID string')
        arg_check.is_int(number, 'new residue number')
        arg_check.is_bool(force, 'force flag')

        # Execute the functional code.
        number_residue(res_id=res_id, number=number, force=force)

    # The function doc info.
    number._doc_title = "Number the residues."
    number._doc_title_short = "Residue numbering."
    number._doc_args = [
        ["res_id", "The residue ID string corresponding to a single residue."],
        ["number", "The new residue number."],
        ["force", "A flag which if True will cause the residue to be renumbered."]]
    number._doc_desc = """
        This simply allows residues to be numbered.  The new number cannot correspond to an existing residue.
        """
    number._doc_examples = """
        The following sequence of commands will renumber the sequence {1 ALA, 2 GLY, 3 LYS} to
        {101 ALA, 102 GLY, 103 LYS}:

        relax> residue.number(':1', 101, force=True)
        relax> residue.number(':2', 102, force=True)
        relax> residue.number(':3', 103, force=True)
        """
    number._doc_additional = [id_string_doc]
    _build_doc(number)
