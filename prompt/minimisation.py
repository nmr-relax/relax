###############################################################################
#                                                                             #
# Copyright (C) 2003-2005, 2008-2010 Edward d'Auvergne                        #
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
"""Module containing the 'minimisation' user function class."""
__docformat__ = 'plaintext'

# Python module imports.
from string import split

# relax module imports.
from base_class import Basic_class
import arg_check
from minfx.generic import generic_minimise
from generic_fns import minimise
from relax_errors import RelaxError, RelaxNoneError, RelaxStrError


class Minimisation(Basic_class):
    """Class containing the calc, grid, minimisation, and set functions."""

    def calc(self, verbosity=1):
        """Function for calculating the function value.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        verbosity:  The amount of information to print to screen.  Zero corresponds to minimal
        output while higher values increase the amount of output.  The default value is 1.
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "calc("
            text = text + "verbosity=" + repr(verbosity) + ")"
            print(text)

        # The argument checks.
        arg_check.is_int(verbosity, 'verbosity level')

        # Execute the functional code.
        minimise.calc(verbosity=verbosity)


    def grid_search(self, lower=None, upper=None, inc=21, constraints=True, verbosity=1):
        """The grid search function.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        lower:  An array of the lower bound parameter values for the grid search.  The length of the
        array should be equal to the number of parameters in the model.

        upper:  An array of the upper bound parameter values for the grid search.  The length of the
        array should be equal to the number of parameters in the model.

        inc:  The number of increments to search over.  If a single integer is given then the number
        of increments will be equal in all dimensions.  Different numbers of increments in each
        direction can be set if 'inc' is set to an array of integers of length equal to the number
        of parameters.

        constraints:  A boolean flag specifying whether the parameters should be constrained.  The
        default is to turn constraints on (constraints=True).

        verbosity:  The amount of information to print to screen.  Zero corresponds to minimal
        output while higher values increase the amount of output.  The default value is 1.
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "grid_search("
            text = text + "lower=" + repr(lower)
            text = text + ", upper=" + repr(upper)
            text = text + ", inc=" + repr(inc)
            text = text + ", constraints=" + repr(constraints)
            text = text + ", verbosity=" + repr(verbosity) + ")"
            print(text)

        # The argument checks.
        arg_check.is_num_list(lower, 'lower bounds', can_be_none=True)
        arg_check.is_num_list(upper, 'upper bounds', can_be_none=True)
        arg_check.is_int_or_int_list(inc, 'incrementation value', none_elements=True)
        arg_check.is_bool(constraints, 'constraints flag')
        arg_check.is_int(verbosity, 'verbosity level')

        # Execute the functional code.
        minimise.grid_search(lower=lower, upper=upper, inc=inc, constraints=constraints, verbosity=verbosity)


    def minimise(self, *args, **keywords):
        """Minimisation function.

        Arguments
        ~~~~~~~~~

        The arguments, which should all be strings, specify the minimiser as well as its options.  A
        minimum of one argument is required.  As this calls the minfx function 'generic_minimise'
        the full list of allowed arguments is shown below in the reproduced 'generic_minimise'
        docstring.  Ignore all sections except those labelled as minimisation algorithms and
        minimisation options.  Also do not select the Method of Multipliers constraint algorithm as
        this is used in combination with the given minimisation algorithm if the keyword argument
        'constraints' is set to 1.  The grid search algorithm should also not be selected as this is
        accessed using the 'grid' function instead.  The first argument passed will be set to the
        minimisation algorithm while all other arguments will be set to the minimisation options.

        Keyword arguments differ from normal arguments having the form 'keyword = value'.  All
        arguments must precede keyword arguments in python.  For more information see the examples
        section below or the python tutorial.


        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        func_tol:  The function tolerance.  This is used to terminate minimisation once the function
        value between iterations is less than the tolerance.  The default value is 1e-25.

        grad_tol:  The gradient tolerance.  Minimisation is terminated if the current gradient value
        is less than the tolerance.  The default value is None.

        max_iterations:  The maximum number of iterations.  The default value is 1e7.

        constraints:  A boolean flag specifying whether the parameters should be constrained.  The
        default is to turn constraints on (constraints=True).

        scaling:  The diagonal scaling boolean flag.  The default that scaling is on (scaling=True).

        verbosity:  The amount of information to print to screen.  Zero corresponds to minimal
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

        To apply Newton minimisation together with the GMW81 Hessian modification algorithm, the
        More and Thuente line search algorithm, a function tolerance of 1e-25, no gradient
        tolerance, a maximum of 10,000,000 iterations, constraints turned on to limit parameter
        values, and have normal printout, type any combination of:

        relax> minimise('newton')
        relax> minimise('Newton')
        relax> minimise('newton', 'gmw')
        relax> minimise('newton', 'mt')
        relax> minimise('newton', 'gmw', 'mt')
        relax> minimise('newton', 'mt', 'gmw')
        relax> minimise('newton', func_tol=1e-25)
        relax> minimise('newton', func_tol=1e-25, grad_tol=None)
        relax> minimise('newton', max_iter=1e7)
        relax> minimise('newton', constraints=True, max_iter=1e7)
        relax> minimise('newton', verbosity=1)

        To use constrained Simplex minimisation with a maximum of 5000 iterations, type:

        relax> minimise('simplex', constraints=True, max_iter=5000)



        Note
        ~~~~

        All the text which follows is a reproduction of the docstring of the generic_minimise
        function from the minfx python package.  Only take note of the minimisation algorithms and
        minimisation options sections, the other sections are not relevant for this function.  The
        Grid search and Method of Multipliers algorithms CANNOT be selected as minimisation
        algorithms for this function.

        The section entitled Keyword Arguments is also completely inaccessible therefore please
        ignore that text.

        """

        # The function intro text is found at the end!

        # Keyword: func_tol.
        if 'func_tol' in keywords:
            func_tol = keywords['func_tol']
        else:
            func_tol = 1e-25

        # Keyword: grad_tol.
        if 'grad_tol' in keywords:
            grad_tol = keywords['grad_tol']
        else:
            grad_tol = None

        # Keyword: max_iterations.
        if 'max_iterations' in keywords:
            max_iterations = keywords['max_iterations']
        elif 'max_iter' in keywords:
            max_iterations = keywords['max_iter']
        else:
            max_iterations = 10000000

        # Keyword: constraints.
        if 'constraints' in keywords:
            constraints = keywords['constraints']
        else:
            constraints = True

        # Keyword: scaling.
        if 'scaling' in keywords:
            scaling = keywords['scaling']
        else:
            scaling = True

        # Keyword: verbosity.
        if 'verbosity' in keywords:
            verbosity = keywords['verbosity']
        else:
            verbosity = 1

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "minimise("
            text = text + "*args=" + repr(args)
            text = text + ", func_tol=" + repr(func_tol)
            text = text + ", max_iterations=" + repr(max_iterations)
            text = text + ", constraints=" + repr(constraints)
            text = text + ", scaling=" + repr(scaling)
            text = text + ", verbosity=" + repr(verbosity) + ")"
            print(text)

        # Minimisation algorithm.
        if len(args) == 0:
            raise RelaxNoneError('minimisation algorithm')
        for i in xrange(len(args)):
            if not isinstance(args[i], str):
                raise RelaxStrError('minimisation algorithm', args[0])
        min_algor = args[0]

        # Minimisation options.
        min_options = args[1:]

        # Test for invalid keywords.
        valid_keywords = ['func_tol', 'grad_tol', 'max_iter', 'max_iterations', 'constraints', 'scaling', 'verbosity']
        for key in keywords:
            valid = False
            for valid_key in valid_keywords:
                if key == valid_key:
                    valid = True
            if not valid:
                raise RelaxError("Unknown keyword argument " + repr(key) + ".")

        # The argument checks.
        arg_check.is_num(func_tol, 'function tolerance')
        arg_check.is_num(grad_tol, 'gradient tolerance', can_be_none=True)
        arg_check.is_int(max_iterations, 'maximum number of iterations')
        arg_check.is_bool(constraints, 'constraints flag')
        arg_check.is_bool(scaling, 'diagonal scaling flag')
        arg_check.is_int(verbosity, 'verbosity level')

        # Constraint flag.
        if constraints:
            min_algor = 'Method of Multipliers'
            min_options = args

        # Execute the functional code.
        minimise.minimise(min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, max_iterations=max_iterations, constraints=constraints, scaling=scaling, verbosity=verbosity)



    # Modify the docstring of the minimise method to include the docstring of the generic_minimise function in 'minimise.generic'.
    ##############################################################################################################################

    minimise.__doc__ = minimise.__doc__ + "\n    "

    # Add four spaces to the start of the generic minimise docstring lines to align with the minimise method docstring.
    doc = split(generic_minimise.__doc__, sep='\n')
    for i in xrange(len(doc)):
        minimise.__doc__ = minimise.__doc__ + "    " + doc[i] + "\n"
