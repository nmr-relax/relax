import code
import readline
from tab_completion import tab_completion


class interpreter:
	def __init__(self, relax):
		"The top level class."

		# Place the program class structure under self.relax
		self.relax = relax


	def run(self):
		"Run the python interpreter"

		# Place the macros in the local namespace.
		create_mf_model = self.relax.macros.mf_model.create
		diffusion_tensor = self.relax.macros.diffusion_tensor.set
		echo_data = self.relax.macros.echo_data.echo
		fixed = self.relax.macros.fixed.set
		format = self.relax.macros.format.format
		init_data = self.relax.macros.init_data.init
		list_preset_mf_model = self.relax.macros.mf_model.list
		load = self.relax.macros.load
		ls = self.relax.macros.ls
		min = self.relax.macros.min.min
		pdb = self.relax.macros.pdb.set
		print_all_data = self.relax.macros.print_all_data.go
		select_preset_mf_model = self.relax.macros.mf_model.select
		set_model_selection = self.relax.macros.set_model_selection.set
		state = self.relax.macros.state
		system = self.relax.macros.system
		value_setup = self.relax.macros.value_setup

		# Setup tab completion.
		readline.set_completer(tab_completion(name_space=locals()).finish)
		readline.parse_and_bind("tab: complete")

		# Modify the function code.InteractiveConsole.raw_input to echo the input.
		code.InteractiveConsole.raw_input = self.raw_input

		# Go to the prompt.
		code.interact(banner=self.relax.intro_string, local=locals())


	def raw_input(self, prompt=""):
		"Function to modify code.InteractiveConsole.raw_input to echo the input."

		input = raw_input(prompt)
		print input
		return input
