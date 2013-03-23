###############################################################################
#                                                                             #
# Copyright (C) 2003-2013 Edward d'Auvergne                                   #
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
"""Module for reading and writing the relax program state."""

# Python module imports.
from re import search

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from pipe_control.reset import reset
from lib.errors import RelaxError
from lib.io import open_read_file, open_write_file
from status import Status; status = Status()


def load_pickle(file):
    """Load the program state from the pickled file.

    @param file:    The file object containing the relax state.
    @type file:     file object
    """

    # Unpickle the data class.
    state = load(file)

    # Close the file.
    file.close()

    # Black list of objects (all dict objects, non-modifiable objects, data store specific methods, and other special objects).
    black_list = dir(dict) + ['__weakref__', '__dict__', '__module__', '__reset__', '_back_compat_hook', 'add', 'from_xml', 'is_empty', 'to_xml']

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
    for key in list(state.keys()):
        # Shift the PipeContainer.
        ds[key] = state[key]

    # Delete the state object.
    del state

    # Success.
    return True


def load_state(state=None, dir=None, verbosity=1, force=False):
    """Function for loading a saved program state.

    @keyword state:     The saved state file.
    @type state:        str
    @keyword dir:       The path of the state file.
    @type dir:          str
    @keyword verbosity: The verbosity level.
    @type verbosity:    int
    @keyword force:     If True, the relax data store will be reset prior to state loading.
    @type force:        bool
    """

    # Open the file for reading.
    file = open_read_file(file_name=state, dir=dir, verbosity=verbosity)

    # Reset.
    if force:
        reset()

    # Make sure that the data store is empty.
    if not ds.is_empty():
        raise RelaxError("The relax data store is not empty.")

    # Restore from the XML.
    ds.from_xml(file)

    # Signal a change in the current data pipe.
    status.observers.pipe_alteration.notify()

    # Signal the state loading
    status.observers.state_load.notify()


def save_state(state=None, dir=None, compress_type=1, verbosity=1, force=False):
    """Function for saving the program state.

    @keyword state:         The saved state file.
    @type state:            str
    @keyword dir:           The path of the state file.
    @type dir:              str
    @keyword verbosity:     The verbosity level.
    @type verbosity:        int
    @keyword force:         Boolean argument which if True causes the file to be overwritten if it
                            already exists.
    @type force:            bool
    @keyword compress_type: The compression type.  The integer values correspond to the compression
                            type: 0, no compression; 1, Bzip2 compression; 2, Gzip compression.
    @type compress_type:    int
    """

    # Open the file for writing.
    file = open_write_file(file_name=state, dir=dir, verbosity=verbosity, force=force, compress_type=compress_type)

    # Save as XML.
    ds.to_xml(file)

    # Close the file.
    file.close()
