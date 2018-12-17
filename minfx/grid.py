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
"""The grid search algorithm.

This file is part of the U{minfx optimisation library<https://gna.org/projects/minfx>}.
"""

# Python module imports.
from numpy import array, float64, ones, zeros

# Minfx module imports.
from minfx.base_classes import print_iter
from minfx.constraint_linear import Constraint_linear
from minfx.errors import MinfxError


def grid(func, args=(), num_incs=None, lower=None, upper=None, incs=None, A=None, b=None, l=None, u=None, c=None, sparseness=None, verbosity=0, print_prefix=""):
    """The grid search algorithm.

    @param func:            The target function.  This should take the parameter vector as the first argument and return a single float.
    @type func:             function
    @keyword args:          A tuple of arguments to pass to the function, if needed.
    @type args:             tuple
    @keyword num_incs:      The number of linear increments to be used in the grid search.  The length should be equal to the number of parameters and each element corresponds to the number of increments for the respective parameter. This is overridden if the incs argument is supplied.
    @type num_incs:         list of int
    @keyword lower:         The list of lower bounds for the linear grid search.  This must be supplied if incs is not.
    @type lower:            list of float
    @keyword upper:         The list of upper bounds for the linear grid search.  This must be supplied if incs is not.
    @type upper:            list of float
    @keyword incs:          The parameter increment values.  This overrides the num_incs, lower, and upper arguments used in generating a linear grid.
    @type incs:             list of lists
    @keyword A:             The linear constraint matrix A, such that A.x >= b.
    @type A:                numpy rank-2 array
    @keyword b:             The linear constraint scalar vectors, such that A.x >= b.
    @type b:                numpy rank-1 array
    @keyword l:             The lower bound constraint vector, such that l <= x <= u.
    @type l:                list of float
    @keyword u:             The upper bound constraint vector, such that l <= x <= u.
    @type u:                list of float
    @keyword c:             A user supplied constraint function.
    @type c:                function
    @keyword sparseness:    An optional argument for defining sparsity, or regions of the grid to not search over.  This is a list whereby each element is a list of two parameters indices.  These two parameters will then be assumed to be decoupled and the grid search space between them will be skipped.  Symmetry is not observed, so if [0, 1] is sent in, then maybe [1, 0] should be as well.
    @type sparseness:       list of list of int
    @keyword verbosity:     The verbosity level.  0 corresponds to no output, 1 is standard, and higher values cause greater and greater amount of output.
    @type verbosity:        int
    @keyword print_prefix:  The text to place before the printed output.
    @type print_prefix:     str
    @return:                The optimisation information including the parameter vector at the best grid point, the function value at this grid point, the number of iterations (equal to the number of function calls), and a warning.
    @rtype:                 tuple of numpy rank-1 array, float, int, str
    """

    # Checks.
    if num_incs == None and incs == None:
        raise MinfxError("Either the incs arg or the num_incs, lower, and upper args must be supplied.")
    elif num_incs:
        # Check that this is a list.
        if not isinstance(num_incs, list):
            raise MinfxError("The num_incs argument '%s' must be a list." % num_incs)
        if not isinstance(lower, list):
            raise MinfxError("The lower argument '%s' must be a list." % lower)
        if not isinstance(upper, list):
            raise MinfxError("The upper argument '%s' must be a list." % upper)

        # Lengths.
        if len(num_incs) != len(lower):
            raise MinfxError("The '%s' num_incs and '%s' lower arguments are of different lengths" % (num_incs, lower))
        if len(num_incs) != len(upper):
            raise MinfxError("The '%s' num_incs and '%s' upper arguments are of different lengths" % (num_incs, upper))

    # Catch models with zero parameters.
    if num_incs == [] or incs == []:
        # Print out.
        if verbosity:
            print("Cannot run a grid search on a model with zero parameters, directly calculating the function value.")

        # Empty parameter vector.
        x0 = zeros(0, float64)

        # The function value.
        fk = func(x0)

        # The results tuple.
        return x0, fk, 1, "No optimisation"


    # Initialise.
    if num_incs:
        n = len(num_incs)
    else:
        n = len(incs)
    grid_size = 0
    total_steps = 1
    step_num = ones(n, int)
    min_step = ones(n, int)
    params = zeros((n), float64)
    min_params = zeros((n), float64)
    sparseness_flag = False
    if sparseness != None and len(sparseness):
        sparseness_flag = True

    # Linear grid search.
    # The incs data structure eliminates the round-off error of summing a step size value to the parameter value.
    if num_incs:
        incs = []

        # Loop over the dimensions.
        for k in range(n):
            params[k] = lower[k]
            min_params[k] = lower[k]
            total_steps = total_steps * num_incs[k]
            incs.append([])

            # Loop over the increments of dimension k.
            for i in range(num_incs[k]):
                # Single grid search increment in dimension k, so use the average of the lower and upper.
                if num_incs[k] == 1:
                    incs[k].append((lower[k] + upper[k]) / 2.0)

                # More than 1 increment.
                else:
                    incs[k].append(lower[k] + i * (upper[k] - lower[k]) / (num_incs[k] - 1))

    # User supplied grid search.
    else:
        for k in range(n):
            total_steps = total_steps * len(incs[k])

    # Print out.
    if verbosity:
        if verbosity >= 2:
            print(print_prefix)
        print(print_prefix)
        print(print_prefix + "Grid search")
        print(print_prefix + "~~~~~~~~~~~")

    # Linear constraints.
    if A is not None and b is not None:
        constraint_flag = 1
        constraint_linear = Constraint_linear(A, b)
        c = constraint_linear.func
        if verbosity >= 3:
            print(print_prefix + "Linear constraint matrices.")
            print(print_prefix + "A: " + repr(A))
            print(print_prefix + "b: " + repr(b))

    # Bound constraints.
    elif l != None and u != None:
        constraint_flag = 1
        raise MinfxError("Bound constraints are not implemented yet.")

    # General constraints.
    elif c != None:
        constraint_flag = 1

    # No constraints.
    else:
        constraint_flag = 0

    # Set a ridiculously large initial grid value.
    f_min = 1e300

    # Initial printout.
    if verbosity:
        print("\n" + print_prefix + "Searching through %s grid nodes." % total_steps)

    # Test if the grid is too large.
    if total_steps >= 1e8:
        raise MinfxError("A grid search of size %s is too large." % total_steps)

    # Search the grid.
    k = 0
    curr_dim = 0
    for i in range(total_steps):
        # The flag for skipping the grid point if outside a constraint or in a sparse region.
        skip = False

        # Check that the grid point does not violate a constraint, and if it does, skip the function call.
        if constraint_flag:
            ci = c(params)
            if min(ci) < 0.0:
                if verbosity >= 3:
                    print_iter(k, min_params, print_prefix=print_prefix)
                    print(print_prefix + "Constraint violated, skipping grid point.")
                    print(print_prefix + "ci: " + repr(ci))
                    print("")
                skip = True

        # Check if in a sparse region to skip.
        if sparseness_flag:
            # Loop over the sparseness blocks.
            for block in sparseness:
                # The currently incremented parameter is in the block.
                if curr_dim == block[0]:
                    if step_num[block[1]] != min_step[block[1]]:
                        skip = True
                        break

        # Function call, test, and increment grid_size.
        min_found = False
        if not skip:
            # Back calculate the current function value.
            f = func(*(params,)+args)

            # Test if the current function value is less than the least function value.
            if f < f_min:
                f_min = f
                min_params = 1.0 * params
                min_step = 1.0 * step_num
                min_found = True

                # Print out code.
                if verbosity:
                    print_iter(k=k, xk=min_params, fk=f_min, print_prefix=print_prefix)

            # Grid count.
            grid_size = grid_size + 1

            # Print out code.
            if verbosity >= 2:
                if not min_found:
                    print_iter(k=k, xk=params, fk=f, print_prefix=print_prefix)
                if verbosity >= 3:
                    if min_found:
                        print(print_prefix + "Minimum found.")
                    print(print_prefix + "%-20s%-20s" % ("Increment:", step_num))
                    print(print_prefix + "%-20s%-20s" % ("Current dimension:", curr_dim))
                    print(print_prefix + "%-20s%-20s" % ("Params:", params))
                    print(print_prefix + "%-20s%-20s" % ("Min params:", min_params))
                    print(print_prefix + "%-20s%-20s" % ("Min indices:", min_step))
                    print(print_prefix + "%-20s%-20.8g" % ("f:", f))
                    print(print_prefix + "%-20s%-20.8g\n" % ("Min f:", f_min))

            # Increment k.
            k = k + 1

        # Increment the grid search.
        for j in range(n):
            if step_num[j] < len(incs[j]):
                step_num[j] = step_num[j] + 1
                params[j] = incs[j][step_num[j]-1]
                if j > curr_dim:
                    curr_dim = j
                break    # Exit so that the other step numbers are not incremented.
            else:
                step_num[j] = 1
                params[j] = incs[j][0]

    # Return the results.
    return min_params, f_min, grid_size, None


