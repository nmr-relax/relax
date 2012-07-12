###############################################################################
#                                                                             #
# Copyright (C) 2003-2012 Edward d'Auvergne                                   #
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
"""The state user function definitions."""

# Python module imports.
import wx

# relax module imports.
from generic_fns.state import load_state, save_state
from graphics import WIZARD_IMAGE_PATH
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The user function class.
uf_class = uf_info.add_class('state')
uf_class.title = "Class for saving or loading the program state."
uf_class.menu_text = "&state"
uf_class.gui_icon = "relax.relax"


# The state.load user function.
uf = uf_info.add_uf('state.load')
uf.title = "Load a saved program state."
uf.title_short = "Saved state loading."
uf.add_keyarg(
    name = "state",
    default = "state.bz2",
    py_type = "str_or_inst",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The file name, which can be a string or a file descriptor object, of a saved program state.",
    wiz_filesel_wildcard = "relax state files (*.bz2)|*.bz2|relax state files (*.gz)|*.gz|relax state files (*.*)|*.*",
    wiz_filesel_style = wx.FD_OPEN
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
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This is able to handle uncompressed, bzip2 compressed files, or gzip compressed files automatically.  The full file name including extension can be supplied, however, if the file cannot be found, this function will search for the file name with '.bz2' appended followed by the file name with '.gz' appended.")
uf.desc[-1].add_paragraph("Both the XML and pickled saved state formats are supported and automatically determined.  For more advanced users, file descriptor objects are also supported.  If the force flag is set to True, then the relax data store will be reset prior to the loading of the saved state.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("The following commands will load the state saved in the file 'save'.")
uf.desc[-1].add_prompt("relax> state.load('save')")
uf.desc[-1].add_prompt("relax> state.load(state='save')")
uf.desc[-1].add_paragraph("Use one of the following commands to load the state saved in the bzip2 compressed file 'save.bz2':")
uf.desc[-1].add_prompt("relax> state.load('save')")
uf.desc[-1].add_prompt("relax> state.load(state='save')")
uf.desc[-1].add_prompt("relax> state.load('save.bz2')")
uf.desc[-1].add_prompt("relax> state.load(state='save.bz2', force=True)")
uf.backend = load_state
uf.menu_text = "&load"
uf.gui_icon = "oxygen.actions.document-open"
uf.wizard_size = (800, 600)
uf.gui_sync = True    # Force synchronous operation to avoid races in the GUI.


# The state.save user function.
uf = uf_info.add_uf('state.save')
uf.title = "Save the program state."
uf.title_short = "Saving state."
uf.add_keyarg(
    name = "state",
    default = "state.bz2",
    py_type = "str_or_inst",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The file name, which can be a string or a file descriptor object, to save the current program state in.",
    wiz_filesel_wildcard = "relax state files (*.bz2)|*.bz2|relax state files (*.gz)|*.gz|relax state files (*.*)|*.*",
    wiz_filesel_style = wx.FD_SAVE
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
    wiz_combo_data = [0, 1, 2]
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
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will place the program state - the relax data store - into a file for later reloading or reference.  The default format is an XML formatted file, but this can be changed to a Python pickled object through the pickle flag.  Note, the pickle format is not human readable and often is not compatible with newer relax versions.")
uf.desc[-1].add_paragraph("The default behaviour of this function is to compress the file using bzip2 compression.  If the extension '.bz2' is not included in the file name, it will be added.  The compression can, however, be changed to either no compression or gzip compression.  This is controlled by the compression type which can be set to")
uf.desc[-1].add_item_list_element("0", "No compression (no file extension).")
uf.desc[-1].add_item_list_element("1", "bzip2 compression ('.bz2' file extension).")
uf.desc[-1].add_item_list_element("2", "gzip compression ('.gz' file extension).")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("The following commands will save the current program state, uncompressed, into the file 'save':")
uf.desc[-1].add_prompt("relax> state.save('save', compress_type=0)")
uf.desc[-1].add_prompt("relax> state.save(state='save', compress_type=0)")
uf.desc[-1].add_paragraph("The following commands will save the current program state into the bzip2 compressed file 'save.bz2':")
uf.desc[-1].add_prompt("relax> state.save('save')")
uf.desc[-1].add_prompt("relax> state.save(state='save')")
uf.desc[-1].add_prompt("relax> state.save('save.bz2')")
uf.desc[-1].add_prompt("relax> state.save(state='save.bz2')")
uf.desc[-1].add_paragraph("If the file 'save' already exists, the following commands will save the current program state by overwriting the file.")
uf.desc[-1].add_prompt("relax> state.save('save', force=True)")
uf.desc[-1].add_prompt("relax> state.save(state='save', force=True)")
uf.backend = save_state
uf.menu_text = "&save"
uf.gui_icon = "oxygen.actions.document-save"
uf.wizard_height_desc = 400
uf.wizard_size = (900, 700)
