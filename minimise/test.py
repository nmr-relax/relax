import sys
from levenberg_marquardt import levenberg_marquardt


class test:
	def __init__(self, mf):

		self.mf = mf
		self.mf.min_debug = 0
		self.mf.data.calc_frq()
		self.mf.data.calc_constants()
		self.mf.levenberg_marquardt = levenberg_marquardt(self.mf)

		#values = [0.44567697591605893, 0.81917801277462055, 8.0577037698155536, 0.50742399909019875, 1.0416801743577564, 7.6074948974342975]
		values = [0.82343423455568543, 0.52339677747515456, 5.591649909518364, 0.80450535030695758, 0.6804432206795199, 5.277837198790734]
		types = [ ['NOE', '600'], ['R1', '600'], ['R2', '600'], ['NOE', '500'], ['R1', '500'], ['R2', '500'] ]
		#errors = [0.04, 0.01638356025549241, 0.16115407539631108, 0.05, 0.020833603487155128, 0.15214989794868594] 
		errors = [0.040000000000000001, 0.010467935549503092, 0.11183299819036728, 0.050000000000000003, 0.013608864413590398, 0.10555674397581469]
		start_params = [0.390, 100.0]
		function_ops = ['iso', [10.0 * 1e-9], 'm3']

		params, chi2 = self.mf.levenberg_marquardt.calc(self.mf, self.mf.functions.relax.Ri, self.mf.functions.relax.dRi, function_ops, self.mf.functions.chi2.relax_data, values, types, errors, start_params)


if __name__ == "__main__":
	test()
