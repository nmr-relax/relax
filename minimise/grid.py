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


from Numeric import Float64, ones, zeros

from constraint_linear import Constraint_linear


def grid(func=None, grid_ops=None, args=(), A=None, b=None, l=None, u=None, c=None, print_flag=0, print_prefix=""):
    """Grid search function.

    Keyword Arguments
    ~~~~~~~~~~~~~~~~~

    func:  The function to minimise.

    grid_ops:  Matrix of options for the grid search.

    args:  The tuple of arguments to supply to the function func.


    Grid options
    ~~~~~~~~~~~~

    The first dimension of grid_ops corresponds to the parameters of the function func, and the
    second dimension corresponds to:
        0 - The number of increments.
        1 - Lower limit.
        2 - Upper limit.
    """

    # Initialise.
    n = len(grid_ops)
    grid_size = 0
    total_steps = 1
    step_num = ones((n))
    params = zeros((n), Float64)
    min_params = zeros((n), Float64)
    param_values = []   # This data structure eliminates the round-off error of summing a step size value to the parameter value.
    for k in xrange(n):
        params[k] = grid_ops[k][1]
        min_params[k] = grid_ops[k][1]
        total_steps = total_steps * grid_ops[k][0]
        param_values.append([])
        for i in xrange(grid_ops[k][0]):
            param_values[k].append(grid_ops[k][1] + i * (grid_ops[k][2] - grid_ops[k][1]) / (grid_ops[k][0] - 1))

    # Print out.
    if print_flag:
        if print_flag >= 2:
            print print_prefix
        print print_prefix
        print print_prefix + "Grid search"
        print print_prefix + "~~~~~~~~~~~"

    # Linear constraints.
    if A != None and b != None:
        constraint_flag = 1
        constraint_linear = Constraint_linear(A, b)
        c = constraint_linear.func
        if print_flag >= 3:
            print print_prefix + "Linear constraint matrices."
            print print_prefix + "A: " + `A`
            print print_prefix + "b: " + `b`

    # Bound constraints.
    elif l != None and u != None:
        constraint_flag = 1
        print "Bound constraints are not implemented yet."
        return

    # General constraints.
    elif c != None:
        constraint_flag = 1

    # No constraints.
    else:
        constraint_flag = 0

    # Set a ridiculously large initial grid value.
    f_min = 1e300

    # Initial print out.
    if print_flag:
        print "\n" + print_prefix + "Searching the grid."

    # Test if the grid is too large (ie total_steps is a long integer)
    if type(total_steps) == long:
        raise NameError, "A grid search of size " + `total_steps` + " is too large."

    # Search the grid.
    k = 0
    for i in xrange(total_steps):
        # Check that the grid point does not violate a constraint, and if it does, skip the function call.
        skip = 0
        if constraint_flag:
            ci = c(params)
            if min(ci) < 0.0:
                if print_flag >= 3:
                    print print_prefix + "%-3s%-8i%-4s%-65s" % ("k:", k, "xk:", `params`)
                    print print_prefix + "Constraint violated, skipping grid point."
                    print print_prefix + "ci: " + `ci`
                    print ""
                skip = 1

        # Function call, test, and increment grid_size.
        if not skip:
            # Back calculate the current function value.
            f = apply(func, (params,)+args)

            # Test if the current function value is less than the least function value.
            if f < f_min:
                f_min = f
                min_params = 1.0 * params

                # Print out code.
                if print_flag:
                    print print_prefix + "%-3s%-8i%-4s%-65s %-4s%-20s" % ("k:", k, "xk:", `min_params`, "fk:", `f_min`)

            # Grid count.
            grid_size = grid_size + 1

            # Print out code.
            if print_flag >= 2:
                if f != f_min:
                    print print_prefix + "%-3s%-8i%-4s%-65s %-4s%-20s" % ("k:", k, "xk:", `params`, "fk:", `f`)
                if print_flag >= 3:
                    print print_prefix + "%-20s%-20s" % ("Increment:", `step_num`)
                    print print_prefix + "%-20s%-20s" % ("Params:", `params`)
                    print print_prefix + "%-20s%-20s" % ("Min params:", `min_params`)
                    print print_prefix + "%-20s%-20g\n" % ("f:", f)
                    print print_prefix + "%-20s%-20g\n" % ("Min f:", f_min)

            # Increment k.
            k = k + 1

        # Increment the grid search.
        for j in xrange(n):
            if step_num[j] < grid_ops[j][0]:
                step_num[j] = step_num[j] + 1
                params[j] = param_values[j][step_num[j]-1]
                break    # Exit so that the other step numbers are not incremented.
            else:
                step_num[j] = 1
                params[j] = grid_ops[j][1]

    # Return the results.
    return min_params, f_min, grid_size
