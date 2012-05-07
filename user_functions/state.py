###############################################################################
#                                                                             #
# Copyright (C) 2003-2012 Edward d'Auvergne                                   #
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
"""Module containing the 'state' user function data."""

# relax module imports.
from generic_fns.state import load_state, save_state
from graphics import WIZARD_IMAGE_PATH
from user_functions.data import Uf_info; uf_info = Uf_info()


# The user function class.
uf_class = uf_info.add_class('state')
uf_class.title = "Class for saving or loading the program state."
uf_class.menu_text = "&state"


# The state.load user function.
uf = uf_info.add_uf('state.load')
uf.title = "Load a saved program state."
uf.title_short = "Saved state loading."
uf.add_keyarg(
    name = "state",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The file name, which can be a string or a file descriptor object, of a saved program state."
)
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir",
    desc_short = "directory name",
    desc = "The name of the directory in which the file is found.",
    can_be_none = True
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A boolean flag which if True will cause the current program state to be overwritten."
)
uf.desc = """
This is able to handle uncompressed, bzip2 compressed files, or gzip compressed files automatically.  The full file name including extension can be supplied, however, if the file cannot be found, this function will search for the file name with '.bz2' appended followed by the file name with '.gz' appended.
        
Both the XML and pickled saved state formats are supported and automatically determined.  For more advanced users, file descriptor objects are also supported.  If the force flag is set to True, then the relax data store will be reset prior to the loading of the saved state.
"""
uf.prompt_examples = """
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
uf.backend = load_state
uf.menu_text = "&load"
uf.gui_icon = "oxygen.actions.document-open"
uf.wizard_size = (800, 600)


# The state.save user function.
uf = uf_info.add_uf('state.save')
uf.title = "Save the program state."
uf.title_short = "Saving state."
uf.add_keyarg(
    name = "state",
    py_type = "str_or_inst",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The file name, which can be a string or a file descriptor object, to save the current program state in."
)
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir",
    desc_short = "directory name",
    desc = "The name of the directory in which to place the file.",
    can_be_none = True
)
uf.add_keyarg(
    name = "compress_type",
    default = 1,
    py_type = "int",
    desc_short = "compression type",
    desc = "The type of compression to use when creating the file.",
    wiz_element_type = "combo",
    wiz_combo_choices = ["No compression", "bzip2 compression", "gzip compression"],
    wiz_combo_data = [0, 1, 2],
    can_be_none = True
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A boolean flag which if set to True will cause the file to be overwritten."
)
uf.add_keyarg(
    name = "pickle",
    default = False,
    py_type = "bool",
    desc_short = "pickle flag",
    desc = "A flag which if true will cause the state file to be a pickled object rather than the default XML format."
)
uf.desc = """
This will place the program state - the relax data store - into a file for later reloading or reference.  The default format is an XML formatted file, but this can be changed to a Python pickled object through the pickle flag.  Note, the pickle format is not human readable and often is not compatible with newer relax versions.

The default behaviour of this function is to compress the file using bzip2 compression.  If the extension '.bz2' is not included in the file name, it will be added.  The compression can, however, be changed to either no compression or gzip compression.  This is controlled by the compress_type argument which can be set to

    0:  No compression (no file extension).
    1:  bzip2 compression ('.bz2' file extension).
    2:  gzip compression ('.gz' file extension).
"""
uf.prompt_examples = """
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
uf.backend = save_state
uf.menu_text = "&save"
uf.gui_icon = "oxygen.actions.document-save"
uf.wizard_size = (800, 600)
