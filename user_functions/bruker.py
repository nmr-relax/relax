###############################################################################
#                                                                             #
# Copyright (C) 2011-2012 Edward d'Auvergne                                   #
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
"""The bruker user function definitions for interfacing with the Bruker Dynamics Center."""

# Python module imports.
import wx

# relax module imports.
from generic_fns import bruker
from graphics import WIZARD_IMAGE_PATH
from user_functions.data import Uf_info; uf_info = Uf_info()


# The user function class.
uf_class = uf_info.add_class('bruker')
uf_class.title = "Class containing the function for reading the Bruker Dynamics Center (DC) files."
uf_class.menu_text = "&bruker"
uf_class.gui_icon = "relax.bruker"


# The bruker.read user function.
uf = uf_info.add_uf('bruker.read')
uf.title = "Read a Bruker Dynamics Center (DC) relaxation data file."
uf.title_short = "Read a Bruker Dynamics Center file."
uf.add_keyarg(
    name = "ri_id",
    py_type = "str",
    desc_short = "relaxation data ID string",
    desc = "The relaxation data ID string.  This must be a unique identifier."
)
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the Bruker Dynamics Center file containing the relaxation data.",
    wiz_filesel_style = wx.FD_OPEN
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
This user function is used to load all of the data out of a Bruker Dynamics Center (DC) relaxation data file for subsequent analysis within relax.  Currently the R1 and R2 relaxation rates and steady-state NOE data is supported.
"""
uf.backend = bruker.read
uf.menu_text = "&read"
uf.gui_icon = "oxygen.actions.document-open"
uf.wizard_height_desc = 140
uf.wizard_size = (800, 500)
uf.wizard_image = WIZARD_IMAGE_PATH + 'bruker.png'
