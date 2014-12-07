###############################################################################
#                                                                             #
# Copyright (C) 2013-2014 Edward d'Auvergne                                   #
# Copyright (C) 2014 Troels E. Linnet                                         #
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
"""The io user function definitions."""

# Python module imports.
import dep_check
if dep_check.wx_module:
    from wx import FD_OPEN
else:
    FD_OPEN = -1
from os import sep

# relax module imports.
from graphics import WIZARD_IMAGE_PATH
from pipe_control import io
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container
from user_functions.wildcards import WILDCARD_SPECTRUM_PEAKLIST


# The user function class.
uf_class = uf_info.add_class('io')
uf_class.title = "Class for handling IO operations."
uf_class.menu_text = "&io"
uf_class.gui_icon = "oxygen.actions.document-preview-archive"

# The io.file_list user function.
uf = uf_info.add_uf('io.file_list')
uf.title = "Store a file list matching a file pattern in a directory."
uf.title_short = "IO file list."
uf.add_keyarg(
    name = "glob",
    py_type = "str",
    desc_short = "file pattern",
    desc = "The pattern that may contain simple shell-style wildcards.",
)
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir sel",
    desc_short = "directory name",
    desc = "The directory where the file is located.",
    can_be_none = True
)
uf.add_keyarg(
    name = "id",
    py_type = "str",
    desc_short = "IO ID string",
    desc = "The IO ID string used to store the filelist under.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will store a list of file basenames and fileroot matching the file pattern.  These are stored in cdp.io_basename and cdp.io_file_root.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("The following commands will store a filelist to cdp:")
uf.desc[-1].add_prompt("relax> io.file_list(glob='128_*_FT.ft2', dir='/path/to/foolder', id='750MHz_128_NI')")
uf.backend = io.file_list
uf.menu_text = "&read"
uf.gui_icon = "oxygen.actions.document-preview-archive"
uf.wizard_size = (800, 500)
uf.wizard_image = WIZARD_IMAGE_PATH + 'oxygen-document-preview-archive.png'