def grid_point_array(func, args=(), points=None, A=None, b=None, l=None, u=None, c=None, verbosity=0, print_prefix=""):
    """The grid search algorithm.

    @param func:            The target function.  This should take the parameter vector as the first argument and return a single float.
    @type func:             function
    @keyword args:          A tuple of arguments to pass to the function, if needed.
    @type args:             tuple
    @keyword points:        The array of grid points to search over.
    @type points:           list or array of lists of float
    @keyword A:             The linear constraint matrix A, such that A.x >= b.
    @type A:                numpy rank-2 array
    @keyword b:             The linear constraint scalar vectors, such that A.x >= b.
    @type b:                numpy rank-1 array
    @keyword l:             The lower bound constraint vector, such that l <= x <= u.
    @type l:                list of float
    @keyword u:             The upper bound constraint vector, such that l <= x <= u.
    @type u:                list of float
    @keyword c:             A user supplied constraint function.
    @type c:                function
    @keyword verbosity:     The verbosity level.  0 corresponds to no output, 1 is standard, and higher values cause greater and greater amount of output.
    @type verbosity:        int
    @keyword print_prefix:  The text to place before the printed output.
    @type print_prefix:     str
    @return:                The optimisation information including the parameter vector at the best grid point, the function value at this grid point, the number of iterations (equal to the number of function calls), and a warning.
    @rtype:                 tuple of numpy rank-1 array, float, int, str
    """

    # Initialise.
    total_steps = len(points)

    # Skip empty grids.
    if total_steps == 0:
        return None, None, None, None

    # The dimensionality.
    n = len(points[0])

    # Set a ridiculously large initial function value.
    f_min = 1e300

    # Initial printout.
    if verbosity:
        print("\n" + print_prefix + "Searching through %s grid nodes." % total_steps)

    # Test if the grid is too large.
    if total_steps >= 1e8:
        raise MinfxError("A grid search of size %s is too large." % total_steps)

    # Linear constraints.
    if A is not None and b is not None:
        constraint_linear = Constraint_linear(A, b)
        c = constraint_linear.func
        if verbosity >= 3:
            print(print_prefix + "Linear constraint matrices.")
            print(print_prefix + "A: " + repr(A))
            print(print_prefix + "b: " + repr(b))

    # Bound constraints.
    elif l != None and u != None:
        raise MinfxError("Bound constraints are not implemented yet.")

    # The constraint flag.
    constraint_flag = False
    if c != None:
        constraint_flag = True

    # Search the grid.
    for k in range(total_steps):
        # If a grid point violates a constraint, skip it.
        if constraint_flag:
            ci = c(params)
            if min(ci) < 0.0:
                if verbosity >= 3:
                    print_iter(k, min_params, print_prefix=print_prefix)
                    print(print_prefix + "Constraint violated, skipping grid point.")
                    print(print_prefix + "ci: " + repr(ci))
                    print("")
                continue

        # Back calculate the current function value.
        f = func(*(points[k],)+args)

        # A better point.
        if f < f_min:
            # Switch to the new point.
            f_min = f
            min_params = 1.0 * points[k]

            # Print out code.
            if verbosity:
                print_iter(k=k, xk=min_params, fk=f_min, print_prefix=print_prefix)

        # Print out code.
        if verbosity >= 2:
            if f != f_min:
                print_iter(k=k, xk=params, fk=f, print_prefix=print_prefix)
            if verbosity >= 3:
                print(print_prefix + "%-20s%-20s" % ("Params:", repr(points[k])))
                print(print_prefix + "%-20s%-20s" % ("Min params:", repr(min_params)))
                print(print_prefix + "%-20s%-20g\n" % ("f:", f))
                print(print_prefix + "%-20s%-20g\n" % ("Min f:", f_min))

    # Return the results.
    return min_params, f_min, total_steps, None


