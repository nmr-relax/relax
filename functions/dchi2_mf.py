class chi2:
	def __init__(self):
		"Class containing functions to calculate chi squared values."


	def relax_data(self, real, back_calc, err):
		"Calculate the chi squared value for the relaxation data."

		self.chi2 = 0.0
		for i in range(len(real)):
			chi2_i = ( real[i] - back_calc[i] ) ** 2
			if err[i] == 0:
				chi2_i = 1e99
			else:
				chi2_i = chi2_i / (err[i]**2)
			self.chi2 = self.chi2 + chi2_i
		return self.chi2
