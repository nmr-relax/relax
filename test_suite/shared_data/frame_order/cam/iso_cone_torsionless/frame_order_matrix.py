# Script for calculating the frame order matrix from the rotation matrices.

# Python module imports.
from numpy import array, float64, kron, zeros

# relax module imports.
from maths_fns.kronecker_product import kron_prod
from generic_fns.frame_order import print_frame_order_2nd_degree


# Load the matrices.
execfile('rotation_matrices.py')

# Init the matrix.
matrix = zeros((9, 9), float64)

# Loop over the structures.
for i in range(len(R)):
    matrix += kron_prod(R[i], R[i])

# Average.
matrix = matrix / len(R)

# Print out.
print_frame_order_2nd_degree(matrix)
