import __builtin__
import code
import readline
import sys
sys.ps1 = 'relax> '
sys.ps2 = 'relax| '

from tab_completion import tab_completion

# Macros.
from macros.diffusion_tensor import diffusion_tensor
from macros.echo_data import echo_data
from macros.format import format
from macros.gpl import gpl
from macros.init_data import init_data
from macros.load import load
from macros.min import min
from macros.mf_model import mf_model
from macros.pdb import pdb
from macros.set_model_selection import set_model_selection
from macros.state import state
from macros.value_setup import value_setup



class interpreter:
	def __init__(self, relax):
		"The interpreter class."

		# Place the program class structure under self.relax
		self.relax = relax
		self.echo = _Echo()

		# Place the macros into the namespace of the interpreter class.
		self.diffusion_tensor = diffusion_tensor(relax)
		self.echo_data = echo_data(relax)
		self.format = format(relax)
		self.init_data = init_data(relax)
		self.load = load(relax)
		self.min = min(relax)
		self.mf_model = mf_model(relax)
		self.pdb = pdb(relax)
		self.set_model_selection = set_model_selection(relax)
		self.state = state(relax)
		self.value_setup = value_setup(relax)

	def run(self):
		"""Run the python interpreter.

		The namespace of this function is the namespace seen inside the interpreter.
		All macros should be defined in this namespace.
		"""

		# Import the macros emulating system commands.
		from macros.command import ls, lh, ll, system
		from macros.print_all_data import print_all_data
		lh = lh()
		ll = ll()
		ls = ls()
		print_all_data = print_all_data(self.relax)

		# Place functions in the local namespace.
		GPL = gpl()

		# Place the macros in the local namespace.
		diffusion_tensor = self.diffusion_tensor.set
		echo_data = self.echo_data.echo
		fixed = self.min.fixed
		format = self.format.format
		grid_search = self.min.grid_search
		init_data = self.init_data.init
		load_relax_data = self.load.relax_data
		load_sequence = self.load.sequence
		minimise = self.min.minimise
		pdb = self.pdb.set
		mf_model_select = self.mf_model.select
		mf_model_create = self.mf_model.create
		set_model_selection = self.set_model_selection.set
		state_load = self.state.load
		state_save = self.state.save
		value_setup = self.value_setup.set

		# Builtin interpreter functions.
		echo_on = self.echo.echo_on
		echo_off = self.echo.echo_off
		exit = bye = quit = _Exit()

		# Setup tab completion.
		readline.set_completer(tab_completion(name_space=locals()).finish)
		readline.parse_and_bind("tab: complete")

		# Modify the help system.
		help_python = _Helper_python()
		help = _Helper()

		# Go to the prompt.
		code.interact(banner=self.relax.intro_string, local=locals())


class _Echo:
	def echo_off(self):
		"""Macro for turning off the echoing of commands.

		The default program state is no echoing but if the macro echo_on() has been run 
		and you no longer want the echoing, this macro will turn it off.


		Example
		~~~~~~~

		To run the macro, type the following.
		
		>>> echo_off()
		"""

		code.InteractiveConsole.raw_input = self.raw_input
		print "Echoing has been turned off."


	def echo_on(self):
		"""Macro for turning on the echoing of commands.

		The default program state is no echoing but if this macro is run all commands will be
		echoed exactly as typed.  This is useful for scipting as commands run from a script are
		not printed to screen.  To turn echoing off, run the macro echo_off()


		Example
		~~~~~~~

		To run the macro, type the following.
		
		>>> echo_on()

		"""

		code.InteractiveConsole.raw_input = self.raw_input_echo
		print "Echoing has been turned on."


	def raw_input(self, prompt=""):
		"Function to restore the function code.InteractiveConsole.raw_input."

		input = raw_input(prompt)
		return input


	def raw_input_echo(self, prompt=""):
		"Function to modify code.InteractiveConsole.raw_input to echo the input."

		input = raw_input(prompt)
		print input
		return input


class _Exit:
	def __repr__(self):
		"Exit the program."

		print "Exiting the program."
		sys.exit()


class _Helper:
	text = "For assistence in using a macro, simply type help(macro).  In addition to macros, if help(object) is typed,\n"
	text = text + "the help for the python object is returned.  This system is similar to the help function built into the\n"
	text = text + "python interpreter, which has been renamed to help_python, with the interactive component removed.  For\n"
	text = text + "the interactive python help system, type help_python()."

	def __repr__(self):
		return self.text

	def __call__(self, *args, **kwds):
		if len(args) != 1 or type(args[0]) == str:
			print self.text
			return
		import pydoc
		return pydoc.help(*args, **kwds)


class _Helper_python:
	def __repr__(self):
		text = "For the interactive python help system, type help_python().  The help_python function\n"
		text = text + "is identical to the help function built into the normal python interpreter."
		return text

	def __call__(self, *args, **kwds):
		import pydoc
		return pydoc.help(*args, **kwds)


