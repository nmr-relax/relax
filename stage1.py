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
		for ftest in self.mf.data.ftests:
			print "Creating input files for the F-test " + ftest
			self.mf.log.write("\n\n<<< F-test " + ftest + " >>>\n\n")
			self.mkdir(ftest)

	def mkdir(self, dir):
		self.mf.log.write("Making directory " + dir)
		try:
			mkdir(dir)
		except OSError:
			print "Directory ./" + dir + " already exists, quitting script.\n"
			sys.exit()
