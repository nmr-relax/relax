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
		self.mf.data.stage = self.ask_stage()
		title = "<<< Stage " + self.mf.data.stage + " of the asymptotic criteria based model-free analysis >>>\n\n\n"
		self.start_up(self.mf.data.stage, title)
		
		self.mf.data.runs = ['m1', 'm2', 'm3', 'm4', 'm5']

		if match('1', self.mf.data.stage):
			print "\n[ Stage 1 ]\n"
			self.initial_runs()
			print "\n[ End of stage 1 ]\n\n"

		if match('^2', self.mf.data.stage):
			print "\n[ Stage 2 ]\n"
			self.mf.file_ops.mkdir('final')
			self.stage2()
			if match('a$', self.mf.data.stage):
				self.final_run()
			if match('b$', self.mf.data.stage):
				self.final_run_optimized()
			print "\n[ End of stage 2 ]\n\n"

		if match('3', self.mf.data.stage):
			print "\n[ Stage 3 ]\n"
			self.stage3()
			print "\n[ End of stage 3 ]\n\n"


	def aic_model_selection(self):
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


	def bic_model_selection(self):
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

		if match('AIC', self.mf.data.usr_param.method):
			print "\n[ AIC model selection ]\n"
			self.aic_model_selection()
		elif match('BIC', self.mf.data.usr_param.method):
			print "\n[ BIC model selection ]\n"
			self.bic_model_selection()

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
