# A method based on AIC model selection.  There are two stages:
#
#	Stage 1:   Creation of the files for the modelfree calculations for models 1 to 5.  Monte Carlo
#		simulations are not used on these initial runs, because the errors are not needed (should
#		speed up analysis considerably).
#	Stage 2:   Model selection and the creation of the final run.  Monte Carlo simulations are used to
#		find errors, and the diffusion tensor is unoptimized.  Files are placed in the directory
#		'final'.

import sys
from re import match

from common_ops import common_operations


class aic(common_operations):
	def __init__(self, mf):
		"Modelfree analysis based on AIC model selection."

		self.mf = mf
		print "Modelfree analysis based on AIC model selection."
		self.mf.data.aic.stage = self.ask_stage()
		self.init_log_file(self.mf.data.aic.stage)

		self.mf.file_ops.input()
		self.extract_relax_data()
		self.log_input_info()
		
		self.mf.data.runs = ['m1', 'm2', 'm3', 'm4', 'm5']

		# Stage 1.
		if match('1', self.mf.data.aic.stage):
			print "\n[ Stage 1 ]\n"
			for run in self.mf.data.runs:
				print "Creating input files for model " + run
				self.mf.log.write("\n\n<<< Model " + run + " >>>\n\n")
				self.mkdir(run)
				self.open_files(run)
				self.set_run_flags(run)
				self.log_params('M1', self.mf.data.usr_param.md1)
				self.log_params('M2', self.mf.data.usr_param.md2)
				self.create_mfin(run, sims='n')
				self.create_run(run)
				for res in range(len(self.mf.data.relax_data[0])):
					# Mfdata.
					self.create_mfdata(res)
					# Mfmodel.
					text = "\nspin     " + self.mf.data.relax_data[0][res][1] + "_" + self.mf.data.relax_data[0][res][0] + "\n"
					self.create_mfmodel(self.mf.data.usr_param.md1, type='M1', header=text)
					# Mfpar.
					self.create_mfpar(res)
				self.close_files(run)
			print "\n[ End of Stage 1 ]\n\n"

		# Stage 2.
		if match('2', self.mf.data.aic.stage):
			print "\n[ Stage 2 ]\n"
			sys.exit()


	def ask_stage(self):
		"User input of stage number."

		print "\n[ Select the stage for Modelfree analysis ]\n"
		print "The stages are:"
		print "   Stage 1 (1):   Creation of the files for the modelfree calculations for models 1 to 5."
		print "Monte Carlo simulations are not used on these initial runs, because the errors are not"
		print "needed (should speed up analysis considerably)."
		print "   Stage 2 (2):   Model selection and the creation of the final run.  Monte Carlo"
		print "simulations are used to find errors, and the diffusion tensor is unoptimized.  Files are"
		print "placed in the directory 'final'."
		while 1:
			stage = raw_input('> ')
			valid_stages = ['1', '2']
			if stage in valid_stages:
				break
			else:
				print "Invalid stage number.  Choose either 1 or 2."
		print "The stage chosen is " + stage + "\n"
		return stage


	def init_log_file(self, stage):
		"Initialize the log file."
		
		self.mf.log = open('log.stage' + stage, 'w')
		self.mf.log.write("<<< Stage " + stage + " of the AIC based modelfree analysis >>>\n\n\n")
