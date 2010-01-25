###############################################################################
#                                                                             #
# Copyright (C) 2004-2010 Edward d'Auvergne                                   #
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
from base_class import User_fn_class
import arg_check
from specific_fns.setup import relax_fit_obj


class Relax_fit(User_fn_class):
    """Class for relaxation curve fitting."""

    def relax_time(self, time=0.0, spectrum_id=None):
        """Function for setting the relaxation time period associated with each spectrum.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        time:  The time, in seconds, of the relaxation period.

        spectrum_id:  The spectrum identification string.


        Description
        ~~~~~~~~~~~

        Peak intensities should be loaded before calling this user function via the
        'spectrum.read_intensities()' user function.  The intensity values will then be associated
        with a spectrum identifier.  To associate each spectrum identifier with a time point in the
        relaxation curve prior to optimisation, this user function should be called.
        """

        # Function intro text.
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "relax_fit.relax_time("
            text = text + "time=" + repr(time)
            text = text + ", spectrum_id=" + repr(spectrum_id) + ")"
            print(text)

        # The argument checks.
        arg_check.is_num(time, 'relaxation time')
        arg_check.is_str(spectrum_id, 'spectrum identification string')

        # Execute the functional code.
        relax_fit_obj._relax_time(time=time, spectrum_id=spectrum_id)


    def select_model(self, model='exp'):
        """Function for the selection of the relaxation curve type.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        model:  The type of relaxation curve to fit.


        The preset models
        ~~~~~~~~~~~~~~~~~

        The supported relaxation experiments include the default two parameter exponential fit,
        selected by setting the 'fit_type' argument to 'exp', and the three parameter inversion
        recovery experiment in which the peak intensity limit is a non-zero value, selected by
        setting the argument to 'inv'.

        The parameters of these two models are
            'exp': [Rx, I0],
            'inv': [Rx, I0, Iinf].
        """

        # Function intro text.
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "relax_fit.select_model("
            text = text + "model=" + repr(model) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(model, 'model')

        # Execute the functional code.
        relax_fit_obj._select_model(model=model)
