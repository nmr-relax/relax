# Grid search.
from grid import grid

# Line search minimisers.
from steepest_descent import steepest_descent
from coordinate_descent import coordinate_descent
from newton import newton
from bfgs import bfgs

# Trust region minimisers.
from levenberg_marquardt import levenberg_marquardt

# Line search functions.
from line_search.backtrack import backtrack
from line_search.more_thuente import more_thuente
from line_search.wolfe import wolfe
from line_search.temp import temp


class minimise:
	def __init__(self):
		"Class used to store all the program functions."

		# Line search functions.
		self.line_search_backtrack = backtrack
		self.line_search_more_thuente = more_thuente
		self.line_search_temp = temp
		self.line_search_wolfe = wolfe
		
		# Grid search.
		self.grid = grid

		# Line search minimisers.
		self.steepest_descent = steepest_descent
		self.coordinate_descent = coordinate_descent
		self.newton = newton
		self.bfgs = bfgs

		# Trust region minimisers.
		self.levenberg_marquardt = levenberg_marquardt
