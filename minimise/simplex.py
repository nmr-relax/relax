import sys
from Numeric import Float64, copy, zeros

from generic_minimise import generic_minimise


class simplex(generic_minimise):
	def __init__(self):
		"Class for downhill simplex minimisation specific functions."


	def minimise(self, func, args, x0, minimiser, func_tol, maxiter, full_output, print_flag):
		"""Downhill simplex minimisation function.

		This code needs extensive modification to work.
		"""

		self.func = func
		self.args = args
		self.xk = x0
		self.minimiser = minimiser
		self.func_tol = func_tol
		self.maxiter = maxiter
		self.full_output = full_output
		self.print_flag = print_flag
		self.print_flag = 2

		# Initialise the function, gradient, and hessian evaluation counters.
		self.f_count = 0
		self.g_count = 0
		self.h_count = 0

		# Initialise the warning string.
		self.warning = None

		self.n = len(self.xk)
		self.m = self.n + 1
		if self.print_flag == 2:
			print "n: " + `self.n`
			print "m: " + `self.m`

		self.factor = 1.0
		self.create_simplex()

		if self.print_flag:
			print "\nThe initial simplex is:\n" + `self.simplex`

		# Create the initial function vector.
		self.fk = zeros(self.m, Float64)
		for i in range(self.m):
			self.fk[i], self.f_count = apply(self.func, (self.simplex[i],)+self.args), self.f_count + 1

		# Print debugging info
		if self.print_flag == 2:
			print "\n\nMinimisation run number: " + `0`
			print "Initial simplex:\n" + `self.simplex`
			print "Initial function vector:\n" + `self.fk`
		minimise_num = 1

		# Iterate until the minimiser is finished.
		while 1:
			# Print debugging info
			if self.print_flag:
				print "\n\n< Minimisation run number: " + `minimise_num` + " >"
				if self.print_flag == 2:
					print "Simplex:\n" + `self.simplex`
					print "Function vector:\n" + `self.fk`

			self.sort_indecies()

			self.calc_center_simplex()

			# Copy the current simplex and function vector to the new data structures.
			self.new_simplex = copy.deepcopy(self.simplex)
			self.new_fk = copy.deepcopy(self.fk)

			# Simplex movement.
			if self.print_flag == 2:
				print "\nReflecting."
			self.reflect()
			if self.print_flag == 2:
				print "Simplex:\n" + `self.new_simplex`
			if self.reflection_fk <= self.fk[self.index_low]:
				if self.print_flag == 2:
					print "\nExtending."
				self.extend()
				if self.print_flag == 2:
					print "Simplex:\n" + `self.new_simplex`
			elif self.reflection_fk >= self.fk[self.index_2nd_high]:
				if self.print_flag == 2:
					print "\nContracting."
				self.contract()
				if self.print_flag == 2:
					print "Simplex:\n" + `self.new_simplex`
				if self.contract_fk >= self.fk[self.index_high]:
					if self.print_flag == 2:
						print "\n\tShrinking."
					self.shrink()
					if self.print_flag == 2:
						print "Simplex:\n" + `self.new_simplex`
			if self.print_flag == 2:
				print "Final simplex:\n" + `self.new_simplex` + "\n"

			# Finish minimising when the function difference is insignificant.
			if abs(self.fk[self.index_high] - self.fk[self.index_low]) < self.func_tol:
				if self.print_flag == 2:
					print "Function diff: " + `self.fk[self.index_high] - self.fk[self.index_low]`
					print "Function diff limit:" + `self.func_tol`
					print "Insignificant function difference, stopped minimising."
				break

			# Update the simplex and function vector.
			self.simplex = copy.deepcopy(self.new_simplex)
			self.fk = copy.deepcopy(self.new_fk)

			# Print debugging info
			if self.print_flag == 2:
				print "New simplex:\n" + `self.simplex`
				print "New function vector:\n" + `self.fk`

			minimise_num = minimise_num + 1
			if minimise_num > self.maxiter:
				self.warning = "Maximum number of iterations reached."
				break

		if self.print_flag:
			print "The final simplex is: " + `self.simplex`
			print "The final function vector is: " + `self.fk`

		self.factor = self.factor / 10.0

		return self.simplex[self.index_low], self.fk[self.index_low], minimise_num, self.f_count, self.g_count, self.h_count, self.warning


	def calc_center_simplex(self):
		"Calculate the center of the simplex."
		self.ave_vector = zeros(self.n, Float64)
		for i in range(self.m):
			self.ave_vector = self.ave_vector + self.simplex[i]
		self.ave_vector = self.ave_vector / float(self.m)
		if self.print_flag == 2:
			print "%-29s%-40s" % ("Ave vector:", `self.ave_vector`)


	def contract(self):
		"Contraction step."

		vect = self.move(self.simplex[self.index_high], -0.5)
		self.contract_fk, self.f_count = apply(self.func, (vect,)+self.args), self.f_count + 1
		if self.print_flag == 2:
			print "\t%-29s%-40s" % ("Contraction vector:", `vect`)
			print "\t%-29s%-40s" % ("Contraction function value:", `self.contract_fk`)

		# Update simplex with the contraction vector.
		if self.contract_fk <= self.fk[self.index_high]:
			self.new_simplex[self.index_high] = copy.deepcopy(vect)
			self.new_fk[self.index_high] = self.contract_fk


	def create_simplex(self):
		"""Function to create the initial simplex.

		self.xk will become the first point of the simplex.
		"""

		self.simplex = zeros((self.m, self.n), Float64)
		for i in range(self.m):
			self.simplex[i] = self.simplex[i] + self.xk
			for j in range(self.n):
				if i == j:
					self.simplex[i+1, j] = self.simplex[i+1, j] + self.factor


	def extend(self):
		"Extension step."

		vect = self.move(self.simplex[self.index_high], 2.0)
		self.extension_fk, self.f_count = apply(self.func, (vect,)+self.args), self.f_count + 1
		if self.print_flag == 2:
			print "\t%-29s%-40s" % ("Extension vector:", `vect`)
			print "\t%-29s%-40s" % ("Extension function value:", `self.extension_fk`)

		# Update simplex with the extension vector.
		if self.extension_fk <= self.fk[self.index_high]:
			self.new_simplex[self.index_high] = copy.deepcopy(vect)
			self.new_fk[self.index_high] = self.extension_fk


	def move(self, vertex, factor):
		"Function to do something?"

		# Calculate the new vector.
		return self.ave_vector*(1.0 + factor) - factor*vertex


	def reflect(self):
		"Reflection step."

		vect = self.move(self.simplex[self.index_high], 1.0)
		self.reflection_fk, self.f_count = apply(self.func, (vect,)+self.args), self.f_count + 1
		if self.print_flag == 2:
			print "\t%-29s%-40s" % ("Reflection vector:", `vect`)
			print "\t%-29s%-40s" % ("Reflection function value:", `self.reflection_fk`)

		# Update simplex with the reflection vector.
		if self.reflection_fk < self.fk[self.index_high]:
			self.new_simplex[self.index_high] = copy.deepcopy(vect)
			self.new_fk[self.index_high] = self.reflection_fk


	def shrink(self):
		"""Shrink step.

		This code has not been debugged!!!
		"""
		# Loop over the vertices.
		for i in range(self.m):
			if i == self.index_low:
				continue
			self.new_simplex[i] = 0.5*(self.simplex[self.index_low] + self.simplex[i])
			self.new_fk[i], self.f_count = apply(self.func, (self.new_simplex[i],)+self.args), self.f_count + 1
		if self.print_flag == 2:
			print "Shrinking"
			print "\t\t%-29s%-40s" % ("Old simplex:", `self.simplex`)
			print "\t\t%-29s%-40s" % ("New simplex:", `self.new_simplex`)


	def sort_indecies(self):
		"Find the simplex point with the lowest function value."
		self.index_high = 0
		self.index_2nd_high = 0
		self.index_low = 0
		for i in range(self.m):
			if self.fk[i] < self.fk[self.index_low]:
				self.index_low = i
			elif self.fk[i] > self.fk[self.index_high]:
				self.index_2nd_high = self.index_high
				self.index_high = i
			elif self.fk[i] > self.fk[self.index_2nd_high]:
				self.index_2nd_high = i

		if self.print_flag == 2:
			print "\n\nIndex high:     " + `self.index_high`
			print "Index 2nd high: " + `self.index_2nd_high`
			print "Index low:      " + `self.index_low`
