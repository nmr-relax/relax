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


from re import match
from grid import grid
from coordinate_descent import coordinate_descent
from steepest_descent import steepest_descent
from bfgs import bfgs
from newton import newton
from ncg import ncg
from cauchy_point import cauchy_point
from dogleg import dogleg
from steihaug_cg import steihaug
from exact_trust_region import exact_trust_region
from fletcher_reeves_cg import fletcher_reeves
from polak_ribiere_cg import polak_ribiere
from polak_ribiere_plus_cg import polak_ribiere_plus
from hestenes_stiefel_cg import hestenes_stiefel
from simplex import simplex
from levenberg_marquardt import levenberg_marquardt
from method_of_multipliers import method_of_multipliers


def generic_minimise(func=None, dfunc=None, d2func=None, args=(), x0=None, min_algor=None, min_options=None, func_tol=1e-25, grad_tol=None, maxiter=1e6, A=None, b=None, l=None, u=None, c=None, dc=None, d2c=None, S=None, full_output=0, print_flag=0, print_prefix=""):
    """Generic minimisation function.

    This is a generic function which can be used to access all minimisers using the same set of
    function arguments.  These are the function tolerance value for convergence tests, the maximum
    number of iterations, a flag specifying which data structures should be returned, and a flag
    specifying the amount of detail to print to screen.


    Keyword Arguments
    ~~~~~~~~~~~~~~~~~

    func:  The function which returns the function value.

    dfunc:  The function which returns the gradient vector.

    d2func:  The function which returns the Hessian matrix or approximation.

    args:  The tuple of arguments to supply to the functions func, dfunc, and d2func.

    x0:  The vector of initial parameter value estimates (as an array).

    min_algor:  A string specifying which minimisation technique to use.

    min_options:  A tuple to pass to the minimisation function as the min_options keyword.

    func_tol:  The function tolerance value.  Once the function value between iterations decreases
    below this value, minimisation is terminated.

    maxiter:  The maximum number of iterations.

    A:  Linear constraint matrix m*n (A.x >= b).

    b:  Linear constraint scalar vector (A.x >= b).

    l:  Lower bound constraint vector (l <= x <= u).

    u:  Upper bound constraint vector (l <= x <= u).

    c:  User supplied constraint function.

    dc:  User supplied constraint gradient function.

    d2c:  User supplied constraint Hessian function.

    S:  Constraint scaling vector.

    full_output:  A flag specifying which data structures should be returned.  The following values
    will return, in tuple form, the following data:
        0 - xk
        1 - (xk, fk, k, f_count, g_count, h_count, warning)
    where the data names correspond to:
        xk:      The array of minimised parameter values.
        fk:      The minimised function value.
        k:       The number of iterations.
        f_count: The number of function calls.
        g_count: The number of gradient calls.
        h_count: The number of Hessian calls.
        warning: The warning string.

    print_flag:  A flag specifying how much information should be printed to standard output during
    minimisation.  The print flag corresponds to:
        0 - No output.
        1 - Minimal output.
        2 - Full output.


    Minimisation algorithms
    ~~~~~~~~~~~~~~~~~~~~~~~

    A minimisation function is selected if the string min_algor matches a certain pattern.  Because
    the python regular expression 'match' statement is used, various values of min_algor can be used
    to select the same minimisation algorithm.  Below is a list of the minimisation algorithms
    available together with the corresponding patterns.  Here is a quick description of pattern
    syntax.  The square brakets [] are used to specify a sequence of characters to match to a single
    character within 'min_algor'.  For example Newton minimisation is carried out if a match to the
    pattern '[Nn]ewton' occurs.  Therefore setting min_algor to either 'Newton' or 'newton' will
    select the Newton algorithm.  The symbol '^' placed at the start of the pattern means match to
    the start of 'min_algor' while the symbol '$' placed at the end of the pattern means match to
    the end of 'min_algor'.  For example, one of the Levenberg-Marquardt patterns is '^[Ll][Mm]$'.
    The algorithm is selected by setting min_algor to 'LM' or 'lm'.  Placing any characters before
    or after these strings will result in the algorithm not being selected.

    To select an algorithm set min_algor to a string which matches the given pattern.

    Parameter initialisation methods:
    ___________________________________________________________________________________________
    |                                   |                                                     |
    | Minimisation algorithm            | Patterns                                            |
    |-----------------------------------|-----------------------------------------------------|
    |                                   |                                                     |
    | Grid search                       | '^[Gg]rid'                                          |
    | Fixed parameter values            | '^[Ff]ixed'                                         |
    |-----------------------------------|-----------------------------------------------------|


    Unconstrained line search methods:
    ___________________________________________________________________________________________
    |                                   |                                                     |
    | Minimisation algorithm            | Patterns                                            |
    |-----------------------------------|-----------------------------------------------------|
    |                                   |                                                     |
    | Back-and-forth coordinate descent | '^[Cc][Dd]$' or '^[Cc]oordinate[ _-][Dd]escent$'    |
    | Steepest descent                  | '^[Ss][Dd]$' or '^[Ss]teepest[ _-][Dd]escent$'      |
    | Quasi-Newton BFGS                 | '^[Nn]ewton$'                                       |
    | Newton                            | '^[Bb][Ff][Gg][Ss]$'                                |
    | Newton-CG                         | '^[Nn]ewton[ _-][Cc][Gg]$' or '^[Nn][Cc][Gg]$'      |
    |-----------------------------------|-----------------------------------------------------|


    Unconstrained trust-region methods:
    ___________________________________________________________________________________________
    |                                   |                                                     |
    | Minimisation algorithm            | Patterns                                            |
    |-----------------------------------|-----------------------------------------------------|
    |                                   |                                                     |
    | Cauchy point                      | '^[Cc]auchy'                                        |
    | Dogleg                            | '^[Dd]ogleg'                                        |
    | CG-Steihaug                       | '^[Cc][Gg][-_ ][Ss]teihaug' or '^[Ss]teihaug'       |
    | Exact trust region                | '^[Ee]xact'                                         |
    |-----------------------------------|-----------------------------------------------------|


    Unconstrained conjugate gradient methods:
    ___________________________________________________________________________________________
    |                                   |                                                     |
    | Minimisation algorithm            | Patterns                                            |
    |-----------------------------------|-----------------------------------------------------|
    |                                   |                                                     |
    | Fletcher-Reeves                   | '^[Ff][Rr]$' or '^[Ff]letcher[-_ ][Rr]eeves$'       |
    | Polak-Ribière                     | '^[Pp][Rr]$' or '^[Pp]olak[-_ ][Rr]ibiere$'         |
    | Polak-Ribière +                   | '^[Pp][Rr]\+$' or '^[Pp]olak[-_ ][Rr]ibiere\+$'     |
    | Hestenes-Stiefel                  | '^[Hh][Ss]$' or '^[Hh]estenes[-_ ][Ss]tiefel$'      |
    |-----------------------------------|-----------------------------------------------------|


    Miscellaneous unconstrained methods:
    ___________________________________________________________________________________________
    |                                   |                                                     |
    | Minimisation algorithm            | Patterns                                            |
    |-----------------------------------|-----------------------------------------------------|
    |                                   |                                                     |
    | Simplex                           | '^[Ss]implex$'                                      |
    | Levenberg-Marquardt               | '^[Ll][Mm]$' or '^[Ll]evenburg-[Mm]arquardt$'       |
    |-----------------------------------|-----------------------------------------------------|


    Constrained methods:
    ___________________________________________________________________________________________
    |                                   |                                                     |
    | Minimisation algorithm            | Patterns                                            |
    |-----------------------------------|-----------------------------------------------------|
    |                                   |                                                     |
    | Method of Multipliers             | '^[Mm][Oo][Mm]$' or '[Mm]ethod of [Mm]ultipliers$'  |
    |-----------------------------------|-----------------------------------------------------|



    Minimisation options
    ~~~~~~~~~~~~~~~~~~~~

    This section needs to be completed.
    """

    # Parameter initialisation methods.
    ###################################

    # Grid search.
    if match('^[Gg]rid', min_algor):
        xk, fk, k = grid(func=func, args=args, grid_ops=min_options, A=A, b=b, l=l, u=u, c=c, print_flag=print_flag)
        if full_output:
            results = (xk, fk, k, k, 0, 0, None)
        else:
            results = xk

    # Fixed parameter values.
    elif match('^[Ff]ixed', min_algor):
        if print_flag:
            if print_flag >= 2:
                print print_prefix
            print print_prefix
            print print_prefix + "Fixed initial parameter values"
            print print_prefix + "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        xk = min_options
        fk = apply(func, (xk,)+args)
        if full_output:
            results = (xk, fk, 1, 1, 0, 0, None)
        else:
            results = xk


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

    # Polak-Ribière conjugate gradient minimisation.
    elif match('^[Pp][Rr]$', min_algor) or match('^[Pp]olak[-_ ][Rr]ibiere$', min_algor):
        results = polak_ribiere(func=func, dfunc=dfunc, args=args, x0=x0, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)

    # Polak-Ribière + conjugate gradient minimisation.
    elif match('^[Pp][Rr]\+$', min_algor) or match('^[Pp]olak[-_ ][Rr]ibiere\+$', min_algor):
        results = polak_ribiere_plus(func=func, dfunc=dfunc, args=args, x0=x0, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)

    # Hestenes-Stiefel conjugate gradient minimisation.
    elif match('^[Hh][Ss]$', min_algor) or match('^[Hh]estenes[-_ ][Ss]tiefel$', min_algor):
        results = hestenes_stiefel(func=func, dfunc=dfunc, args=args, x0=x0, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)


    # Miscellaneous unconstrained algorithms.
    #########################################

    # Simplex minimisation.
    elif match('^[Ss]implex$', min_algor):
        if func_tol:
            results = simplex(func=func, args=args, x0=x0, func_tol=func_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)
        elif grad_tol:
            results = simplex(func=func, args=args, x0=x0, func_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)

    # Levenberg-Marquardt minimisation.
    elif match('^[Ll][Mm]$', min_algor) or match('^[Ll]evenburg-[Mm]arquardt$', min_algor):
        results = levenberg_marquardt(chi2_func=func, dchi2_func=dfunc, dfunc=min_options[0], errors=min_options[1], args=args, x0=x0, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag, print_prefix=print_prefix)


    # Constrainted algorithms.
    ##########################

    # Method of Multipliers.
    elif match('^[Mm][Oo][Mm]$', min_algor) or match('[Mm]ethod of [Mm]ultipliers$', min_algor):
        results = method_of_multipliers(func=func, dfunc=dfunc, d2func=d2func, args=args, x0=x0, min_options=min_options, A=A, b=b, l=l, u=u, c=c, dc=dc, d2c=d2c, S=S, func_tol=func_tol, grad_tol=grad_tol, maxiter=maxiter, full_output=full_output, print_flag=print_flag)


    # No match to minimiser string.
    ###############################

    else:
        print print_prefix + "Minimiser type set incorrectly.  The minimiser " + min_algor + " is not programmed.\n"
        return


    # Finish.
    #########

    if print_flag and results != None:
        print ""
        if full_output:
            xk, fk, k, f_count, g_count, h_count, warning = results
            print print_prefix + "Parameter values: " + `xk`
            print print_prefix + "Function value:   " + `fk`
            print print_prefix + "Iterations:       " + `k`
            print print_prefix + "Function calls:   " + `f_count`
            print print_prefix + "Gradient calls:   " + `g_count`
            print print_prefix + "Hessian calls:    " + `h_count`
            if warning:
                print print_prefix + "Warning:          " + warning
            else:
                print print_prefix + "Warning:          None"
        else:
            print print_prefix + "Parameter values: " + `results`
        print ""

    return results
