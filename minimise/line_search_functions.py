from re import match

# Line search functions.
from line_search.backtrack import backtrack
from line_search.nocedal_wright_interpol import nocedal_wright_interpol
from line_search.nocedal_wright_wolfe import nocedal_wright_wolfe
from line_search.more_thuente import more_thuente


class line_search_functions:
	def __init__(self):
		"Class containing line search algorithm code."


	def init_line_functions(self):
		"The line search function."

		if match('^[Bb]ack', self.line_search_algor):
			if self.print_flag:
				print "Line search:  Backtracking line search."
			self.line_search = self.backline
		elif match('^[Nn]ocedal[ _][Ww]right[ _][Ii]nt', self.line_search_algor):
			if self.print_flag:
				print "Line search:  Nocedal and Wright interpolation based line search."
			self.line_search = self.nwi
		elif match('^[Nn]ocedal[ _][Ww]right[ _][Ww]olfe', self.line_search_algor):
			if self.print_flag:
				print "Line search:  Nocedal and Wright line search for the Wolfe conditions."
			self.line_search = self.nww
		elif match('^[Mm]ore[ _][Tt]huente$', self.line_search_algor):
			if self.print_flag:
				print "Line search:  Moré and Thuente line search."
			self.line_search = self.mt
		elif match('^[Nn]one$', self.line_search_algor):
			if self.print_flag:
				print "Line search:  No line search."
			self.line_search = self.no_search
		else:
			raise NameError, "The line search algorithm " + self.line_search_algor + " is not coded.\n"


	def backline(self):
		"Function for running the backtracking line search."

		self.alpha, fc = backtrack(self.func, self.args, self.xk, self.fk, self.dfk, self.pk, a_init=self.a0)
		self.f_count = self.f_count + fc


	def mt(self):
		"Function for running the Moré and Thuente line search."

		self.alpha, fc, gc = more_thuente(self.func, self.dfunc, self.args, self.xk, self.fk, self.dfk, self.pk, a_init=self.a0, mu=self.mu, eta=self.eta, print_flag=0)
		self.f_count = self.f_count + fc
		self.g_count = self.g_count + gc


	def no_search(self):
		"Set alpha to alpha0."

		self.alpha = self.a0


	def nwi(self):
		"Function for running the Nocedal and Wright interpolation based line search."

		self.alpha, fc = nocedal_wright_interpol(self.func, self.args, self.xk, self.fk, self.dfk, self.pk, a_init=self.a0, mu=self.mu, print_flag=0)
		self.f_count = self.f_count + fc


	def nww(self):
		"Function for running the Nocedal and Wright line search for the Wolfe conditions."

		self.alpha, fc, gc = nocedal_wright_wolfe(self.func, self.dfunc, self.args, self.xk, self.fk, self.dfk, self.pk, a_init=self.a0, mu=self.mu, eta=self.eta, print_flag=0)
		self.f_count = self.f_count + fc
		self.g_count = self.g_count + gc


