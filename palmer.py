# The method given by (Mandel et al., 1995) is divided into the three stages:
#
#	Stage 1:  Creation of the files for the initial model-free calculations for models 1 to 5,
#		and f-tests between them.
#	Stage 2:  Model selection and the creation of the final run.  Monte Carlo simulations are used to
#		find errors.  This stage has the option of optimizing the diffusion tensor along with the
#		model-free parameters.
#	Stage 3:  Extraction of the data.
#
# These stages are repeated until the data converges.

import sys
from re import match

from common_ops import common_operations


class palmer(common_operations):
	def __init__(self, mf):
		"The model-free analysis of Palmer."

		self.mf = mf

		print "Palmer's method for model-free analysis. (Mandel et al., 1995)"
		self.mf.data.stage = self.ask_stage()
		title = "<<< Stage " + self.mf.data.stage + " of Palmer's method for model-free analysis >>>\n\n\n"
		self.start_up(self.mf.data.stage, title)

		self.mf.data.runs = ['m1', 'm2', 'm3', 'm4', 'm5', 'f-m1m2', 'f-m1m3']
		if self.mf.data.num_data_sets > 3:
			self.mf.data.runs.append('f-m2m4')
			self.mf.data.runs.append('f-m2m5')
			self.mf.data.runs.append('f-m3m4')

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


	def initial_runs(self):
		"Creation of the files for the Modelfree calculations for models 1 to 5 and the F-tests."
		
		for run in self.mf.data.runs:
			if match('^m', run):
				print "Creating input files for model " + run
				self.mf.log.write("\n\n<<< Model " + run + " >>>\n\n")
			elif match('^f', run):
				print "Creating input files for the F-test " + run
				self.mf.log.write("\n\n<<< F-test " + run + " >>>\n\n")
			else:
				print "The run '" + run + "'does not start with an m or f, quitting script!\n\n"
				sys.exit()
			self.mf.file_ops.mkdir(dir=run)
			self.mf.file_ops.open_mf_files(dir=run)
			self.set_run_flags(run)
			self.log_params('M1', self.mf.data.usr_param.md1)
			self.log_params('M2', self.mf.data.usr_param.md2)
			if match('^m', run):
				self.create_mfin(sims='y', sim_type='pred')
			elif match('^f', run):
				self.create_mfin(sel='ftest', sims='y', sim_type='pred')
			self.create_run(dir=run)
			for res in range(len(self.mf.data.relax_data[0])):
				# Mfdata.
				self.create_mfdata(res)
				# Mfmodel.
				self.create_mfmodel(res, self.mf.data.usr_param.md1, type='M1')
				if match('^f', run):
					self.create_mfmodel(res, self.mf.data.usr_param.md2, type='M2')
				# Mfpar.
				self.create_mfpar(res)
			self.mf.file_ops.close_mf_files(dir=run)


	def model_selection(self):
		"Palmer's model selection."

		data = self.mf.data.data

		self.mf.log.write("\n\n<<< Palmer's model selection >>>")
		for res in range(len(self.mf.data.relax_data[0])):
			self.mf.data.results.append({})
			self.mf.log.write('\n%-22s' % ( "   Checking res " + data['m1'][res]['res_num'] ))

			# Model 1 test.
			if data['m1'][res]['sse_test'] == 1:
				self.mf.log.write('%-12s' % '[Model 1]')
				self.mf.data.results[res] = self.fill_results(data['m1'][res], model='1')

			# Test if both model 2 and 3 fit!!! (Should not occur)
			elif data['m2'][res]['sse_test'] == 1 and data['f-m1m2'][res]['ftest'] == 1 \
				and data['m3'][res]['sse_test'] == 1 and data['f-m1m3'][res]['ftest'] == 1:
				self.mf.log.write('%-12s' % '[Model 2 and 3]')
				self.mf.data.results[res] = self.fill_results(data['m1'][res], model='2+3')

			# Model 2 test.
			elif data['m2'][res]['sse_test'] == 1 and data['f-m1m2'][res]['ftest'] == 1:
				self.mf.log.write('%-12s' % '[Model 2]')
				self.mf.data.results[res] = self.fill_results(data['m2'][res], model='2')

			# Model 3 test.
			elif data['m3'][res]['sse_test'] == 1 and data['f-m1m3'][res]['ftest'] == 1:
				self.mf.log.write('%-12s' % '[Model 3]')
				self.mf.data.results[res] = self.fill_results(data['m3'][res], model='3')

			# Large SSE test for model 1.
			elif data['m1'][res]['large_sse'] == 0:
				self.mf.log.write('%-12s' % '[Model 1*]')
				self.mf.data.results[res] = self.fill_results(data['m1'][res], model='1')

			# Test if both model 4 and 5 fit!!! (Should not occur)
			elif data['m4'][res]['zero_sse'] == 1 and data['m5'][res]['zero_sse'] == 1:
				self.mf.log.write('%-12s' % '[Model 4 and 5]')
				self.mf.data.results[res] = self.fill_results(data['m1'][res], model='4+5')
				
			# Model 4 test.
			elif data['m4'][res]['zero_sse'] == 1:
				self.mf.log.write('%-12s' % '[Model 4]')
				self.mf.data.results[res] = self.fill_results(data['m4'][res], model='4')

			# Model 5 test.
			elif data['m5'][res]['zero_sse'] == 1:
				self.mf.log.write('%-12s' % '[Model 5]')
				self.mf.data.results[res] = self.fill_results(data['m5'][res], model='5')

			# No model fits!
			else:
				self.mf.log.write('%-12s' % '[Model 0]')
				self.mf.data.results[res] = self.fill_results(data['m1'][res], model='0')


	def model_selection_extended(self):
		"""Palmer's model selection (extended).
		
		Palmer's model selection, but with additional chi-squared and F-tests for models 4 and 5
		because the number of degrees of freedom for these models are greater than 0.  See the code
		below for details of these changes.
		"""

		data = self.mf.data.data

		self.mf.log.write("\n\n<<< Palmer's model selection (extended) >>>")
		for res in range(len(self.mf.data.relax_data[0])):
			self.mf.data.results.append({})
			self.mf.log.write('\n%-22s' % ( "   Checking res " + data['m1'][res]['res_num'] ))

			# Model 1 test.
			if data['m1'][res]['sse_test'] == 1:
				self.mf.log.write('%-12s' % '[Model 1]')
				self.mf.data.results[res] = self.fill_results(data['m1'][res], model='1')

			# Test if both model 2 and 3 fit!!! (Should not occur)
			elif data['m2'][res]['sse_test'] == 1 and data['f-m1m2'][res]['ftest'] == 1 \
				and data['m3'][res]['sse_test'] == 1 and data['f-m1m3'][res]['ftest'] == 1:
				self.mf.log.write('%-12s' % '[Model 2 and 3]')
				self.mf.data.results[res] = self.fill_results(data['m1'][res], model='2+3')

			# Model 2 test.
			elif data['m2'][res]['sse_test'] == 1 and data['f-m1m2'][res]['ftest'] == 1:
				self.mf.log.write('%-12s' % '[Model 2]')
				self.mf.data.results[res] = self.fill_results(data['m2'][res], model='2')

			# Model 3 test.
			elif data['m3'][res]['sse_test'] == 1 and data['f-m1m3'][res]['ftest'] == 1:
				self.mf.log.write('%-12s' % '[Model 3]')
				self.mf.data.results[res] = self.fill_results(data['m3'][res], model='3')

			# Large SSE test for model 1.
			elif data['m1'][res]['large_sse'] == 0:
				self.mf.log.write('%-12s' % '[Model 1*]')
				self.mf.data.results[res] = self.fill_results(data['m1'][res], model='1')

			# Test if both model 4 and 5 fit!!! (Should not occur)
			elif data['m4'][res]['sse_test'] == 1 and ( data['f-m2m4'][res]['ftest'] == 1 or data['f-m3m4'][res]['ftest'] == 1 ) \
				and data['m5'][res]['sse_test'] == 1 and data['f-m2m5'][res]['ftest'] == 1:
				self.mf.log.write('%-12s' % '[Model 4 and 5]')
				self.mf.data.results[res] = self.fill_results(data['m1'][res], model='4+5')
				
			# Model 4 test.
			elif data['m4'][res]['sse_test'] == 1 and ( data['f-m2m4'][res]['ftest'] == 1 or data['f-m3m4'][res]['ftest'] == 1 ):
				self.mf.log.write('%-12s' % '[Model 4]')
				self.mf.data.results[res] = self.fill_results(data['m4'][res], model='4')
				
			# Model 5 test.
			elif data['m5'][res]['sse_test'] == 1 and data['f-m2m5'][res]['ftest'] == 1:
				self.mf.log.write('%-12s' % '[Model 5]')
				self.mf.data.results[res] = self.fill_results(data['m5'][res], model='5')

			# No model fits!
			else:
				self.mf.log.write('%-12s' % '[Model 0]')
				self.mf.data.results[res] = self.fill_results(data['m1'][res], model='0')


	def stage2(self):
		self.mf.file_ops.mkdir('grace')

		print "\n[ Model-free data extraction ]\n"
		for run in self.mf.data.runs:
			mfout = self.mf.file_ops.read_file(run + '/mfout')
			mfout_lines = mfout.readlines()
			mfout.close()
			print "Extracting model-free data from " + run + "/mfout."
			num_res = len(self.mf.data.relax_data[0])
			if match('^m', run):
				self.mf.data.data[run] = self.mf.star.extract(mfout_lines, num_res, self.mf.data.usr_param.sse_lim, self.mf.data.usr_param.ftest_lim, float(self.mf.data.usr_param.large_sse), ftest='n')
			if match('^f', run):
				self.mf.data.data[run] = self.mf.star.extract(mfout_lines, num_res, self.mf.data.usr_param.sse_lim, self.mf.data.usr_param.ftest_lim, float(self.mf.data.usr_param.large_sse), ftest='y')

		print "\n[ Palmer's model selection ]\n"
		if self.mf.data.num_data_sets > 3:
			# ie degrees of freedom > 0 in all models.
			self.mf.log.write("Extended model selection.\n\n")
			print "The number of data sets is greater than 3."
			print "\tRunning Palmer's model selection, with additional chi-squared and F-tests"
			print "\tfor models 4 and 5 (the degrees of freedom for these models are greater than 0).\n"
			self.model_selection_extended()
		else:
			self.mf.log.write("Normal model selection.\n\n")
			print "The number of data sets is equal to 3."
			print "\tRunning Palmer's model selection.\n"
			self.model_selection()

		print "\n[ Printing results ]\n"
		self.print_results()

		print "\n[ Placing data structures into \"data_all\" ]\n"
		self.print_data(ftests='y')

		print "\n[ Grace file creation ]\n"
		self.grace('grace/S2.agr', 'S2', subtitle="After model selection, unoptimized")
		self.grace('grace/S2f.agr', 'S2f', subtitle="After model selection, unoptimized")
		self.grace('grace/S2s.agr', 'S2s', subtitle="After model selection, unoptimized")
		self.grace('grace/te.agr', 'te', subtitle="After model selection, unoptimized")
		self.grace('grace/Rex.agr', 'Rex', subtitle="After model selection, unoptimized")
		self.grace('grace/SSE.agr', 'SSE', subtitle="After model selection, unoptimized")
