# The method given by (Mandel et al., 1995) is divided into the three stages:
#
#	Stage 1:   Creation of the files for the modelfree calculations for models 1 to 5,
#		and f-tests between them.
#	Stage 2:   Model selection and creation of the final optimization run.  The modelfree
#		input files for optimization are placed into the directory "optimize".
#	Stage 3:   Extraction of optimized data.
#
# These stages are repeated until the data converges.

import sys
from re import match

from common_ops import common_operations


class palmer(common_operations):
	def __init__(self, mf):
		"The modelfree analysis of Palmer."

		self.mf = mf

		print "Palmer's method for modelfree analysis. (Mandel et al., 1995)"
		self.mf.data.palmer.stage = self.ask_stage()
		self.init_log_file(self.mf.data.palmer.stage)

		self.mf.file_ops.input()
		self.extract_relax_data()
		self.log_input_info()

		self.mf.data.runs = ['m1', 'm2', 'm3', 'm4', 'm5', 'f-m1m2', 'f-m1m3']
		if self.mf.data.num_data_sets > 3:
			self.mf.data.runs.append('f-m2m4')
			self.mf.data.runs.append('f-m2m5')
			self.mf.data.runs.append('f-m3m4')

		# Stage 1.
		if match('1', self.mf.data.palmer.stage):
			print "\n[ Stage 1 ]\n"
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
				self.mkdir(run)
				self.open_files(run)
				self.set_run_flags(run)
				self.log_params('M1', self.mf.data.usr_param.md1)
				self.log_params('M2', self.mf.data.usr_param.md2)
				if match('^m', run):
					self.create_mfin(run)
				elif match('^f', run):
					self.create_mfin(run, sel='ftest')
				self.create_run(run)
				for res in range(len(self.mf.data.relax_data[0])):
					# Mfdata.
					self.create_mfdata(res)
					# Mfmodel.
					text = "\nspin     " + self.mf.data.relax_data[0][res][1] + "_" + self.mf.data.relax_data[0][res][0] + "\n"
					self.create_mfmodel(self.mf.data.usr_param.md1, type='M1', header=text)
					if match('^f', run):
						self.create_mfmodel(self.mf.data.usr_param.md2, type='M1', header='\n')
					# Mfpar.
					self.create_mfpar(res)
				self.close_files(run)
			print "\n[ End of Stage 1 ]\n\n"

		# Stage 2.
		if match('2', self.mf.data.palmer.stage):
			self.mkdir('optimize')
			self.mkdir('grace')
			self.files2 = self.init_stage2_files()
			print "\n[ Modelfree Data Extraction ]\n"
			for run in self.mf.data.runs:
				file_name = run + '/mfout'
				self.mfout = self.read_file(file_name)


			print "Stage 2 incomplete.\n\n"
			sys.exit()

			# Final optimization.
#			self.open_files('optimize')
#			if match('isotropic', self.mf.data.usr_param.diff):
#				self.create_mfin(run, algorithm='brent', diffusion_search='grid')
#			elif match('axial', self.mf.data.usr_param.diff):
#				self.create_mfin(run, algorithm='powell')
#
#			for res in range(len(self.mf.data.relax_data[0])):
#				if match('0', self.mf.data.results[res]{model}):
#					self.opt_model = 'none'
#				elif match('2+3', self.mf.data.results[res]{model}):
#					self.opt_model = 'none'
#				elif match('4+5', self.mf.data.results[res]{model}):
#					self.opt_model = 'none'
#				elif match('^1', results[res]{model}):
#					self.opt_model = "m1"
#				else:
#					self.opt_model = 'm' + results[res]{model}
#
#				self.set_run_flags(self.opt_model)
#				# Mfdata.
#				if match('none', self.opt_model):
#					self.create_mfdata(res, flag='0')
#				else:
#					self.create_mfdata(res, flag='1')
#				# Mfmodel.
#				text = "\nspin     " + self.mf.data.relax_data[0][res][1] + "_" + self.mf.data.relax_data[0][res][0] + "\n"
#				self.create_mfmodel(type='M1', self.mf.data.usr_param.md1, header=text)
#				# Mfpar.
#				self.create_mfpar(res)

		# Stage 3.
		if match('3', self.mf.data.palmer.stage):
			print "Stage 3 not implemented yet.\n"
			sys.exit()

	class init_stage2_files:
		def __init__(self):
			"Class containing the stage 2 specific files."
			
			self.data_all = open('data_all', 'w')
			self.results = open('results.stage2', 'w')
			self.s2agr = open('grace/S2.stage2.agr', 'w')
			self.s2fagr = open('grace/S2f.stage2.agr', 'w')
			self.teagr = open('grace/te.stage2.agr', 'w')
			self.rexagr = open('grace/Rex.stage2.agr', 'w')
			self.sseagr = open('grace/SSE.stage2.agr', 'w')


	def ask_stage(self):
		"User input of stage number."

		print "\n[ Select the stage for Modelfree analysis ]\n"
		print "The stages are:"
		print "   Stage 1 (1):   Initial run of all models 1 to 5 and f-tests between them."
		print "   Stage 2 (2):   Model selection and creation of the final optimization run."
		print "   Stage 3 (3):   Extraction of optimized data."
		while 1:
			stage = raw_input('> ')
			valid_stages = ['1', '2', '3']
			if stage in valid_stages:
				break
			else:
				print "Invalid stage number.  Choose either 1, 2, or 3."
		print "The stage chosen is " + stage + "\n"
		return stage


	def init_log_file(self, stage):
		"Initialize the log file."
		
		self.mf.log = open('log.stage' + stage, 'w')
		text = "<<< Stage " + stage + " of Palmer's method for Modelfree "
		text = text + "analysis >>>\n\n\n"
		self.mf.log.write(text)


	def read_file(self, file_name):
		"Attempt to read the file, or quit the script if it does not exist."

		try:
			open(file_name, 'r')
		except IOError:
			print "The file '" + file_name + "' does not exist, quitting script.\n\n"
			sys.exit()
		file = open(file_name, 'r')
		return file
