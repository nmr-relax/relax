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

from common_ops import common_operations


class asymptotic(common_operations):
	def __init__(self, mf):
		"Model-free analysis based on asymptotic model selection methods."

		self.mf = mf

		print "Model-free analysis based on " + self.mf.data.usr_param.method + " model selection."
		self.initialize()
		self.mf.data.runs = ['m1', 'm2', 'm3', 'm4', 'm5']
		self.goto_stage()


	def calc_crit(self, res, n, k, chisq):
		"Calculate the criteria"

		sum_ln_err = 0
		for i in range(len(self.mf.data.relax_data)):
			if self.mf.data.relax_data[i][res][3] == 0:
				ln_err = -99
			else:
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


	def initial_runs(self):
		"Creation of the files for the Modelfree calculations for models 1 to 5."
		
		for run in self.mf.data.runs:
			print "Creating input files for model " + run
			self.mf.log.write("\n\n<<< Model " + run + " >>>\n\n")
			self.mf.file_ops.mkdir(dir=run)
			self.mf.file_ops.open_mf_files(dir=run)
			self.set_run_flags(run)
			self.log_params('M1', self.mf.data.usr_param.md1)
			self.log_params('M2', self.mf.data.usr_param.md2)
			self.create_mfin(sims='n', sim_type='pred')
			self.create_run(dir=run)
			for res in range(len(self.mf.data.relax_data[0])):
				# Mfdata.
				self.create_mfdata(res)
				# Mfmodel.
				self.create_mfmodel(res, self.mf.data.usr_param.md1, type='M1')
				# Mfpar.
				self.create_mfpar(res)
			self.mf.file_ops.close_mf_files(dir=run)


	def model_selection(self):
		"Model selection."
		
		data = self.mf.data.data

		self.mf.log.write("\n\n<<< " + self.mf.data.usr_param.method + " model selection >>>")
		for res in range(len(self.mf.data.relax_data[0])):
			self.mf.data.results.append({})
			self.mf.log.write('\n%-22s' % ( "   Checking res " + data['m1'][res]['res_num'] ))

			n = self.mf.data.num_data_sets

			data['m1'][res]['crit'] = self.calc_crit(res, n, k=1, chisq=data['m1'][res]['sse'])
			data['m2'][res]['crit'] = self.calc_crit(res, n, k=2, chisq=data['m2'][res]['sse'])
			data['m3'][res]['crit'] = self.calc_crit(res, n, k=2, chisq=data['m3'][res]['sse'])
			data['m4'][res]['crit'] = self.calc_crit(res, n, k=3, chisq=data['m4'][res]['sse'])
			data['m5'][res]['crit'] = self.calc_crit(res, n, k=3, chisq=data['m5'][res]['sse'])

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


	def stage2(self):
		self.mf.file_ops.mkdir('grace')
		
		print "\n[ Model-free data extraction ]\n"
		for run in self.mf.data.runs:
			mfout = self.mf.file_ops.read_file(run + '/mfout')
			mfout_lines = mfout.readlines()
			mfout.close()
			print "Extracting model-free data from " + run + "/mfout."
			num_res = len(self.mf.data.relax_data[0])
			self.mf.data.data[run] = self.mf.star.extract(mfout_lines, num_res)

 		print "\n[ " + self.mf.data.usr_param.method + " model selection ]\n"
		self.model_selection()

		print "\n[ Printing results ]\n"
		self.print_results()

		print "\n[ Placing data structures into \"data_all\" ]\n"
		self.print_data()

		print "\n[ Grace file creation ]\n"
		self.grace('grace/S2.agr', 'S2', subtitle="After model selection, unoptimized")
		self.grace('grace/S2f.agr', 'S2f', subtitle="After model selection, unoptimized")
		self.grace('grace/S2s.agr', 'S2s', subtitle="After model selection, unoptimized")
		self.grace('grace/te.agr', 'te', subtitle="After model selection, unoptimized")
		self.grace('grace/Rex.agr', 'Rex', subtitle="After model selection, unoptimized")
		self.grace('grace/SSE.agr', 'SSE', subtitle="After model selection, unoptimized")
