import __builtin__
import code
import readline
import sys
sys.ps1 = 'relax> '
sys.ps2 = 'relax| '

from tab_completion import tab_completion

# Macro functions.
from macros.diffusion_tensor import diffusion_tensor
from macros.gpl import gpl
from macros.init_data import init_data

# Macro classes.
import macros.echo_data
import macros.format
import macros.load
import macros.min
import macros.mf_model
import macros.pdb
import macros.modsel
import macros.state
import macros.value


class interpreter:
    def __init__(self, relax):
        """The interpreter class."""

        # Place the program class structure under self.relax
        self.relax = relax

        # Place the macros into the namespace of the interpreter class.
        self._diffusion_tensor = diffusion_tensor(relax)
        self._init_data = init_data(relax)


    def run(self):
        """Run the python interpreter.

        The namespace of this function is the namespace seen inside the interpreter.  All macros
        should be defined in this namespace.
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

        # Place the macro functions in the local namespace.
        diffusion_tensor = self._diffusion_tensor.set
        init_data = self._init_data.init

        # Place the macro classes in the local namespace.
        echo_data = macros.echo_data.skin(self.relax)
        format = macros.format.skin(self.relax)
        load = macros.load.skin(self.relax)
        min = macros.min.skin(self.relax)
        pdb = macros.pdb.skin(self.relax)
        mf_model = macros.mf_model.skin(self.relax)
        modsel = macros.modsel.skin(self.relax)
        state = macros.state.skin(self.relax)
        value = macros.value.skin(self.relax)

        # Builtin interpreter functions.
        echo = _Echo()
        exit = bye = quit = q = _Exit()

        # Setup tab completion.
        readline.set_completer(tab_completion(name_space=locals()).finish)
        readline.parse_and_bind("tab: complete")

        # Modify the help system.
        help_python = _Helper_python()
        help = _Helper()

        # Go to the prompt.
        code.interact(banner=self.relax.intro_string, local=locals())


class _Echo:
    def off(self):
        """Macro for turning off the echoing of commands.

        The default program state is no echoing but if the macro echo_on() has been run and you no
        longer want the echoing, this macro will turn it off.


        Example
        ~~~~~~~

        To run the macro, type the following.

        >>> echo_off()


        FIN
        """

        code.InteractiveConsole.raw_input = self._raw_input
        print "Echoing has been turned off."


    def on(self):
        """Macro for turning on the echoing of commands.

        The default program state is no echoing but if this macro is run all commands will be echoed
        exactly as typed.  This is useful for scipting as commands run from a script are not printed
        to screen.  To turn echoing off, run the macro echo_off()


        Example
        ~~~~~~~

        To run the macro, type the following.

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
For assistence in using a macro, simply type help(macro).  In addition to macros, if help(object)
is typed, the help for the python object is returned.  This system is similar to the help function
built into the python interpreter, which has been renamed to help_python, with the interactive
component removed.  For the interactive python help the interactive python help system, type
help_python().\
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


