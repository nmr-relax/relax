###############################################################################
#                                                                             #
# Copyright (C) 2003-2015 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the minfx optimisation library,                        #
# https://gna.org/projects/minfx                                              #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""Generic minimisation function for easy access to all of the optimization algorithms.

This file is part of the U{minfx optimisation library<https://gna.org/projects/minfx>}.
"""

# Python module imports.
from re import match, search

# Minfx module imports.
from minfx.bfgs import bfgs
from minfx.cauchy_point import cauchy_point
from minfx.coordinate_descent import coordinate_descent
from minfx.dogleg import dogleg
from minfx.errors import MinfxError
from minfx.exact_trust_region import exact_trust_region
from minfx.fletcher_reeves_cg import fletcher_reeves
from minfx.hestenes_stiefel_cg import hestenes_stiefel
from minfx.levenberg_marquardt import levenberg_marquardt
from minfx.log_barrier_function import log_barrier_function
from minfx.method_of_multipliers import method_of_multipliers
from minfx.ncg import ncg
from minfx.newton import newton
from minfx.polak_ribiere_cg import polak_ribiere
from minfx.polak_ribiere_plus_cg import polak_ribiere_plus
from minfx.simplex import simplex
from minfx.steepest_descent import steepest_descent
from minfx.steihaug_cg import steihaug

# Scipy module imports.
try:
    from minfx.scipy_subset.anneal import anneal
except ImportError:
    SA_flag = False
else:
    SA_flag = True



def generic_minimise(func=None, dfunc=None, d2func=None, args=(), x0=None, min_algor=None, min_options=None, func_tol=1e-25, grad_tol=None, maxiter=1e6, A=None, b=None, l=None, u=None, c=None, dc=None, d2c=None, print_flag=0, print_prefix="", full_output=False):
    """Generic minimisation function.

    This is a generic function which can be used to access all minimisers using the same set of function arguments.  These are the function tolerance value for convergence tests, the maximum number of iterations, a flag specifying which data structures should be returned, and a flag specifying the amount of detail to print to screen.


    Minimisation output
    ===================

    The following values of the 'full_output' flag will return, in tuple form, the following data:

        - 0:  'xk',
        - 1:  '(xk, fk, k, f_count, g_count, h_count, warning)',

    where the data names correspond to:

        - 'xk':      The array of minimised parameter values,
        - 'fk':      The minimised function value,
        - 'k':       The number of iterations,
        - 'f_count': The number of function calls,
        - 'g_count': The number of gradient calls,
        - 'h_count': The number of Hessian calls,
        - 'warning': The warning string.


    Minimisation algorithms
    =======================

    A minimisation function is selected if the minimisation algorithm argument, which should be a string, matches a certain pattern.  Because the python regular expression 'match' statement is used, various strings can be supplied to select the same minimisation algorithm.  Below is a list of the minimisation algorithms available together with the corresponding patterns.

    This is a short description of python regular expression, for more information, see the regular expression syntax section of the Python Library Reference.  Some of the regular expression syntax used in this function is:

        - '[]':  A sequence or set of characters to match to a single character.  For example, '[Nn]ewton' will match both 'Newton' and 'newton'.

        - '^':  Match the start of the string.

        - '$':  Match the end of the string.  For example, '^[Ll][Mm]$' will match 'lm' and 'LM' but will not match if characters are placed either before or after these strings.

    To select a minimisation algorithm, set the argument to a string which matches the given pattern.


    Unconstrained line search methods::
        ___________________________________________________________________________________________
        |                                   |                                                     |
        | Minimisation algorithm            | Patterns                                            |
        |___________________________________|_____________________________________________________|
        |                                   |                                                     |
        | Back-and-forth coordinate descent | '^[Cc][Dd]$' or '^[Cc]oordinate[ _-][Dd]escent$'    |
        |                                   |                                                     |
        | Steepest descent                  | '^[Ss][Dd]$' or '^[Ss]teepest[ _-][Dd]escent$'      |
        |                                   |                                                     |
        | Quasi-Newton BFGS                 | '^[Bb][Ff][Gg][Ss]$'                                |
        |                                   |                                                     |
        | Newton                            | '^[Nn]ewton$'                                       |
        |                                   |                                                     |
        | Newton-CG                         | '^[Nn]ewton[ _-][Cc][Gg]$' or '^[Nn][Cc][Gg]$'      |
        |___________________________________|_____________________________________________________|


    Unconstrained trust-region methods::
        ___________________________________________________________________________________________
        |                                   |                                                     |
        | Minimisation algorithm            | Patterns                                            |
        |___________________________________|_____________________________________________________|
        |                                   |                                                     |
        | Cauchy point                      | '^[Cc]auchy'                                        |
        |                                   |                                                     |
        | Dogleg                            | '^[Dd]ogleg'                                        |
        |                                   |                                                     |
        | CG-Steihaug                       | '^[Cc][Gg][-_ ][Ss]teihaug' or '^[Ss]teihaug'       |
        |                                   |                                                     |
        | Exact trust region                | '^[Ee]xact'                                         |
        |___________________________________|_____________________________________________________|


    Unconstrained conjugate gradient methods::
        ___________________________________________________________________________________________
        |                                   |                                                     |
        | Minimisation algorithm            | Patterns                                            |
        |___________________________________|_____________________________________________________|
        |                                   |                                                     |
        | Fletcher-Reeves                   | '^[Ff][Rr]$' or '^[Ff]letcher[-_ ][Rr]eeves$'       |
        |                                   |                                                     |
        | Polak-Ribiere                     | '^[Pp][Rr]$' or '^[Pp]olak[-_ ][Rr]ibiere$'         |
        |                                   |                                                     |
        | Polak-Ribiere +                   | '^[Pp][Rr]\+$' or '^[Pp]olak[-_ ][Rr]ibiere\+$'     |
        |                                   |                                                     |
        | Hestenes-Stiefel                  | '^[Hh][Ss]$' or '^[Hh]estenes[-_ ][Ss]tiefel$'      |
        |___________________________________|_____________________________________________________|


    Miscellaneous unconstrained methods::
        ___________________________________________________________________________________________
        |                                   |                                                     |
        | Minimisation algorithm            | Patterns                                            |
        |___________________________________|_____________________________________________________|
        |                                   |                                                     |
        | Simplex                           | '^[Ss]implex$'                                      |
        |                                   |                                                     |
        | Levenberg-Marquardt               | '^[Ll][Mm]$' or '^[Ll]evenburg-[Mm]arquardt$'       |
        |___________________________________|_____________________________________________________|


    Constrained methods::
        ___________________________________________________________________________________________
        |                                   |                                                     |
        | Minimisation algorithm            | Patterns                                            |
        |___________________________________|_____________________________________________________|
        |                                   |                                                     |
        | Method of Multipliers             | '^[Mm][Oo][Mm]$' or '[Mm]ethod of [Mm]ultipliers$'  |
        |                                   |                                                     |
        | Logarithmic barrier function      | 'Log barrier'                                       |
        |___________________________________|_____________________________________________________|


    Global minimisation methods::
        ___________________________________________________________________________________________
        |                                   |                                                     |
        | Minimisation algorithm            | Patterns                                            |
        |___________________________________|_____________________________________________________|
        |                                   |                                                     |
        | Simulated Annealing               | '^[Ss][Aa]$' or '^[Ss]imulated [Aa]nnealing$'       |
        |___________________________________|_____________________________________________________|



    Minimisation options
    ====================

    The minimisation options can be given in any order.


    Line search algorithms.  These are used in the line search methods and the conjugate gradient methods.  The default is the Backtracking line search.  The algorithms are::
        ___________________________________________________________________________________________
        |                                   |                                                     |
        | Line search algorithm             | Patterns                                            |
        |___________________________________|_____________________________________________________|
        |                                   |                                                     |
        | Backtracking line search          | '^[Bb]ack'                                          |
        |                                   |                                                     |
        | Nocedal and Wright interpolation  | '^[Nn][Ww][Ii]' or                                  |
        | based line search                 | '^[Nn]ocedal[ _][Ww]right[ _][Ii]nt'                |
        |                                   |                                                     |
        | Nocedal and Wright line search    | '^[Nn][Ww][Ww]' or                                  |
        | for the Wolfe conditions          | '^[Nn]ocedal[ _][Ww]right[ _][Ww]olfe'              |
        |                                   |                                                     |
        | More and Thuente line search      | '^[Mm][Tt]' or '^[Mm]ore[ _][Tt]huente$'            |
        |                                   |                                                     |
        | No line search                    | '^[Nn]o [Ll]ine [Ss]earch$'                         |
        |___________________________________|_____________________________________________________|



    Hessian modifications.  These are used in the Newton, Dogleg, and Exact trust region algorithms::
        ___________________________________________________________________________________________
        |                                   |                                                     |
        | Hessian modification              | Patterns                                            |
        |___________________________________|_____________________________________________________|
        |                                   |                                                     |
        | Unmodified Hessian                | '^[Nn]o [Hh]essian [Mm]od'                          |
        |                                   |                                                     |
        | Eigenvalue modification           | '^[Ee]igen'                                         |
        |                                   |                                                     |
        | Cholesky with added multiple of   | '^[Cc]hol'                                          |
        | the identity                      |                                                     |
        |                                   |                                                     |
        | The Gill, Murray, and Wright      | '^[Gg][Mm][Ww]$'                                    |
        | modified Cholesky algorithm       |                                                     |
        |                                   |                                                     |
        | The Schnabel and Eskow 1999       | '^[Ss][Ee]99'                                       |
        | algorithm                         |                                                     |
        |___________________________________|_____________________________________________________|



    Hessian type, these are used in a few of the trust region methods including the Dogleg and Exact trust region algorithms.  In these cases, when the Hessian type is set to Newton, a Hessian modification can also be supplied as above.  The default Hessian type is Newton, and the default Hessian modification when Newton is selected is the GMW algorithm::
        ___________________________________________________________________________________________
        |                                   |                                                     |
        | Hessian type                      | Patterns                                            |
        |___________________________________|_____________________________________________________|
        |                                   |                                                     |
        | Quasi-Newton BFGS                 | '^[Bb][Ff][Gg][Ss]$'                                |
        |                                   |                                                     |
        | Newton                            | '^[Nn]ewton$'                                       |
        |___________________________________|_____________________________________________________|


    For Newton minimisation, the default line search algorithm is the More and Thuente line search, while the default Hessian modification is the GMW algorithm.


    @keyword func:          The function which returns the value.
    @type func:             func
    @keyword dfunc:         The function which returns the gradient.
    @type dfunc:            func
    @keyword d2func:        The function which returns the Hessian.
    @type d2func:           func
    @keyword args:          The tuple of arguments to supply to the functions func, dfunc, and d2func.
    @type args:             tuple
    @keyword x0:            The vector of initial parameter value estimates (as an array).
    @type x0:               numpy rank-1 array
    @keyword min_algor:     A string specifying which minimisation technique to use.
    @type min_algor:        str
    @keyword min_options:   A tuple to pass to the minimisation function as the min_options keyword.
    @type min_options:      tuple
    @keyword func_tol:      The function tolerance value.  Once the function value between iterations decreases below this value, minimisation is terminated.
    @type func_tol:         float
    @keyword grad_tol:      The gradient tolerance value.
    @type grad_tol:         float
    @keyword maxiter:       The maximum number of iterations.
    @type maxiter:          int
    @keyword A:             Linear constraint matrix m*n (A.x >= b).
    @type A:                numpy rank-2 array
    @keyword b:             Linear constraint scalar vector (A.x >= b).
    @type b:                numpy rank-1 array
    @keyword l:             Lower bound constraint vector (l <= x <= u).
    @type l:                numpy rank-1 array
    @keyword u:             Upper bound constraint vector (l <= x <= u).
    @type u:                numpy rank-1 array
    @keyword c:             User supplied constraint function.
    @type c:                func
    @keyword dc:            User supplied constraint gradient function.
    @type dc:               func
    @keyword d2c:           User supplied constraint Hessian function.
    @type d2c:              func
    @keyword print_flag:    A flag specifying how much information should be printed to standard output during minimisation.  0 means no output, 1 means minimal output, and values above 1 increase the amount of output printed. 
    @type print_flag:       int
    @keyword print_prefix:  The text to add out to the front of all print outs.
    @type print_prefix:     str
    @keyword full_output:   A flag specifying which data structures should be returned.
    @type full_output:      bool
    """

    # Catch models with zero parameters.
    ####################################

    if not len(x0):
        # Print out.
        if print_flag:
            print("Cannot run optimisation on a model with zero parameters, directly calculating the function value.")

        # The function value.
        fk = func(x0)

        # The results tuple.
        results = (x0, fk, 0, 1, 0, 0, "No optimisation")

    
    # Unconstrained line search algorithms.
    #######################################

    # Back-and-forth coordinate descent minimisation.
    elif match('^[Cc][Dd]$', min_algor) or match('^[Cc]oordinate[ _-][Dd]escent$', min_algor):
        results = coordinate_descent(func=func, dfunc=dfunc, args=args, x0=x0, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)

    # Steepest descent minimisation.
    elif match('^[Ss][Dd]$', min_algor) or match('^[Ss]teepest[ _-][Dd]escent$', min_algor):
        results = steepest_descent(func=func, dfunc=dfunc, args=args, x0=x0, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)

    # Quasi-Newton BFGS minimisation.
    elif match('^[Bb][Ff][Gg][Ss]$', min_algor):
        results = bfgs(func=func, dfunc=dfunc, args=args, x0=x0, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)

    # Newton minimisation.
    elif match('^[Nn]ewton$', min_algor):
        results = newton(func=func, dfunc=dfunc, d2func=d2func, args=args, x0=x0, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)

    # Newton-CG minimisation.
    elif match('^[Nn]ewton[ _-][Cc][Gg]$', min_algor) or match('^[Nn][Cc][Gg]$', min_algor):
        results = ncg(func=func, dfunc=dfunc, d2func=d2func, args=args, x0=x0, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)


    # Unconstrained trust-region algorithms.
    ########################################

    # Cauchy point minimisation.
    elif match('^[Cc]auchy', min_algor):
        results = cauchy_point(func=func, dfunc=dfunc, d2func=d2func, args=args, x0=x0, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)

    # Dogleg minimisation.
    elif match('^[Dd]ogleg', min_algor):
        results = dogleg(func=func, dfunc=dfunc, d2func=d2func, args=args, x0=x0, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)

    # CG-Steihaug minimisation.
    elif match('^[Cc][Gg][-_ ][Ss]teihaug', min_algor) or match('^[Ss]teihaug', min_algor):
        results = steihaug(func=func, dfunc=dfunc, d2func=d2func, args=args, x0=x0, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)

    # Exact trust region minimisation.
    elif match('^[Ee]xact', min_algor):
        results = exact_trust_region(func=func, dfunc=dfunc, d2func=d2func, args=args, x0=x0, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)


    # Unconstrained conjugate gradient algorithms.
    ##############################################

    # Fletcher-Reeves conjugate gradient minimisation.
    elif match('^[Ff][Rr]$', min_algor) or match('^[Ff]letcher[-_ ][Rr]eeves$', min_algor):
        results = fletcher_reeves(func=func, dfunc=dfunc, args=args, x0=x0, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)

    # Polak-Ribiere conjugate gradient minimisation.
    elif match('^[Pp][Rr]$', min_algor) or match('^[Pp]olak[-_ ][Rr]ibiere$', min_algor):
        results = polak_ribiere(func=func, dfunc=dfunc, args=args, x0=x0, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)

    # Polak-Ribiere + conjugate gradient minimisation.
    elif match('^[Pp][Rr]\+$', min_algor) or match('^[Pp]olak[-_ ][Rr]ibiere\+$', min_algor):
        results = polak_ribiere_plus(func=func, dfunc=dfunc, args=args, x0=x0, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)

    # Hestenes-Stiefel conjugate gradient minimisation.
    elif match('^[Hh][Ss]$', min_algor) or match('^[Hh]estenes[-_ ][Ss]tiefel$', min_algor):
        results = hestenes_stiefel(func=func, dfunc=dfunc, args=args, x0=x0, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)


    # Miscellaneous unconstrained algorithms.
    #########################################

    # Simplex minimisation.
    elif match('^[Ss]implex$', min_algor):
        if func_tol != None:
            results = simplex(func=func, args=args, x0=x0, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)
        elif grad_tol != None:
            results = simplex(func=func, args=args, x0=x0, func_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)
        else:
            raise NameError("Simplex minimisation cannot be setup.")

    # Levenberg-Marquardt minimisation.
    elif match('^[Ll][Mm]$', min_algor) or match('^[Ll]evenburg-[Mm]arquardt$', min_algor):
        results = levenberg_marquardt(chi2_func=func, dchi2_func=dfunc, dfunc=min_options[0], errors=min_options[1], args=args, x0=x0, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)


    # Constrainted algorithms.
    ##########################

    # Method of Multipliers.
    elif match('^[Mm][Oo][Mm]$', min_algor) or match('[Mm]ethod of [Mm]ultipliers$', min_algor):
        results = method_of_multipliers(func=func, dfunc=dfunc, d2func=d2func, args=args, x0=x0, min_options=min_options, A=A, b=b, l=l, u=u, c=c, dc=dc, d2c=d2c, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)

    # Logarithmic barrier function.
    elif min_algor == 'Log barrier':
        results = log_barrier_function(func=func, dfunc=dfunc, d2func=d2func, args=args, x0=x0, min_options=min_options, A=A, b=b, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)


    # Global optimisation algorithms.
    #################################

    # Simulated annealing.
    elif match('^[Ss][Aa]$', min_algor) or match('^[Ss]imulated [Aa]nnealing$', min_algor):
        # No Scipy installed.
        if not SA_flag:
            raise NameError("Simulated annealing is not available as the scipy Python package has not been installed.")

        output = anneal(func=func, x0=x0, args=args, schedule='boltzmann', full_output=full_output, maxiter=maxiter, lower=l, upper=u)

        # The warning.
        warning = None
        if output[6] == 2:
            warning = "Maximum number of iterations reached"
        elif output[6] == 3:
            warning = "Maximum cooling iterations reached"
        elif output[6] == 4:
            warning = "Maximum accepted query locations reached"

        # Rearrange the results.
        results = [
                output[0],  # Parameter vector.
                output[1],  # Function value.
                output[4],  # Number of cooling iterations.
                output[3],  # Number of function evaluations.
                0,
                0,
                warning
        ]


    # No match to minimiser string.
    ###############################

    else:
        raise MinfxError("The '%s' minimisation algorithm is not available.\n" % min_algor)


    # Finish.
    #########

    if print_flag and results is not None:
        print("")
        if full_output:
            xk, fk, k, f_count, g_count, h_count, warning = results
            print(print_prefix + "Parameter values: " + repr(list(xk)))
            print(print_prefix + "Function value:   " + repr(fk))
            print(print_prefix + "Iterations:       " + repr(k))
            print(print_prefix + "Function calls:   " + repr(f_count))
            print(print_prefix + "Gradient calls:   " + repr(g_count))
            print(print_prefix + "Hessian calls:    " + repr(h_count))
            if warning:
                print(print_prefix + "Warning:          " + warning)
            else:
                print(print_prefix + "Warning:          None")
        else:
            print(print_prefix + "Parameter values: " + repr(results))
        print("")

    return results
