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


class Minimise:
    def __init__(self, relax):
        """Class containing the calc, grid, minimisation, and set functions."""

        self.relax = relax


    def calc(self, run=None):
        """Function for calculating the function value.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.
        """

        # Function intro text.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "calc("
            text = text + "run=" + `run` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Execute the functional code.
        self.relax.generic.minimise.calc(run=run)


    def grid_search(self, run=None, lower=None, upper=None, inc=21, constraints=1, print_flag=1):
        """The grid search function.

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

        # Function intro text.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "grid_search("
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
        self.relax.generic.minimise.grid_search(run=run, lower=lower, upper=upper, inc=inc, constraints=constraints, print_flag=print_flag)


    def minimise(self, *args, **keywords):
        """Minimisation function.

        Arguments
        ~~~~~~~~~

        The arguments are all strings which specify the minimiser to use as well as its options.  A
        minimum of one argument is required.  As this calls the function 'generic_minimise', to see
        the full list of allowed arguments import 'generic_minimise' and view its docstring by
        typing:

        relax> from minimise.generic import generic_minimise
        relax> help(generic_minimise)


        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        func_tol:  The function tolerance.  This is used to terminate minisation once the function
        value between iterations is less than the tolerance.  The default value is 1e-25.

        grad_tol:  The gradient tolerance.  Minimisation is terminated if the current gradient value
        is less than the tolerance.  The default value is None.

        max_iterations:  The maximum number of iterations.  The default value is 1e7.

        constraints:  A flag specifying whether the parameters should be constrained.  The default
        is to turn constraints on (constraints=1).

        print_flag:  The amount of information to print to screen.  Zero corresponds to minimal
        output while higher values increase the amount of output.  The default value is 1.
        """

        # Function intro text is found at the end.

        # Keyword: run.
        if keywords.has_key('run'):
            run = keywords['run']
        else:
            run = None

        # Keyword: func_tol.
        if keywords.has_key('func_tol'):
            func_tol = keywords['func_tol']
        else:
            func_tol = 1e-25

        # Keyword: grad_tol.
        if keywords.has_key('grad_tol'):
            grad_tol = keywords['grad_tol']
        else:
            grad_tol = None

        # Keyword: max_iterations.
        if keywords.has_key('max_iterations'):
            max_iterations = keywords['max_iterations']
        elif keywords.has_key('max_iter'):
            max_iterations = keywords['max_iter']
        else:
            max_iterations = 10000000

        # Keyword: constraints.
        if keywords.has_key('constraints'):
            constraints = keywords['constraints']
        else:
            constraints = 1

        # Keyword: print_flag.
        if keywords.has_key('print_flag'):
            print_flag = keywords['print_flag']
        else:
            print_flag = 1

        # Function intro text.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "minimise("
            text = text + "*args=" + `args`
            text = text + ", run=" + `run`
            text = text + ", func_tol=" + `func_tol`
            text = text + ", max_iterations=" + `max_iterations`
            text = text + ", constraints=" + `constraints`
            text = text + ", print_flag=" + `print_flag` + ")"
            print text

        # Minimization algorithm.
        if len(args) == 0:
            raise RelaxNoneError, 'minimisation algorithm'
        elif type(args[0]) != str:
            raise RelaxStrError, ('minimisation algorithm', args[0])
        min_algor = args[0]

        # Minimization options.
        min_options = args[1:]

        # Test for invalid keywords.
        valid_keywords = ['run', 'func_tol', 'grad_tol', 'max_iter', 'max_iterations', 'constraints', 'print_flag']
        for key in keywords:
            valid = 0
            for valid_key in valid_keywords:
                if key == valid_key:
                    valid = 1
            if not valid:
                raise RelaxError, "The keyword " + `key` + " is invalid."

        # The run keyword.
        if run == None:
            raise RelaxNoneError, 'run'
        elif type(run) != str:
            raise RelaxStrError, ('run', run)

        # The function tolerance value.
        if func_tol != None and type(func_tol) != int and type(func_tol) != float:
            raise RelaxNoneNumError, ('function tolerance', func_tol)

        # The gradient tolerance value.
        if grad_tol != None and type(grad_tol) != int and type(grad_tol) != float:
            raise RelaxNoneNumError, ('gradient tolerance', grad_tol)

        # The maximum number of iterations.
        if type(max_iterations) != int and type(max_iterations) != float:
            raise RelaxNumError, ('maximum number of iterations', max_iterations)

        # Constraint flag.
        if type(constraints) != int or (constraints != 0 and constraints != 1):
            raise RelaxBinError, ('constraint flag', constraints)
        elif constraints == 1:
            min_algor = 'Method of Multipliers'
            min_options = args

        # Print flag.
        if type(print_flag) != int:
            raise RelaxIntError, ('print flag', print_flag)

        # Execute the functional code.
        self.relax.generic.minimise.minimise(run=run, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, max_iterations=max_iterations, constraints=constraints, print_flag=print_flag)


    def set(self, run=None, values=None, print_flag=1):
        """Function for setting the initial parameter values.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        values:  An array of numbers of length equal to the number of parameters in the model.

        print_flag:  The amount of information to print to screen.  Zero corresponds to minimal
        output while higher values increase the amount of output.  The default value is 1.


        Examples
        ~~~~~~~~

        This command will set the parameter values of the run 'm2', which is the original
        model-free equation with parameters {S2, te}, before minimisation to the preselected values
        of this function.

        relax> set('m2')


        This command will do the same except the S2 and te values will be set to one and ten ps
        respectively.

        relax> set('m2', [1.0, 10 * 10e-12])
        relax> set(run='m2', values=[1.0, 10 * 10e-12])
        """

        # Function intro text.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "set("
            text = text + "run=" + `run`
            text = text + ", values=" + `values`
            text = text + ", print_flag=" + `print_flag` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Relax defined values.
        if values != None:
            if type(values) != list:
                raise RelaxListError, ('values', values)
            for i in xrange(len(values)):
                if type(values[i]) != float and type(values[i]) != int:
                    raise RelaxListIntError, ('values', values)

        # The print flag.
        if type(print_flag) != int:
            raise RelaxIntError, ('print_flag', print_flag)

        # Execute the functional code.
        self.relax.generic.minimise.set(run=run, values=values, print_flag=print_flag)
