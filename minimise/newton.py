from LinearAlgebra import inverse
from Numeric import matrixmultiply


def init_data(func, dfunc, d2func, args, x0):
	"Setup values for Newton minimisation."

	# The initial Newton function value, gradient vector, and hessian matrix.
	f0 = apply(func, (x0,)+args)
	df0 = apply(dfunc, (x0,)+args)
	d2f0 = apply(d2func, (x0,)+args)

	return f0, df0, d2f0


def dir(dfk, d2fk):
	"Calculate the Newton direction."

	return -matrixmultiply(inverse(d2fk), dfk)
