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

    The current data pipe will be changed to this new data pipe.


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

    # Change the current data pipe.
    relax_data_store.current_pipe = pipe_name


def current():
    """Print the name of the current data pipe."""

    print relax_data_store.current_pipe


def delete(pipe_name=None):
    """Delete a data pipe.

    @param pipe_name:   The name of the data pipe to delete.
    @type pipe_name:    str
    """

    # Test if the data pipe exists.
    if pipe_name != None and not relax_data_store.has_key(pipe_name):
        raise RelaxNoRunError, pipe_name

    # Delete the data pipe.
    del relax_data_store[pipe_name]

    # Set the current data pipe to None if it is the deleted data pipe.
    if relax_data_store.current_pipe == pipe_name:
        relax_data_store.current_pipe = None
