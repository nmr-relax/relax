from Numeric import Float64, dot, identity, matrixmultiply, outerproduct


def init_data(func, dfunc, d2func, args, x0):
	"Setup values for BFGS minimisation."

	# The initial BFGS function value, gradient vector, and BFGS approximation to the inverse hessian matrix.
	f0 = apply(func, (x0,)+args)
	df0 = apply(dfunc, (x0,)+args)
	d2f0 = identity(len(x0), Float64)

	return f0, df0, d2f0


def dir(dfk, Hk):
	"Calculate the BFGS direction."

	return -matrixmultiply(Hk, dfk)


def matrix_update(xk_new, xk, dfk_new, dfk, Hk):
	"BFGS matrix update."

	sk = xk_new - xk
	yk = dfk_new - dfk
	if dot(yk, sk) == 0:
		raise NameError, "The BFGS matrix is indefinite.  This should not occur."

	rk = 1.0 / dot(yk, sk)

	I = identity(len(xk), Float64)
	a = I - rk*outerproduct(sk, yk)
	b = I - rk*outerproduct(yk, sk)
	c = rk*outerproduct(sk, sk)
	Hk_new = matrixmultiply(matrixmultiply(a, Hk), b) + c
	return Hk_new


def refresh_d2f_args(xk_last, xk, fk_last, fk, dfk_last, dfk, d2fk_last):
	return xk_last, dfk, dfk_last, d2fk_last
