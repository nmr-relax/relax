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


class aic(asymptotic):
	def __init__(self, mf):
		"Model-free analysis based on AIC model selection methods."

		self.mf = mf

		print "Model-free analysis based on AIC model selection."
		self.mf.data.runs = ['m1', 'm2', 'm3', 'm4', 'm5']
		self.initialize()


	def model_selection(self):
		"AIC model selection."
		
		data = self.mf.data.data

		self.mf.log.write("\n\n<<< AIC model selection >>>")
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
			aic = n*log(2*pi) + sum_ln_err + data['m1'][res]['sse'] + 2*1
			aic = aic / ( 2 * n )
			data['m1'][res]['aic'] = aic

			# Model 2.
			aic = n*log(2*pi) + sum_ln_err + data['m2'][res]['sse'] + 2*2
			aic = aic / ( 2 * n )
			data['m2'][res]['aic'] = aic

			# Model 3.
			aic = n*log(2*pi) + sum_ln_err + data['m3'][res]['sse'] + 2*2
			aic = aic / ( 2 * n )
			data['m3'][res]['aic'] = aic

			# Model 4.
			aic = n*log(2*pi) + sum_ln_err + data['m4'][res]['sse'] + 2*3
			aic = aic / ( 2 * n )
			data['m4'][res]['aic'] = aic

			# Model 5.
			aic = n*log(2*pi) + sum_ln_err + data['m5'][res]['sse'] + 2*3
			aic = aic / ( 2 * n )
			data['m5'][res]['aic'] = aic

			# Select model.
			min = 'm1'
			for run in self.mf.data.runs:
				if data[run][res]['aic'] < data[min][res]['aic']:
					min = run
			self.mf.data.results[res] = self.fill_results(data[min][res], model=min[1])

			self.mf.log.write("\n\tAIC (m1): " + `data['m1'][res]['aic']` + "\n")
			self.mf.log.write("\tAIC (m2): " + `data['m2'][res]['aic']` + "\n")
			self.mf.log.write("\tAIC (m3): " + `data['m3'][res]['aic']` + "\n")
			self.mf.log.write("\tAIC (m4): " + `data['m4'][res]['aic']` + "\n")
			self.mf.log.write("\tAIC (m5): " + `data['m5'][res]['aic']` + "\n")
			self.mf.log.write("\tThe selected model is: " + min + "\n\n")
