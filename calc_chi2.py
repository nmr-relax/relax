class calc_chi2:
	def __init__(self):
		"Class containing functions to calculate chi squared values."


	def relax_data(self, real, real_err, back_calc):
		"Calculate the chi squared value for the relaxation data."

		self.chi2 = 0
		for set in range(len(real)):
			chi2_set = ( real[set] - back_calc[set] ) ** 2
			chi2_set = chi2_set / real_err[set]
			self.chi2 = self.chi2 + chi2_set
		return self.chi2
