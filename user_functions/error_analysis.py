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
"""The error_analysis user function definitions."""

# Python module imports.
from os import sep

# relax module imports.
from graphics import ANALYSIS_IMAGE_PATH
from pipe_control.error_analysis import covariance_matrix
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The user function class.
uf_class = uf_info.add_class('error_analysis')
uf_class.title = "Class for relaxation curve fitting."
uf_class.menu_text = "&error_analysis"


# The error_analysis.covariance_matrix user function.
uf = uf_info.add_uf('error_analysis.covariance_matrix')
uf.title = "Parameter error estimation via the covariance matrix."
uf.title_short = "Covariance matrix parameter error estimation."
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
uf.desc[-1].add_paragraph("This will estimate parameter errors by using the exponential decay Jacobian matrix 'J' to compute the covariance matrix of the best-fit parameters.")
uf.desc[-1].add_paragraph("This can be used to for comparison to Monte-Carlo simulations.")
uf.desc[-1].add_paragraph("This method is inspired from the GNU Scientific Library (GSL).")
uf.desc[-1].add_paragraph("The covariance matrix is given by: covar = Qxx = (J^T.W.J)^-1, where the weight matrix W is constructed by the multiplication of an Identity matrix I and a weight array w.  The weight array is 1/errors^2, which then gives W = I.w = I x 1/errors^2.")
uf.desc[-1].add_paragraph("Qxx is computed by QR decomposition, J^T.W.J=QR, Qxx=R^-1. Q^T.  The columns of R which satisfy: |R_{kk}| <= epsrel |R_{11}| are considered linearly-dependent and are excluded from the covariance matrix (the corresponding rows and columns of the covariance matrix are set to zero).")
uf.desc[-1].add_paragraph("The parameter 'epsrel' is used to remove linear-dependent columns when J is rank deficient.")
uf.backend = covariance_matrix
uf.menu_text = "&covariance_matrix"
uf.wizard_size = (800, 800)
uf.wizard_image = ANALYSIS_IMAGE_PATH + sep + 'blank_150x150.png'
