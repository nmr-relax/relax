# A method based on asymptotic model selection criteria.
#
# The following asymptotic methods are supported:
#	AIC - Akaike Information Criteria
#	BIC - Schwartz Criteria
#
# The program is divided into the following stages:
#	Stage 1:  Creation of the files for the model-free calculations for models 1 to 5.  Monte Carlo
#		simulations are not used on these initial runs, because the errors are not needed (should
#		speed up analysis considerably).
#	Stage 2:  Model selection and the creation of the final run.  Monte Carlo simulations are used to
#		find errors.  This stage has the option of optimizing the diffusion tensor along with the
#		model-free parameters.
#	Stage 3:  Extraction of the data.

import sys
from math import log, pi
from re import match

from asymptotic import asymptotic


class asymptotic(common_operations):
	def __init__(self, mf):
		"Model-free analysis based on asymptotic model selection methods."

		self.mf = mf

		print "Model-free analysis based on BIC model selection."
		self.mf.data.runs = ['m1', 'm2', 'm3', 'm4', 'm5']
		self.initialize()


	def model_selection(self):
		"BIC model selection."
		
		data = self.mf.data.data

		self.mf.log.write("\n\n<<< BIC model selection >>>")
		for res in range(len(self.mf.data.relax_data[0])):
			self.mf.data.results.append({})
			self.mf.log.write('\n%-22s' % ( "   Checking res " + data['m1'][res]['res_num'] ))

			# Set up.
			n = self.mf.data.num_data_sets

			sum_ln_err = 0
			for i in range(len(self.mf.data.relax_data)):
				ln_err = log(float(self.mf.data.relax_data[i][res][3]))
				sum_ln_err = sum_ln_err + ln_err

			# Model 1.
			bic = n*log(2*pi) + sum_ln_err + data['m1'][res]['sse'] + log(1)
			bic = bic / ( 2 * n )
			data['m1'][res]['bic'] = bic

			# Model 2.
			bic = n*log(2*pi) + sum_ln_err + data['m2'][res]['sse'] + log(2)
			bic = bic / ( 2 * n )
			data['m2'][res]['bic'] = bic

			# Model 3.
			bic = n*log(2*pi) + sum_ln_err + data['m3'][res]['sse'] + log(2)
			bic = bic / ( 2 * n )
			data['m3'][res]['bic'] = bic

			# Model 4.
			bic = n*log(2*pi) + sum_ln_err + data['m4'][res]['sse'] + log(3)
			bic = bic / ( 2 * n )
			data['m4'][res]['bic'] = bic

			# Model 5.
			bic = n*log(2*pi) + sum_ln_err + data['m5'][res]['sse'] + log(3)
			bic = bic / ( 2 * n )
			data['m5'][res]['bic'] = bic

			# Select model.
			min = 'm1'
			for run in self.mf.data.runs:
				if data[run][res]['bic'] < data[min][res]['bic']:
					min = run
			self.mf.data.results[res] = self.fill_results(data[min][res], model=min[1])

			self.mf.log.write("\n\tBIC (m1): " + `data['m1'][res]['bic']` + "\n")
			self.mf.log.write("\tBIC (m2): " + `data['m2'][res]['bic']` + "\n")
			self.mf.log.write("\tBIC (m3): " + `data['m3'][res]['bic']` + "\n")
			self.mf.log.write("\tBIC (m4): " + `data['m4'][res]['bic']` + "\n")
			self.mf.log.write("\tBIC (m5): " + `data['m5'][res]['bic']` + "\n")
			self.mf.log.write("\tThe selected model is: " + min + "\n\n")
