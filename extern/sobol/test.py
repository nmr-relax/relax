# Python module imports.
from numpy import float64, ones, zeros
from numpy.linalg import norm

# relax module imports.
from sobol_lib import i4_sobol


# Some variables.
DIM = 3
OFFSET = 0.5 * ones(DIM)

# Loop over different number of points.
for exponent in range(7): 
    # The number of points.
    N = int(10**exponent)

    # Initialise a vector.
    ave_pos = zeros(DIM, float64)

    # Print out.
    print("\nN = %s" % N)

    # Loop over the points.
    for i in range(N):
        # The raw point.
        point, seed = i4_sobol(DIM, i)

        # Sum the point, minus the offset.
        ave_pos += point - OFFSET

    # The average vector length.
    ave_pos = ave_pos / float(N)
    r = norm(ave_pos)
    print("Average vector length: %s" % r)
