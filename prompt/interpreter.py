import __builtin__
import code
import readline
import sys
sys.ps1 = 'relax> '
sys.ps2 = 'relax| '

from tab_completion import Tab_completion
from command import Ls, Lh, Ll, system
from print_all_data import Print_all_data

# Macro functions.
from diffusion_tensor import Diffusion_tensor
from gpl import GPL
from init_data import Init_data
from map import Map
from min import Min
from write import Write

# Macro classes.
import echo_data
import format
import load
import model
import min
import model_selection
import pdb
import state
import value


class Interpreter:
    def __init__(self, relax):
        """The interpreter class."""

        # Place the program class structure under self.relax
        self.relax = relax

        # Place the functions into the namespace of the interpreter class.
        self._diffusion_tensor = Diffusion_tensor(relax)
        self._gpl = GPL
        self._init_data = Init_data(relax)
        self._map = Map(relax)
        self._min = Min(relax)
        self._system = system
        self._write = Write(relax)

        # Place the classes into the interpreter class namespace.
        self._echo_data = echo_data.Skin(relax)
        self._format = format.Skin(relax)
        self._load = load.Skin(relax)
        self._pdb = pdb.Skin(relax)
        self._model = model.Model(relax)
        self._model_selection = model_selection.Skin(relax)
        self._state = state.Skin(relax)
        self._value = value.Skin(relax)

    def run(self):
        """Run the python interpreter.

        The namespace of this function is the namespace seen inside the interpreter.  All functions
        should be defined in this namespace.
        """

        # Import the functions emulating system commands.
        lh = Lh()
        ll = Ll()
        ls = Ls()
        system = self._system
        print_all_data = Print_all_data(self.relax)

        # Place functions in the local namespace.
        gpl = GPL = self._gpl()

        # Place the functions in the local namespace.
        diffusion_tensor = self._diffusion_tensor.set
        fixed = self._min.fixed
        grid_search = self._min.grid_search
        init_data = self._init_data.init
        map = self._map.map
        minimise = self._min.minimise
        write = self._write.write

        # Place the classes in the local namespace.
        echo_data = self._echo_data
        format = self._format
        load = self._load
        pdb = self._pdb
        model = self._model
        model_selection = self._model_selection
        state = self._state
        value = self._value

        # Builtin interpreter functions.
        echo = _Echo()
        exit = bye = quit = q = _Exit()

        # Setup tab completion.
        readline.set_completer(Tab_completion(name_space=locals()).finish)
        readline.parse_and_bind("tab: complete")

        # Modify the help system.
        help_python = _Helper_python()
        help = _Helper()

        # Go to the prompt.
        code.interact(banner=self.relax.intro_string, local=locals())


class _Echo:
    def off(self):
        """Macro for turning off the echoing of commands.

        The default program state is no echoing but if the function echo_on() has been run and you
        no longer want the echoing, this function will turn it off.


        Example
        ~~~~~~~

        To run the function, type the following.

        >>> echo_off()


        FIN
        """

        code.InteractiveConsole.raw_input = self._raw_input
        print "Echoing has been turned off."


    def on(self):
        """Macro for turning on the echoing of commands.

        The default program state is no echoing but if this function is run all commands will be
        echoed exactly as typed.  This is useful for scipting as commands run from a script are not
        printed to screen.  To turn echoing off, run the function echo_off()


        Example
        ~~~~~~~

        To run the function, type the following.

        >>> echo_on()


        FIN
        """

        code.InteractiveConsole.raw_input = self._raw_input_echo
        print "Echoing has been turned on."


    def _raw_input(self, prompt=""):
        """Function to restore the function code.InteractiveConsole.raw_input."""

        input = raw_input(prompt)
        return input


    def _raw_input_echo(self, prompt=""):
        """Function to modify code.InteractiveConsole.raw_input to echo the input."""

        input = raw_input(prompt)
        print input
        return input


class _Exit:
    def __repr__(self):
        """Exit the program."""

        print "Exiting the program."
        sys.exit()


class _Helper:
    text = """\
For assistence in using a function, simply type help(function).  In addition to functions, if
help(object) is typed, the help for the python object is returned.  This system is similar to the
help function built into the python interpreter, which has been renamed to help_python, with the
interactive component removed.  For the interactive python help the interactive python help system,
type help_python().\
    """

    def __repr__(self):
        return self.text

    def __call__(self, *args, **kwds):
        if len(args) != 1 or type(args[0]) == str:
            print self.text
            return
        import pydoc
        return pydoc.help(*args, **kwds)


class _Helper_python:
    text = """\
For the interactive python help system, type help_python().  The help_python function is identical
to the help function built into the normal python interpreter.\
    """

    def __repr__(self):
        return self.text

    def __call__(self, *args, **kwds):
        import pydoc
        return pydoc.help(*args, **kwds)


