import code
import readline
from tab_completion import tab_completion


class interpreter:
	def __init__(self, relax):
		"The top level class."

		# Place the program class structure under self.relax
		self.relax = relax
		del relax

		# Place the macros in the local namespace.
		bond_length = self.relax.macros.bond_length.set
		create_mf_model = self.relax.macros.mf_model.create
		csa = self.relax.macros.csa.set
		echo_data = self.relax.macros.echo_data.echo
		list_preset_mf_model = self.relax.macros.mf_model.list
		load_bond_length = self.relax.macros.bond_length.load
		load_csa = self.relax.macros.csa.load
		load_relax_data = self.relax.macros.load_relax_data.load
		load_seq = self.relax.macros.load_seq.load
		load_state = self.relax.macros.load_state.load
		ls = self.relax.macros.ls
		pdb = self.relax.macros.pdb.set
		save_state = self.relax.macros.save_state.save
		select_preset_mf_model = self.relax.macros.mf_model.select
		diffusion_tensor = self.relax.macros.diffusion_tensor.set
		set_model_selection = self.relax.macros.set_model_selection.set

		# Setup tab completion.
		readline.set_completer(tab_completion(name_space=locals()).finish)
		readline.parse_and_bind("tab: complete")

		# Go to the prompt.
		code.interact(banner=self.relax.intro_string, local=locals())
