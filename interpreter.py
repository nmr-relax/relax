import code
import readline
import rlcompleter

from macros import macros

class interpreter(macros):
	def __init__(self, mf):
		"The top level class."

		self.mf = mf
		self.run()

	def run(self):
		exit = self.exit
		load = self.load
		readline.parse_and_bind("tab: complete")
		code.interact(banner=self.mf.intro_string, local=locals())
