import sys
from os import mkdir
from stage_all import stage_all

class stage1(stage_all):
	def __init__(self, mf):
		"""The stage 1 class.

		Creation of the files for the modelfree calculations for models 1 to 5,
		and f-tests between them.
		"""

		self.mf = mf
		print "\n[ Stage 1 ]\n"
		for model in self.mf.data.models:
			print "Creating input files for model " + model
			self.mf.log.write("\n\n<<< Model " + model + " >>>\n\n")
			self.mkdir(model)
			self.open_files(model)
			self.set_model_flags(model)
			self.log_params()
			for res in range(len(self.mf.data.relax_data[0])):
				self.create_mfdata()

		for ftest in self.mf.data.ftests:
			print "Creating input files for the F-test " + ftest
			self.mf.log.write("\n\n<<< F-test " + ftest + " >>>\n\n")
			self.mkdir(ftest)
			self.open_files(ftest)
			self.set_ftest_flags(ftest)
			self.log_params()
#			for res in range(len(self.mf.data.relax_data[0])):
#				self.mfdata(model)


	def log_params(self):
		"Put the parameter data structures into the log file."

		self.mf.log.write("\nmd1 data structure\n")
		for param in ['tloc', 'theta', 'ss2', 'sf2', 'te', 'rex']:
			self.mf.log.write('%-10s' % ( param + ":" ))
			self.mf.log.write('%-15s' % ( "start = " + `self.mf.data.usr_param.md1[param]['start']`))
			self.mf.log.write('%-10s' % ( "flag = " + `self.mf.data.usr_param.md1[param]['flag']`))
			self.mf.log.write('%-12s' % ( "bound = " + `self.mf.data.usr_param.md1[param]['bound']`))
			self.mf.log.write('%-20s' % ( "lower = " + `self.mf.data.usr_param.md1[param]['lower']`))
			self.mf.log.write('%-20s' % ( "upper = " + `self.mf.data.usr_param.md1[param]['upper']`))
			self.mf.log.write('%-10s' % ( "steps = " + `self.mf.data.usr_param.md1[param]['steps']`))
			self.mf.log.write("\n")

		self.mf.log.write("\nmd2 data structure\n")
		for param in ['tloc', 'theta', 'ss2', 'sf2', 'te', 'rex']:
			self.mf.log.write('%-10s' % ( param + ":" ))
			self.mf.log.write('%-15s' % ( "start = " + `self.mf.data.usr_param.md2[param]['start']`))
			self.mf.log.write('%-10s' % ( "flag = " + `self.mf.data.usr_param.md2[param]['flag']`))
			self.mf.log.write('%-12s' % ( "bound = " + `self.mf.data.usr_param.md2[param]['bound']`))
			self.mf.log.write('%-20s' % ( "lower = " + `self.mf.data.usr_param.md2[param]['lower']`))
			self.mf.log.write('%-20s' % ( "upper = " + `self.mf.data.usr_param.md2[param]['upper']`))
			self.mf.log.write('%-10s' % ( "steps = " + `self.mf.data.usr_param.md2[param]['steps']`))
			self.mf.log.write("\n")


	def mkdir(self, dir):
		"Create the given directory, or exit if the directory exists."

		self.mf.log.write("Making directory " + dir + "\n")
		try:
			mkdir(dir)
		except OSError:
			print "Directory ./" + dir + " already exists, quitting script.\n"
			sys.exit()


	def create_mfdata(self):
		"Create the Modelfree input file mfdata"

		return


	def open_files(self, dir):
		"Open the mfin, mfdata, mfmodel, mfpar, and run files for writing."

		mfin = dir + "/mfin"
		mfdata = dir + "/mfdata"
		mfmodel = dir + "/mfmodel"
		mfpar = dir + "/mfpar"
		run = dir + "/run"

		self.mfin = open(mfin, 'w')
		self.mfdata = open(mfdata, 'w')
		self.mfmodel = open(mfmodel, 'w')
		self.mfpar = open(mfpar, 'w')
		self.run = open(run, 'w')
	
	
	def set_ftest_flags(self, ftest):
		"Reset, and then set the flags in self.mf.data.usr_param.md1 and md2."
		
		self.mf.data.usr_param.md1['sf2']['flag'] = 0
		self.mf.data.usr_param.md1['ss2']['flag'] = 0
		self.mf.data.usr_param.md1['te']['flag']  = 0
		self.mf.data.usr_param.md1['rex']['flag'] = 0

		self.mf.data.usr_param.md2['sf2']['flag'] = 0
		self.mf.data.usr_param.md2['ss2']['flag'] = 0
		self.mf.data.usr_param.md2['te']['flag']  = 0
		self.mf.data.usr_param.md2['rex']['flag'] = 0

		if ftest == "f-m1m2":
			self.mf.data.usr_param.md1['ss2']['flag'] = 1
			self.mf.data.usr_param.md2['ss2']['flag'] = 1
			self.mf.data.usr_param.md2['te']['flag']  = 1
		if ftest == "f-m1m3":
			self.mf.data.usr_param.md1['ss2']['flag'] = 1
			self.mf.data.usr_param.md2['ss2']['flag'] = 1
			self.mf.data.usr_param.md2['rex']['flag'] = 1
		if ftest == "f-m1m4":
			self.mf.data.usr_param.md1['ss2']['flag'] = 1
			self.mf.data.usr_param.md2['ss2']['flag'] = 1
			self.mf.data.usr_param.md2['te']['flag']  = 1
			self.mf.data.usr_param.md2['rex']['flag'] = 1
		if ftest == "f-m1m5":
			self.mf.data.usr_param.md1['ss2']['flag'] = 1
			self.mf.data.usr_param.md2['ss2']['flag'] = 1
			self.mf.data.usr_param.md2['sf2']['flag'] = 1
			self.mf.data.usr_param.md2['te']['flag']  = 1
		if ftest == "f-m2m4":
			self.mf.data.usr_param.md1['ss2']['flag'] = 1
			self.mf.data.usr_param.md1['te']['flag']  = 1
			self.mf.data.usr_param.md2['ss2']['flag'] = 1
			self.mf.data.usr_param.md2['te']['flag']  = 1
			self.mf.data.usr_param.md2['rex']['flag'] = 1
		if ftest == "f-m2m5":
			self.mf.data.usr_param.md1['ss2']['flag'] = 1
			self.mf.data.usr_param.md1['te']['flag']  = 1
			self.mf.data.usr_param.md2['ss2']['flag'] = 1
			self.mf.data.usr_param.md2['sf2']['flag'] = 1
			self.mf.data.usr_param.md2['te']['flag']  = 1
		if ftest == "f-m3m4":
			self.mf.data.usr_param.md1['ss2']['flag'] = 1
			self.mf.data.usr_param.md1['rex']['flag'] = 1
			self.mf.data.usr_param.md2['ss2']['flag'] = 1
			self.mf.data.usr_param.md2['te']['flag']  = 1
			self.mf.data.usr_param.md2['rex']['flag'] = 1
	
	
	def set_model_flags(self, model):
		"Reset, and then set the flags in self.mf.data.usr_param.md1"
		
		self.mf.data.usr_param.md1['sf2']['flag'] = 0
		self.mf.data.usr_param.md1['ss2']['flag'] = 0
		self.mf.data.usr_param.md1['te']['flag']  = 0
		self.mf.data.usr_param.md1['rex']['flag'] = 0

		if model == "m1":
			self.mf.data.usr_param.md1['ss2']['flag'] = 1
		if model == "m2":
			self.mf.data.usr_param.md1['ss2']['flag'] = 1
			self.mf.data.usr_param.md1['te']['flag']  = 1
		if model == "m3":
			self.mf.data.usr_param.md1['ss2']['flag'] = 1
			self.mf.data.usr_param.md1['rex']['flag'] = 1
		if model == "m4":
			self.mf.data.usr_param.md1['ss2']['flag'] = 1
			self.mf.data.usr_param.md1['te']['flag']  = 1
			self.mf.data.usr_param.md1['rex']['flag'] = 1
		if model == "m5":
			self.mf.data.usr_param.md1['sf2']['flag'] = 1
			self.mf.data.usr_param.md1['ss2']['flag'] = 1
			self.mf.data.usr_param.md1['te']['flag']  = 1


