###############################################################################
#                                                                             #
# Copyright (C) 2003-2005, 2007, 2009-2010 Edward d'Auvergne                  #
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
"""Module containing the 'state' user function class."""
__docformat__ = 'plaintext'

# relax module imports.
from base_class import User_fn_class
import arg_check
from generic_fns.state import load_state, save_state


class State(User_fn_class):
    """Class for saving or loading the program state."""

    def load(self, state=None, dir=None, force=False):
        """Function for loading a saved program state.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        state:  The file name, which can be a string or a file descriptor object, of a saved program
                state.

        dir:  The name of the directory in which the file is found.

        force:  A boolean flag which if True will cause the current program state to be overwritten.


        Description
        ~~~~~~~~~~~

        This function is able to handle uncompressed, bzip2 compressed files, or gzip compressed
        files automatically.  The full file name including extension can be supplied, however, if
        the file cannot be found, this function will search for the file name with '.bz2' appended
        followed by the file name with '.gz' appended.
        
        Both the XML and pickled saved state formats are supported and automatically determined.
        For more advanced users, file descriptor objects are also supported.  If the force flag is
        set to True, then the relax data store will be reset prior to the loading of the saved
        state.


        Examples
        ~~~~~~~~

        The following commands will load the state saved in the file 'save'.

        relax> state.load('save')
        relax> state.load(state='save')


        Use one of the following commands to load the state saved in the bzip2 compressed file
        'save.bz2':

        relax> state.load('save')
        relax> state.load(state='save')
        relax> state.load('save.bz2')
        relax> state.load(state='save.bz2', force=True)
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "state.load("
            text = text + "state=" + repr(state)
            text = text + ", dir=" + repr(dir)
            text = text + ", force=" + repr(force) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str_or_inst(state, 'file name')
        arg_check.is_str(dir, 'directory name', can_be_none=True)
        arg_check.is_bool(force, 'force flag')

        # Execute the functional code.
        load_state(state=state, dir=dir, force=force)


    def save(self, state=None, dir=None, compress_type=1, force=False, pickle=False):
        """Function for saving the program state.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        state:  The file name, which can be a string or a file descriptor object, to save the
                current program state in.

        dir:  The name of the directory in which to place the file.

        compress_type:  The type of compression to use when creating the file.

        force:  A boolean flag which if set to True will cause the file to be overwritten.

        pickle:  A flag which if true will cause the state file to be a pickled object rather than
            the default XML format.


        Description
        ~~~~~~~~~~~

        This user function will place the program state - the relax data store - into a file for
        later reloading or reference.  The default format is an XML formatted file, but this can be
        changed to a Python pickled object through the pickle flag.  Note, the pickle format is not
        human readable and often is not compatible with newer relax versions.

        The default behaviour of this function is to compress the file using bzip2 compression.  If
        the extension '.bz2' is not included in the file name, it will be added.  The compression
        can, however, be changed to either no compression or gzip compression.  This is controlled
        by the compress_type argument which can be set to

            0:  No compression (no file extension).
            1:  bzip2 compression ('.bz2' file extension).
            2:  gzip compression ('.gz' file extension).


        Examples
        ~~~~~~~~

        The following commands will save the current program state, uncompressed, into the file 'save':

        relax> state.save('save', compress_type=0)
        relax> state.save(state='save', compress_type=0)


        The following commands will save the current program state into the bzip2 compressed file
        'save.bz2':

        relax> state.save('save')
        relax> state.save(state='save')
        relax> state.save('save.bz2')
        relax> state.save(state='save.bz2')


        If the file 'save' already exists, the following commands will save the current program
        state by overwriting the file.

        relax> state.save('save', force=True)
        relax> state.save(state='save', force=True)
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "state.save("
            text = text + "state=" + repr(state)
            text = text + ", dir=" + repr(dir)
            text = text + ", compress_type=" + repr(compress_type)
            text = text + ", force=" + repr(force)
            text = text + ", pickle=" + repr(pickle) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str_or_inst(state, 'file name')
        arg_check.is_str(dir, 'directory name', can_be_none=True)
        arg_check.is_int(compress_type, 'compression type')
        arg_check.is_bool(force, 'force flag')
        arg_check.is_bool(pickle, 'pickle flag')

        # Execute the functional code.
        save_state(state=state, dir=dir, compress_type=compress_type, force=force, pickle=pickle)
