###############################################################################
#                                                                             #
# Copyright (C) 2003-2004, 2007-2008 Edward d'Auvergne                        #
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
"""Module for reading and writing the relax program state."""

# Python module imports.
from cPickle import dump, load

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from relax_errors import RelaxError
from relax_io import open_read_file, open_write_file


def load_state(state=None, dir_name=None):
    """Function for loading a saved program state.

    @keyword state:     The saved state file.
    @type state:        str
    @keyword dir_name:  The path of the state file.
    @type dir_name:     str
    """

    # Open the file for reading.
    file = open_read_file(file_name=state, dir=dir_name)

    # Unpickle the data class.
    try:
        state = load(file)
    except:
        raise RelaxError("The saved state " + repr(state) + " is not compatible with this version of relax.")

    # Close the file.
    file.close()

    # Reset the relax data storage object.
    ds.__reset__()

    # Black list of objects (all dict objects, non-modifiable objects, data store specific methods, and other special objects).
    black_list = dir(dict) + ['__weakref__', '__dict__', '__module__', '__reset__', 'add', 'from_xml', 'to_xml']

    # Loop over the objects in the saved state, and dump them into the relax data store.
    for name in dir(state):
        # Skip blacklisted objects.
        if name in black_list:
            continue

        # Get the object.
        obj = getattr(state, name)

        # Place ALL objects into the singleton!
        setattr(ds, name, obj)
 
    # Loop over the keys of the dictionary.
    for key in state.keys():
        # Shift the PipeContainer.
        ds[key] = state[key]

    # Delete the state object.
    del state


def save_state(state=None, dir_name=None, force=False, compress_type=1):
    """Function for saving the program state.

    @keyword state:         The saved state file.
    @type state:            str
    @keyword dir_name:      The path of the state file.
    @type dir_name:         str
    @keyword force:         Boolean argument which if True causes the file to be overwritten if it
                            already exists.
    @type force:            bool
    @keyword compress_type: The compression type.  The integer values correspond to the compression
                            type: 0, no compression; 1, Bzip2 compression; 2, Gzip compression.
    @type compress_type:    int
    """

    # Open the file for writing.
    file = open_write_file(file_name=state, dir=dir_name, force=force, compress_type=compress_type)

    # Pickle the data class and write it to file
    dump(ds, file, 1)

    # Close the file.
    file.close()
