###############################################################################
#                                                                             #
# Copyright (C) 2003-2005 Edward d'Auvergne                                   #
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

from string import split
import sys

from minimise.generic import generic_minimise


class Minimisation:
    def __init__(self, relax):
        """Class containing the calc, grid, minimisation, and set functions."""

        self.relax = relax


    def calc(self, run=None, print_flag=1):
        """Function for calculating the function value.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.
        """

        # Function intro text.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "calc("
            text = text + "run=" + `run`
            text = text + ", print_flag=" + `print_flag` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # The print flag.
        if type(print_flag) != int:
            raise RelaxIntError, ('print flag', print_flag)

        # Execute the functional code.
        self.relax.generic.minimise.calc(run=run, print_flag=print_flag)


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

        The arguments, which should all be strings, specify the minimiser as well as its options.  A
        minimum of one argument is required.  As this calls the function 'generic_minimise' the full
        list of allowed arguments is shown below in the reproduced 'generic_minimise' docstring.
        Ignore all sections except those labelled as minimisation algorithms and minimisation
        options.  Also do not select the Method of Multipliers constraint algorithm as this is used
        in combination with the given minimisation algorithm if the keyword argument 'constraints'
        is set to 1.  The grid search algorithm should also not be selected as this is accessed
        using the 'grid' function instead.  The first argument passed will be set to the
        minimisation algorithm while all other arguments will be set to the minimisation options.

        Keyword arguments differ from normal arguments having the form 'keyword = value'.  All
        arguments must precede keyword arguments in python.  For more information see the examples
        section below or the python tutorial.


        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        func_tol:  The function tolerance.  This is used to terminate minimisation once the function
        value between iterations is less than the tolerance.  The default value is 1e-25.

        grad_tol:  The gradient tolerance.  Minimisation is terminated if the current gradient value
        is less than the tolerance.  The default value is None.

        max_iterations:  The maximum number of iterations.  The default value is 1e7.

        constraints:  A flag specifying whether the parameters should be constrained.  The default
        is to turn constraints on (constraints=1).

        scaling:  The diagonal scaling flag.  The default that scaling is on (scaling=1).


        print_flag:  The amount of information to print to screen.  Zero corresponds to minimal
        output while higher values increase the amount of output.  The default value is 1.


        Diagonal scaling
        ~~~~~~~~~~~~~~~~

        Diagonal scaling is the transformation of parameter values such that each value has a
        similar order of magnitude.  Certain minimisation techniques, for example the trust region
        methods, perform extremely poorly with badly scaled problems.  In addition, methods which
        are insensitive to scaling such as Newton minimisation may still benefit due to the
        minimisation of round off errors.

        In Model-free analysis for example, if S2 = 0.5, te = 200 ps, and Rex = 15 1/s at 600 MHz,
        the unscaled parameter vector would be [0.5, 2.0e-10, 1.055e-18].  Rex is divided by
        (2 * pi * 600,000,000)**2 to make it field strength independent.  The scaling vector for
        this model may be something like [1.0, 1e-9, 1/(2 * pi * 6e8)**2].  By dividing the unscaled
        parameter vector by the scaling vector the scaled parameter vector is [0.5, 0.2, 15.0].  To
        revert to the original unscaled parameter vector, the scaled parameter vector and scaling
        vector are multiplied.


        Examples
        ~~~~~~~~

        To minimise the model-free run 'm4' using Newton minimisation together with the GMW81
        Hessian modification algorithm, the More and Thuente line search algorithm, a function
        tolerance of 1e-25, no gradient tolerance, a maximum of 10,000,000 iterations, constraints
        turned on to limit parameter values, and have normal printout, type any combination of:

        relax> minimise('newton', run='m4')
        relax> minimise('Newton', run='m4')
        relax> minimise('newton', 'gmw', run='m4')
        relax> minimise('newton', 'mt', run='m4')
        relax> minimise('newton', 'gmw', 'mt', run='m4')
        relax> minimise('newton', 'mt', 'gmw', run='m4')
        relax> minimise('newton', run='m4', func_tol=1e-25)
        relax> minimise('newton', run='m4', func_tol=1e-25, grad_tol=None)
        relax> minimise('newton', run='m4', max_iter=1e7)
        relax> minimise('newton', run=name, constraints=1, max_iter=1e7)
        relax> minimise('newton', run='m4', print_flag=1)

        To minimise the model-free run 'm5' using constrained Simplex minimisation with a maximum of
        5000 iterations, type:

        relax> minimise('simplex', run='m5', constraints=1, max_iter=5000)



        Note
        ~~~~

        --------------------------------------------------------------------------------------------

        All the text which follows is a reproduction of the docstring of the generic_minimise
        function.  Only take note of the minimisation algorithms and minimisation options sections,
        the other sections are not relevant for this function.  The Grid search and Method of
        Multipliers algorithms CANNOT be selected as minimisation algorithms for this function.

        The section entitled Keyword Arguments is also completely inaccessible therefore please
        ignore that text.

        --------------------------------------------------------------------------------------------

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

        # Keyword: scaling.
        if keywords.has_key('scaling'):
            scaling = keywords['scaling']
        else:
            scaling = 1

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
            text = text + ", scaling=" + `scaling`
            text = text + ", print_flag=" + `print_flag` + ")"
            print text

        # Minimisation algorithm.
        if len(args) == 0:
            raise RelaxNoneError, 'minimisation algorithm'
        elif type(args[0]) != str:
            raise RelaxStrError, ('minimisation algorithm', args[0])
        min_algor = args[0]

        # Minimisation options.
        min_options = args[1:]

        # Test for invalid keywords.
        valid_keywords = ['run', 'func_tol', 'grad_tol', 'max_iter', 'max_iterations', 'constraints', 'scaling', 'print_flag']
        for key in keywords:
            valid = 0
            for valid_key in valid_keywords:
                if key == valid_key:
                    valid = 1
            if not valid:
                raise RelaxError, "Unknown keyword argument " + `key` + "."

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

        # Scaling.
        if type(scaling) != int or (scaling != 0 and scaling != 1):
            raise RelaxBinError, ('scaling', scaling)

        # Print flag.
        if type(print_flag) != int:
            raise RelaxIntError, ('print flag', print_flag)

        # Execute the functional code.
        self.relax.generic.minimise.minimise(run=run, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, max_iterations=max_iterations, constraints=constraints, scaling=scaling, print_flag=print_flag)



    # Modify the docstring of the minimise method to include the docstring of the generic_minimise function in 'minimise.generic'.
    ##############################################################################################################################

    minimise.__doc__ = minimise.__doc__ + "\n    "

    # Add four spaces to the start of the generic minimise docstring lines to align with the minimise method docstring.
    doc = split(generic_minimise.__doc__, sep='\n')
    for i in xrange(len(doc)):
        minimise.__doc__ = minimise.__doc__ + "    " + doc[i] + "\n"
