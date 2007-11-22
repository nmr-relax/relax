###############################################################################
#                                                                             #
# Copyright (C) 2003-2004, 2007 Edward d'Auvergne                             #
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
from cPickle import dump, load

# relax module imports.
from data import Data as relax_data_store
from relax_io import open_read_file, open_write_file


def load_state(state=None, dir_name=None, compress_type=1):
    """Function for loading a saved program state."""

    # Open the file for reading.
    file = open_read_file(file_name=state, dir=dir_name, compress_type=compress_type)

    # Unpickle the data class.
    state = load(file)

    # Close the file.
    file.close()

    # Reset the relax data storage object.
    relax_data_store.__reset__()

    # Black list of objects.
    black_list = ['__weakref__']

    # Loop over the objects in the saved state, and dump them into the relax data store.
    for name in dir(state):
        # Skip blacklisted objects.
        if name in black_list:
            continue

        # Get the object.
        obj = getattr(state, name)

        # Place ALL objects into the singleton!
        setattr(relax_data_store, name, obj)
 
    # Loop over the keys of the dictionary.
    for key in state.keys():
        # Shift the PipeContainer.
        relax_data_store[key] = state[key]

    # Delete the state object.
    del state


def save_state(state=None, dir_name=None, force=0, compress_type=1):
    """Function for saving the program state."""

    # Open the file for writing.
    file = open_write_file(file_name=state, dir=dir_name, force=force, compress_type=compress_type)

    # Pickle the data class and write it to file
    dump(relax_data_store, file, 1)

    # Close the file.
    file.close()
