# Grid search.
from grid import grid

# Line search minimisers.
from generic_line_search import generic_line_search
from coordinate_descent import coordinate_descent
from steepest_descent import steepest_descent

# Trust region minimisers.
from cauchy_point import cauchy_point
from levenberg_marquardt import levenberg_marquardt

class minimise:
	def __init__(self):
		"Class used to store all the program functions."

		# Grid search.
		self.grid = grid

		# Line search minimisers.
		self.generic_line_search = generic_line_search
		self.coordinate_descent = coordinate_descent
		self.steepest_descent = steepest_descent

		# Trust region minimisers.
		self.cauchy_point = cauchy_point
		self.levenberg_marquardt = levenberg_marquardt
