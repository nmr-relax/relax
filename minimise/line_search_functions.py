from re import match

# Line search functions.
from line_search.backtrack import backtrack
from line_search.nocedal_wright_interpol import nocedal_wright_interpol
from line_search.nocedal_wright_wolfe import nocedal_wright_wolfe
from line_search.more_thuente import more_thuente


class line_search_functions:
	def __init__(self):
		"Class containing line search algorithm code."


	def backline(self):
		"Function for running the backtracking line search."

		self.alpha, fc = backtrack(self.func, self.args, self.xk, self.fk, self.dfk, self.pk, a_init=self.a0)
		self.f_count = self.f_count + fc


	def init_line_functions(self):
		"The line search function."

		if match('^[Bb]ack', self.line_search_algor):
			if self.print_flag:
				print "Line search:  Backtracking line search."
			self.line_search = self.backline
		elif match('^[Nn]ocedal[ _][Ww]right[ _][Ii]nt', self.line_search_algor) or match('^[Nn][Ww][Ii]', self.line_search_algor):
			if self.print_flag:
				print "Line search:  Nocedal and Wright interpolation based line search."
			self.line_search = self.nwi
		elif match('^[Nn]ocedal[ _][Ww]right[ _][Ww]olfe', self.line_search_algor) or match('^[Nn][Ww][Ww]', self.line_search_algor):
			if self.print_flag:
				print "Line search:  Nocedal and Wright line search for the Wolfe conditions."
			self.line_search = self.nww
		elif match('^[Mm]ore[ _][Tt]huente$', self.line_search_algor) or match('^[Mm][Tt]', self.line_search_algor):
			if self.print_flag:
				print "Line search:  Moré and Thuente line search."
			self.line_search = self.mt
		elif match('^[Nn]one$', self.line_search_algor):
			if self.print_flag:
				print "Line search:  No line search."
			self.line_search = self.no_search


	def line_search_option(self, min_options):
		"""Line search options.

		Function for sorting out the minimisation options when the only option can be a line
		search.
		"""

		# Initialise.
		self.line_search_algor = None
		self.init_failure = 0

		# Test if the options are a tuple.
		if type(min_options) != tuple:
			print "The minimisation options " + `min_options` + " is not a tuple."
			self.init_failure = 1; return

		# No more than one option is allowed.
		if len(min_options) > 1:
			print "A maximum of one minimisation options is allowed (the line search algorithm)."
			self.init_failure = 1; return

		# Sort out the minimisation options.
		for opt in min_options:
			if self.valid_line_search(opt):
				self.line_search_algor = opt
			else:
				print "The minimisation option " + `opt` + " from " + `min_options` + " is not a valid line search algorithm."
				self.init_failure = 1; return

		# Default line search algorithm.
		if self.line_search_algor == None:
			self.line_search_algor = 'More Thuente'


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


	def valid_line_search(self, type):
		"Test if the string 'type' is a valid line search algorithm."

		if match('^[Bb]ack', type) or match('^[Nn]ocedal[ _][Ww]right[ _][Ii]nt', type) or match('^[Nn][Ww][Ii]', type) or match('^[Nn]ocedal[ _][Ww]right[ _][Ww]olfe', type) or match('^[Nn][Ww][Ww]', type) or match('^[Mm]ore[ _][Tt]huente$', type) or match('^[Mm][Tt]', type) or match('^[Nn]one$', type):
			return 1
		else:
			return 0
