import sys
from re import match

from print_macros import print_macros


class macros(print_macros):
	def __init__(self):
		"Macros."


	def load(self, file=None, num=0, name=1, data=2, error=3):
		"""Macro to load the contents of a file into memory.



		"""

		if not file:
			print "No file is specified."
			return
		print "\nExecuting macro load."
		print "   File name: " + file
		print "   Residue number column: " + `num`
		print "   Residue name column:   " + `name`
		print "   Data column:           " + `data`
		print "   Error column:          " + `error`


	def load_seq(self, file=None, num=0, name=1):
		"""Macro to load the contents of a file into memory.

		"""

		if not file:
			print "No file is specified."
			return
		print "\nExecuting macro load_seq."
		print "   File name: " + file
		print "   Residue number column: " + `num`
		print "   Residue name column:   " + `name`

		self.relax.data.seq = []
		file_data = self.relax.file_ops.open_file(file)
		for i in range(len(file_data)):
			if len(file_data[i]) == 0:
				continue
			if match("#", file_data[i][0]):
				continue
			self.relax.data.seq.append([int(file_data[i][num]), file_data[i][name]])


	def ls(self):
		print "\nExecuting macro ls."
		return
