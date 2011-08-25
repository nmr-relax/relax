###############################################################################
#                                                                             #
# Copyright (C) 2004-2011 Edward d'Auvergne                                   #
# Copyright (C) 2011 Sebastien Morin                                          #
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
"""Module containing the 'relax_fit' user function class."""
__docformat__ = 'plaintext'

# relax module imports.
from base_class import User_fn_class, _build_doc
import arg_check
from specific_fns.setup import relax_fit_obj


class Relax_fit(User_fn_class):
    """Class for relaxation curve fitting."""

    def relax_time(self, time=0.0, spectrum_id=None):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "relax_fit.relax_time("
            text = text + "time=" + repr(time)
            text = text + ", spectrum_id=" + repr(spectrum_id) + ")"
            print(text)
        # The argument checks.
        arg_check.is_num(time, 'relaxation time')
        arg_check.is_str(spectrum_id, 'spectrum identification string')

        # Execute the functional code.
        relax_fit_obj._relax_time(time=time, spectrum_id=spectrum_id)

    # The function doc info.
    relax_time._doc_title = "Set the relaxation delay time associated with each spectrum."
    relax_time._doc_title_short = "Relaxation delay time setting."
    relax_time._doc_args = [
        ["time", "The time, in seconds, of the relaxation period."],
        ["spectrum_id", "The spectrum identification string."]
    ]
    relax_time._doc_desc = """
        Peak intensities should be loaded before calling this user function via the spectrum.read_intensities user function.  The intensity values will then be associated with a spectrum identifier.  To associate each spectrum identifier with a time point in the relaxation curve prior to optimisation, this user function should be called.
        """
    _build_doc(relax_time)


    def select_model(self, model='exp_2param_neg'):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "relax_fit.select_model("
            text = text + "model=" + repr(model) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(model, 'model')

        # Execute the functional code.
        relax_fit_obj._select_model(model=model)

    # The function doc info.
    select_model._doc_title = "Select the relaxation curve type."
    select_model._doc_title_short = "Relaxation curve type selection."
    select_model._doc_args = [
        ["model", "The type of relaxation curve to fit."]
    ]
    select_model._doc_desc = """
        The supported curve fitting procedures include the default two parameter exponential fit, selected by setting the 'fit_type' argument to 'exp_2param_neg', the three parameter inversion recovery experiment in which the peak intensity limit is a non-zero value, selected by setting the argument to 'exp_3param_inv_neg', as well as various other forms.

        The general parameters of these models are
            'exp_2param*': [Rx, I0],
            'exp_3param*': [Rx, I0, Iinf].

        The different models available are
            'exp_2param',
            'exp_2param_neg',
            'exp_2param_inv',
            'exp_2param_inv_neg',
            'exp_3param',
            'exp_3param_neg',
            'exp_3param_inv',
            'exp_3param_inv_neg'.
        """
    _build_doc(select_model)
