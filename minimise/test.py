import sys
from re import match

from grid import grid
from levenberg_marquardt import levenberg_marquardt


class test:
	def __init__(self, mf):

		self.mf = mf
		self.mf.min_debug = 0
		self.mf.data.calc_frq()
		self.mf.data.calc_constants()
		self.mf.grid = grid(self.mf)
		self.mf.levenberg_marquardt = levenberg_marquardt(self.mf)

		types = [ ['NOE', '600'], ['R1', '600'], ['R2', '600'], ['NOE', '500'], ['R1', '500'], ['R2', '500'] ]

		# S2f = 0.952, S2s = 0.582, ts = 32
		values = [0.44567697591605893, 0.81917801277462055, 8.0577037698155536, 0.50742399909019875, 1.0416801743577564, 7.6074948974342975]
		errors = [0.04, 0.01638356025549241, 0.16115407539631108, 0.05, 0.020833603487155128, 0.15214989794868594] 

		# S2 = 0.388, te = 128, Rex = 0
		#values = [-0.9534604563532787, 0.9177679134957264, 5.993346374650093, -0.77718701713341587, 1.0755202543571325, 5.6779208718023364]
		#errors = [0.04, 0.018355358269914527, 0.11986692749300186, 0.05, 0.021510405087142651, 0.11355841743604674]

		# S2 = 0.388, te = 128, Rex = 0 (Noise)
		#values = [-0.9634604563532787, 0.9177679134957264, 5.793346374650093, -0.71718701713341587, 1.0955202543571325, 5.6779208718023364]
		#errors = [0.04, 0.018355358269914527, 0.11986692749300186, 0.05, 0.021510405087142651, 0.11355841743604674]

		# S2 = 0.388, te = 0, Rex = 0
		#values = [0.82343423455568543, 0.52339677747515456, 5.591649909518364, 0.80450535030695758, 0.6804432206795199, 5.277837198790734]
		#errors = [0.04, 0.010467935549503092, 0.11183299819036728, 0.05, 0.013608864413590398, 0.10555674397581469]

		#start_params = [0.952, 0.582, 32.0 * 1e-12]
		#start_params = [1.000, 100.0 * 1e-12]
		function_ops = ['iso', [10.0 * 1e-9], 'm5']

		grid_ops = []
		if match('m1', function_ops[2]):
			grid_ops.append([20.0, 0.0, 1.0])
		elif match('m2', function_ops[2]):
			grid_ops.append([20.0, 0.0, 1.0])
			grid_ops.append([20.0, 0.0, 10000.0 * 1e-12])
		elif match('m3', function_ops[2]):
			grid_ops.append([20.0, 0.0, 1.0])
			grid_ops.append([20.0, 0.0, 30.0])
		elif match('m4', function_ops[2]):
			grid_ops.append([20.0, 0.0, 1.0])
			grid_ops.append([20.0, 0.0, 10000.0 * 1e-12])
			grid_ops.append([20.0, 0.0, 30.0])
		elif match('m5', function_ops[2]):
			grid_ops.append([20.0, 0.0, 1.0])
			grid_ops.append([20.0, 0.0, 1.0])
			grid_ops.append([20.0, 0.0, 10000.0 * 1e-12])

		print "\n\n<<< Grid search >>>"
		params, chi2 = self.mf.grid.search(self.mf.functions.relax.Ri, function_ops, self.mf.functions.chi2.relax_data, grid_ops, values, types, errors)
		
		print "\nThe grid parameters are: " + `params`
		print "The grid chi-squared value is: " + `chi2`

		print "\n\n<<< LM min >>>"
		params, chi2 = self.mf.levenberg_marquardt.fit(self.mf.functions.relax.Ri, self.mf.functions.relax.dRi, function_ops, self.mf.functions.chi2.relax_data, values, types, errors, params)
		
		print "\n\n<<< Finished minimiser >>>"
		print "The final parameters are: " + `params`
		print "The final chi-squared value is: " + `chi2` + "\n"


if __name__ == "__main__":
	test()