def grid_split(divisions=None, lower=None, upper=None, inc=None, A=None, b=None, l=None, u=None, c=None, verbosity=0, print_prefix=""):
    """Generator method yielding arrays of grid points.

    This method will loop over the grid points one-by-one, generating a list of points and yielding these for each subdivision.


    @keyword divisions:     The number of grid subdivisions.
    @type divisions:        int
    @keyword lower:         The lower bounds of the grid search which must be equal to the number of parameters in the model.
    @type lower:            array of numbers
    @keyword upper:         The upper bounds of the grid search which must be equal to the number of parameters in the model.
    @type upper:            array of numbers
    @keyword inc:           The increments for each dimension of the space for the grid search.  The number of elements in the array must equal to the number of parameters in the model.
    @type inc:              array of int
    @keyword A:             The linear constraint matrix A, such that A.x >= b.
    @type A:                numpy rank-2 array
    @keyword b:             The linear constraint scalar vectors, such that A.x >= b.
    @type b:                numpy rank-1 array
    @keyword l:             The lower bound constraint vector, such that l <= x <= u.
    @type l:                list of float
    @keyword u:             The upper bound constraint vector, such that l <= x <= u.
    @type u:                list of float
    @keyword c:             A user supplied constraint function.
    @type c:                function
    @keyword verbosity:     The verbosity level.  0 corresponds to no output, 1 is standard, and higher values cause greater and greater amount of output.
    @type verbosity:        int
    @keyword print_prefix:  The text to place before the printed output.
    @type print_prefix:     str
    @return:                A list of grid points for each subdivision is yielded.
    @rtype:                 list of list of float
    """

    # Printout.
    if verbosity and divisions > 1:
        print("%sSplitting up the grid points." % print_prefix)

    # The dimensionality.
    n = len(inc)

    # Linear constraints.
    if A is not None and b is not None:
        constraint_flag = True
        constraint_linear = Constraint_linear(A, b)
        c = constraint_linear.func
        if verbosity >= 3:
            print(print_prefix + "Linear constraint matrices.")
            print(print_prefix + "A: " + repr(A))
            print(print_prefix + "b: " + repr(b))

    # Bound constraints.
    elif l != None and u != None:
        constraint_flag = True
        raise MinfxError("Bound constraints are not implemented yet.")

    # General constraints.
    elif c != None:
        constraint_flag = True

    # No constraints.
    else:
        constraint_flag = False

    # Total number of points.
    total_pts = 1
    for i in range(n):
        total_pts = total_pts * inc[i]

    # Init.
    indices = zeros(n, int)
    pts = zeros((total_pts, n), float64)

    # The increment values for each dimension.
    incs = []
    for k in range(n):
        incs.append([])
        if inc[k] == 1:
            incs[k].append((lower[k] + upper[k])/2.0)
        else:
            for i in range(inc[k]):
                incs[k].append(lower[k] + i * (upper[k] - lower[k]) / (inc[k] - 1))

    # Construct the list of all grid points.
    for i in range(total_pts):
        # Loop over the dimensions.
        for j in range(n):
            # Add the point coordinate.
            pts[i][j] = incs[j][indices[j]]

        # Increment the step positions.
        for j in range(n):
            if indices[j] < inc[j]-1:
                indices[j] += 1
                break    # Exit so that the other step numbers are not incremented.
            else:
                indices[j] = 0

    # Eliminate points outside of constraints.
    if constraint_flag:
        # Loop over all points.
        pts_trimmed = []
        for i in range(total_pts):
            # The constraint values.
            ci = c(pts[i])

            # No constraint violations, so store the point.
            if min(ci) >= 0.0:
                pts_trimmed.append(pts[i])

    # No point elimination.
    else:
        pts_trimmed = pts

    # Convert to numpy.
    pts_trimmed = array(pts_trimmed)

    # The total number of points has changed.
    total_pts = len(pts_trimmed)

    # The subdivision size (round up so the last subdivision is smaller than the rest).
    size_float = total_pts / float(divisions)
    size = int(size_float)
    if size_float % 1:
        size = size + 1

    # Printout.
    if verbosity and divisions > 1:
        print("%s    Total number of grid points:  %20i" % (print_prefix, total_pts))
        print("%s    Number of divisions:          %20i" % (print_prefix, divisions))
        print("%s    Subdivision size:             %20i" % (print_prefix, size))

    # Subdivide.
    for i in range(min(divisions, total_pts)):
        # The start index.
        start = i * size

        # The end index.
        if i != divisions - 1:
            end = (i + 1) * size
        else:
            end = total_pts

        # Yield the subdivision.
        yield pts_trimmed[start: end]


