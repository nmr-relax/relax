from re import match

# Line search functions.
from line_search.backtrack import backtrack
from line_search.nocedal_wright_interpol import nocedal_wright_interpol
from line_search.nocedal_wright_wolfe import nocedal_wright_wolfe
from line_search.more_thuente import more_thuente


class generic_line_search:
	def __init__(self):
		"Class containing line search algorithm code."


	def line_search(self):
		"The line search function."

		# Initialise.
		fc, gc, hc = 0, 0, 0

		# Backtracking line search.
		if match('^[Bb]ack', self.line_search_algor):
			self.alpha, fc = backtrack(self.func, self.args, self.xk, self.fk, self.dfk, self.pk, a_init=self.a0)
		# Nocedal and Wright interpolation based line search.
		elif match('^[Nn]ocedal[ _][Ww]right[ _][Ii]nt', self.line_search_algor):
			self.alpha, fc = nocedal_wright_interpol(self.func, self.args, self.xk, self.fk, self.dfk, self.pk, a_init=self.a0, mu=self.mu, print_flag=0)
		# Nocedal and Wright line search for the Wolfe conditions.
		elif match('^[Nn]ocedal[ _][Ww]right[ _][Ww]olfe', self.line_search_algor):
			self.alpha, fc, gc = nocedal_wright_wolfe(self.func, self.dfunc, self.args, self.xk, self.fk, self.dfk, self.pk, a_init=self.a0, mu=self.mu, eta=self.eta, print_flag=0)
		# Moré and Thuente line search.
		elif match('^[Mm]ore[ _][Tt]huente$', self.line_search_algor):
			self.alpha, fc, gc = more_thuente(self.func, self.dfunc, self.args, self.xk, self.fk, self.dfk, self.pk, a_init=self.a0, mu=self.mu, eta=self.eta, print_flag=0)
		# No line search.
		elif match('^[Nn]one$', self.line_search_algor):
			self.alpha = self.a0
		# No match to line search string.
		else:
			raise NameError, "The line search algorithm " + self.line_search_algor + " is not coded.\n"

		self.f_count = self.f_count + fc
		self.g_count = self.g_count + gc
		self.h_count = self.h_count + hc
