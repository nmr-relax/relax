###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004 Edward d'Auvergne                                  #
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

# Python module imports.
import sys
from types import FunctionType

# relax module imports.
from generic_fns import eliminate
from relax_errors import RelaxFunctionError, RelaxListStrError, RelaxNoneStrListError, RelaxNoneTupleError
from specific_fns.model_free import Model_free


class Eliminate:
    def __init__(self, relax):
        """Class containing the function for model elimination."""

        self.relax = relax


    def eliminate(self, function=None, args=None):
        """Function for model elimination.

        Keyword arguments
        ~~~~~~~~~~~~~~~~~

        function:  A user supplied function for model elimination.

        args:  A tuple of arguments for model elimination.


        Description
        ~~~~~~~~~~~

        This function is used for model validation to eliminate or reject models prior to model
        selection.  Model validation is a part of mathematical modelling whereby models are either
        accepted or rejected.

        Empirical rules are used for model rejection and are listed below.  However these can be
        overridden by supplying a function.  The function should accept five arguments, a string
        defining a certain parameter, the value of the parameter, the minimisation
        instance (ie the residue index if the model is residue specific), and the function
        arguments.  If the model is rejected, the function should return True, otherwise it should
        return False.  The function will be executed multiple times, once for each parameter of the
        model.

        The 'args' keyword argument should be a tuple, a list enclosed in round brackets, and will
        be passed to the user supplied function or the inbuilt function.  For a description of the
        arguments accepted by the inbuilt functions, see below.

        Once a model is rejected, the select flag corresponding to that model will be set to False
        so that model selection, or any other function, will then skip the model.
        """

        # Function intro text.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "eliminate("
            text = text + "function=" + `function`
            text = text + ", args=" + `args` + ")"
            print text

        # User supplied function.
        if function != None and type(function) != FunctionType:
            raise RelaxFunctionError, ('function', function)

        # Function arguments.
        if args != None and type(args) != tuple:
            raise RelaxNoneTupleError, ('args', args)

        # Execute the functional code.
        eliminate.eliminate(function=function, args=args)


    # Docstring modification.
    #########################

    eliminate.__doc__ = eliminate.__doc__ + "\n\n" + Model_free.eliminate.__doc__ + "\n"
