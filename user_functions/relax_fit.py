###############################################################################
#                                                                             #
# Copyright (C) 2004-2014 Edward d'Auvergne                                   #
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
"""The relax_fit user function definitions."""

# Python module imports.
from os import sep

# relax module imports.
from graphics import ANALYSIS_IMAGE_PATH
from pipe_control import spectrum
from specific_analyses.relax_fit.uf import relax_time, select_model
from specific_analyses.relax_fit.estimate_rx_err import estimate_rx_err
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The user function class.
uf_class = uf_info.add_class('relax_fit')
uf_class.title = "Class for relaxation curve fitting."
uf_class.menu_text = "&relax_fit"
uf_class.gui_icon = "relax.relax_fit"


# The relax_fit.relax_time user function.
uf = uf_info.add_uf('relax_fit.relax_time')
uf.title = "Set the relaxation delay time associated with each spectrum."
uf.title_short = "Relaxation delay time setting."
uf.add_keyarg(
    name = "time",
    default = 0.0,
    py_type = "num",
    desc_short = "relaxation time",
    desc = "The time, in seconds, of the relaxation period."
)
uf.add_keyarg(
    name = "spectrum_id",
    py_type = "str",
    desc_short = "spectrum identification string",
    desc = "The spectrum identification string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = spectrum.get_ids,
    wiz_read_only = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("Peak intensities should be loaded before calling this user function via the spectrum.read_intensities user function.  The intensity values will then be associated with a spectrum identifier.  To associate each spectrum identifier with a time point in the relaxation curve prior to optimisation, this user function should be called.")
uf.backend = relax_time
uf.menu_text = "&relax_time"
uf.gui_icon = "oxygen.actions.chronometer"
uf.wizard_size = (700, 500)


# The relax_fit.rx_err_estimate user function.
uf = uf_info.add_uf('relax_fit.rx_err_estimate')
uf.title = "Estimate Rx errors by the Jacobian matrix."
uf.title_short = "Estimate Rx errors."
uf.add_keyarg(
    name = "spin_id",
    py_type = "str",
    arg_type = "spin ID",
    desc_short = "spin ID to restrict value setting to",
    desc = "The spin ID string to restrict value setting to.",
    can_be_none = True
)
uf.add_keyarg(
    name = "epsrel",
    py_type = "float",
    default = 0.0,
    desc_short = "parameter to remove linear-dependent columns.",
    desc = "The parameter to remove linear-dependent columns when J is rank deficient.",
    can_be_none = False
)
uf.add_keyarg(
    name = "verbosity",
    default = 1,
    py_type = "int",
    desc_short = "amount of information to print.",
    desc = "The higher the value, the greater the verbosity.",
    can_be_none = False
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This is a new experimental feature from version 3.3.")
uf.desc[-1].add_paragraph("This will estimate Rx errors by using the exponential decay Jacobian matrix 'J' to compute the covariance matrix of the best-fit parameters.")
uf.desc[-1].add_paragraph("This can be used to for comparison to Monte-Carlo simulations.")
uf.desc[-1].add_paragraph("This method is inspired from the GNU Scientific Library (GSL).")
uf.desc[-1].add_paragraph("The covariance matrix is given by: covar = Qxx = (J^T.W.J)^-1, where the weight matrix W is constructed by the multiplication of an Identity matrix I and a weight array w.  The weight array is 1/errors^2, which then gives W = I.w = I x 1/errors^2.")
uf.desc[-1].add_paragraph("Qxx is computed by QR decomposition, J^T.W.J=QR, Qxx=R^-1. Q^T.  The columns of R which satisfy: |R_{kk}| <= epsrel |R_{11}| are considered linearly-dependent and are excluded from the covariance matrix (the corresponding rows and columns of the covariance matrix are set to zero).")
uf.desc[-1].add_paragraph("The parameter 'epsrel' is used to remove linear-dependent columns when J is rank deficient.")
uf.backend = estimate_rx_err
uf.menu_text = "&rx_err_estimate"
uf.gui_icon = "relax.relax_fit"
uf.wizard_size = (800, 800)
uf.wizard_image = ANALYSIS_IMAGE_PATH + sep + 'blank_150x150.png'


# The relax_fit.select_model user function.
uf = uf_info.add_uf('relax_fit.select_model')
uf.title = "Select the relaxation curve type."
uf.title_short = "Relaxation curve type selection."
uf.display = True
uf.add_keyarg(
    name = "model",
    default = "exp",
    py_type = "str",
    desc_short = "model",
    desc = "The type of relaxation curve to fit.",
    wiz_element_type = "combo",
    wiz_combo_choices = [
        "exp: [Rx, I0]",
        "inv: [Rx, I0, Iinf]"
    ],
    wiz_combo_data = [
        "exp",
        "inv"
    ],
    wiz_read_only = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("The supported relaxation experiments include the default two parameter exponential fit, selected by setting the model type to 'exp', and the three parameter inversion recovery experiment in which the peak intensity limit is a non-zero value, selected by setting the model to 'inv'.")
uf.desc[-1].add_paragraph("The parameters of these two models are")
uf.desc[-1].add_item_list_element("'exp'", "[Rx, I0],")
uf.desc[-1].add_item_list_element("'inv'", "[Rx, I0, Iinf].")
uf.backend = select_model
uf.menu_text = "&select_model"
uf.gui_icon = "oxygen.actions.list-add"
uf.wizard_height_desc = 300
uf.wizard_size = (800, 500)
uf.wizard_apply_button = False
