import __builtin__
from code import InteractiveConsole
import readline
import sys
sys.ps1 = 'relax> '
sys.ps2 = 'relax| '

from tab_completion import Tab_completion
from command import Ls, Lh, Ll, system
from print_all_data import Print_all_data

# Macro functions.
from diffusion_tensor import Diffusion_tensor
from fixed import Fixed
from gpl import GPL
from grid import Grid
from init_data import Init_data
from map import Map
from minimise import Minimise
from write import Write

# Macro classes.
import echo_data
import format
import load
import model
import model_selection
import pdb
import state
import value


class Interpreter:
    def __init__(self, relax):
        """The interpreter class."""

        # Place the program class structure under self.relax
        self.relax = relax

        self.echo = 1

        # Place the functions into the namespace of the interpreter class.
        self._Diffusion_tensor = Diffusion_tensor(relax)
        self._Fixed = Fixed(relax)
        self._GPL = GPL
        self._Grid = Grid(relax)
        self._Init_data = Init_data(relax)
        self._Map = Map(relax)
        self._Minimise = Minimise(relax)
        self._system = system
        self._Write = Write(relax)

        # Place the classes into the interpreter class namespace.
        self._Echo_data = echo_data.Skin(relax)
        self._Format = format.Skin(relax)
        self._Load = load.Skin(relax, self.echo)
        self._Pdb = pdb.Skin(relax)
        self._Model = model.Model(relax)
        self._Model_selection = model_selection.Skin(relax)
        self._State = state.Skin(relax)
        self._Value = value.Skin(relax)


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
        gpl = GPL = self._GPL()

        # Place the functions in the local namespace.
        diffusion_tensor = self._Diffusion_tensor.set
        fixed = self._Fixed.fixed
        grid_search = self._Grid.grid_search
        init_data = self._Init_data.init
        map = self._Map.map
        minimise = self._Minimise.minimise
        write = self._Write.write

        # Place the classes in the local namespace.
        echo_data = self._Echo_data
        format = self._Format
        load = self._Load
        pdb = self._Pdb
        model = self._Model
        model_selection = self._Model_selection
        state = self._State
        value = self._Value

        # Builtin interpreter functions.
        echo = _Echo()
        execfile = __builtin__.execfile
        exit = bye = quit = q = _Exit

        # Modify the help system.
        help_python = _Helper_python()
        help = _Helper()

        # Setup tab completion.
        readline.set_completer(Tab_completion(name_space=locals()).finish)
        readline.parse_and_bind("tab: complete")

        # Go to the prompt.
        prompt(intro=self.relax.intro_string, local=locals(), script=self.relax.script_file)


class _Echo:
    def __init__(self):
        """Class containing functions for turning echoing on and off."""


    def off(self):
        """Macro for turning off the echoing of commands.

        The default program state is no echoing but if the function echo_on() has been run and you
        no longer want the echoing, this function will turn it off.


        Example
        ~~~~~~~

        To run the function, type the following.

        >>> echo_off()
        """

        InteractiveConsole.raw_input = self._raw_input
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
        """


        InteractiveConsole.raw_input = self._raw_input_echo
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


def interact(self, intro=None, local=None, script=None):
    """Replacement function for 'code.InteractiveConsole.interact'.

    This will initially execute a command line specified script file before entering into the
    prompt.
    """

    # Print the program introduction.
    self.write("%s\n" % intro)

    # Execute the script file (if given on the command line).
    if script != None:
        try:
            execfile(script, globals(), local)
        except KeyboardInterrupt:
            self.write("\nScript execution cancelled.\n")
        sys.exit()

    # Interactive prompt.
    more = 0
    while 1:
        try:
            if more:
                prompt = sys.ps2
            else:
                prompt = sys.ps1
            try:
                line = self.raw_input(prompt)
            except EOFError:
                self.write("\n")
                break
            else:
                more = self.push(line)
        except KeyboardInterrupt:
            self.write("\nKeyboardInterrupt\n")
            self.resetbuffer()
            more = 0


def prompt(intro=None, local=None, script=None):
    """Python interpreter emulation.

    This function replaces 'code.interact'.
    """

    # Replace the 'InteractiveConsole.interact' function.
    InteractiveConsole.interact = interact

    # The console.
    console = InteractiveConsole(local)
    console.interact(intro, local, script)
