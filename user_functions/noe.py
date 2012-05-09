###############################################################################
#                                                                             #
# Copyright (C) 2004-2012 Edward d'Auvergne                                   #
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
"""Module containing the 'noe' user function data."""

# relax module imports.
from generic_fns import noesy, spectrum
from graphics import ANALYSIS_IMAGE_PATH
from specific_fns.setup import noe_obj
from user_functions.data import Uf_info; uf_info = Uf_info()


# The user function class.
uf_class = uf_info.add_class('noe')
uf_class.title = "Class for handling steady-state NOE and NOESY data."
uf_class.menu_text = "&noe"
uf_class.gui_icon = "relax.noe"


# The noe.read_restraints user function.
uf = uf_info.add_uf('noe.read_restraints')
uf.title = "Read NOESY or ROESY restraints from a file."
uf.title_short = "Restraint reading."
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the file containing the restraint data."
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
    name = "proton1_col",
    py_type = "int",
    desc_short = "first proton column",
    desc = "The column containing the first proton of the NOE or ROE cross peak.",
    wiz_element_type = "text",
    can_be_none = True
)
uf.add_keyarg(
    name = "proton2_col",
    py_type = "int",
    desc_short = "second proton column",
    desc = "The column containing the second proton of the NOE or ROE cross peak.",
    wiz_element_type = "text",
    can_be_none = True
)
uf.add_keyarg(
    name = "lower_col",
    py_type = "int",
    desc_short = "lower bound column",
    desc = "The column containing the lower NOE bound.",
    wiz_element_type = "text",
    can_be_none = True
)
uf.add_keyarg(
    name = "upper_col",
    py_type = "int",
    desc_short = "upper bound column",
    desc = "The column containing the upper NOE bound.",
    wiz_element_type = "text",
    can_be_none = True
)
uf.add_keyarg(
    name = "sep",
    py_type = "str",
    desc_short = "column separator",
    desc = "The column separator (the default is white space).",
    wiz_element_type = "combo",
    wiz_combo_choices = [",", ";", "\\t"],
    can_be_none = True
)
uf.desc = """
The format of the file will be automatically determined, for example Xplor formatted restraint files.  A generically formatted file is also supported if it contains minimally four columns with the two proton names and the upper and lower bounds, as specified by the column numbers.  The proton names need to be in the spin ID string format.
"""
uf.prompt_examples = """
To read the Xplor formatted restraint file 'NOE.xpl', type one of:

relax> noe.read_restraints('NOE.xpl')
relax> noe.read_restraints(file='NOE.xpl')

To read the generic formatted file 'noes', type one of:

relax> noe.read_restraints(file='NOE.xpl', proton1_col=0, proton2_col=1, lower_col=2, upper_col=3)
"""
uf.backend = noesy.read_restraints
uf.menu_text = "&read_restraints"
uf.gui_icon = "oxygen.actions.document-open"
uf.wizard_size = (800, 600)
uf.wizard_image = ANALYSIS_IMAGE_PATH + 'noe_200x200.png'


# The noe.spectrum_type user function.
uf = uf_info.add_uf('noe.spectrum_type')
uf.title = "Set the steady-state NOE spectrum type for pre-loaded peak intensities."
uf.title_short = "Steady-state NOE spectrum type."
uf.add_keyarg(
    name = "spectrum_type",
    py_type = "str",
    desc_short = "spectrum type",
    desc = "The type of steady-state NOE spectrum, one of 'ref' for the reference spectrum or 'sat' for the saturated spectrum.",
    wiz_element_type = "combo",
    wiz_combo_choices = ["Reference spectrum", "Saturated spectrum"],
    wiz_combo_data = ["ref", "sat"],
    wiz_read_only = True,
)
uf.add_keyarg(
    name = "spectrum_id",
    py_type = "str",
    desc_short = "spectrum ID string",
    desc = "The spectrum ID string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = spectrum.get_ids,
    wiz_read_only = True
)
uf.desc = """
The spectrum type can be one of the following:

    The steady-state NOE reference spectrum.
    The steady-state NOE spectrum with proton saturation turned on.

Peak intensities should be loaded before this user function via the spectrum.read_intensities user function.  The intensity values will then be associated with a spectrum ID string which can be used here.
"""
uf.backend = noe_obj._spectrum_type
uf.menu_text = "&spectrum_type"
uf.gui_icon = "oxygen.actions.edit-rename"
uf.wizard_height_desc = 350
uf.wizard_size = (800, 600)
uf.wizard_image = ANALYSIS_IMAGE_PATH + 'noe_200x200.png'
