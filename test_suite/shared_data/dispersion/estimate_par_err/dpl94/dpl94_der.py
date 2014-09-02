from sympy import *

# In contrast to other Computer Algebra Systems, in SymPy you have to declare symbolic variables explicitly:
r1rho_prime = Symbol('r1rho_prime')
phi_ex = Symbol('phi_ex')
kex = Symbol('kex')
theta = Symbol('theta')
R1 = Symbol('R1')
spin_lock_fields2 = Symbol('spin_lock_fields2')


sin_theta2 = sin(theta)**2
R1_R2 = R1 * cos(theta)**2 + r1rho_prime * sin_theta2
# The numerator.
numer = sin_theta2 * phi_ex * kex
# Denominator.
denom = kex**2 + spin_lock_fields2
back_calc = R1_R2 + numer / denom

d_f_d_r1rho_prime = diff(back_calc, r1rho_prime)
d_f_d_phi_ex = diff(back_calc, phi_ex)
d_f_d_kex = diff(back_calc, kex)
d_f_d_theta = diff(back_calc, theta)
d_f_R1 = diff(back_calc, R1)

print("""Form the Jacobian matrix by:
------------------------------------------------------------------------------

d_f_d_r1rho_prime = %s

d_f_d_phi_ex = %s

d_f_d_kex = %s

d_f_d_theta = %s

d_f_R1 = %s

------------------------------------------------------------------------------
""" % (d_f_d_r1rho_prime, d_f_d_phi_ex, d_f_d_kex, d_f_d_theta, d_f_R1) )


print("""Form the Jacobian matrix by:
------------------------------------------------------------------------------

d_f_d_r1rho_prime = %s

d_f_d_phi_ex = %s

d_f_d_kex = %s

d_f_d_theta = %s

d_f_R1 = %s

------------------------------------------------------------------------------
""" % (simplify(d_f_d_r1rho_prime), simplify(d_f_d_phi_ex), simplify(d_f_d_kex), simplify(d_f_d_theta), simplify(d_f_R1)) )