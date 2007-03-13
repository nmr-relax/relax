###############################################################################
#                                                                             #
# Copyright (C) 2004, 2006-2007 Edward d'Auvergne                             #
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
from copy import deepcopy

# relax module imports.
from data import Data
from data.pipe_container import PipeContainer
from relax_errors import RelaxError, RelaxNoRunError, RelaxRunError
from specific_fns.relax_fit import C_module_exp_fn


# The relax data storage object.
relax_data_store = Data()


"""Class containing the methods for manipulating data pipes."""


def create(pipe_name=None, pipe_type=None):
    """Create a new data pipe.

    @param pipe_name:   The name of the new data pipe.
    @type pipe_name:    str
    @param pipe_type:   The new data pipe type which can be one of the following:
        'jw':  Reduced spectral density mapping,
        'mf':  Model-free analysis,
        'noe':  Steady state NOE calculation,
        'relax_fit':  Relaxation curve fitting,
        'srls':  SRLS analysis.
    @type pipe_type:    str
    """

    # Test if the pipe already exists.
    if pipe_name in relax_data_store.keys():
        raise RelaxRunError, pipe_name

    # List of valid data pipe types.
    valid = ['jw', 'mf', 'noe', 'relax_fit', 'srls']

    # Test if pipe_type is valid.
    if not pipe_type in valid:
        raise RelaxError, "The data pipe type " + `pipe_type` + " is invalid and must be one of the strings in the list " + `valid` + "."

    # Test that the C modules have been loaded.
    if pipe_type == 'relax_fit' and not C_module_exp_fn:
        raise RelaxError, "Relaxation curve fitting is not availible.  Try compiling the C modules on your platform."

    # Create a new container.
    relax_data_store[pipe_name] = PipeContainer()

    # Add the data pipe type string to the container.
    relax_data_store[pipe_name].pipe_type = pipe_type


def delete(pipe_name=None):
    """Function for deleting a data pipe."""

    # Test if the data pipe exists.
    if pipe_name != None and not pipe_name in relax_data_store.pipe_names:
        raise RelaxNoRunError, pipe_name

    # Find out if any data in 'relax_data_store' is assigned to a data pipe.
    for name in dir(relax_data_store):
        # Get the object.
        object = getattr(relax_data_store, name)

        # Skip to the next data structure if the object is not a dictionary.
        if not hasattr(object, 'keys'):
            continue

        # Delete the data if the object contains the key 'pipe_name'.
        if object.has_key(pipe_name):
            del(object[pipe_name])

    # Clean up the data pipes, ie delete any data pipes for which there is no data left.
    eliminate_unused_pipes()


def eliminate_unused_pipes():
    """Function for eliminating any data pipes for which there is no data."""

    # An array of data pipes to retain.
    keep_pipes = []

    # Find out if any data in 'relax_data_store' is assigned to a data pipe.
    for name in dir(relax_data_store):
        # Skip to the next data structure if the object is not a dictionary.
        object = getattr(relax_data_store, name)
        if not hasattr(object, 'keys'):
            continue

        # Add the keys to 'keep_pipes'.
        for key in object.keys():
            if not key in keep_pipes:
                keep_pipes.append(key)

    # Delete the data pipes in 'relax_data_store.pipe_names' and 'relax_data_store.pipe_types' which are not in 'keep_pipes'.
    for pipe in relax_data_store.pipe_names:
        if not pipe in keep_pipes:
            # Index.
            index = relax_data_store.pipe_names.index(pipe)

            # Remove from pipe_names.
            relax_data_store.pipe_names.remove(pipe)

            # Remove from pipe_types.
            temp = relax_data_store.pipe_types.pop(index)


def list_of_pipes(pipe):
    """Function for creating a list of data pipes."""

    # All data pipes.
    if pipe == None:
            pipes = deepcopy(relax_data_store.pipe_names)

    # Single data pipe.
    elif type(pipe) == str:
        pipes = [pipe]

    # List of data pipes.
    else:
        pipes = pipe

    # Return the list.
    return pipes
