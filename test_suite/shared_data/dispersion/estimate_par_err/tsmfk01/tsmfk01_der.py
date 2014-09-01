from sympy import *

# In contrast to other Computer Algebra Systems, in SymPy you have to declare symbolic variables explicitly:
r20a = Symbol('r20a')
dw = Symbol('dw')
k_AB = Symbol('k_AB')
tcp = Symbol('tcp')

denom = dw * tcp
numer = sin(denom)
back_calc = r20a + k_AB - k_AB * numer / denom

d_f_d_r20a = diff(back_calc, r20a)
d_f_d_dw = diff(back_calc, dw)
d_f_d_k_AB = diff(back_calc, k_AB)

print("""Form the Jacobian matrix by:
------------------------------------------------------------------------------

d_f_d_r20a = %s
d_f_d_dw = %s
d_f_d_k_AB = %s
jacobian_matrix = transpose(array( [d_f_d_r20a , d_f_d_dw, d_f_d_k_AB] ) )

d_f_d_r20a = %s
d_f_d_dw = %s
d_f_d_k_AB = %s
jacobian_matrix = transpose(array( [d_f_d_r20a , d_f_d_dw, d_f_d_k_AB] ) )

------------------------------------------------------------------------------
""" % (d_f_d_r20a, d_f_d_dw, d_f_d_k_AB, simplify(d_f_d_r20a), simplify(d_f_d_dw), simplify(d_f_d_k_AB)) )

# Try again.

# The vectorial function.
X = Matrix([r20a + k_AB - k_AB * sin(dw * tcp) / (dw * tcp)])
# What to derive for.
Y = Matrix([r20a, dw, k_AB])

# Make the Jacobian
Jacobian = X.jacobian(Y)

jac_string = str(Jacobian)
jac_string_arr = jac_string.replace("Matrix", "array")

print("""Form the Jacobian matrix by:
------------------------------------------------------------------------------
from numpy import array, cos, sin, pi, transpose

jacobian_matrix_2 = %s

print jacobian_matrix_2
------------------------------------------------------------------------------
""" % (jac_string_arr) )