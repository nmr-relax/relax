###############################################################################
#                                                                             #
# Copyright (C) 2012-2013 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""Module for the manipulation of the interatomic data structures in the relax data store."""

# Python module imports.
from copy import deepcopy
from re import search
import sys

# relax module imports.
from generic_fns import pipes
from generic_fns.mol_res_spin import Selection, count_spins, return_spin, spin_loop
from lib.errors import RelaxError, RelaxInteratomError, RelaxInteratomInconsistentError, RelaxNoInteratomError, RelaxNoSpinError
from relax_io import write_data


def copy(pipe_from=None, pipe_to=None, spin_id1=None, spin_id2=None, verbose=True):
    """Copy the interatomic data from one data pipe to another.

    @keyword pipe_from:         The data pipe to copy the interatomic data from.  This defaults to the current data pipe.
    @type pipe_from:            str
    @keyword pipe_to:           The data pipe to copy the interatomic data to.  This defaults to the current data pipe.
    @type pipe_to:              str
    @keyword spin_id1:          The spin ID string of the first atom.
    @type spin_id1:             str
    @keyword spin_id2:          The spin ID string of the second atom.
    @type spin_id2:             str
    @keyword verbose:           A flag which if True will cause info about each spin pair to be printed out.
    @type verbose:              bool
    """

    # Defaults.
    if pipe_from == None and pipe_to == None:
        raise RelaxError("The pipe_from and pipe_to arguments cannot both be set to None.")
    elif pipe_from == None:
        pipe_from = pipes.cdp_name()
    elif pipe_to == None:
        pipe_to = pipes.cdp_name()

    # Test if the pipe_from and pipe_to data pipes exist.
    pipes.test(pipe_from)
    pipes.test(pipe_to)

    # Check that the spin IDs exist.
    if spin_id1:
        if count_spins(selection=spin_id1, pipe=pipe_from, skip_desel=False) == 0:
            raise RelaxNoSpinError(spin_id1, pipe_from)
        if count_spins(selection=spin_id1, pipe=pipe_to, skip_desel=False) == 0:
            raise RelaxNoSpinError(spin_id1, pipe_to)
    if spin_id2:
        if count_spins(selection=spin_id2, pipe=pipe_from, skip_desel=False) == 0:
            raise RelaxNoSpinError(spin_id2, pipe_from)
        if count_spins(selection=spin_id2, pipe=pipe_to, skip_desel=False) == 0:
            raise RelaxNoSpinError(spin_id2, pipe_to)

    # Check for the sequence data in the target pipe if no spin IDs are given.
    if not spin_id1 and not spin_id2:
        for spin, spin_id in spin_loop(pipe=pipe_from, return_id=True):
            if not return_spin(spin_id, pipe=pipe_to):
                raise RelaxNoSpinError(spin_id, pipe_to)

    # Test if pipe_from contains interatomic data (skipping the rest of the function if it is missing).
    if not exists_data(pipe_from):
        return

    # Loop over the interatomic data of the pipe_from data pipe.
    ids = []
    for interatom in interatomic_loop(selection1=spin_id1, selection2=spin_id2, pipe=pipe_from):
        # Create a new container.
        new_interatom = create_interatom(spin_id1=interatom.spin_id1, spin_id2=interatom.spin_id2, pipe=pipe_to)

        # Duplicate all the objects of the container.
        for name in dir(interatom):
            # Skip special objects.
            if search('^_', name):
                continue

            # Skip the spin IDs.
            if name in ['spin_id1', 'spin_id2']:
                continue

            # Skip class methods.
            if name in list(interatom.__class__.__dict__.keys()):
                continue

            # Duplicate all other objects.
            obj = deepcopy(getattr(interatom, name))
            setattr(new_interatom, name, obj)

        # Store the IDs for the printout.
        ids.append([repr(interatom.spin_id1), repr(interatom.spin_id2)])

    # Print out.
    if verbose:
        write_data(out=sys.stdout, headings=["Spin_ID_1", "Spin_ID_2"], data=ids)


