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


class Minimise:
    def __init__(self, relax):
        """Class containing the minimisation macro."""

        self.relax = relax


    def minimise(self, *args, **keywords):
        """Minimisation macro.

        Arguments
        ~~~~~~~~~

        The arguments are all strings which specify which minimiser to use as well as the
        minimisation options.  At least one argument is required.  As this function calls the
        generic minimisation function 'generic_minimise', to see the full list of allowed arguments
        import the function and view its docstring by typing:

        relax> from minimise.generic import generic_minimise
        relax> help(generic_minimise)


        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        model:  The name of the model.

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

        # Macro intro text is found at the end.

        # Minimization algorithm.
        if len(args) == 0:
            print "The minimisation algorithm has not been specified."
            return
        min_algor = args[0]

        # Minimization options.
        min_options = args[1:]

        # Test for invalid keywords.
        valid_keywords = ['model', 'func_tol', 'grad_tol', 'max_iterations', 'constraints', 'print_flag']
        for key in keywords:
            valid = 0
            for valid_key in valid_keywords:
                if key == valid_key:
                    valid = 1
            if not valid:
                print "The keyword " + `key` + " is invalid."
                return

        # The model keyword.
        if keywords.has_key('model'):
            model = keywords['model']
            if type(model) != str:
                print "The model argument " + `model` + " must be a string."
                return
        else:
            print "No model has been given."
            return
        # self.res causing problems here!
        #if len(self.relax.data.params[model][self.res]) == 0:
        #    print "The minimisation of a zero parameter model is not allowed."
        #    return
        if not self.relax.data.equations.has_key(model):   # Find the index of the model.
            print "The model '" + model + "' has not been created yet."
            return

        # The function tolerance value.
        if keywords.has_key('func_tol'):
            func_tol = keywords['func_tol']
        else:
            func_tol = 1e-25

        # The gradient tolerance value.
        if keywords.has_key('grad_tol'):
            grad_tol = keywords['grad_tol']
        else:
            grad_tol = None

        # The maximum number of iterations.
        if keywords.has_key('max_iterations'):
            max_iterations = keywords['max_iterations']
        elif keywords.has_key('max_iter'):
            max_iterations = keywords['max_iter']
        else:
            max_iterations = 10000000

        # Constraint flag.
        if keywords.has_key('constraints'):
            constraints = keywords['constraints']
        else:
            constraints = 1
        if constraints == 1:
            min_algor = 'Method of Multipliers'
            min_options = args
        elif constraints != 0:
            print "The constraints flag (constraints=" + `constraints` + ") must be either 0 or 1."
            return

        # Print options.
        if keywords.has_key('print_flag'):
            print_flag = keywords['print_flag']
        else:
            print_flag = 1

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = self.relax.interpreter.macro_prompt + "minimise("
            text = text + "model=" + `model`
            text = text + ", func_tol=" + `func_tol`
            text = text + ", max_iterations=" + `max_iterations`
            text = text + ", constraints=" + `constraints`
            text = text + ", print_flag=" + `print_flag` + ")\n"
            print text

        # Execute the functional code.
        self.relax.min.minimise(model=model, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, max_iterations=max_iterations, constraints=constraints, print_flag=print_flag)
