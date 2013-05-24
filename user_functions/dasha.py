###############################################################################
#                                                                             #
# Copyright (C) 2005-2013 Edward d'Auvergne                                   #
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
"""The dasha user function definitions for controlling the Dasha model-free software."""

# Python module imports.
import dep_check
if dep_check.wx_module:
    from wx import FD_OPEN
else:
    FD_OPEN = -1

# relax module imports.
from pipe_control import dasha
from graphics import WIZARD_IMAGE_PATH
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The user function class.
uf_class = uf_info.add_class('dasha')
uf_class.title = "Class for interfacing with the program Dasha."
uf_class.menu_text = "&dasha"


# The dasha.create user function.
uf = uf_info.add_uf('dasha.create')
uf.title = "Create the Dasha script."
uf.title_short = "Script creation."
uf.add_keyarg(
    name = "algor",
    default = "LM",
    py_type = "str",
    desc_short = "optimisation algorithm",
    desc = "The minimisation algorithm.",
    wiz_element_type = "combo",
    wiz_combo_choices = ["Levenberg-Marquardt", "Newton-Raphson"],
    wiz_combo_data = ["LM", "NR"],
    wiz_read_only = True
)
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir sel",
    desc_short = "directory name",
    desc = "The directory to place the files.",
    can_be_none = True
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which if set to True will cause the results file to be overwritten if it already exists."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("The script file created is called 'dir/dasha_script'.")
# Optimisation algorithms.
uf.desc.append(Desc_container("Optimisation algorithms"))
uf.desc[-1].add_paragraph("The two minimisation algorithms within Dasha are accessible through the algorithm which can be set to:")
uf.desc[-1].add_item_list_element("'LM'", "The Levenberg-Marquardt algorithm,")
uf.desc[-1].add_item_list_element("'NR'", "Newton-Raphson algorithm.")
uf.desc[-1].add_paragraph("For Levenberg-Marquardt minimisation, the function 'lmin' will be called, while for Newton-Raphson, the function 'min' will be executed.")
uf.backend = dasha.create
uf.menu_text = "&create"
uf.gui_icon = "oxygen.actions.list-add-relax-blue"
uf.wizard_height_desc = 400
uf.wizard_size = (800, 700)
uf.wizard_apply_button = False


# The dasha.execute user function.
uf = uf_info.add_uf('dasha.execute')
uf.title = "Perform a model-free optimisation using Dasha."
uf.title_short = "Dasha execution."
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir sel",
    desc_short = "directory name",
    desc = "The directory to place the files.",
    can_be_none = True
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which if set to True will cause the results file to be overwritten if it already exists."
)
uf.add_keyarg(
    name = "binary",
    default = "dasha",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "Dasha executable file",
    desc = "The name of the executable Dasha program file.",
    wiz_filesel_style = FD_OPEN,
    wiz_filesel_preview = False
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("Dasha will be executed as")
uf.desc[-1].add_prompt("$ dasha < dasha_script | tee dasha_results")
uf.desc[-1].add_paragraph("If you would like to use a different Dasha executable file, change the binary name to the appropriate file name.  If the file is not located within the environment's path, include the full path in front of the binary file name.")
uf.backend = dasha.execute
uf.gui_icon = "oxygen.categories.applications-education"
uf.menu_text = "&execute"
uf.wizard_size = (700, 500)
uf.wizard_apply_button = False


# The dasha.extract user function.
uf = uf_info.add_uf('dasha.extract')
uf.title = "Extract data from the Dasha results file."
uf.title_short = "Dasha data extraction."
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir sel",
    desc_short = "directory name",
    desc = "The directory where the file 'dasha_results' is found.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("The model-free results will be extracted from the Dasha results file 'dasha_results' located in the given directory.")
uf.backend = dasha.extract
uf.menu_text = "ex&tract"
uf.gui_icon = "oxygen.actions.archive-extract"
uf.wizard_apply_button = False
