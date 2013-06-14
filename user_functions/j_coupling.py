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
"""The j_coupling user function definitions."""

# Python module imports.
import dep_check
if dep_check.wx_module:
    from wx import FD_OPEN, FD_SAVE
else:
    FD_OPEN = -1
    FD_SAVE = -1

# relax module imports.
from pipe_control import pipes, j_coupling
from graphics import WIZARD_IMAGE_PATH
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The user function class.
uf_class = uf_info.add_class('j_coupling')
uf_class.title = "Class for handling scalar couplings."
uf_class.menu_text = "&j_coupling"
uf_class.gui_icon = "relax.j_coupling"


# The j_coupling.copy user function.
uf = uf_info.add_uf('j_coupling.copy')
uf.title = "Copy J coupling data from one data pipe to another."
uf.title_short = "J coupling copying."
uf.add_keyarg(
    name = "pipe_from",
    py_type = "str",
    desc_short = "source pipe",
    desc = "The name of the pipe to copy the J coupling data from.",
    wiz_element_type = 'combo',
    wiz_combo_iter = pipes.pipe_names,
    can_be_none = True
)
uf.add_keyarg(
    name = "pipe_to",
    py_type = "str",
    desc_short = "destination pipe",
    desc = "The name of the pipe to copy the J coupling data to.",
    wiz_element_type = 'combo',
    wiz_combo_iter = pipes.pipe_names,
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This function will copy J coupling data from one pipe to another.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To copy all J coupling data from pipe 'DMSO' to pipe 'CDCl3', type one of:")
uf.desc[-1].add_prompt("relax> j_coupling.copy('DMSO', 'CDCl3')")
uf.desc[-1].add_prompt("relax> j_coupling.copy(pipe_from='DMSO', pipe_to='CDCl3')")
uf.backend = j_coupling.copy
uf.menu_text = "cop&y"
uf.gui_icon = "oxygen.actions.list-add"
uf.wizard_size = (750, 450)
uf.wizard_image = WIZARD_IMAGE_PATH + 'j_coupling.png'


# The j_coupling.delete user function.
uf = uf_info.add_uf('j_coupling.delete')
uf.title = "Delete the J coupling values."
uf.title_short = "J coupling deletion."
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will delete all J coupling data in the current data pipe.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To delete all J coupling data, type:")
uf.desc[-1].add_prompt("relax> j_coupling.delete()")
uf.backend = j_coupling.delete
uf.menu_text = "&delete"
uf.gui_icon = "oxygen.actions.list-remove"
uf.wizard_size = (750, 450)
uf.wizard_image = WIZARD_IMAGE_PATH + 'j_coupling.png'


# The j_coupling.display user function.
uf = uf_info.add_uf('j_coupling.display')
uf.title = "Display the J coupling data in the current data pipe."
uf.title_short = "J coupling display."
uf.display = True
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will display all of the J coupling data in the current data pipe.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To display all J coupling data, type:")
uf.desc[-1].add_prompt("relax> j_coupling.display()")
uf.backend = j_coupling.display
uf.menu_text = "di&splay"
uf.gui_icon = "oxygen.actions.document-preview"
uf.wizard_size = (750, 450)
uf.wizard_image = WIZARD_IMAGE_PATH + 'j_coupling.png'


# The j_coupling.read user function.
uf = uf_info.add_uf('j_coupling.read')
uf.title = "Read the J coupling data from file."
uf.title_short = "J coupling data reading."
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the file containing the J coupling data.",
    wiz_filesel_style = FD_OPEN
)
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir",
    desc_short = "directory name",
    desc = "The directory where the file is located.",
    can_be_none = True
)
uf.add_keyarg(
    name = "spin_id1_col",
    default = 1,
    py_type = "int",
    min = 1,
    desc_short = "first spin ID column",
    desc = "The spin ID string column for the first spin."
)
uf.add_keyarg(
    name = "spin_id2_col",
    default = 2,
    py_type = "int",
    min = 1,
    desc_short = "second spin ID column",
    desc = "The spin ID string column for the second spin."
)
uf.add_keyarg(
    name = "data_col",
    py_type = "int",
    desc_short = "data column",
    desc = "The J coupling data column.",
    can_be_none = True
)
uf.add_keyarg(
    name = "error_col",
    py_type = "int",
    desc_short = "error column",
    desc = "The experimental error column.",
    can_be_none = True
)
uf.add_keyarg(
    name = "sign_col",
    py_type = "int",
    desc_short = "sign column",
    desc = "A special column holding the sign of the J coupling, being either 1 or -1, in case this data is obtained separately.",
    can_be_none = True
)
uf.add_keyarg(
    name = "sep",
    py_type = "str",
    desc_short = "column separator",
    desc = "The column separator (the default is white space).",
    wiz_element_type = "combo",
    wiz_combo_choices = ["white space", ",", ";", ":"],
    wiz_combo_data = [None, ",", ";", ":"],
    wiz_read_only = False,
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will read J coupling data from a file.  If the sign of the J coupling has been determined by a different experiment, this information can be present in a different column having either the value of 1 or -1.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("The following commands will read the J coupling data out of the file 'J.txt' where the columns are separated by the symbol ',':")
uf.desc[-1].add_prompt("relax> j_coupling.read('J.txt', sep=',')")
uf.desc[-1].add_paragraph("If the individual spin J coupling errors are located in the file 'j_err.txt' in column number 5 then, to read these values into relax, type one of:")
uf.desc[-1].add_prompt("relax> j_coupling.read('j_err.txt', error_col=5)")
uf.desc[-1].add_prompt("relax> j_coupling.read(file='j_err.txt', error_col=5)")
uf.backend = j_coupling.read
uf.menu_text = "&read"
uf.gui_icon = "oxygen.actions.document-open"
uf.wizard_height_desc = 300
uf.wizard_size = (1000, 750)
uf.wizard_image = WIZARD_IMAGE_PATH + 'j_coupling.png'


# The j_coupling.write user function.
uf = uf_info.add_uf('j_coupling.write')
uf.title = "Write the J coupling data to file."
uf.title_short = "J coupling writing."
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the file.",
    wiz_filesel_style = FD_SAVE
)
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir",
    desc_short = "directory name",
    desc = "The directory name.",
    can_be_none = True
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which if True will cause the file to be overwritten."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will write the J coupling values to file.  If no directory name is given, the file will be placed in the current working directory.")
uf.backend = j_coupling.write
uf.menu_text = "&write"
uf.gui_icon = "oxygen.actions.document-save"
uf.wizard_size = (800, 500)
uf.wizard_image = WIZARD_IMAGE_PATH + 'j_coupling.png'
