###############################################################################
#                                                                             #
# Copyright (C) 2007-2011 Edward d'Auvergne                                   #
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
"""Module containing the 'molecule' user function class."""
__docformat__ = 'plaintext'

# relax module imports.
from base_class import User_fn_class, _build_doc
import arg_check
from generic_fns.mol_res_spin import ALLOWED_MOL_TYPES, copy_molecule, create_molecule, delete_molecule, display_molecule, id_string_doc, name_molecule, type_molecule


class Molecule(User_fn_class):
    """Class for manipulating the molecule data."""

    def copy(self, pipe_from=None, mol_from=None, pipe_to=None, mol_to=None):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "molecule.copy("
            text = text + "pipe_from=" + repr(pipe_from)
            text = text + ", mol_from=" + repr(mol_from)
            text = text + ", pipe_to=" + repr(pipe_to)
            text = text + ", mol_to=" + repr(mol_to) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(pipe_from, 'pipe from', can_be_none=True)
        arg_check.is_str(mol_from, 'molecule from')
        arg_check.is_str(pipe_to, 'pipe to', can_be_none=True)
        arg_check.is_str(mol_to, 'molecule to', can_be_none=True)

        # Execute the functional code.
        copy_molecule(pipe_from=pipe_from, mol_from=mol_from, pipe_to=pipe_to, mol_to=mol_to)

    # The function doc info.
    copy._doc_title = "Copy all data associated with a molecule."
    copy._doc_title_short = "Molecule copying."
    copy._doc_args = [
        ["pipe_from", "The data pipe containing the molecule from which the data will be copied.  This defaults to the current data pipe."],
        ["mol_from", "The name of the molecule from which to copy data from."],
        ["pipe_to", "The data pipe to copy the data to.  This defaults to the current data pipe."],
        ["mol_to", "The name of the new molecule.  If left blank, the new molecule will have the same name as the old."]]
    copy._doc_desc = """
        This will copy all the data associated with a molecule to a second molecule.  This includes all residue and spin system information.  The new molecule name must be unique in the destination data pipe.
        """
    copy._doc_examples = """
        To copy the molecule data from the molecule 'GST' to the new molecule 'wt-GST', type:

        relax> molecule.copy('#GST', '#wt-GST')
        relax> molecule.copy(mol_from='#GST', mol_to='#wt-GST')


        To copy the molecule data of the molecule 'Ap4Aase' from the data pipe 'm1' to 'm2', assuming the current
        data pipe is 'm1', type:

        relax> molecule.copy(mol_from='#ApAase', pipe_to='m2')
        relax> molecule.copy(pipe_from='m1', mol_from='#ApAase', pipe_to='m2', mol_to='#ApAase')
        """
    _build_doc(copy)


    def create(self, mol_name=None, mol_type=None):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "molecule.create("
            text = text + "mol_name=" + repr(mol_name)
            text = text + ", mol_type=" + repr(mol_type) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(mol_name, 'molecule name')
        arg_check.is_str(mol_type, 'molecule type', can_be_none=True)

        # Execute the functional code.
        create_molecule(mol_name=mol_name, mol_type=mol_type)

    # The function doc info.
    create._doc_title = "Create a new molecule."
    create._doc_title_short = "Molecule creation."
    create._doc_args = [
        ["mol_name", "The name of the new molecule."],
        ["mol_type", "The type of molecule."]]
    create._doc_desc = """
        This adds a new molecule data container to the relax data storage object.  The same molecule name cannot be used more than once.  The molecule type need not be specified.  However, if given, it should be one of"""
    for _i in range(len(ALLOWED_MOL_TYPES)):
        create._doc_desc = "%s '%s'," % (create._doc_desc, ALLOWED_MOL_TYPES[_i]) 
    create._doc_desc = "%s or '%s'." % (create._doc_desc, ALLOWED_MOL_TYPES[-1]) 
    create._doc_examples = """
        To create the molecules 'Ap4Aase', 'ATP', and 'MgF4', type:

        relax> molecule.create('Ap4Aase')
        relax> molecule.create('ATP')
        relax> molecule.create('MgF4')
        """
    _build_doc(create)


    def delete(self, mol_id=None):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "molecule.delete("
            text = text + "mol_id=" + repr(mol_id) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(mol_id, 'molecule ID string')

        # Execute the functional code.
        delete_molecule(mol_id=mol_id)

    # The function doc info.
    delete._doc_title = "Deleting molecules from the relax data store."
    delete._doc_title_short = "Molecule deletion."
    delete._doc_args = [
        ["mol_id", "The molecule ID string."]]
    delete._doc_desc = """
        This can be used to delete a single or sets of molecules from the relax data store.  The molecule will be deleted from the current data pipe.
        """
    delete._doc_additional = [id_string_doc]
    _build_doc(delete)


    def display(self, mol_id=None):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "molecule.display("
            text = text + "mol_id=" + repr(mol_id) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(mol_id, 'molecule ID string', can_be_none=True)

        # Execute the functional code.
        display_molecule(mol_id=mol_id)

    # The function doc info.
    display._doc_title = "Display the molecule information."
    display._doc_title_short = "Molecule information."
    display._doc_args = [
        ["mol_id", "The molecule ID string."]]
    display._doc_additional = [id_string_doc]
    _build_doc(display)


    def name(self, mol_id=None, name=None, force=False):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "molecule.name("
            text = text + "mol_id=" + repr(mol_id)
            text = text + ", name=" + repr(name)
            text = text + ", force=" + repr(force) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(mol_id, 'molecule ID string', can_be_none=True)
        arg_check.is_str(name, 'new molecule name')
        arg_check.is_bool(force, 'force flag')

        # Execute the functional code.
        name_molecule(mol_id=mol_id, name=name, force=force)

    # The function doc info.
    name._doc_title = "Name a molecule."
    name._doc_args = [
        ["mol_id", "The molecule ID string corresponding to one or more molecules."],
        ["name", "The new molecule name."],
        ["force", "A flag which if True will cause the molecule to be renamed."]]
    name._doc_desc = """
        This simply allows molecules to be named (or renamed).
        """
    name._doc_examples = """
        To rename the molecule 'Ap4Aase' to 'Inhib Ap4Aase', type one of:

        relax> molecule.name('#Ap4Aase', 'Inhib Ap4Aase', True)
        relax> molecule.name(mol_id='#Ap4Aase', name='Inhib Ap4Aase', force=True)

        This assumes the molecule 'Ap4Aase' already exists.
        """
    name._doc_additional = [id_string_doc]
    _build_doc(name)


    def type(self, mol_id=None, type=None, force=False):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "molecule.type("
            text = text + "mol_id=" + repr(mol_id)
            text = text + ", type=" + repr(type)
            text = text + ", force=" + repr(force) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(mol_id, 'molecule ID string', can_be_none=True)
        arg_check.is_str(type, 'molecule type')
        arg_check.is_bool(force, 'force flag')

        # Execute the functional code.
        type_molecule(mol_id=mol_id, type=type, force=force)

    # The function doc info.
    type._doc_title = "Set the molecule type."
    type._doc_title_short = "Setting molecule type."
    type._doc_args = [
        ["mol_id", "The molecule ID string corresponding to one or more molecules."],
        ["type", "The molecule type."],
        ["force", "A flag which if True will cause the molecule to type to be overwritten."]]
    type._doc_desc = """
        This allows the type of the molecule to be specified.  It can be one of:

        """
    for _i in range(len(ALLOWED_MOL_TYPES)):
        type._doc_desc = "%s            '%s',\n" % (type._doc_desc, ALLOWED_MOL_TYPES[_i]) 
    type._doc_desc = "%s            '%s'.\n" % (type._doc_desc, ALLOWED_MOL_TYPES[-1]) 
    type._doc_examples = """
        To set the molecule 'Ap4Aase' to the 'protein' type, type one of:

        relax> molecule.type('#Ap4Aase', 'protein', True)
        relax> molecule.type(mol_id='#Ap4Aase', type='protein', force=True)
        """
    type._doc_additional = [id_string_doc]
    _build_doc(type)
