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

import sys


class Eliminate:
    def __init__(self, relax):
        """Class containing the function for model elimination."""

        self.relax = relax


    def eliminate(self, run=None, function=None):
        """Function for model elimination.

        Keyword arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run(s).  By supplying a single string, array of strings, or None, a
        single run, multiple runs, or all runs will be selected respectively.


        Description
        ~~~~~~~~~~~

        This function is used for model validation to eliminate or reject models prior to model
        selection.  Model validation is a part of mathematical modelling whereby models are either
        accepted or rejected.

        Empirical rules are used for model rejection and are listed below.  However these can be
        overriden by supplying a function.  The function should accept two arguments, a string
        defining a certain parameter and the value of the parameter.  If the model is rejected, the
        function should return 1, otherwise it should return 0.  The function will be executed
        multiple times, once for each parameter of the model.
        
        Once a model is rejected, the select flag corresponding to that model will be set to 0 so
        that model selection, or any other function, will then skip that model.
        """

        # Function intro text.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "eliminate("
            text = text + "run=" + `run`
            text = text + ", function=" + `function` + ")"
            print text

        # The run argument.
        if run != None and type(run) != str and type(run) != list:
            raise RelaxNoneStrListError, ('run', run)
        if type(run) == list:
            for i in xrange(len(run)):
                if type(run[i]) != str:
                    raise RelaxListStrError, ('run', run)

        # User supplied function.
        if function != None and type(function) != FunctionType:
            raise RelaxFunctionError, ('function', function)

        # Execute the functional code.
        self.relax.generic.eliminate.eliminate(run=run, function=function)
