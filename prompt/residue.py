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
from generic_fns.mol_res_spin import copy_residue, create_residue, delete_residue, display_residue, id_string_doc, name_residue, number_residue
from relax_errors import RelaxIntError, RelaxNoneStrError, RelaxStrError


class Residue:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for manipulating the residue data."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def copy(self, pipe_from=None, res_from=None, pipe_to=None, res_to=None):
        """Function for copying all data associated with a residue.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        pipe_from:  The data pipe containing the residue from which the data will be copied.  This
            defaults to the current data pipe.

        res_from:  The residue identifier string of the residue to copy the data from.

        pipe_to:  The data pipe to copy the data to.  This defaults to the current data pipe.

        res_to:  The residue identifier string of the residue to copy the data to.


        Description
        ~~~~~~~~~~~

        This function will copy all the data associated with the identified residue to the new,
        non-existent residue.  The new residue must not already exist.


        Examples
        ~~~~~~~~

        To copy the residue data from residue 1 to the new residue 2, type:

        relax> residue.copy(res_from=':1', res_to=':2')


        To copy residue 1 of the molecule 'Old mol' to residue 5 of the molecule 'New mol', type:

        relax> residue.copy(res_from='#Old mol:1', res_to='#New mol:5')


        To copy the residue data of residue 1 from the data pipe 'm1' to 'm2', assuming the current
        data pipe is 'm1', type:

        relax> residue.copy(res_from=':1', pipe_to='m2')
        relax> residue.copy(pipe_from='m1', res_from=':1', pipe_to='m2', res_to=':1')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "residue.copy("
            text = text + "pipe_from=" + `pipe_from`
            text = text + ", res_from=" + `res_from`
            text = text + ", pipe_to=" + `pipe_to`
            text = text + ", res_to=" + `res_to` + ")"
            print text

        # The data pipe from argument.
        if pipe_from != None and type(pipe_from) != str:
            raise RelaxNoneStrError, ('data pipe from', pipe_from)

        # The residue from argument.
        if type(res_from) != str:
            raise RelaxStrError, ('residue from', res_from)

        # The data pipe to argument.
        if pipe_to != None and type(pipe_to) != str:
            raise RelaxNoneStrError, ('data pipe to', pipe_to)

        # The residue to argument.
        if res_to != None and type(res_to) != str:
            raise RelaxNoneStrError, ('residue to', res_to)

        # Execute the functional code.
        copy_residue(pipe_from=pipe_from, res_from=res_from, pipe_to=pipe_to, res_to=res_to)


    def create(self, res_num=None, res_name=None, mol_id=None):
        """Function for creating a new residue.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        res_num:  The residue number.

        res_name:  The name of the residue.

        mol_id:  The ID string for selecting the molecule to add the residue to.


        Description
        ~~~~~~~~~~~

        Using this function a new sequence can be generated without using the sequence user
        functions.  However if the sequence already exists, the new residue will be added to the end
        of the residue list (the residue numbers of this list need not be sequential).  The same
        residue number cannot be used more than once.  A corresponding single spin system will be
        created for this residue.  The spin system number and name or additional spin systems can be
        added later if desired.


        Examples
        ~~~~~~~~

        The following sequence of commands will generate the sequence 1 ALA, 2 GLY, 3 LYS:

        relax> residue.create(1, 'ALA')
        relax> residue.create(2, 'GLY')
        relax> residue.create(3, 'LYS')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "residue.create("
            text = text + "res_num=" + `res_num`
            text = text + ", res_name=" + `res_name`
            text = text + ", mol_id=" + `mol_id` + ")"
            print text

        # Residue number.
        if type(res_num) != int:
            raise RelaxIntError, ('residue number', res_num)

        # Residue name.
        if type(res_name) != str:
            raise RelaxStrError, ('residue name', res_name)

        # The molecule ID.
        if mol_id != None and type(mol_id) != str:
            raise RelaxNoneStrError, ('molecule identification string', mol_id)

        # Execute the functional code.
        create_residue(res_num=res_num, res_name=res_name, mol_id=mol_id)


    def delete(self, res_id=None):
        """Function for deleting residues.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        res_id:  The residue identifier string.


        Description
        ~~~~~~~~~~~

        This function can be used to delete a single or sets of residues.  See the identification
        string documentation below for more information.  If spin system/atom ids are included a
        RelaxError will be raised.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "residue.delete("
            text = text + "res_id=" + `res_id` + ")"
            print text

        # The residue identifier argument.
        if type(res_id) != str:
            raise RelaxStrError, ('residue identifier', res_id)

        # Execute the functional code.
        delete_residue(res_id=res_id)


    def display(self, res_id=None):
        """Function for displaying information about the residue(s).

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        res_id:  The residue identification string.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "residue.display("
            text = text + "res_id=" + `res_id` + ")"
            print text

        # The res_id argument.
        if res_id != None and type(res_id) != str:
            raise RelaxNoneStrError, ('residue identification string', res_id)

        # Execute the functional code.
        display_residue(res_id=res_id)


    def rename(self, res_id=None, new_name=None):
        """Function for renaming an existent residue(s).

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        res_id:  The residue identification string corresponding to one or more residues.

        new_name:  The new name.


        Description
        ~~~~~~~~~~~

        This function simply allows residues to be renamed.


        Examples
        ~~~~~~~~

        The following sequence of commands will rename the sequence {1 ALA, 2 GLY, 3 LYS} to {1 XXX,
        2 XXX, 3 XXX}:

        relax> residue.rename(':1', 'XXX')
        relax> residue.rename(':2', 'XXX')
        relax> residue.rename(':3', 'XXX')

        Alternatively:

        relax> residue.rename(':1,2,3', 'XXX')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "residue.rename("
            text = text + "res_id=" + `res_id`
            text = text + ", new_name=" + `new_name` + ")"
            print text

        # Residue identification string.
        if type(res_id) != str:
            raise RelaxStrError, ('residue identification string', res_id)

        # New residue name.
        if type(new_name) != str:
            raise RelaxStrError, ('new residue name', new_name)

        # Execute the functional code.
        rename_residue(res_id=res_id, new_name=new_name)


    def renumber(self, res_id=None, new_number=None):
        """Function for renumbering an existent residue.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        res_id:  The residue identification string corresponding to a single residue.

        new_number:  The new residue number.


        Description
        ~~~~~~~~~~~

        This function simply allows residues to be renumbered.  The new number cannot correspond to
        an existing residue.


        Examples
        ~~~~~~~~

        The following sequence of commands will renumber the sequence {1 ALA, 2 GLY, 3 LYS} to
        {101 ALA, 102 GLY, 103 LYS}:

        relax> residue.renumber(':1', 101)
        relax> residue.renumber(':2', 102)
        relax> residue.renumber(':3', 103)
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "residue.renumber("
            text = text + "res_id=" + `res_id`
            text = text + ", new_number=" + `new_number` + ")"
            print text

        # Residue identification string.
        if type(res_id) != str:
            raise RelaxStrError, ('residue identification string', res_id)

        # New residue number.
        if type(new_number) != int:
            raise RelaxIntError, ('new residue number', new_number)

        # Execute the functional code.
        renumber_residue(res_id=res_id, new_number=new_number)



    # Docstring modification.
    #########################

    # Add the residue identification string description.
    copy.__doc__ = copy.__doc__ + "\n\n" + id_string_doc + "\n"
    delete.__doc__ = delete.__doc__ + "\n\n" + id_string_doc + "\n"
    display.__doc__ = display.__doc__ + "\n\n" + id_string_doc + "\n"
    rename.__doc__ = rename.__doc__ + "\n\n" + id_string_doc + "\n"
    renumber.__doc__ = renumber.__doc__ + "\n\n" + id_string_doc + "\n"
