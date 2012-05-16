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
"""The results user function definitions."""

# relax module imports.
from generic_fns import results
from graphics import WIZARD_IMAGE_PATH
from user_functions.data import Uf_info; uf_info = Uf_info()


# The user function class.
uf_class = uf_info.add_class('results')
uf_class.title = "Class for manipulating results."
uf_class.menu_text = "&results"
uf_class.gui_icon = "relax.relax"


# The results.display user function.
uf = uf_info.add_uf('results.display')
uf.title = "Display the results."
uf.title_short = "Results display."
uf.display = True
uf.desc = """
This will print to screen (STDOUT) the results contained within the current data pipe.
"""
uf.backend = results.display
uf.menu_text = "&display"
uf.gui_icon = "oxygen.actions.document-preview"
uf.wizard_size = (600, 300)
uf.wizard_apply_button = False


# The results.read user function.
uf = uf_info.add_uf('results.read')
uf.title = "Read the contents of a relax results file into the relax data store."
uf.title_short = "Results reading."
uf.add_keyarg(
    name = "file",
    default = "results",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the file to read results from."
)
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir",
    desc_short = "directory name",
    desc = "The directory where the file is located.",
    can_be_none = True
)
uf.desc = """
This is able to handle uncompressed, bzip2 compressed files, or gzip compressed files automatically.  The full file name including extension can be supplied, however, if the file cannot be found the file with '.bz2' appended followed by the file name with '.gz' appended will be searched for.
"""
uf.backend = results.read
uf.menu_text = "&read"
uf.gui_icon = "oxygen.actions.document-open"
uf.wizard_size = (700, 500)
uf.wizard_apply_button = False


# The results.write user function.
uf = uf_info.add_uf('results.write')
uf.title = "Write the results to a file."
uf.title_short = "Results writing."
uf.add_keyarg(
    name = "file",
    default = "results",
    py_type = "str_or_inst",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the file to output results to.  The default is 'results'.  Optionally this can be a file object, or any object with a write() method."
)
uf.add_keyarg(
    name = "dir",
    default = "pipe_name",
    py_type = "str",
    arg_type = "dir",
    desc_short = "directory name",
    desc = "The directory name.",
    can_be_none = True
)
uf.add_keyarg(
    name = "compress_type",
    default = 1,
    py_type = "int",
    desc_short = "compression type",
    desc = "The type of compression to use when creating the file.",
    wiz_element_type = "combo",
    wiz_combo_choices = [
        "No compression",
        "bzip2 compression",
        "gzip compression"
    ],
    wiz_combo_data = [
        0,
        1,
        2
    ],
    wiz_read_only = True,
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which if True will cause the results file to be overwritten."
)
uf.desc = """
This will write the entire contents of the current data pipe into an XML formatted file.  This results file can then be read back into relax at a later point in time, or transfered to another machine.  This is in contrast to the state.save user function whereby the entire data store, including all data pipes, are saved into a similarly XML formatted file.

To place the results file in the current working directory in the prompt and scripting modes, leave the directory unset.  If the directory is set to the special name 'pipe_name', then the results file will be placed into a directory with the same name as the current data pipe.

The default behaviour of this function is to compress the file using bzip2 compression.  If the extension '.bz2' is not included in the file name, it will be added.  The compression can, however, be changed to either no compression or gzip compression.  This is controlled by the compression type which can be set to

    0:  No compression (no file extension),
    1:  bzip2 compression ('.bz2' file extension),
    2:  gzip compression ('.gz' file extension).

The complementary read function will automatically handle the compressed files.
"""
uf.backend = results.write
uf.menu_text = "&write"
uf.gui_icon = "oxygen.actions.document-save"
uf.wizard_height_desc = 400
uf.wizard_size = (1000, 800)
uf.wizard_apply_button = False