def grid_split_array(divisions=None, points=None, A=None, b=None, l=None, u=None, c=None, verbosity=0, print_prefix=""):
    """Generator method yielding arrays of grid points.

    This method will loop over the grid points one-by-one, generating a list of points and yielding these for each subdivision.


    @keyword divisions:     The number of grid subdivisions.
    @type divisions:        int
    @keyword points:        The array of grid points to split up.
    @type points:           list of lists or rank-2 numpy array
    @keyword A:             The linear constraint matrix A, such that A.x >= b.
    @type A:                numpy rank-2 array
    @keyword b:             The linear constraint scalar vectors, such that A.x >= b.
    @type b:                numpy rank-1 array
    @keyword l:             The lower bound constraint vector, such that l <= x <= u.
    @type l:                list of float
    @keyword u:             The upper bound constraint vector, such that l <= x <= u.
    @type u:                list of float
    @keyword c:             A user supplied constraint function.
    @type c:                function
    @keyword verbosity:     The verbosity level.  0 corresponds to no output, 1 is standard, and higher values cause greater and greater amount of output.
    @type verbosity:        int
    @keyword print_prefix:  The text to place before the printed output.
    @type print_prefix:     str
    @return:                A list of grid points for each subdivision is yielded.
    @rtype:                 list of list of float
    """

    # Printout.
    if verbosity and divisions > 1:
        print("%sSplitting up the array of grid points." % print_prefix)

    # Linear constraints.
    if A is not None and b is not None:
        constraint_flag = True
        constraint_linear = Constraint_linear(A, b)
        c = constraint_linear.func
        if verbosity >= 3:
            print(print_prefix + "Linear constraint matrices.")
            print(print_prefix + "A: " + repr(A))
            print(print_prefix + "b: " + repr(b))

    # Bound constraints.
    elif l != None and u != None:
        constraint_flag = True
        raise MinfxError("Bound constraints are not implemented yet.")

    # General constraints.
    elif c != None:
        constraint_flag = True

    # No constraints.
    else:
        constraint_flag = False

    # Eliminate points outside of constraints.
    if constraint_flag:
        # Loop over all points.
        pts_trimmed = []
        for i in range(len(points)):
            # The constraint values.
            ci = c(points[i])

            # No constraint violations, so store the point.
            if min(ci) >= 0.0:
                pts_trimmed.append(points[i])

    # No point elimination.
    else:
        pts_trimmed = points

    # Convert to numpy.
    pts_trimmed = array(pts_trimmed)

    # Total number of points remaining.
    total_pts = len(pts_trimmed)

    # The subdivision size (round up so the last subdivision is smaller than the rest).
    size_float = total_pts / float(divisions)
    size = int(size_float)
    if size_float % 1:
        size = size + 1

    # Printout.
    if verbosity and divisions > 1:
        print("%s    Total number of grid points:  %20i" % (print_prefix, total_pts))
        print("%s    Number of divisions:          %20i" % (print_prefix, divisions))
        print("%s    Subdivision size:             %20i" % (print_prefix, size))

    # Subdivide.
    for i in range(min(divisions, total_pts)):
        # The start index.
        start = i * size

        # The end index.
        if i != divisions - 1:
            end = (i + 1) * size
        else:
            end = total_pts

        # Yield the subdivision.
        yield pts_trimmed[start: end]
