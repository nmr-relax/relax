from Numeric import copy, dot, sqrt


class generic_trust_region:
	def __init__(self):
		"Class containing non-specific trust region algorithm code."


	def new_param_func(self):
		"""An algorithm for trust region radius selection.

		Page 68 from 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright, 1999
		"""

		# Optain pk.
		self.calc_pk()

		# Evaluate rho.
		self.calc_rho()

		# Calculate the Euclidean norm of pk.
		self.norm_pk = sqrt(dot(self.pk, self.pk))

		if self.print_flag == 2:
			print "Delta orig: " + `self.delta`
			print "rho:        " + `self.rho`
			print "pk:         " + `self.pk`
			print "||pk||:     " + `self.norm_pk`
			print "dfk:        " + `self.dfk`

		# Choose the trust region radius for the next iteration.
		# Rho is close to zero or negative, therefore the trust region is shrunk.
		if self.rho < 0.25:
			self.delta_new = 0.25 * self.norm_pk
		# Rho is close to one and pk has reached the boundary of the trust region, therefore the trust region is expanded.
		elif self.rho > 0.75 and self.norm_pk == self.delta:
			self.delta_new = min(2.0*self.delta, self.delta_max)
		# Rho is positive but not close to one, therefore the trust region is unaltered.
		else:
			self.delta_new = self.delta

		if self.print_flag == 2:
			print "Delta fin: " + `self.delta`

		# Choose the position for the next iteration.
		if self.rho > self.eta:
			self.xk_new = self.xk + self.pk
		else:
			self.xk_new = copy.deepcopy(self.xk)


	def calc_rho(self):
		"""Function to calculate the ratio rho used to choose the trust region radius.

		The ratio is defined as:

			        f(xk) - f(xk + pk)
			rho  =  ------------------
			          mk(0) - mk(pk)

		Where the numerator is called the actual reduction and the denominator is the predicted reduction.
		"""

		# Actual reduction.
		fxkpk, self.f_count = apply(self.func, (self.xk + self.pk,)+self.args), self.f_count + 1
		act_red = self.fk - fxkpk

		# Predicted reduction.
		mk_pk = self.fk + dot(self.dfk, self.pk) + 0.5 * dot(self.pk, dot(self.d2fk, self.pk))
		pred_red = self.fk - mk_pk

		# Rho.
		self.rho = act_red / pred_red
