# A method based on asymptotic model selection criteria.
#
# The following asymptotic methods are supported:
#	AIC - Akaike Information Criteria
#	AICc - Akaike Information Criteria corrected for small sample sizes 
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

from common_ops import common_operations


class asymptotic(common_operations):
	def __init__(self, mf):
		"Model-free analysis based on asymptotic model selection methods."

		self.mf = mf

		print "Model-free analysis based on " + self.mf.data.usr_param.method + " model selection."
		self.initialize()
		self.mf.data.runs = ['m1', 'm2', 'm3', 'm4', 'm5']
		self.mf.data.mfin.default_data()
		self.goto_stage()


	def calc_crit(self, res, n, k, chisq):
		"Calculate the criteria."

		sum_ln_err = 0.0
		for i in range(len(self.mf.data.relax_data)):
			if self.mf.data.relax_data[i][res][3] == 0:
				ln_err = -99.0
			else:
				ln_err = log(float(self.mf.data.relax_data[i][res][3]))
			sum_ln_err = sum_ln_err + ln_err

		if match('^AIC$', self.mf.data.usr_param.method):
			aic = n*log(2.0*pi) + sum_ln_err + chisq + 2.0*k
			aic = aic / (2.0*n)
			return aic

		elif match('^AICc$', self.mf.data.usr_param.method):
			aicc = n*log(2.0*pi) + sum_ln_err + chisq + 2.0*k + 2.0*k*(k+1.0)/(n-k-1.0)
			aicc = aicc / (2.0*n)
			return aicc

		elif match('^BIC$', self.mf.data.usr_param.method):
			bic = n*log(2.0*pi) + sum_ln_err + chisq + k*log(n)
			bic = bic / ( 2.0 * n )
			return bic


	def model_selection(self):
		"Model selection."

		data = self.mf.data.data

		self.mf.log.write("\n\n<<< " + self.mf.data.usr_param.method + " model selection >>>")
		for res in range(len(self.mf.data.relax_data[0])):
			self.mf.data.results.append({})
			self.mf.log.write('\n%-22s' % ( "   Checking res " + data['m1'][res]['res_num'] ))

			n = float(self.mf.data.num_data_sets)

			data['m1'][res]['crit'] = self.calc_crit(res, n, k=1.0, chisq=data['m1'][res]['chi2'])
			data['m2'][res]['crit'] = self.calc_crit(res, n, k=2.0, chisq=data['m2'][res]['chi2'])
			data['m3'][res]['crit'] = self.calc_crit(res, n, k=2.0, chisq=data['m3'][res]['chi2'])
			data['m4'][res]['crit'] = self.calc_crit(res, n, k=3.0, chisq=data['m4'][res]['chi2'])
			data['m5'][res]['crit'] = self.calc_crit(res, n, k=3.0, chisq=data['m5'][res]['chi2'])

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


	def print_data(self):
		"Print all the data into the 'data_all' file."

		file = open('data_all', 'w')

		sys.stdout.write("[")
		for res in range(len(self.mf.data.results)):
			sys.stdout.write("-")
			file.write("\n\n<<< Residue " + self.mf.data.results[res]['res_num'])
			file.write(", Model " + self.mf.data.results[res]['model'] + " >>>\n")
			file.write('%-20s' % '')
			file.write('%-17s' % 'Model 1')
			file.write('%-17s' % 'Model 2')
			file.write('%-17s' % 'Model 3')
			file.write('%-17s' % 'Model 4')
			file.write('%-17s' % 'Model 5')

			# S2.
			file.write('\n%-20s' % 'S2')
			for run in self.mf.data.runs:
				if match('^m', run):
					file.write('%8.3f' % self.mf.data.data[run][res]['s2'])
					file.write('%1s' % '±')
					file.write('%-8.3f' % self.mf.data.data[run][res]['s2_err'])

			# S2f.
			file.write('\n%-20s' % 'S2f')
			for run in self.mf.data.runs:
				if match('^m', run):
					file.write('%8.3f' % self.mf.data.data[run][res]['s2f'])
					file.write('%1s' % '±')
					file.write('%-8.3f' % self.mf.data.data[run][res]['s2f_err'])

			# S2s.
			file.write('\n%-20s' % 'S2s')
			for run in self.mf.data.runs:
				if match('^m', run):
					file.write('%8.3f' % self.mf.data.data[run][res]['s2s'])
					file.write('%1s' % '±')
					file.write('%-8.3f' % self.mf.data.data[run][res]['s2s_err'])

			# te.
			file.write('\n%-20s' % 'te')
			for run in self.mf.data.runs:
				if match('^m', run):
					file.write('%8.3f' % self.mf.data.data[run][res]['te'])
					file.write('%1s' % '±')
					file.write('%-8.3f' % self.mf.data.data[run][res]['te_err'])

			# Rex.
			file.write('\n%-20s' % 'Rex')
			for run in self.mf.data.runs:
				if match('^m', run):
					file.write('%8.3f' % self.mf.data.data[run][res]['rex'])
					file.write('%1s' % '±')
					file.write('%-8.3f' % self.mf.data.data[run][res]['rex_err'])

			# Chi2.
			file.write('\n%-20s' % 'Chi2')
			for run in self.mf.data.runs:
				if match('^m', run):
					file.write('%-17.3f' % self.mf.data.data[run][res]['chi2'])

			# Model selection criteria.
			file.write('\n%-20s' % self.mf.data.usr_param.method)
			for run in self.mf.data.runs:
				if match('^m', run):
					file.write('%-17.6f' % self.mf.data.data[run][res]['crit'])

		file.write('\n')
		sys.stdout.write("]\n")
		file.close()


	def set_vars_stage_initial(self):
		"Set the options for the initial runs."
		
		self.mf.data.mfin.sims = 'n'


	def set_vars_stage_selection(self):
		"Set the options for the final run."
		
		self.mf.data.mfin.sims = 'y'
