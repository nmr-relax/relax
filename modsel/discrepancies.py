from math import log, pi

class kl:
	def __init__(self):
		"Class used for the calculation of the Kullback-Leibler discrepancy."


	def calc(self, n, chi2, err):
		"Calculate the discrepancy."

		# Sum ln(variance).
		self.sum_ln_var = 0.0
		for i in range(len(err)):
			self.var = float(err[i]) ** 2
			if self.var == 0.0:
				self.ln_var = -1000.0
			else:
				self.ln_var = log(self.var)
			self.sum_ln_var = self.sum_ln_var + self.ln_var

		# Discrepancy.
		self.constant_term = log(2.0 * pi) / 2.0
		self.ln_var_term = self.sum_ln_var / (2.0 * n)
		self.chi2_term = chi2 / (2.0 * n)

		self.kl = self.constant_term + self.ln_var_term + self.chi2_term

		# Debugging code.
		#
		#print "self.kl: " + `self.constant_term` + " + " + `self.ln_var_term` + " + " + `self.chi2_term` + "\t= " + `self.kl`

		# Test K-L.
		#a = n * log(chi2 / n)
		#b = n * log(2.0 * pi)
		#c = n
		#self.kl = a + b + c
		
		return self.kl
