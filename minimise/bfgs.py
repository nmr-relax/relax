from Numeric import Float64, dot, identity, matrixmultiply, outerproduct


def setup(func, dfunc, d2func, f_args, df_args, d2f_args, xk, fk, dfk, d2fk, xk_new, fk_new, dfk_new, d2fk_new, args, print_flag):
	"Setup values for BFGS minimisation."

	if print_flag:
		print "\n\n<<< Quasi-Newton BFGS minimisation >>>"

	# The initial BFGS function value, gradient vector, and BFGS approximation to the inverse hessian matrix.
	fk = apply(func, (xk,)+f_args)
	dfk = apply(dfunc, (xk,)+df_args)
	d2fk = identity(len(xk), Float64)

	d2func = matrix_update
	d2f_args = (dfk, d2fk, xk_new, dfk_new)


def dir(dfk, Hk):
	"Calculate the BFGS direction."

	return -matrixmultiply(Hk, dfk)


def matrix_update(xk, dfk, Hk, xk_new, dfk_new):
	"BFGS matrix update."

	sk = xk_new - xk
	yk = dfk_new - dfk
	if dot(yk, sk) == 0:
		raise NameError, "The BFGS matrix is indefinite.  This should not occur."
		#if full_output:
		#	return xk_new, fk_new, k+1, 2
		#else:
		#	return xk_new

	rk = 1.0 / dot(yk, sk)

	a = I - rk*outerproduct(sk, yk)
	b = I - rk*outerproduct(yk, sk)
	c = rk*outerproduct(sk, sk)
	Hk_new = matrixmultiply(matrixmultiply(a, Hk), b) + c
	return Hk_new
