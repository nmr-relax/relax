from LinearAlgebra import inverse
from Numeric import matrixmultiply


def setup(func, dfunc, d2func, f_args, df_args, d2f_args, xk, fk, dfk, d2fk, args, print_flag):
	"Setup values for Newton minimisation."

	if print_flag:
		print "\n\n<<< Newton minimisation >>>"

	# The initial Newton function value, gradient vector, and hessian matrix.
	fk = apply(func, (xk,)+f_args)
	dfk = apply(dfunc, (xk,)+df_args)
	d2fk = apply(d2func, (xk,)+d2f_args)


def dir(dfk, d2fk):
	"Calculate the Newton direction."

	return -matrixmultiply(inverse(d2fk), dfk)
