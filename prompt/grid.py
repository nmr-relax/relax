###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# Relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# Relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################


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
            text = self.relax.interpreter.macro_prompt + "grid_search("
            text = text + "run=" + `run`
            text = text + ", lower=" + `lower`
            text = text + ", upper=" + `upper`
            text = text + ", inc=" + `inc`
            text = text + ", constraints=" + `constraints`
            text = text + ", print_flag=" + `print_flag` + ")\n"
            print text

        # The run argument.
        if type(run) != str:
            print "The run argument " + `run` + " must be a string."
            return

        # The lower bounds.
        if lower != None:
            bad_arg = 0
            for i in range(len(lower)):
                if type(lower[i]) != float and type(lower[i]) != int:
                    bad_arg = 1
            if bad_arg:
                print "The argument 'lower' must be an array of numbers."
                return

        # The upper bounds.
        if upper != None:
            bad_arg = 0
            for i in range(len(upper)):
                if type(upper[i]) != float and type(upper[i]) != int:
                    bad_arg = 1
            if bad_arg:
                print "The argument 'upper' must be an array of numbers."
                return

        # The incrementation value.
        bad_arg = 0
        if type(inc) != int and type(inc) != list:
            bad_arg = 1
        if type(inc) == list:
            for i in range(len(inc)):
                if type(inc[i]) != int:
                    bad_arg = 1
        if bad_arg:
            print "The argument 'inc' must be either an integer or an array of integers."

        # Constraint flag.
        if type(constraints) != int or (constraints != 0 and constraints != 1):
            print "The constraint flag should be the integer values of either 0 or 1."
            return

        # The print flag.
        if type(print_flag) != int:
            print "The print_flag argument must be an integer."
            return

        # Execute the functional code.
        self.relax.min.grid_search(run=run, lower=lower, upper=upper, inc=inc, constraints=constraints, print_flag=print_flag)
