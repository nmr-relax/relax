# Grid search.
from grid import grid

# Line search minimisers.
from steepest_descent import steepest_descent
from coordinate_descent import coordinate_descent
from newton import newton
from bfgs import bfgs

# Trust region minimisers.
from levenberg_marquardt import levenberg_marquardt

class minimise:
	def __init__(self):
		"Class used to store all the program functions."

		# Grid search.
		self.grid = grid

		# Line search minimisers.
		self.steepest_descent = steepest_descent
		self.coordinate_descent = coordinate_descent
		self.newton = newton
		self.bfgs = bfgs

		# Trust region minimisers.
		self.levenberg_marquardt = levenberg_marquardt
