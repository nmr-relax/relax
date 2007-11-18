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
from generic_fns import residue
from generic_fns.selection import id_string_doc
from relax_errors import RelaxIntError, RelaxStrError


class Spin:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for manipulating the spin data."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def copy(self, pipe_from=None, spin_from=None, pipe_to=None, spin_to=None):
        """Function for copying all data associated with a spin.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        pipe_from:  The data pipe containing the spin from which the data will be copied.  This
            defaults to the current data pipe.

        spin_from:  The spin identifier string of the spin to copy the data from.

        pipe_to:  The data pipe to copy the data to.  This defaults to the current data pipe.

        spin_to:  The spin identifier string of the spin to copy the data to.


        Description
        ~~~~~~~~~~~

        This function will copy all the data associated with the identified spin to the new,
        non-existent spin.  The new spin must not already exist.


        Examples
        ~~~~~~~~

        To copy the spin data from spin 1 to the new spin 2, type:

        relax> spin.copy(spin_from='@1', spin_to='@2')


        To copy spin 1 of the molecule 'Old mol' to spin 5 of the molecule 'New mol', type:

        relax> spin.copy(spin_from='#Old mol@1', spin_to='#New mol@5')


        To copy the spin data of spin 1 from the data pipe 'm1' to 'm2', assuming the current
        data pipe is 'm1', type:

        relax> spin.copy(spin_from='@1', pipe_to='m2')
        relax> spin.copy(pipe_from='m1', spin_from='@1', pipe_to='m2', spin_to='@1')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "spin.copy("
            text = text + "pipe_from=" + `pipe_from`
            text = text + "spin_from=" + `spin_from`
            text = text + "pipe_to=" + `pipe_to`
            text = text + ", spin_to=" + `spin_to` + ")"
            print text

        # The data pipe from argument.
        if type(pipe_from) != str:
            raise RelaxStrError, ('data pipe from', pipe_from)

        # The spin from argument.
        if type(spin_from) != str:
            raise RelaxStrError, ('spin from', spin_from)

        # The data pipe to argument.
        if type(pipe_to) != str:
            raise RelaxStrError, ('data pipe to', pipe_to)

        # The spin to argument.
        if type(spin_to) != str:
            raise RelaxStrError, ('spin to', spin_to)

        # Execute the functional code.
        spin.copy(pipe_from=pipe_from, spin_from=spin_from, pipe_to=pipe_to, spin_to=spin_to)


    def create(self, spin_num=None, spin_name=None, res_id=None):
        """Function for creating a new spin.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        spin_num:  The spin number.

        spin_name:  The name of the spin.

        res_id:  The residue ID string identifying the residue to add the spin to.


        Description
        ~~~~~~~~~~~

        This function will add a new spin data container to the relax data storage object.  The same
        spin number cannot be used more than once.


        Examples
        ~~~~~~~~

        The following sequence of commands will generate the sequence 1 C4, 2 C9, 3 C15:

        relax> spin.create(1, 'C4')
        relax> spin.create(2, 'C9')
        relax> spin.create(3, 'C15')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "spin.create("
            text = text + ", spin_num=" + `spin_num`
            text = text + ", spin_name=" + `spin_name`
            text = text + ", res_id=" + `res_id` + ")"
            print text

        # Spin number.
        if type(spin_num) != int:
            raise RelaxIntError, ('spin number', spin_num)

        # Spin name.
        if type(spin_name) != str:
            raise RelaxStrError, ('spin name', spin_name)

        # The residue ID.
        if type(res_id) != str:
            raise RelaxStrError, ('residue identification string', res_id)

        # Execute the functional code.
        spin.create(spin_num=spin_num, spin_name=spin_name, res_id=res_id)


    def delete(self, spin_id=None):
        """Function for deleting spins.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        spin_id:  The spin identifier string.


        Description
        ~~~~~~~~~~~

        This function can be used to delete a single or sets of spins.  See the identification
        string documentation below for more information.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "spin.delete("
            text = text + "spin_id=" + `spin_id` + ")"
            print text

        # The spin identifier argument.
        if type(spin_id) != str:
            raise RelaxStrError, ('spin identifier', spin_id)

        # Execute the functional code.
        spin.delete(spin_id=spin_id)


    def display(self, spin_id=None):
        """Function for displaying information about the spin(s).

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        spin_id:  The spin identification string.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "spin.display("
            text = text + "spin_id=" + `spin_id` + ")"
            print text

        # The spin_id argument.
        if type(spin_id) != str:
            raise RelaxStrError, ('spin identification string', spin_id)

        # Execute the functional code.
        spin.display(spin_id=spin_id)


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
            text = text + ", res_id=" + `res_id`
            text = text + ", new_name=" + `new_name` + ")"
            print text

        # Residue identification string.
        if type(res_id) != int:
            raise RelaxIntError, ('residue identification string', res_id)

        # New residue name.
        if type(new_name) != str:
            raise RelaxStrError, ('new residue name', new_name)

        # Execute the functional code.
        residue.create(res_num=res_num, new_name=new_name)


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
            text = text + ", res_id=" + `res_id`
            text = text + ", new_number=" + `new_number` + ")"
            print text

        # Residue identification string.
        if type(res_id) != int:
            raise RelaxIntError, ('residue identification string', res_id)

        # New residue number.
        if type(new_number) != str:
            raise RelaxStrError, ('new residue number', new_number)

        # Execute the functional code.
        residue.create(res_num=res_num, new_number=new_number)



    # Docstring modification.
    #########################

    # Add the residue identification string description.
    copy.__doc__ = copy.__doc__ + "\n\n" + id_string_doc + "\n"
    delete.__doc__ = delete.__doc__ + "\n\n" + id_string_doc + "\n"
    display.__doc__ = display.__doc__ + "\n\n" + id_string_doc + "\n"
    rename.__doc__ = rename.__doc__ + "\n\n" + id_string_doc + "\n"
    renumber.__doc__ = renumber.__doc__ + "\n\n" + id_string_doc + "\n"
