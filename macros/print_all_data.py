from generic_functions import generic_functions


class print_all_data(generic_functions):
	def __init__(self, relax):
		"Class containing the macros for manipulating the program state."

		self.relax = relax


	def __repr__(self):
		"Macro for printing all the data in self.relax.data"

		string = ""
		# Loop over the data structures in self.relax.data
		for name in dir(self.relax.data):
			if not self.filter_data_structure(name):
				string = string +  "self.relax.data." + name + ":\n" + `getattr(self.relax.data, name)` + "\n\n"
		return string
