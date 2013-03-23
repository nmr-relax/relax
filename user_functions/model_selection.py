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
"""The model_selection user function definitions."""

# relax module imports.
from pipe_control import model_selection, pipes
from graphics import WIZARD_IMAGE_PATH
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The model_selection user function.
uf = uf_info.add_uf('model_selection')
uf.title = "Select the best model from a set of optimised models."
uf.title_short = "Model selection."
uf.display = True
uf.add_keyarg(
    name = "method",
    default = "AIC",
    py_type = "str",
    desc_short = "model selection method",
    desc = "The model selection technique (see below).",
    wiz_element_type = 'combo',
    wiz_combo_choices = [
        "Akaike's Information Criteria",
        "Small sample size corrected AIC",
        "Bayesian or Schwarz Information Criteria",
        "Bootstrap model selection",
        "Single-item-out cross-validation",
        "Expected overall discrepancy",
        "Farrow et al., 1994",
        "Mandel et al., 1995",
        "Realised overall discrepancy"
    ],
    wiz_combo_data = [
        "AIC",
        "AICc",
        "BIC",
        "Bootstrap",
        "CV",
        "Expect",
        "Farrow",
        "Palmer",
        "Overall"
    ],
    wiz_read_only = True
)
uf.add_keyarg(
    name = "modsel_pipe",
    py_type = "str",
    desc_short = "model selection data pipe name",
    desc = "The name of the new data pipe which will be created by this user function by the copying of the selected data pipe."
)
uf.add_keyarg(
    name = "bundle",
    py_type = "str",
    desc_short = "pipe bundle",
    desc = "The optional pipe bundle is a special grouping or clustering of data pipes.  If this is specified, the newly created data pipe will be added to this bundle.",
    wiz_element_type = 'combo',
    wiz_combo_iter = pipes.bundle_names,
    wiz_read_only = False,
    can_be_none = True
)
uf.add_keyarg(
    name = "pipes",
    py_type = "str_list_of_lists",
    desc_short = "data pipes",
    desc = "An array containing the names of all data pipes to include in model selection.",
    wiz_element_type = 'combo_list',
    wiz_combo_iter = pipes.pipe_names,
    wiz_read_only = True,
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("The following model selection methods are supported:")
uf.desc[-1].add_item_list_element("AIC", "Akaike's Information Criteria.")
uf.desc[-1].add_item_list_element("AICc", "Small sample size corrected AIC.")
uf.desc[-1].add_item_list_element("BIC", "Bayesian or Schwarz Information Criteria.")
uf.desc[-1].add_item_list_element("Bootstrap", "Bootstrap model selection.")
uf.desc[-1].add_item_list_element("CV", "Single-item-out cross-validation.")
uf.desc[-1].add_item_list_element("Expect", "The expected overall discrepancy (the true values of the parameters are required).")
uf.desc[-1].add_item_list_element("Farrow", "Old model-free method by Farrow et al., 1994.")
uf.desc[-1].add_item_list_element("Palmer", "Old model-free method by Mandel et al., 1995.")
uf.desc[-1].add_item_list_element("Overall", "The realised overall discrepancy (the true values of the parameters are required).")
uf.desc[-1].add_paragraph("For the methods 'Bootstrap', 'Expect', and 'Overall', the Monte Carlo simulations should have previously been executed with the monte_carlo.create_data method set to Bootstrapping to modify its behaviour.")
uf.desc[-1].add_paragraph("If the data pipes have not been specified, then all data pipes will be used for model selection.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("For model-free analysis, if the preset models 1 to 5 are minimised and loaded into the program, the following commands will carry out AIC model selection and to place the selected results into the 'mixed' data pipe, type one of:")
uf.desc[-1].add_prompt("relax> model_selection('AIC', 'mixed')")
uf.desc[-1].add_prompt("relax> model_selection(method='AIC', modsel_pipe='mixed')")
uf.desc[-1].add_prompt("relax> model_selection('AIC', 'mixed', ['m1', 'm2', 'm3', 'm4', 'm5'])")
uf.desc[-1].add_prompt("relax> model_selection(method='AIC', modsel_pipe='mixed', pipes=['m1', 'm2', 'm3', 'm4', 'm5'])")
uf.backend = model_selection.select
uf.menu_text = "m&odel_selection"
uf.gui_icon = "relax.discrepancy_curve"
uf.wizard_height_desc = 450
uf.wizard_size = (900, 750)
uf.wizard_image = WIZARD_IMAGE_PATH + 'discrepancy_curve.png'
