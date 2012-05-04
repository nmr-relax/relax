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
"""Module containing the 'model_selection' user function class."""
__docformat__ = 'plaintext'

# relax module imports.
import arg_check
from generic_fns import model_selection
from status import Status; status = Status()


class Modsel:
    """Class containing the function for selecting which model selection method should be used."""

    def model_selection(self, method=None, modsel_pipe=None, pipes=None):
        """Function for model selection.

        Keyword arguments
        ~~~~~~~~~~~~~~~~~

        method:  The model selection technique (see below).

        modsel_pipe:  The name of the new data pipe which will be created by this user function by
            the copying of the selected data pipe.

        pipes:  An array containing the names of all data pipes to include in model selection.


        Description
        ~~~~~~~~~~~

        The following model selection methods are supported:

            AIC:  Akaike's Information Criteria.

            AICc:  Small sample size corrected AIC.

            BIC:  Bayesian or Schwarz Information Criteria.

            Bootstrap:  Bootstrap model selection.

            CV:  Single-item-out cross-validation.

            Expect:  The expected overall discrepancy (the true values of the parameters are
                     required).

            Farrow:  Old model-free method by Farrow et al., 1994.

            Palmer:  Old model-free method by Mandel et al., 1995.

            Overall:  The realised overall discrepancy (the true values of the parameters are
                      required).

        For the methods 'Bootstrap', 'Expect', and 'Overall', the function 'monte_carlo' should have
        previously been executed with the type argument set to the appropriate value to modify its
        behaviour.

        If the pipes argument is not supplied then all data pipes will be used for model selection.


        Example
        ~~~~~~~

        For model-free analysis, if the preset models 1 to 5 are minimised and loaded into the
        program, the following commands will carry out AIC model selection and to place the selected
        results into the 'mixed' data pipe, type one of:

        relax> model_selection('AIC', 'mixed')
        relax> model_selection(method='AIC', modsel_pipe='mixed')
        relax> model_selection('AIC', 'mixed', ['m1', 'm2', 'm3', 'm4', 'm5'])
        relax> model_selection(method='AIC', modsel_pipe='mixed', pipes=['m1', 'm2', 'm3', 'm4', 'm5'])
        """

        # Function intro text.
        if status.prompt_intro:
            text = status.ps3 + "model_selection("
            text = text + "method=" + repr(method)
            text = text + ", modsel_pipe=" + repr(modsel_pipe)
            text = text + ", pipes=" + repr(pipes) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(method, 'model selection method')
        arg_check.is_str(modsel_pipe, 'model selection data pipe name')
        arg_check.is_str_list(pipes, 'data pipes', can_be_none=True, list_of_lists=True)

        # Execute the functional code.
        model_selection.select(method=method, modsel_pipe=modsel_pipe, pipes=pipes)
