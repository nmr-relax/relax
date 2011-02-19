###############################################################################
#                                                                             #
# Copyright (C) 2007-2010 Edward d'Auvergne                                   #
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
"""Module containing the 'spin' user function class."""
__docformat__ = 'plaintext'

# relax module imports.
from base_class import User_fn_class
import arg_check
from generic_fns.mol_res_spin import copy_spin, create_pseudo_spin, create_spin, delete_spin, display_spin, id_string_doc, name_spin, number_spin, set_spin_element


class Spin(User_fn_class):
    """Class for manipulating the spin data."""

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
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "spin.copy("
            text = text + "pipe_from=" + repr(pipe_from)
            text = text + ", spin_from=" + repr(spin_from)
            text = text + ", pipe_to=" + repr(pipe_to)
            text = text + ", spin_to=" + repr(spin_to) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(pipe_from, 'pipe from', can_be_none=True)
        arg_check.is_str(spin_from, 'spin from')
        arg_check.is_str(pipe_to, 'pipe to', can_be_none=True)
        arg_check.is_str(spin_to, 'spin to', can_be_none=True)

        # Execute the functional code.
        copy_spin(pipe_from=pipe_from, spin_from=spin_from, pipe_to=pipe_to, spin_to=spin_to)


    def create(self, spin_num=None, spin_name=None, res_num=None, res_name=None, mol_name=None):
        """Function for creating a new spin.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        spin_num:  The spin number.

        spin_name:  The name of the spin.

        res_num:  The number of the residue to add the spin to.

        res_name:  The name of the residue to add the spin to.

        mol_name:  The name of the molecule to add the spin to.


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
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "spin.create("
            text = text + "spin_num=" + repr(spin_num)
            text = text + ", spin_name=" + repr(spin_name)
            text = text + ", res_num=" + repr(res_num)
            text = text + ", res_name=" + repr(res_name)
            text = text + ", mol_name=" + repr(mol_name) + ")"
            print(text)

        # The argument checks.
        arg_check.is_int(spin_num, 'spin number', can_be_none=True)
        arg_check.is_str(spin_name, 'spin name', can_be_none=True)
        arg_check.is_int(res_num, 'residue number', can_be_none=True)
        arg_check.is_str(res_name, 'residue name', can_be_none=True)
        arg_check.is_str(mol_name, 'molecule name', can_be_none=True)

        # Execute the functional code.
        create_spin(spin_num=spin_num, spin_name=spin_name, res_num=res_num, res_name=res_name, mol_name=mol_name)


    def create_pseudo(self, spin_name=None, spin_num=None, res_id=None, members=None, averaging='linear'):
        """Function for creating a spin system representing a pseudo-atom.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        spin_name:  The name of the pseudo-atom spin.

        spin_num:  The spin number.

        res_id:  The molecule and residue ID string identifying the position to add the pseudo-spin
            to.

        mol_id:  The molecule ID string identifying the molecule to add the pseudo-spin to.

        members:  A list of the atoms the pseudo-atom is composed of.

        averaging:  The positional averaging technique.


        Description
        ~~~~~~~~~~~

        This function will create a spin data container representing a number of pre-existing spin
        containers as a pseudo-atom.  The optional spin number must not already exist.


        Examples
        ~~~~~~~~

        The following will create the pseudo-atom named 'Q9' consisting of the protons '@H16',
        '@H17', '@H18':

        relax> spin.create_pseudo('Q9', members=['@H16', '@H17', '@H18'])
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "spin.create_pseudo("
            text = text + "spin_name=" + repr(spin_name)
            text = text + ", spin_num=" + repr(spin_num)
            text = text + ", res_id=" + repr(res_id)
            text = text + ", members=" + repr(members)
            text = text + ", averaging=" + repr(averaging) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(spin_name, 'spin name')
        arg_check.is_int(spin_num, 'spin number', can_be_none=True)
        arg_check.is_str(res_id, 'residue identification string', can_be_none=True)
        arg_check.is_str_list(members, 'members')
        arg_check.is_str(averaging, 'positional averaging technique')

        # Execute the functional code.
        create_pseudo_spin(spin_num=spin_num, spin_name=spin_name, res_id=res_id, members=members, averaging=averaging)


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
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "spin.delete("
            text = text + "spin_id=" + repr(spin_id) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(spin_id, 'spin identification string')

        # Execute the functional code.
        delete_spin(spin_id=spin_id)


    def display(self, spin_id=None):
        """Function for displaying information about the spin(s).

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        spin_id:  The spin identification string.
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "spin.display("
            text = text + "spin_id=" + repr(spin_id) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(spin_id, 'spin identification string', can_be_none=True)

        # Execute the functional code.
        display_spin(spin_id=spin_id)


    def element(self, spin_id=None, element=None, force=False):
        """Set the element type of the spin.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        spin_id:  The spin identification string corresponding to one or more spins.

        element:  The IUPAC element name.

        force:  A flag which if True will cause the element to be changed.


        Description
        ~~~~~~~~~~~

        This function allows the element type of the spins to be set.


        Examples
        ~~~~~~~~

        The set all spins of residue 1 to be carbons, type one of:

        relax> spin.element('@1', 'C', force=True)
        relax> spin.element(spin_id='@1', element='C', force=True)
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "spin.element("
            text = text + "spin_id=" + repr(spin_id)
            text = text + ", element=" + repr(element)
            text = text + ", force=" + repr(force) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(spin_id, 'spin identification string', can_be_none=True)
        arg_check.is_str(element, 'IUPAC element name')
        arg_check.is_bool(force, 'force flag')

        # Execute the functional code.
        set_spin_element(spin_id=spin_id, element=element, force=force)


    def name(self, spin_id=None, name=None, force=False):
        """Function for naming spins.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        spin_id:  The spin identification string corresponding to one or more spins.

        name:  The new name.

        force:  A flag which if True will cause the spin to be renamed.


        Description
        ~~~~~~~~~~~

        This function simply allows spins to be named (or renamed).


        Examples
        ~~~~~~~~

        The following sequence of commands will rename the sequence {1 C1, 2 C2, 3 C3} to {1 C11,
        2 C12, 3 C13}:

        relax> spin.name('@1', 'C11', force=True)
        relax> spin.name('@2', 'C12', force=True)
        relax> spin.name('@3', 'C13', force=True)
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "spin.name("
            text = text + "spin_id=" + repr(spin_id)
            text = text + ", name=" + repr(name)
            text = text + ", force=" + repr(force) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(spin_id, 'spin identification string', can_be_none=True)
        arg_check.is_str(name, 'new spin name')
        arg_check.is_bool(force, 'force flag')

        # Execute the functional code.
        name_spin(spin_id=spin_id, name=name, force=force)


    def number(self, spin_id=None, number=None, force=False):
        """Function for numbering spins.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        spin_id:  The spin identification string corresponding to a single spin.

        number:  The new spin number.

        force:  A flag which if True will cause the spin to be renumbered.


        Description
        ~~~~~~~~~~~

        This function simply allows spins to be numbered.  The new number cannot correspond to
        an existing spin number.


        Examples
        ~~~~~~~~

        The following sequence of commands will renumber the sequence {1 C1, 2 C2, 3 C3} to
        {-1 C1, -2 C2, -3 C3}:

        relax> spin.number('@1', -1, force=True)
        relax> spin.number('@2', -2, force=True)
        relax> spin.number('@3', -3, force=True)

        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "spin.number("
            text = text + "spin_id=" + repr(spin_id)
            text = text + ", number=" + repr(number)
            text = text + ", force=" + repr(force) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(spin_id, 'spin identification string', can_be_none=True)
        arg_check.is_int(number, 'new spin number', can_be_none=True)
        arg_check.is_bool(force, 'force flag')

        # Execute the functional code.
        number_spin(spin_id=spin_id, number=number, force=force)



    # Docstring modification.
    #########################

    # Add the identification string description.
    copy.__doc__ = copy.__doc__ + "\n\n" + id_string_doc + "\n"
    create.__doc__ = create.__doc__ + "\n\n" + id_string_doc + "\n"
    delete.__doc__ = delete.__doc__ + "\n\n" + id_string_doc + "\n"
    display.__doc__ = display.__doc__ + "\n\n" + id_string_doc + "\n"
    name.__doc__ = name.__doc__ + "\n\n" + id_string_doc + "\n"
    number.__doc__ = number.__doc__ + "\n\n" + id_string_doc + "\n"
