###############################################################################
#                                                                             #
# Copyright (C) 2003-2014 Edward d'Auvergne                                   #
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
"""The eliminate user function definitions for removing failed models."""

# relax module imports.
from graphics import WIZARD_IMAGE_PATH
from pipe_control import eliminate
from specific_analyses.model_free import uf as model_free_uf
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The eliminate user function.
uf = uf_info.add_uf('eliminate')
uf.title = "Elimination or rejection of models."
uf.title_short = "Model elimination."
uf.display = True
uf.add_keyarg(
    name = "function",
    py_type = "func",
    arg_type = "func",
    desc_short = "function",
    desc = "An optional user supplied function for model elimination.",
    can_be_none = True
)
uf.add_keyarg(
    name = "args",
    py_type = "tuple",
    arg_type = "func args",
    desc_short = "function arguments",
    desc = "A tuple of arguments used by the optional function for model elimination.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This is used for model validation to eliminate or reject models prior to model selection.  Model validation is a part of mathematical modelling whereby models are either accepted or rejected.")
uf.desc[-1].add_paragraph("Empirical rules are used for model rejection and are listed below.  However these can be overridden by supplying a function in the prompt and scripting modes.  The function should accept five arguments, a string defining a certain parameter, the value of the parameter, the minimisation instance (ie the residue index if the model is residue specific), and the function arguments.  If the model is rejected, the function should return True, otherwise it should return False.  The function will be executed multiple times, once for each parameter of the model.")
uf.desc[-1].add_paragraph("The function arguments should be a tuple, a list enclosed in round brackets, and will be passed to the user supplied function or the inbuilt function.  For a description of the arguments accepted by the inbuilt functions, see below.")
uf.desc[-1].add_paragraph("Once a model is rejected, the select flag corresponding to that model will be set to False so that model selection, or any other function, will then skip the model.")
uf.desc += model_free_uf.eliminate_doc
uf.backend = eliminate.eliminate
uf.menu_text = "&eliminate"
uf.gui_icon = "oxygen.actions.edit-delete"
uf.wizard_height_desc = 620
uf.wizard_size = (1000, 750)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'model_elimination.png'
