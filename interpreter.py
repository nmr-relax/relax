import code
import readline
from tab_completion import tab_completion

from macros import macros

class interpreter(macros):
	def __init__(self, relax):
		"The top level class."

		# Place the program class structure under self.relax
		self.relax = relax
		del relax

		# Place the macros in the local namespace.
		exit = self.exit
		load = self.load

		# Setup tab completion.
		readline.set_completer(tab_completion(name_space=locals()).finish)
		readline.parse_and_bind("tab: complete")

		# Go to the prompt.
		code.interact(banner=self.relax.intro_string, local=locals())
