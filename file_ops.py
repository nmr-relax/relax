from os import mkdir
from re import match
from string import split
import sys

class file_ops:
	def __init__(self, relax):
		"Class containing the file operations"

		self.relax = relax


	def init_log_file(self, title='Log file'):
		"Initialise the log file."

		self.relax.log = open('log.stage' + self.relax.data.stage, 'w')
		self.relax.log.write(title)


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

		if self.relax.debug:
			self.relax.log.write("Making directory " + dir + "\n")
		try:
			mkdir(dir)
		except OSError:
			print "Directory ./" + dir + " already exists.\n"


	def read_file(self, file_name, message=''):
		"Attempt to read the file, or quit the program if it does not exist."

		try:
			open(file_name, 'r')
		except IOError:
			print message
			print "The file '" + file_name + "' does not exist, quitting program.\n\n\n"
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
