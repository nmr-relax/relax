from os import mkdir, chmod
import sys


class common_operations:
	def __init__(self):
		"""The stage 1 class.

		Creation of the files for the modelfree calculations for models 1 to 5,
		and f-tests between them.
		"""

	def extract_relax_data(self):
		"Extract the relaxation data from the files given in the file 'input'"
		print "\n[ Relaxation Data Extraction ]\n"
		for i in range(len(self.mf.data.input_info)):
			data = self.mf.file_ops.relax_data(self.mf.data.input_info[i][3])
			self.mf.data.relax_data[i] = data


	def log_input_info(self):
		self.mf.log.write("The input info data structure is:\n" + `self.mf.data.input_info` + "\n\n")
		for i in range(len(self.mf.data.input_info)):
			text = ""
			text = text + '%-25s%-20s\n' % ("Data label:", self.mf.data.input_info[i][0])
			text = text + '%-25s%-20s\n' % ("NMR frequency label:", self.mf.data.input_info[i][1])
			text = text + '%-25s%-20s\n' % ("NMR proton frequency:", `self.mf.data.input_info[i][2]`)
			text = text + '%-25s%-20s\n\n' % ("File name:", self.mf.data.input_info[i][3])
			self.mf.log.write(text)
		self.mf.log.write("Number of frequencies:\t" + `self.mf.data.num_frq` + "\n")
		self.mf.log.write("Number of data sets:\t" + `self.mf.data.num_data_sets` + "\n\n")


	def mkdir(self, dir):
		"Create the given directory, or exit if the directory exists."

		self.mf.log.write("Making directory " + dir + "\n")
		try:
			mkdir(dir)
		except OSError:
			print "Directory ./" + dir + " already exists, quitting script.\n"
			sys.exit()
