from re import match
from os import chmod
import sys

from common_ops import common_ops

class palmer(common_ops):
	def __init__(self, mf):
		"Class used to create and process input and output for the program Modelfree 4."

		self.mf = mf

		print "Model-free analysis based on " + self.mf.usr_param.method + " model selection."
		self.ask_stage()
		title = "<<< Stage " + self.mf.data.stage + " - "
		title = title + self.mf.usr_param.method + " model selection >>>\n\n\n"

		if self.mf.debug == 1:
			self.mf.file_ops.init_log_file(title)

		self.update_data()
		self.extract_relax_data()

		if self.mf.debug == 1:
			self.log_input_info()

		if match('^AIC$', self.mf.usr_param.method) or match('^AICc$', self.mf.usr_param.method):
			self.mf.data.runs = ['m1', 'm2', 'm3', 'm4', 'm5']
			self.model_selection = self.mf.modsel.asymptotic
		elif match('^BIC$', self.mf.usr_param.method):
			self.mf.data.runs = ['m1', 'm2', 'm3', 'm4', 'm5']
			self.model_selection = self.mf.modsel.asymptotic
		elif match('^Bootstrap$', self.mf.usr_param.method):
			self.mf.data.runs = ['m1', 'm2', 'm3', 'm4', 'm5']
			self.model_selection = self.mf.modsel.bootstrap
		elif match('^CV$', self.mf.usr_param.method):
			self.mf.data.runs = ['m1', 'm2', 'm3', 'm4', 'm5']
			self.model_selection = self.mf.modsel.cv
		elif match('^Expect$', self.mf.usr_param.method):
			self.mf.data.runs = ['m1', 'm2', 'm3', 'm4', 'm5']
			self.model_selection = self.mf.modsel.exp_overall_disc
		elif match('^Farrow$', self.mf.usr_param.method):
			self.mf.data.runs = ['m1', 'm2', 'm3', 'm4', 'm5']
			self.model_selection = self.mf.modsel.farrow
		elif match('^Palmer$', self.mf.usr_param.method):
			self.mf.data.runs = ['m1', 'm2', 'm3', 'm4', 'm5', 'f-m1m2', 'f-m1m3']
			if self.mf.data.num_data_sets > 3:
				self.mf.data.runs.append('f-m2m4')
				self.mf.data.runs.append('f-m2m5')
				self.mf.data.runs.append('f-m3m4')
			self.model_selection = self.mf.modsel.palmer
		elif match('^Overall$', self.mf.usr_param.method):
			message = "See the file 'modsel/overall_disc.py' for details.\n"
			self.mf.file_ops.read_file('op_data', message)
			self.mf.data.overall_disc.op_data = self.mf.file_ops.open_file(file_name='op_data')
			self.mf.data.runs = ['m1', 'm2', 'm3', 'm4', 'm5']
			#self.mf.modsel.overall_disc(self.mf)
		else:
			raise NameError, "The model-free analysis method is not set correctly.  Check self.method in the file 'usr_param.py', quitting program."

		self.mf.data.mfin.default_data()
		self.goto_stage()


	def ask_stage(self):
		"User input of stage number."

		print "\n[ Select the stage for model-free analysis ]\n"
		print "The stages are:"
		print "   Stage 1 (1):  Creation of the files for the model-free calculations for models 1 to 5."
		print "   Stage 2 (2):  Model selection and creation of a final run."
		print "   Stage 3 (3):  Extraction of the data."

		while 1:
			input = raw_input('> ')
			valid_stages = ['1', '2', '3']
			if input in valid_stages:
				self.mf.data.stage = input
				break
			else:
				print "Invalid stage number.  Choose either 1, 2, or 3."
		if match('2', self.mf.data.stage):
			while 1:
				print "Stage 2 has the following two options for the final run:"
				print "   (a):   No optimization of the diffusion tensor."
				print "   (b):   Optimization of the diffusion tensor."
				input = raw_input('> ')
				valid_stages = ['a', 'b']
				if input in valid_stages:
					self.mf.data.stage = self.mf.data.stage + input
					break
				else:
					print "Invalid option, choose either a or b."

		print "The stage chosen is " + self.mf.data.stage + "\n"


	def close_mf_files(self, dir):
		"Close the mfin, mfdata, mfmodel, mfpar, and run files, and make the run file executable."

		self.mf.mfin.close()
		self.mf.mfdata.close()
		self.mf.mfmodel.close()
		self.mf.mfpar.close()
		self.mf.run.close()
		chmod(dir + '/run', 0777)


	def create_mfdata(self, res, flag='1'):
		"""Create the Modelfree input file mfdata.

		This function is run once for each residue.  If the flag variable is set to 0, all data
		for this residue will be excluded.  If the exclude_set variable is given, the data flag
		corresponding to that set will be set to 0 (Used by the cross-validation method).
		"""

		mfdata = self.mf.mfdata

		mfdata.write("\nspin     " + self.mf.data.relax_data[0][res][1] + "_" + self.mf.data.relax_data[0][res][0] + "\n")
		for i in range(self.mf.data.num_ri):
			mfdata.write('%-7s' % self.mf.data.data_types[i])
			mfdata.write('%-10s' % self.mf.data.frq_label[self.mf.data.remap_table[i]])
			mfdata.write('%20s' % self.mf.data.relax_data[i][res][2])
			mfdata.write('%20s' % self.mf.data.relax_data[i][res][3])
			mfdata.write(' %-3s\n' % flag)


	def create_mfin(self):
		"Create the Modelfree input file mfin"

		mfin = self.mf.mfin

		mfin.write("optimization    tval\n\n")
		mfin.write("seed            0\n\n")
		mfin.write("search          grid\n\n")
		mfin.write("diffusion       " + self.mf.data.mfin.diff + " " + self.mf.data.mfin.diff_search + "\n\n")
		mfin.write("algorithm       " + self.mf.data.mfin.algorithm + "\n\n")
		if match('y', self.mf.data.mfin.sims):
			mfin.write("simulations     " + self.mf.data.mfin.sim_type + "    " + self.mf.data.mfin.num_sim)
			mfin.write("       " + self.mf.data.mfin.trim + "\n\n")
		elif match('n', self.mf.data.mfin.sims):
			mfin.write("simulations     none\n\n")
		mfin.write("selection       " + self.mf.data.mfin.selection + "\n\n")
		mfin.write("sim_algorithm   " + self.mf.data.mfin.algorithm + "\n\n")
		mfin.write("fields          " + `self.mf.data.num_frq`)
		for frq in range(self.mf.data.num_frq):
			mfin.write("  " + `self.mf.data.frq[frq]*1e-6`)
		mfin.write("\n")
		# tm.
		mfin.write('%-7s' % 'tm')
		mfin.write('%14s' % self.mf.usr_param.tm['val'])
		mfin.write('%2s' % self.mf.usr_param.tm['flag'])
		mfin.write('%3s' % self.mf.usr_param.tm['bound'])
		mfin.write('%5s' % self.mf.usr_param.tm['lower'])
		mfin.write('%6s' % self.mf.usr_param.tm['upper'])
		mfin.write('%4s\n' % self.mf.usr_param.tm['steps'])
		# dratio.
		mfin.write('%-7s' % 'Dratio')
		mfin.write('%14s' % self.mf.usr_param.dratio['val'])
		mfin.write('%2s' % self.mf.usr_param.dratio['flag'])
		mfin.write('%3s' % self.mf.usr_param.dratio['bound'])
		mfin.write('%5s' % self.mf.usr_param.dratio['lower'])
		mfin.write('%6s' % self.mf.usr_param.dratio['upper'])
		mfin.write('%4s\n' % self.mf.usr_param.dratio['steps'])
		# theta.
		mfin.write('%-7s' % 'Theta')
		mfin.write('%14s' % self.mf.usr_param.theta['val'])
		mfin.write('%2s' % self.mf.usr_param.theta['flag'])
		mfin.write('%3s' % self.mf.usr_param.theta['bound'])
		mfin.write('%5s' % self.mf.usr_param.theta['lower'])
		mfin.write('%6s' % self.mf.usr_param.theta['upper'])
		mfin.write('%4s\n' % self.mf.usr_param.theta['steps'])
		# phi.
		mfin.write('%-7s' % 'Phi')
		mfin.write('%14s' % self.mf.usr_param.phi['val'])
		mfin.write('%2s' % self.mf.usr_param.phi['flag'])
		mfin.write('%3s' % self.mf.usr_param.phi['bound'])
		mfin.write('%5s' % self.mf.usr_param.phi['lower'])
		mfin.write('%6s' % self.mf.usr_param.phi['upper'])
		mfin.write('%4s\n' % self.mf.usr_param.phi['steps'])


	def create_mfmodel(self, res, md, type='M1'):
		"Create the M1 or M2 section of the Modelfree input file mfmodel"

		mfmodel = self.mf.mfmodel

		if match('M1', type):
			mfmodel.write("\nspin     " + self.mf.data.relax_data[0][res][1] + "_" + self.mf.data.relax_data[0][res][0] + "\n")
		else:
			mfmodel.write("\n")

		# tloc.
		mfmodel.write('%-3s' % type)
		mfmodel.write('%-6s' % 'tloc')
		mfmodel.write('%-6s' % md['tloc']['start'])
		mfmodel.write('%-4s' % md['tloc']['flag'])
		mfmodel.write('%-2s' % md['tloc']['bound'])
		mfmodel.write('%11s' % md['tloc']['lower'])
		mfmodel.write('%12s' % md['tloc']['upper'])
		mfmodel.write(' %-4s\n' % md['tloc']['steps'])
		# Theta.
		mfmodel.write('%-3s' % type)
		mfmodel.write('%-6s' % 'Theta')
		mfmodel.write('%-6s' % md['theta']['start'])
		mfmodel.write('%-4s' % md['theta']['flag'])
		mfmodel.write('%-2s' % md['theta']['bound'])
		mfmodel.write('%11s' % md['theta']['lower'])
		mfmodel.write('%12s' % md['theta']['upper'])
		mfmodel.write(' %-4s\n' % md['theta']['steps'])
		# S2f.
		mfmodel.write('%-3s' % type)
		mfmodel.write('%-6s' % 'Sf2')
		mfmodel.write('%-6s' % md['sf2']['start'])
		mfmodel.write('%-4s' % md['sf2']['flag'])
		mfmodel.write('%-2s' % md['sf2']['bound'])
		mfmodel.write('%11s' % md['sf2']['lower'])
		mfmodel.write('%12s' % md['sf2']['upper'])
		mfmodel.write(' %-4s\n' % md['sf2']['steps'])
		# S2s.
		mfmodel.write('%-3s' % type)
		mfmodel.write('%-6s' % 'Ss2')
		mfmodel.write('%-6s' % md['ss2']['start'])
		mfmodel.write('%-4s' % md['ss2']['flag'])
		mfmodel.write('%-2s' % md['ss2']['bound'])
		mfmodel.write('%11s' % md['ss2']['lower'])
		mfmodel.write('%12s' % md['ss2']['upper'])
		mfmodel.write(' %-4s\n' % md['ss2']['steps'])
		# te.
		mfmodel.write('%-3s' % type)
		mfmodel.write('%-6s' % 'te')
		mfmodel.write('%-6s' % md['te']['start'])
		mfmodel.write('%-4s' % md['te']['flag'])
		mfmodel.write('%-2s' % md['te']['bound'])
		mfmodel.write('%11s' % md['te']['lower'])
		mfmodel.write('%12s' % md['te']['upper'])
		mfmodel.write(' %-4s\n' % md['te']['steps'])
		# Rex.
		mfmodel.write('%-3s' % type)
		mfmodel.write('%-6s' % 'Rex')
		mfmodel.write('%-6s' % md['rex']['start'])
		mfmodel.write('%-4s' % md['rex']['flag'])
		mfmodel.write('%-2s' % md['rex']['bound'])
		mfmodel.write('%11s' % md['rex']['lower'])
		mfmodel.write('%12s' % md['rex']['upper'])
		mfmodel.write(' %-4s\n' % md['rex']['steps'])


	def create_mfpar(self, res):
		"Create the Modelfree input file mfpar"

		mfpar = self.mf.mfpar

		mfpar.write("\nspin     " + self.mf.data.relax_data[0][res][1] + "_" + self.mf.data.relax_data[0][res][0] + "\n")

		mfpar.write('%-14s' % "constants")
		mfpar.write('%-6s' % self.mf.data.relax_data[0][res][0])
		mfpar.write('%-7s' % self.mf.usr_param.const['nucleus'])
		mfpar.write('%-8s' % self.mf.usr_param.const['gamma'])
		mfpar.write('%-8s' % `self.mf.usr_param.const['rxh']*1e10`)
		mfpar.write('%-8s\n' % `self.mf.usr_param.const['csa']*1e6`)

		mfpar.write('%-10s' % "vector")
		mfpar.write('%-4s' % self.mf.usr_param.vector['atom1'])
		mfpar.write('%-4s\n' % self.mf.usr_param.vector['atom2'])


	def create_run(self, dir):
		"Create the file 'run' to execute the model-free run"

		self.mf.run.write("modelfree4 -i mfin -d mfdata -p mfpar -m mfmodel -o mfout -e out")
		if self.mf.usr_param.diff == 'axial':
			# Copy the pdb file to the model directory so there are no problems with the *.rotate
			# file already existing.
			cmd = 'cp ' + self.mf.usr_param.pdb_full + ' ' + dir
			system(cmd)
			self.mf.run.write(" -s " + self.mf.usr_param.pdb_file)
		self.mf.run.write("\n")


	def extract_mf_data(self):
		"Extract the model-free results."

		for model in self.mf.data.runs:
			mfout = self.mf.file_ops.read_file(model + '/mfout')
			mfout_lines = mfout.readlines()
			mfout.close()
			print "Extracting model-free data from " + model + "/mfout."
			num_res = len(self.mf.data.relax_data[0])
			if match('^m', model):
				self.mf.data.model = self.mf.star.extract(mfout_lines, num_res, self.mf.usr_param.chi2_lim, self.mf.usr_param.ftest_lim, ftest='n')
			if match('^f', model):
				self.mf.data.model = self.mf.star.extract(mfout_lines, num_res, self.mf.usr_param.chi2_lim, self.mf.usr_param.ftest_lim, ftest='y')


	def final_run(self):
		"Creation of the final run.  Files are placed in the directory 'final'."

		self.mf.file_ops.mkdir('final')
		open_mf_files(dir='final')
		self.create_mfin()

		self.create_run(dir='final')
		for res in range(len(self.mf.data.relax_data[0])):
			if match('0', self.mf.data.results[res]['model']):
				model = 'none'
			elif match('2+3', self.mf.data.results[res]['model']):
				model = 'none'
			elif match('4+5', self.mf.data.results[res]['model']):
				model = 'none'
			elif match('^1', self.mf.data.results[res]['model']):
				model = "m1"
			else:
				model = 'm' + self.mf.data.results[res]['model']
			self.set_run_flags(model)
			# Mfdata.
			if match('none', model):
				self.create_mfdata(res, flag='0')
			else:
				self.create_mfdata(res, flag='1')
			# Mfmodel.
			self.create_mfmodel(res, self.mf.usr_param.md1, type='M1')
			# Mfpar.
			self.create_mfpar(res)
		self.close_mf_files(dir='final')


	def goto_stage(self):
		if match('1', self.mf.data.stage):
			print "\n[ Stage 1 ]\n"
			self.set_vars_stage_initial()
			if match('^CV$', self.mf.usr_param.method):
				self.stage_initial_cv()
			else:
				self.stage_initial()
			print "\n[ End of stage 1 ]\n\n"

		if match('^2', self.mf.data.stage):
			print "\n[ Stage 2 ]\n"
			self.set_vars_stage_selection()
			self.stage_selection()
			if match('2a', self.mf.data.stage):
				self.final_run()
			if match('2b', self.mf.data.stage):
				if match('isotropic', self.mf.data.mfin.diff):
					self.mf.data.mfin.algorithm = 'brent'
					self.mf.data.mfin.diff_search = 'grid'
				elif match('axial', self.mf.data.mfin.diff):
					self.mf.data.mfin.algorithm = 'powell'
				self.final_run()
			print "\n[ End of stage 2 ]\n\n"

		if match('3', self.mf.data.stage):
			print "\n[ Stage 3 ]\n"
			self.stage_final()
			print "\n[ End of stage 3 ]\n\n"


	def open_mf_files(self, dir):
		"Open the mfin, mfdata, mfmodel, mfpar, and run files for writing."

		self.mf.mfin = open(dir + '/mfin', 'w')
		self.mf.mfdata = open(dir + '/mfdata', 'w')
		self.mf.mfmodel = open(dir + '/mfmodel', 'w')
		self.mf.mfpar = open(dir + '/mfpar', 'w')
		self.mf.run = open(dir + '/run', 'w')


	def set_run_flags(self, model):
		"Reset, and then set the flags in self.mf.usr_param.md1 and md2."

		self.mf.usr_param.md1['sf2']['flag'] = '0'
		self.mf.usr_param.md1['ss2']['flag'] = '0'
		self.mf.usr_param.md1['te']['flag']  = '0'
		self.mf.usr_param.md1['rex']['flag'] = '0'

		self.mf.usr_param.md2['sf2']['flag'] = '0'
		self.mf.usr_param.md2['ss2']['flag'] = '0'
		self.mf.usr_param.md2['te']['flag']  = '0'
		self.mf.usr_param.md2['rex']['flag'] = '0'

		# Normal runs.
		if model == "m1":
			self.mf.usr_param.md1['ss2']['flag'] = '1'
		if model == "m2":
			self.mf.usr_param.md1['ss2']['flag'] = '1'
			self.mf.usr_param.md1['te']['flag']  = '1'
		if model == "m3":
			self.mf.usr_param.md1['ss2']['flag'] = '1'
			self.mf.usr_param.md1['rex']['flag'] = '1'
		if model == "m4":
			self.mf.usr_param.md1['ss2']['flag'] = '1'
			self.mf.usr_param.md1['te']['flag']  = '1'
			self.mf.usr_param.md1['rex']['flag'] = '1'
		if model == "m5":
			self.mf.usr_param.md1['sf2']['flag'] = '1'
			self.mf.usr_param.md1['ss2']['flag'] = '1'
			self.mf.usr_param.md1['te']['flag']  = '1'

		# F-tests.
		if model == "f-m1m2":
			self.mf.usr_param.md1['ss2']['flag'] = '1'
			self.mf.usr_param.md2['ss2']['flag'] = '1'
			self.mf.usr_param.md2['te']['flag']  = '1'
		if model == "f-m1m3":
			self.mf.usr_param.md1['ss2']['flag'] = '1'
			self.mf.usr_param.md2['ss2']['flag'] = '1'
			self.mf.usr_param.md2['rex']['flag'] = '1'
		if model == "f-m1m4":
			self.mf.usr_param.md1['ss2']['flag'] = '1'
			self.mf.usr_param.md2['ss2']['flag'] = '1'
			self.mf.usr_param.md2['te']['flag']  = '1'
			self.mf.usr_param.md2['rex']['flag'] = '1'
		if model == "f-m1m5":
			self.mf.usr_param.md1['ss2']['flag'] = '1'
			self.mf.usr_param.md2['ss2']['flag'] = '1'
			self.mf.usr_param.md2['sf2']['flag'] = '1'
			self.mf.usr_param.md2['te']['flag']  = '1'
		if model == "f-m2m4":
			self.mf.usr_param.md1['ss2']['flag'] = '1'
			self.mf.usr_param.md1['te']['flag']  = '1'
			self.mf.usr_param.md2['ss2']['flag'] = '1'
			self.mf.usr_param.md2['te']['flag']  = '1'
			self.mf.usr_param.md2['rex']['flag'] = '1'
		if model == "f-m2m5":
			self.mf.usr_param.md1['ss2']['flag'] = '1'
			self.mf.usr_param.md1['te']['flag']  = '1'
			self.mf.usr_param.md2['ss2']['flag'] = '1'
			self.mf.usr_param.md2['sf2']['flag'] = '1'
			self.mf.usr_param.md2['te']['flag']  = '1'
		if model == "f-m3m4":
			self.mf.usr_param.md1['ss2']['flag'] = '1'
			self.mf.usr_param.md1['rex']['flag'] = '1'
			self.mf.usr_param.md2['ss2']['flag'] = '1'
			self.mf.usr_param.md2['te']['flag']  = '1'
			self.mf.usr_param.md2['rex']['flag'] = '1'


	def stage_final(self):
		raise NameError, "Stage 3 not implemented yet.\n"


	def stage_initial(self):
		"Creation of the files for the Modelfree calculations for the models in self.mf.data.runs."

		for model in self.mf.data.runs:
			if match('^m', model):
				print "Creating input files for model " + model
				if self.mf.debug == 1:
					self.mf.log.write("\n\n<<< Model " + model + " >>>\n\n")
			elif match('^f', model):
				print "Creating input files for the F-test " + model
				if self.mf.debug == 1:
					self.mf.log.write("\n\n<<< F-test " + model + " >>>\n\n")
			else:
				raise NameError, "The run '" + model + "'does not start with an m or f, quitting program!\n\n"
			self.mf.file_ops.mkdir(dir=model)
			self.open_mf_files(dir=model)
			self.set_run_flags(model)

			if self.mf.debug == 1:
				self.log_params('M1', self.mf.usr_param.md1)
				self.log_params('M2', self.mf.usr_param.md2)

			if match('^m', model):
				self.mf.data.mfin.selection = 'none'
				self.create_mfin()
			elif match('^f', model):
				self.mf.data.mfin.selection = 'ftest'
				self.create_mfin()
			self.create_run(dir=model)
			for res in range(len(self.mf.data.relax_data[0])):
				# Mfdata.
				self.create_mfdata(res)
				# Mfmodel.
				self.create_mfmodel(res, self.mf.usr_param.md1, type='M1')
				if match('^f', model):
					self.create_mfmodel(res, self.mf.usr_param.md2, type='M2')
				# Mfpar.
				self.create_mfpar(res)
			self.close_mf_files(dir=model)


	def stage_initial_cv(self):
		"Creation of the files for the Modelfree calculations for the models in self.mf.data.runs."

		for model in self.mf.data.runs:
			print "Creating input files for model " + model

			if self.mf.debug == 1:
				self.mf.log.write("\n\n<<< Model " + model + " >>>\n\n")

			self.mf.file_ops.mkdir(dir=model)
			self.set_run_flags(model)

			if self.mf.debug == 1:
				self.log_params('M1', self.mf.usr_param.md1)
				self.log_params('M2', self.mf.usr_param.md2)

			for i in range(self.mf.data.num_ri):
				cv_dir = model + "/" + model + "-" + self.mf.data.frq_label[self.mf.data.remap_table[i]] + "_" + self.mf.data.data_types[i]
				self.mf.file_ops.mkdir(dir=cv_dir)
				open_mf_files(dir=cv_dir)
				self.mf.data.mfin.selection = 'none'
				self.create_mfin()
				self.create_run(dir=model)
				for res in range(len(self.mf.data.relax_data[0])):
					# Mfdata.
					self.create_mfdata(res, i)
					# Mfmodel.
					self.create_mfmodel(res, self.mf.usr_param.md1, type='M1')
					# Mfpar.
					self.create_mfpar(res)
				self.close_mf_files(dir=cv_dir)


	def set_vars_stage_initial(self):
		"Set the options for the initial runs."

		self.mf.data.mfin.sims = 'n'


	def set_vars_stage_selection(self):
		"Set the options for the final run."

		self.mf.data.mfin.sims = 'y'
