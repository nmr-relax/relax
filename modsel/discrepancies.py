from math import log, pi

class kl:
	def __init__(self):
		"Class used for the calculation of the Kullback-Leibler discrepancy."


	def calc(self, n, chi2, err):
		"Calculate the discrepancy."

		# Sum ln(var).
		sum_ln_var = 0.0
		for i in range(len(err)):
			var = float(err[i]) ** 2
			if var == 0.0:
				ln_var = -1000.0
			else:
				ln_var = log(var)
			sum_ln_var = sum_ln_var + ln_var

		# Discrepancy.
		self.kl = n * log(2.0 * pi) + sum_ln_var + chi2
		#print "self.kl: " + `n * log(2.0 * pi)` + " + " + `sum_ln_var` + " + " + `chi2` + "\t= " + `self.kl`
		return self.kl

