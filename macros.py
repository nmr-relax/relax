import sys


class macros:
	def __init__(self):
		"Macros."

	def exit(self):
		"Exit the program."

		sys.exit()


	def load(self, file=None):
		"Macro to load the contents of a file into memory."

		if not file:
			print "No file is specified."
			return
		print "The file is " + file
