from sympy import *

# In contrast to other Computer Algebra Systems, in SymPy you have to declare symbolic variables explicitly:
r20a = Symbol('r20a')
r20b = Symbol('r20b')
pA = Symbol('pA')
dw = Symbol('dw')
kex = Symbol('kex')
cpmg_frqs = Symbol('cpmg_frqs')

eta_scale = 2.0**(-3.0/2.0)
pB = 1.0 - pA
dw2 = dw**2
r20_kex = (r20a + r20b + kex) / 2.0
k_BA = pA * kex
k_AB = pB * kex
fact = r20a - r20b - k_BA + k_AB
Psi = fact**2 - dw2 + 4.0*k_BA*k_AB
zeta = 2.0*dw * fact
sqrt_psi2_zeta2 = sqrt(Psi**2 + zeta**2)
D_part = (0.5*Psi + dw2) / sqrt_psi2_zeta2
Dpos = 0.5 + D_part
Dneg = -0.5 + D_part
eta_fact = eta_scale / cpmg_frqs
etapos = eta_fact * sqrt(Psi + sqrt_psi2_zeta2)
etaneg = eta_fact * sqrt(-Psi + sqrt_psi2_zeta2)
fact = Dpos * cosh(etapos) - Dneg * cos(etaneg)
back_calc = cpmg_frqs * acosh(fact)
back_calc = r20_kex - back_calc

d_f_d_r20a = diff(back_calc, r20a)
d_f_d_r20b = diff(back_calc, r20b)
d_f_d_pA = diff(back_calc, pA)
d_f_d_dw = diff(back_calc, dw)
d_f_d_kex = diff(back_calc, kex)

print("""Form the Jacobian matrix by:
------------------------------------------------------------------------------

d_f_d_r20a = %s

d_f_d_r20b = %s

d_f_d_pA = %s

d_f_d_dw = %s

d_f_d_kex = %s

jacobian_matrix = transpose(array( [d_f_d_r20a , d_f_d_r20b, d_f_d_pA, d_f_d_dw, d_f_d_kex] ) )

------------------------------------------------------------------------------
"""% (d_f_d_r20a, d_f_d_r20b, d_f_d_pA, d_f_d_dw, d_f_d_kex) )

# Numpy chokes on this.
#sim_d_f_d_r20a = simplify(d_f_d_r20a)
#sim_d_f_d_r20b = simplify(d_f_d_r20b)
#sim_d_f_d_r20b = simplify(d_f_d_pA)
#sim_d_f_d_dw = simplify(d_f_d_dw)
#sim_d_f_d_kex = simplify(d_f_d_kex)

# The vectorial function.
X = Matrix([back_calc])
# What to derive for.
Y = Matrix([r20a, r20b, pA, dw, kex])

# Make the Jacobian
Jacobian = X.jacobian(Y)

Jac2 = Jacobian.simplify()
#simplify(Jacobian)