###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
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


class Grid:
    def __init__(self, relax):
        """Class containing the grid_search macro."""

        self.relax = relax


    def grid_search(self, run=None, lower=None, upper=None, inc=21, constraints=1, print_flag=1):
        """The grid search macro.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run to apply the grid search to.

        lower:  An array of the lower bound parameter values for the grid search.  The length of the
        array should be equal to the number of parameters in the model.

        upper:  An array of the upper bound parameter values for the grid search.  The length of the
        array should be equal to the number of parameters in the model.

        inc:  The number of increments to search over.  If a single integer is given then the number
        of increments will be equal in all dimensions.  Different numbers of increments in each
        direction can be set if 'inc' is set to an array of integers of length equal to the number
        of parameters.

        constraints:  A flag specifying whether the parameters should be constrained.  The default
        is to turn constraints on (constraints=1).

        print_flag:  The amount of information to print to screen.  Zero corresponds to minimal
        output while higher values increase the amount of output.  The default value is 1.
        """

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = sys.macro_prompt + "grid_search("
            text = text + "run=" + `run`
            text = text + ", lower=" + `lower`
            text = text + ", upper=" + `upper`
            text = text + ", inc=" + `inc`
            text = text + ", constraints=" + `constraints`
            text = text + ", print_flag=" + `print_flag` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # The lower bounds.
        if lower == None:
            pass
        elif type(lower) != list:
            raise RelaxListError, ('lower bounds', lower)
        else:
            for i in xrange(len(lower)):
                if type(lower[i]) != float and type(lower[i]) != int:
                    raise RelaxListNumError, ('lower bounds', lower)

        # The upper bounds.
        if upper == None:
            pass
        elif type(upper) != list:
            raise RelaxListError, ('upper bounds', upper)
        else:
            for i in xrange(len(upper)):
                if type(upper[i]) != float and type(upper[i]) != int:
                    raise RelaxListNumError, ('upper bounds', upper)

        # The incrementation value.
        if type(inc) == int:
            pass
        elif type(inc) == list:
            for i in xrange(len(inc)):
                if type(inc[i]) != int:
                    raise RelaxIntListIntError, ('incrementation value', inc)
        else:
            raise RelaxIntListIntError, ('incrementation value', inc)

        # Constraint flag.
        if type(constraints) != int or (constraints != 0 and constraints != 1):
            raise RelaxBinError, ('constraint flag', constraints)

        # The print flag.
        if type(print_flag) != int:
            raise RelaxIntError, ('print flag', print_flag)

        # Execute the functional code.
        self.relax.min.grid_search(run=run, lower=lower, upper=upper, inc=inc, constraints=constraints, print_flag=print_flag)
