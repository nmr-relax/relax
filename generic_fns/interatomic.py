###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
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
"""Module for the manipulation of the interatomic data structures in the relax data store."""

# Python module imports.
from copy import deepcopy
from re import search

# relax module imports.
from generic_fns import pipes
from generic_fns.mol_res_spin import return_spin
from relax_errors import RelaxError, RelaxInteratomError, RelaxNoInteratomError
from relax_io import write_data
from relax_warnings import RelaxNoSpinWarning


def copy(pipe_from=None, pipe_to=None, verbose=True):
    """Copy the interatomic data from one data pipe to another.

    @keyword pipe_from:         The data pipe to copy the interatomic data from.  This defaults to the current data pipe.
    @type pipe_from:            str
    @keyword pipe_to:           The data pipe to copy the interatomic data to.  This defaults to the current data pipe.
    @type pipe_to:              str
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

    # Test if pipe_from contains interatomic data.
    if not exists_data(pipe_from):
        raise RelaxNoInteratomError

    # Test if pipe_to contains interatomic data.
    if exists_data(pipe_to):
        raise RelaxInteratomError

    # Loop over the interatomic data of the pipe_from data pipe.
    ids = []
    for interatom in interatomic_loop(pipe=pipe_from):
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

        # Store the IDs for the print out.
        ids.append([repr(interatom.spin_id1), repr(interatom.spin_id2)])

    # Print out.
    if verbose:
        write_data(out=sys.stdout, headings=["Spin_ID_1", "Spin_ID_2"], data=ids)


def create_interatom(spin_id1=None, spin_id2=None, pipe=None):
    """Create and return the interatomic data container for the two spins.

    @keyword spin_id1:  The spin ID string of the first atom.
    @type spin_id1:     str
    @keyword spin_id2:  The spin ID string of the first atom.
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
        raise RelaxNoSpinWarning(spin_id1)
    spin = return_spin(spin_id2, pipe)
    if spin == None:
        raise RelaxNoSpinWarning(spin_id2)

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


def interatomic_loop(pipe=None):
    """Generator function for looping over all the interatomic data containers.

    @keyword pipe:      The data pipe containing the spin.  Defaults to the current data pipe.
    @type pipe:         str
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Loop over the containers, yielding them.
    for i in range(len(dp.interatomic)):
        yield dp.interatomic[i]


def return_interatom(spin_id1=None, spin_id2=None, pipe=None):
    """Return the list of interatomic data containers for the two spins.

    @keyword spin_id1:  The spin ID string of the first atom.
    @type spin_id1:     str
    @keyword spin_id2:  The spin ID string of the optional second atom.
    @type spin_id2:     str or None
    @keyword pipe:      The data pipe holding the container.  Defaults to the current data pipe.
    @type pipe:         str or None
    @return:            The list of matching interatomic data containers, if any exist.
    @rtype:             list of data.interatomic.InteratomContainer instances
    """

    # Check.
    if spin_id1 == None:
        raise RelaxError("The first spin ID must be supplied.")

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Initialise.
    interatoms = []

    # Precise match.
    if spin_id1 != None and spin_id2 != None:
        for i in range(len(dp.interatomic)):
            if dp.interatomic[i].id_match(spin_id1, spin_id2):
                interatoms.append(dp.interatomic[i])

    # Single spin.
    else:
        for i in range(len(dp.interatomic)):
            if dp.interatomic[i].spin_id1 == spin_id1 or dp.interatomic[i].spin_id2 == spin_id1:
                interatoms.append(dp.interatomic[i])

    # Return the list of containers.
    return interatoms