def consistent_interatomic_data(pipe1=None, pipe2=None):
    """Check that the interatomic data is consistent between two data pipes.

    @keyword pipe1:     The name of the first data pipe to compare.
    @type pipe1:        str
    @keyword pipe2:     The name of the second data pipe to compare.
    @type pipe2:        str
    @raises RelaxError: If the data is inconsistent.
    """

    # Get the data pipes.
    dp1 = pipes.get_pipe(pipe1)
    dp2 = pipes.get_pipe(pipe2)

    # Check the data lengths.
    if len(dp1.interatomic) != len(dp2.interatomic):
        raise RelaxInteratomInconsistentError(pipe1, pipe2)

    # Loop over the interatomic data.
    for i in range(len(dp1.interatomic)):
        # Alias the containers.
        interatom1 = dp1.interatomic[i]
        interatom2 = dp2.interatomic[i]

        # Check the spin IDs.
        if interatom1.spin_id1 != interatom2.spin_id1:
            raise RelaxInteratomInconsistentError(pipe1, pipe2)
        if interatom1.spin_id2 != interatom2.spin_id2:
            raise RelaxInteratomInconsistentError(pipe1, pipe2)


def create_interatom(spin_id1=None, spin_id2=None, pipe=None):
    """Create and return the interatomic data container for the two spins.

    @keyword spin_id1:  The spin ID string of the first atom.
    @type spin_id1:     str
    @keyword spin_id2:  The spin ID string of the second atom.
    @type spin_id2:     str
    @keyword pipe:      The data pipe to create the interatomic data container for.  This defaults to the current data pipe if not supplied.
    @type pipe:         str or None
    @return:            The newly created interatomic data container.
    @rtype:             data.interatomic.InteratomContainer instance
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Check that the spin IDs exist.
    spin = return_spin(spin_id1, pipe)
    if spin == None:
        raise RelaxNoSpinError(spin_id1)
    spin = return_spin(spin_id2, pipe)
    if spin == None:
        raise RelaxNoSpinError(spin_id2)

    # Check if the two spin IDs have already been added.
    for i in range(len(dp.interatomic)):
        if id_match(spin_id=spin_id1, interatom=dp.interatomic[i], pipe=pipe) and id_match(spin_id=spin_id2, interatom=dp.interatomic[i], pipe=pipe):
            raise RelaxError("The spin pair %s and %s have already been added." % (spin_id1, spin_id2))

    # Add and return the data.
    return dp.interatomic.add_item(spin_id1=spin_id1, spin_id2=spin_id2)


def exists_data(pipe=None):
    """Determine if any interatomic data exists.

    @keyword pipe:      The data pipe in which the interatomic data will be checked for.
    @type pipe:         str
    @return:            The answer to the question about the existence of data.
    @rtype:             bool
    """

    # The current data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # The interatomic data structure is empty.
    if dp.interatomic.is_empty():
        return False

    # Otherwise.
    return True


def id_match(spin_id=None, interatom=None, pipe=None):
    """Test if the spin ID matches one of the two spins of the given container.

    @keyword spin_id:   The spin ID string of the first atom.
    @type spin_id:      str
    @keyword interatom: The interatomic data container.
    @type interatom:    InteratomContainer instance
    @keyword pipe:      The data pipe containing the interatomic data container.  Defaults to the current data pipe.
    @type pipe:         str or None
    @return:            True if the spin ID matches one of the two spins, False otherwise.
    @rtype:             bool
    """

    # Get the spin containers.
    spin1 = return_spin(interatom.spin_id1, pipe=pipe)
    spin2 = return_spin(interatom.spin_id2, pipe=pipe)

    # No spins.
    if spin1 == None or spin2 == None:
        return False

    # Check if the ID is in the private metadata list.
    if spin_id in spin1._spin_ids or spin_id in spin2._spin_ids:
        return True

    # Nothing found.
    return False


def interatomic_loop(selection1=None, selection2=None, pipe=None, selected=True):
    """Generator function for looping over all the interatomic data containers.

    @keyword selection1:    The optional spin ID selection of the first atom.
    @type selection1:       str
    @keyword selection2:    The optional spin ID selection of the second atom.
    @type selection2:       str
    @keyword pipe:          The data pipe containing the spin.  Defaults to the current data pipe.
    @type pipe:             str
    @keyword selected:      A flag which if True will only return selected interatomic data containers.
    @type selected:         bool
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Parse the spin ID selection strings.
    select_obj = None
    select_obj1 = None
    select_obj2 = None
    if selection1 and selection2:
        select_obj1 = Selection(selection1)
        select_obj2 = Selection(selection2)
    elif selection1:
        select_obj = Selection(selection1)
    elif selection2:
        select_obj = Selection(selection2)

    # Loop over the containers, yielding them.
    for i in range(len(dp.interatomic)):
        # Skip deselected containers.
        if selected and not dp.interatomic[i].select:
            continue

        # Aliases.
        interatom = dp.interatomic[i]
        mol_index1, res_index1, spin_index1 = cdp.mol._spin_id_lookup[interatom.spin_id1]
        mol_index2, res_index2, spin_index2 = cdp.mol._spin_id_lookup[interatom.spin_id2]
        mol1 =  cdp.mol[mol_index1]
        res1 =  cdp.mol[mol_index1].res[res_index1]
        spin1 = cdp.mol[mol_index1].res[res_index1].spin[spin_index1]
        mol2 = cdp.mol[mol_index2]
        res2 =  cdp.mol[mol_index2].res[res_index2]
        spin2 = cdp.mol[mol_index2].res[res_index2].spin[spin_index2]

        # Check that the selections are met.
        if select_obj:
            if (mol1, res1, spin1) not in select_obj and (mol2, res2, spin2) not in select_obj:
                continue
        if select_obj1:
            if not ((mol1, res1, spin1) in select_obj1 or (mol2, res2, spin2) in select_obj1) or not ((mol1, res1, spin1) in select_obj2 or (mol2, res2, spin2) in select_obj2):
                continue

        # Return the container.
        yield interatom


