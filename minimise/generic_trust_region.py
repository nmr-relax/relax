from Numeric import dot, sqrt


class generic_trust_region:
	def __init__(self):
		"Class containing non-specific trust region algorithm code."


	def trust_region_update(self):
		"""An algorithm for trust region radius selection.

		Page 68 from 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright, 1999
		
		First calculate rho using the formula:

			        f(xk) - f(xk + pk)
			rho  =  ------------------
			          mk(0) - mk(pk)

		Where the numerator is called the actual reduction and the denominator is the predicted reduction.

		Secondly choose the trust region radius for the next iteration.
		Finally decide if xk+1 should be shifted to xk.
		"""

		# Actual reduction.
		act_red = self.fk - self.fk_new

		# Predicted reduction.
		mk_pk = self.fk + dot(self.dfk, self.pk) + 0.5 * dot(self.pk, dot(self.d2fk, self.pk))
		pred_red = self.fk - mk_pk

		# Rho.
		if pred_red == 0.0:
			self.rho = 1e99
		else:
			self.rho = act_red / pred_red

		if self.print_flag == 2:
			print "Actual reduction: " + `act_red`
			print "Predicted reduction: " + `pred_red`
			print "fk: " + `self.fk`
			print "mk_pk: " + `mk_pk`
			if pred_red < 0.0:
				import sys
				sys.exit()

		# Calculate the Euclidean norm of pk.
		self.norm_pk = sqrt(dot(self.pk, self.pk))

		# Rho is close to zero or negative, therefore the trust region is shrunk.
		if self.rho < 0.25:
			self.delta = 0.25 * self.norm_pk
			if self.print_flag == 2:
				print "Shrinking the trust region."

		# Rho is close to one and pk has reached the boundary of the trust region, therefore the trust region is expanded.
		elif self.rho > 0.75 and abs(self.norm_pk - self.delta) < 1e-10:
			self.delta = min(2.0*self.delta, self.delta_max)
			if self.print_flag == 2:
				print "Expanding the trust region."

		# Rho is positive but not close to one, therefore the trust region is unaltered.
		else:
			if self.print_flag == 2:
				print "Trust region is unaltered."

		if self.print_flag == 2:
			print "New trust region: " + `self.delta`

		# Choose the position for the next iteration.
		if self.rho > self.eta:
			self.shift_flag = 1
			if self.print_flag == 2:
				print "Moving to: " + `self.xk`
		else:
			self.shift_flag = 0
			if self.print_flag == 2:
				print "Not moving: " + `self.xk`
