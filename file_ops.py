from os import mkdir, chmod
from re import match
from string import split
import sys

class file_ops:
	def __init__(self, mf):
		"Class containing the file operations"

		self.mf = mf


	def close_mf_files(self, dir):
		"Close the mfin, mfdata, mfmodel, mfpar, and run files, and make the run file executable."

		self.mf.mfin.close()
		self.mf.mfdata.close()
		self.mf.mfmodel.close()
		self.mf.mfpar.close()
		self.mf.run.close()
		chmod(dir + '/run', 0777)


	def init_log_file(self, title):
		"Initialize the log file."

		self.mf.log = open('log.stage' + self.mf.data.stage, 'w')
		self.mf.log.write(title)


	def open_file(self, file_name):
		"Open the file 'file' and return all the data."

		file = open(file_name, 'r')
		lines = file.readlines()
		data = []
		i = 0
		for line in lines:
			if i != 0:
				j = i - 1
				row = split(line)
				data.append([])
				data[j].append(row[0])
				data[j].append(row[1])
				for k in range(len(row)):
					if k > 1:
						data[j].append(float(row[k]))
			i = i + 1
		return data


	def mkdir(self, dir):
		"Create the given directory, or exit if the directory exists."

		if self.mf.debug == 1:
			self.mf.log.write("Making directory " + dir + "\n")
		try:
			mkdir(dir)
		except OSError:
			print "Directory ./" + dir + " already exists, quitting script.\n"
			sys.exit()


	def open_mf_files(self, dir):
		"Open the mfin, mfdata, mfmodel, mfpar, and run files for writing."

		self.mf.mfin = open(dir + '/mfin', 'w')
		self.mf.mfdata = open(dir + '/mfdata', 'w')
		self.mf.mfmodel = open(dir + '/mfmodel', 'w')
		self.mf.mfpar = open(dir + '/mfpar', 'w')
		self.mf.run = open(dir + '/run', 'w')


	def read_file(self, file_name, message=''):
		"Attempt to read the file, or quit the script if it does not exist."

		try:
			open(file_name, 'r')
		except IOError:
			sys.stdout.write(message)
			sys.stdout.write("The file '" + file_name + "' does not exist, quitting script.\n\n\n")
			sys.exit()
		file = open(file_name, 'r')
		return file


	def relax_data(self, file):
		"""Open the relaxation data in the file 'file' and return all the data.

		It is assumed that the file has four columns separated by whitespace.  The columns should be:
			0 - Residue numbers
			1 - Residue names
			2 - R1, R2, or NOE values
			3 - The errors
		"""

		lines = open(file, 'r')
		lines = lines.readlines()
		data = []
		i = 0
		for line in lines:
			if i != 0:
				j = i - 1
				row = split(line)
				data.append([])
				data[j].append(row[0])
				data[j].append(row[1])
				data[j].append(float(row[2]))
				data[j].append(float(row[3]))
			i = i + 1
		return data
