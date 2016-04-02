###############################################################################
#                                                                             #
# Copyright (C) 2011-2014 Edward d'Auvergne                                   #
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
"""The sys_info user function definitions."""

# Python module imports.
from os import sep

# relax module imports.
from graphics import WIZARD_OXYGEN_PATH
from info import print_sys_info
from lib.system import cd, pwd
from lib.timing import print_time
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The user function class.
uf_class = uf_info.add_class('system')
uf_class.title = "Class containing the OS system related functions."
uf_class.menu_text = "&system"
uf_class.gui_icon = "oxygen.actions.help-about"


# The cd user function.
uf = uf_info.add_uf('system.cd')
uf.title = "Change the current working directory to the specified path."
uf.title_short = "Change current working directory."
uf.display = True
uf.add_keyarg(
    name = "path",
    py_type = "str",
    desc_short = "path",
    desc = "The path to the new current working directory."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("The equivalent of python module os.chdir(path).  Change the current working directory to the specified path.")
uf.desc[-1].add_paragraph("To change the current working directory, type:")
uf.desc[-1].add_prompt("relax> system.cd(\"/path/to/dir\")")
uf.backend = cd
uf.menu_text = "&cd"
uf.gui_icon = "oxygen.places.folder-favorites"
uf.wizard_size = (700, 400)
uf.wizard_image = WIZARD_OXYGEN_PATH + 'places' + sep + 'folder-favorites.png'
uf.wizard_apply_button = False


# The system.pwd user function.
uf = uf_info.add_uf('system.pwd')
uf.title = "Display the current working directory."
uf.title_short = "Display working directory."
uf.display = True
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will display the current working directory.")
uf.desc[-1].add_paragraph("The directory can be changed with the system.cd(path) user function.")
uf.desc[-1].add_prompt("relax> system.pwd()")
uf.desc[-1].add_prompt("relax> system.cd(\"/path/to/dir\")")
uf.backend = pwd
uf.menu_text = "&pwd"
uf.gui_icon = "oxygen.places.folder-development"
uf.wizard_size = (700, 400)
uf.wizard_image = WIZARD_OXYGEN_PATH + 'places' + sep + 'folder-development.png'
uf.wizard_apply_button = False


# The sys_info user function.
uf = uf_info.add_uf('system.sys_info')
uf.title = "Display all system information relating to this version of relax."
uf.title_short = "Display system information."
uf.display = True
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will display all of the relax, Python, python package and hardware information currently being used by relax.  This is useful for seeing if all packages are up to date and if the correct software versions are being used.  It is also very useful information for reporting relax bugs.")
uf.backend = print_sys_info
uf.menu_text = "s&ys_info"
uf.gui_icon = "oxygen.actions.help-about"
uf.wizard_size = (700, 400)
uf.wizard_apply_button = False


# The time user function.
uf = uf_info.add_uf('system.time')
uf.title = "Display the current time."
uf.title_short = "Current time."
uf.display = True
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This user function will display the current time which can be useful for timing long calculations by having time information in any saved log files.")
uf.backend = print_time
uf.menu_text = "&time"
uf.gui_icon = "oxygen.actions.chronometer"
uf.wizard_size = (700, 400)
uf.wizard_apply_button = False
