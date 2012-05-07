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
"""Module containing the 'model_selection' user function data."""

# relax module imports.
from generic_fns import model_selection, pipes
from graphics import WIZARD_IMAGE_PATH
from user_functions.data import Uf_info; uf_info = Uf_info()


# The model_selection user function.
uf = uf_info.add_uf('model_selection')
uf.title = "Select the best model from a set of optimised models."
uf.title_short = "Model selection."
uf.display = True
uf.add_keyarg(
    name = "method",
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
    name = "pipes",
    py_type = "str_list_of_lists",
    desc_short = "data pipes",
    desc = "An array containing the names of all data pipes to include in model selection.",
    wiz_element_type = 'combo_list',
    wiz_combo_iter = pipes.pipe_names,
    wiz_read_only = True,
    can_be_none = True
)
uf.desc = """
The following model selection methods are supported:

    AIC:  Akaike's Information Criteria.
    AICc:  Small sample size corrected AIC.
    BIC:  Bayesian or Schwarz Information Criteria.
    Bootstrap:  Bootstrap model selection.
    CV:  Single-item-out cross-validation.
    Expect:  The expected overall discrepancy (the true values of the parameters are required).
    Farrow:  Old model-free method by Farrow et al., 1994.
    Palmer:  Old model-free method by Mandel et al., 1995.
    Overall:  The realised overall discrepancy (the true values of the parameters are required).

For the methods 'Bootstrap', 'Expect', and 'Overall', the function 'monte_carlo' should have previously been executed with the type argument set to the appropriate value to modify its behaviour.

If the pipes argument is not supplied then all data pipes will be used for model selection.
"""
uf.prompt_examples = """
For model-free analysis, if the preset models 1 to 5 are minimised and loaded into the
program, the following commands will carry out AIC model selection and to place the selected
results into the 'mixed' data pipe, type one of:

relax> model_selection('AIC', 'mixed')
relax> model_selection(method='AIC', modsel_pipe='mixed')
relax> model_selection('AIC', 'mixed', ['m1', 'm2', 'm3', 'm4', 'm5'])
relax> model_selection(method='AIC', modsel_pipe='mixed', pipes=['m1', 'm2', 'm3', 'm4', 'm5'])
"""
uf.backend = model_selection.select
uf.menu_text = "m&odel_selection"
uf.gui_icon = "relax.discrepancy_curve"
uf.wizard_size = (800, 600)
uf.wizard_image = WIZARD_IMAGE_PATH + 'discrepancy_curve.png'
