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

# Module docstring.
"""Module containing the 'molecule' user function class."""
__docformat__ = 'plaintext'

# Python module imports.
import sys

# relax module imports.
import help
from generic_fns.mol_res_spin import copy_molecule, create_molecule, delete_molecule, display_molecule, id_string_doc, name_molecule
from relax_errors import RelaxIntError, RelaxNoneStrError, RelaxStrError


class Molecule:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for manipulating the residue data."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def copy(self, pipe_from=None, mol_from=None, pipe_to=None, mol_to=None):
        """Function for copying all data associated with a molecule.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        pipe_from:  The data pipe containing the molecule from which the data will be copied.  This
            defaults to the current data pipe.

        mol_from:  The molecule identifier string of the molecule to copy the data from.

        pipe_to:  The data pipe to copy the data to.  This defaults to the current data pipe.

        mol_to:  The molecule identifier string of the molecule to copy the data to.


        Description
        ~~~~~~~~~~~

        This function will copy all the data associated with a molecule to a second molecule.  This
        includes residue and spin system information.  The new molecule must not yet exist.


        Examples
        ~~~~~~~~

        To copy the molecule data from the molecule 'GST' to the new molecule 'wt-GST', type:

        relax> molecule.copy('#GST', '#wt-GST')
        relax> molecule.copy(mol_from='#GST', mol_to='#wt-GST')


        To copy the molecule data of the molecule 'Ap4Aase' from the data pipe 'm1' to 'm2', assuming the current
        data pipe is 'm1', type:

        relax> molecule.copy(mol_from='#ApAase', pipe_to='m2')
        relax> molecule.copy(pipe_from='m1', mol_from='#ApAase', pipe_to='m2', mol_to='#ApAase')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "molecule.copy("
            text = text + "pipe_from=" + repr(pipe_from)
            text = text + ", mol_from=" + repr(mol_from)
            text = text + ", pipe_to=" + repr(pipe_to)
            text = text + ", mol_to=" + repr(mol_to) + ")"
            print(text)

        # The pipe_from argument.
        if pipe_from != None and type(pipe_from) != str:
            raise RelaxNoneStrError('data pipe from', pipe_from)

        # The molecule from argument.
        if type(mol_from) != str:
            raise RelaxStrError('molecule from', mol_from)

        # The pipe_to argument.
        if pipe_to != None and type(pipe_to) != str:
            raise RelaxNoneStrError('data pipe to', pipe_to)

        # The molecule to argument.
        if mol_to != None and type(mol_to) != str:
            raise RelaxNoneStrError('molecule to', mol_to)

        # Execute the functional code.
        copy_molecule(pipe_from=pipe_from, mol_from=mol_from, pipe_to=pipe_to, mol_to=mol_to)


    def create(self, mol_name=None):
        """Function for creating a new molecule.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        mol_name:  The name of the molecule.


        Description
        ~~~~~~~~~~~

        This function will add a new molecule data container to the relax data storage object.  The
        same molecule name cannot be used more than once.


        Examples
        ~~~~~~~~

        To create the molecules 'Ap4Aase', 'ATP', and 'MgF4', type:

        relax> molecule.create('Ap4Aase')
        relax> molecule.create('ATP')
        relax> molecule.create('MgF4')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "molecule.create("
            text = text + "mol_name=" + repr(mol_name) + ")"
            print(text)

        # Molecule name.
        if type(mol_name) != str:
            raise RelaxStrError('molecule name', mol_name)

        # Execute the functional code.
        create_molecule(mol_name=mol_name)


    def delete(self, mol_id=None):
        """Function for deleting molecules.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        mol_id:  The molecule identifier string.


        Description
        ~~~~~~~~~~~

        This function can be used to delete a single or sets of molecules.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "molecule.delete("
            text = text + "mol_id=" + repr(mol_id) + ")"
            print(text)

        # The molecule identifier argument.
        if type(mol_id) != str:
            raise RelaxStrError('molecule identifier', mol_id)

        # Execute the functional code.
        delete_molecule(mol_id=mol_id)


    def display(self, mol_id=None):
        """Function for displaying the molecule information.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        mol_id:  The molecule identifier string.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "molecule.display("
            text = text + "mol_id=" + repr(mol_id) + ")"
            print(text)

        # The molecule identifier argument.
        if mol_id != None and type(mol_id) != str:
            raise RelaxNoneStrError('molecule identifier', mol_id)

        # Execute the functional code.
        display_molecule(mol_id=mol_id)


    def name(self, mol_id=None, name=None, force=False):
        """Function for naming a molecule.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        mol_id:  The molecule identification string corresponding to one or more molecules.

        name:  The new molecule name.

        force:  A flag which if True will cause the molecule to be renamed.


        Description
        ~~~~~~~~~~~

        This function simply allows molecules to be named (or renamed).


        Examples
        ~~~~~~~~

        To rename the molecule 'Ap4Aase' to 'Inhib Ap4Aase', type one of:

        relax> molecule.name('#Ap4Aase', 'Inhib Ap4Aase', True)
        relax> molecule.name(mol_id='#Ap4Aase', name='Inhib Ap4Aase', force=True)

        This assumes the molecule 'Ap4Aase' already exists.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "molecule.name("
            text = text + "mol_id=" + repr(mol_id)
            text = text + ", name=" + repr(name)
            text = text + ", force=" + repr(force) + ")"
            print(text)

        # Residue identification string.
        if mol_id != None and type(mol_id) != str:
            raise RelaxNoneStrError('molecule identification string', mol_id)

        # New molecule name.
        if type(name) != str:
            raise RelaxStrError('new molecule name', name)

        # The force flag.
        if type(force) != bool:
            raise RelaxBoolError('force flag', force)

        # Execute the functional code.
        name_molecule(mol_id=mol_id, name=name, force=force)



    # Docstring modification.
    #########################

    # Add the residue identification string description.
    copy.__doc__ = copy.__doc__ + "\n\n" + id_string_doc + "\n"
    delete.__doc__ = delete.__doc__ + "\n\n" + id_string_doc + "\n"
    display.__doc__ = display.__doc__ + "\n\n" + id_string_doc + "\n"
    name.__doc__ = name.__doc__ + "\n\n" + id_string_doc + "\n"
