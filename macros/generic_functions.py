class generic_functions:
	def __init__(self):
		"Base class containing generic functions used by many macros."


	def sequence_data_test(self):
		"Test if sequence data is loaded."

		try:
			self.relax.data.seq
			return 1
		except AttributeError:
			print "Sequence data has to be loaded first."
			print "[ failed ]"
			return 0
