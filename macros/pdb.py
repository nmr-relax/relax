
class pdb:
	def __init__(self, relax):
		"Class containing the macro for setting the pdb file."

		self.relax = relax


	def set(self, path=None, file=None):
		"Macro for setting the pdb file."

		if not path:
			print "The path has not been set."
		elif not file:
			print "The file has not been set."
		else:
			self.relax.data.pdb_path = path
			self.relax.data.pdb_file = file
			self.relax.data.pdb = path + file