def return_interatom(spin_id1=None, spin_id2=None, pipe=None):
    """Return the list of interatomic data containers for the two spins.

    @keyword spin_id1:  The spin ID string of the first atom.
    @type spin_id1:     str
    @keyword spin_id2:  The spin ID string of the second atom.
    @type spin_id2:     str
    @keyword pipe:      The data pipe holding the container.  Defaults to the current data pipe.
    @type pipe:         str or None
    @return:            The matching interatomic data container, if it exists.
    @rtype:             data.interatomic.InteratomContainer instance or None
    """

    # Checks.
    if spin_id1 == None:
        raise RelaxError("The first spin ID must be supplied.")
    if spin_id2 == None:
        raise RelaxError("The second spin ID must be supplied.")

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Return the matching container.
    for i in range(len(dp.interatomic)):
        if id_match(spin_id=spin_id1, interatom=dp.interatomic[i], pipe=pipe) and id_match(spin_id=spin_id2, interatom=dp.interatomic[i], pipe=pipe):
            return dp.interatomic[i]

    # No matchs.
    return None


def return_interatom_list(spin_id=None, pipe=None):
    """Return the list of interatomic data containers for the given spin.

    @keyword spin_id:   The spin ID string.
    @type spin_id:      str
    @keyword pipe:      The data pipe holding the container.  This defaults to the current data pipe.
    @type pipe:         str or None
    @return:            The list of matching interatomic data containers, if any exist.
    @rtype:             list of data.interatomic.InteratomContainer instances
    """

    # Check.
    if spin_id == None:
        raise RelaxError("The spin ID must be supplied.")

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Initialise.
    interatoms = []

    # Find and append all containers.
    for i in range(len(dp.interatomic)):
        if id_match(spin_id=spin_id, interatom=dp.interatomic[i], pipe=pipe) or id_match(spin_id=spin_id, interatom=dp.interatomic[i], pipe=pipe):
            interatoms.append(dp.interatomic[i])

    # Return the list of containers.
    return interatoms
