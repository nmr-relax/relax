# Calculate the overall discrepency.
#
# The input relaxation data for this method should be the operating model data (the theoretical, back calculated
# relaxation values) which has been Gaussian randomized for a given error.  The original operating model data
# should be placed in the file 'op_data'.  The format of the file should be as follows.  The first line is a
# header line and is ignored.  The columns are:
#	0 - Residue number.
#	1 - Residue name.
#	2 - R1 operating model data (1st field strength).
#	3 - R2 operating model data (1st field strength).
#	4 - NOE operating model data (1st field strength).
#	5 - R1 operating model data (2nd field strength).
#	6 - R2 operating model data (2nd field strength).
#	7 - NOE operating model data (2nd field strength).
#	8 - etc
#
#
# The program is divided into the following stages:
#	Stage 1:   Creation of the files for the modelfree calculations for models 1 to 5 for the randomized
#		data.
#	Stage 2a:  Calculation of the overall discrepency for model selection, and the creation of the final
#		run.  Monte Carlo simulations are used to find errors, and the diffusion tensor is unoptimized.
#		Files are placed in the directory 'final'.
#	Stage 2b:  Calculation of the overall discrepency for model selection, and the creation of the final
#		optimization run.  Monte Carlo simulations are used to find errors, and the diffusion tensor
#		is optimized.  Files are placed in the directory 'optimized'.
#	Stage 3:   Extraction of optimized data.

import sys
from math import log, pi
from re import match

from common_ops import common_operations


class true(common_operations):
	def __init__(self, mf):
		"Calculation of the theoretical overall discrepency."

		self.mf = mf

		print "Modelfree analysis based on the overall discrepency for model selection."
		self.initialize()
		message = "See the file 'true.py' for details."
		self.mf.file_ops.read_file('op_data', message)
		self.mf.data.true.op_data = self.mf.file_ops.open_file(file_name='op_data')
		self.mf.data.runs = ['m1', 'm2', 'm3', 'm4', 'm5']
		self.goto_stage()


	def calc_crit(self, res, n, k, chisq):
		"Calculate the criteria"

		sum_ln_err = 0
		for i in range(len(self.mf.data.relax_data)):
			ln_err = log(float(self.mf.data.relax_data[i][res][3]))
			sum_ln_err = sum_ln_err + ln_err

		if match('^AIC$', self.mf.data.usr_param.method):
			aic = n*log(2*pi) + sum_ln_err + chisq + 2*k
			aic = aic / (2*n)
			return aic

		elif match('^AICc$', self.mf.data.usr_param.method):
			aicc = n*log(2*pi) + sum_ln_err + chisq + 2*k + 2*k*(k+1)/(n-k-1)
			aicc = aicc / (2*n)
			return aicc

		elif match('^BIC$', self.mf.data.usr_param.method):
			bic = n*log(2*pi) + sum_ln_err + chisq + k*log(n)
			bic = bic / ( 2 * n )
			return bic


	def model_selection(self):
		"Model selection."

		data = self.mf.data.data

		self.mf.log.write("\n\n<<< " + self.mf.data.usr_param.method + " model selection >>>")
		for res in range(len(self.mf.data.relax_data[0])):
			self.mf.data.results.append({})
			self.mf.log.write('\n%-22s' % ( "   Checking res " + data['m1'][res]['res_num'] ))

			n = self.mf.data.num_data_sets

			data['m1'][res]['crit'] = self.calc_crit(res, n, k=1, chisq=data['m1'][res]['chi2'])
			data['m2'][res]['crit'] = self.calc_crit(res, n, k=2, chisq=data['m2'][res]['chi2'])
			data['m3'][res]['crit'] = self.calc_crit(res, n, k=2, chisq=data['m3'][res]['chi2'])
			data['m4'][res]['crit'] = self.calc_crit(res, n, k=3, chisq=data['m4'][res]['chi2'])
			data['m5'][res]['crit'] = self.calc_crit(res, n, k=3, chisq=data['m5'][res]['chi2'])

			# Select model.
			min = 'm1'
			for run in self.mf.data.runs:
				if data[run][res]['crit'] < data[min][res]['crit']:
					min = run
			self.mf.data.results[res] = self.fill_results(data[min][res], model=min[1])

			self.mf.log.write("\n\t" + self.mf.data.usr_param.method + " (m1): " + `data['m1'][res]['crit']` + "\n")
			self.mf.log.write("\n\t" + self.mf.data.usr_param.method + " (m2): " + `data['m2'][res]['crit']` + "\n")
			self.mf.log.write("\n\t" + self.mf.data.usr_param.method + " (m3): " + `data['m3'][res]['crit']` + "\n")
			self.mf.log.write("\n\t" + self.mf.data.usr_param.method + " (m4): " + `data['m4'][res]['crit']` + "\n")
			self.mf.log.write("\n\t" + self.mf.data.usr_param.method + " (m5): " + `data['m5'][res]['crit']` + "\n")
			self.mf.log.write("\tThe selected model is: " + min + "\n\n")
