from stage_all import stage_all

class stage2(stage_all):
	def __init__(self, mf):
		"""The stage 2 class.

		Model selection and creation of the final optimization run.  The modelfree
		input files for optimization are placed into the directory "optimize".
		"""

		self.mf = mf
		print "[ Stage 2 ]"
