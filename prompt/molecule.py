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

# relax module imports.
import help
from generic_fns import molecule
from relax_errors import RelaxBinError, RelaxIntError, RelaxNoneStrError, RelaxStrError


class Molecule:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for manipulating the residue data."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


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
            text = text + "mol_name=" + `mol_name` + ")"
            print text

        # Molecule name.
        if type(mol_name) != str:
            raise RelaxStrError, ('molecule name', mol_name)

        # Execute the functional code.
        molecule.create(mol_name=mol_name)


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
            text = text + "pipe_from=" + `pipe_from`
            text = text + "mol_from=" + `mol_from`
            text = text + "pipe_to=" + `pipe_to`
            text = text + ", mol_to=" + `mol_to` + ")"
            print text

        # The pipe_from argument.
        if type(pipe_from) != str:
            raise RelaxStrError, ('data pipe from', pipe_from)

        # The molecule from argument.
        if type(mol_from) != str:
            raise RelaxStrError, ('molecule from', mol_from)

        # The pipe_to argument.
        if type(pipe_to) != str:
            raise RelaxStrError, ('data pipe to', pipe_to)

        # The molecule to argument.
        if type(mol_to) != str:
            raise RelaxStrError, ('molecule to', mol_to)

        # Execute the functional code.
        molecule.copy(pipe_from=pipe_from, mol_from=mol_from, pipe_to=pipe_to, mol_to=mol_to)


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
            text = text + "mol_id=" + `mol_id` + ")"
            print text

        # The molecule identifier argument.
        if type(mol_id) != str:
            raise RelaxStrError, ('molecule identifier', mol_id)

        # Execute the functional code.
        molecule.delete(mol_id=mol_id)


    def display(self, mol_id=None):
        """Function for displaying the molecule information.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        mol_id:  The molecule identifier string.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "molecule.display("
            text = text + "mol_id=" + `mol_id` + ")"
            print text

        # The molecule identifier argument.
        if type(mol_id) != str:
            raise RelaxStrError, ('molecule identifier', mol_id)

        # Execute the functional code.
        molecule.display(mol_id=mol_id)
