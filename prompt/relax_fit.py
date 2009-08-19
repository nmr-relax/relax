###############################################################################
#                                                                             #
# Copyright (C) 2004-2008 Edward d'Auvergne                                   #
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

# Python module imports.
import sys

# relax module imports.
import help
from relax_errors import RelaxNumError, RelaxStrError
from specific_fns.setup import relax_fit_obj


class Relax_fit:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for relaxation curve fitting."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


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
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "relax_fit.relax_time("
            text = text + "time=" + repr(time)
            text = text + ", spectrum_id=" + repr(spectrum_id) + ")"
            print(text)

        # The relaxation time.
        if type(time) != int and type(time) != float:
            raise RelaxNumError, ('relaxation time', time)

        # The spectrum identification string.
        if type(spectrum_id) != str:
            raise RelaxStrError, ('spectrum identification string', spectrum_id)

        # Execute the functional code.
        relax_fit_obj.relax_time(time=time, spectrum_id=spectrum_id)


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
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "relax_fit.select_model("
            text = text + "model=" + repr(model) + ")"
            print(text)

        # The model argument.
        if type(model) != str:
            raise RelaxStrError, ('model', model)

        # Execute the functional code.
        relax_fit_obj.select_model(model=model)
