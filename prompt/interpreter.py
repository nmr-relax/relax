###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# Relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# Relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

import __builtin__
from code import InteractiveConsole, softspace
from os import F_OK, access
import readline
import sys

# Python modules accessable on the command prompt.
import Numeric
import Scientific

# Auxillary modules.
from tab_completion import Tab_completion
from command import Ls, Lh, Ll, system
from print_all_data import Print_all_data

# Macro functions.
from angles import Angles
from calc import Calc
from delete import Delete
from diffusion_tensor import Diffusion_tensor
from dx import OpenDX
from fixed import Fixed
from gpl import GPL
from grid import Grid
from init_data import Init_data
from map import Map
from minimise import Minimise
from model_selection import Modsel
from nuclei import Nuclei
from pdb import PDB
from vectors import Vectors
from view import View
from write import Write

# Macro classes.
import echo_data
import format
import model
import read
import select
import state
import value


class Interpreter:
    def __init__(self, relax):
        """The interpreter class."""

        # Place the program class structure under self.relax
        self.relax = relax

        # The prompts.
        sys.ps1 = 'relax> '
        sys.ps2 = 'relax| '
        sys.macro_prompt = '\n<macro> '

        # The macro intro flag.
        self.intro = 0

        # Python modules.
        self._Numeric = Numeric
        self._Scientific = Scientific

        # Place the functions into the namespace of the interpreter class.
        self._Angles = Angles(relax)
        self._Calc = Calc(relax)
        self._Delete = Delete(relax)
        self._Diffusion_tensor = Diffusion_tensor(relax)
        self._Fixed = Fixed(relax)
        self._GPL = GPL
        self._Grid = Grid(relax)
        self._Init_data = Init_data(relax)
        self._Map = Map(relax)
        self._Minimise = Minimise(relax)
        self._Modsel = Modsel(relax)
        self._Nuclei = Nuclei(relax)
        self._OpenDX = OpenDX(relax)
        self._PDB = PDB(relax)
        self._system = system
        self._Vectors = Vectors(relax)
        self._View = View(relax)
        self._Write = Write(relax)

        # Place the classes into the interpreter class namespace.
        self._Echo_data = echo_data.Skin(relax)
        self._Format = format.Skin(relax)
        self._Model = model.Model(relax)
        self._Read = read.Skin(relax)
        self._Select = select.Skin(relax)
        self._State = state.Skin(relax)
        self._Value = value.Skin(relax)


    def run(self):
        """Run the python interpreter.

        The namespace of this function is the namespace seen inside the interpreter.  All user
        accessable functions, macros, etc, should be placed in this namespace.
        """

        # Python modules.
        Numeric = self._Numeric
        Scientific = self._Scientific

        # Import the functions emulating system commands.
        lh = Lh()
        ll = Ll()
        ls = Ls()
        system = self._system
        print_all_data = Print_all_data(self.relax)

        # Place functions in the local namespace.
        gpl = GPL = self._GPL()

        # Place the functions in the local namespace.
        angles = self._Angles.angles
        calc = self._Calc.calc
        delete = self._Delete.delete
        diffusion_tensor = self._Diffusion_tensor.diffusion_tensor
        dx = self._OpenDX.dx
        fixed = self._Fixed.fixed
        grid_search = self._Grid.grid_search
        init_data = self._Init_data.init
        map = self._Map.map
        minimise = self._Minimise.minimise
        model_selection = self._Modsel.model_selection
        nuclei = self._Nuclei.nuclei
        pdb = self._PDB.pdb
        vectors = self._Vectors.vectors
        view = self._View.view
        write = self._Write.write

        # Place the classes in the local namespace.
        echo_data = self._Echo_data
        format = self._Format
        read = self._Read
        model = self._Model
        select = self._Select
        state = self._State
        value = self._Value

        # Builtin interpreter functions.
        intro_off = self._off
        intro_on = self._on
        execfile = __builtin__.execfile
        exit = bye = quit = q = _Exit()
        script = self.script

        # Modify the help system.
        help_python = _Helper_python()
        help = _Helper()

        # The local namespace.
        self.local = locals()

        # Setup tab completion.
        readline.set_completer(Tab_completion(name_space=self.local).finish)
        readline.set_completer_delims(' \t\n`~!@#$%^&*()=+{}\\|;:",<>/?')
        #readline.set_completer_delims(' \t\n`~!@#$%^&*()=+{}\\|;:\'",<>/?')
        readline.parse_and_bind("tab: complete")

        # Go to the prompt.
        prompt(intro=self.relax.intro_string, local=self.local, script_file=self.relax.script_file)


    def _off(self):
        """Function for turning the macro intro's off."""

        self.intro = 0
        print "Macro intro's have been disabled."


    def _on(self):
        """Function for turning the macro intro's on."""

        self.intro = 1
        print "Macro intro's have been enabled."


    def script(self, file=None):
        """Macro for executing a script file."""

        # File argument.
        if file == None:
            raise RelaxNoneError, 'file'
        elif type(file) != str:
            raise RelaxStrError, ('file', file)

        # Turn on the macro intro flag.
        self.intro = 1

        # Execute the script.
        script(file, self.local)

        # Turn off the macro intro flag.
        self.intro = 0


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


def interact(self, intro=None, local=None, script_file=None):
    """Replacement function for 'code.InteractiveConsole.interact'.

    This will either execute a command line specified script file or enter into the prompt.
    """

    # Print the program introduction.
    self.write("%s\n" % intro)

    # Execute the script file, if given on the command line, and then exit.
    if script_file != None:
        # Turn the intro flag on so macros will print there intro strings.
        local['self'].intro = 1

        # Execute the script.
        script(script_file, local)
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


def prompt(intro=None, local=None, script_file=None):
    """Python interpreter emulation.

    This function replaces 'code.interact'.
    """

    # Replace the 'InteractiveConsole.interact' and 'InteractiveConsole.runcode' functions.
    InteractiveConsole.interact = interact
    InteractiveConsole.runcode = runcode

    # The console.
    console = InteractiveConsole(local)
    console.interact(intro, local, script_file)


def runcode(self, code):
    """Replacement code for code.InteractiveInterpreter.runcode"""

    try:
        exec code in self.locals
    except SystemExit:
        raise
    except AllRelaxErrors, instance:
        self.write(instance.__str__())
        self.write("\n")
    except:
        self.showtraceback()
    else:
        if softspace(sys.stdout, 0):
            print


def script(script_file, local):
    """Function for executing the script file."""

    # Test if the script file exists.
    if not access(script_file, F_OK):
        sys.stderr.write("The script file '" + script_file + "' does not exist.\n")
        return

    # Print the script.
    file = open(script_file, 'r')
    sys.stdout.write("script = " + `script_file` + "\n")
    sys.stdout.write("----------------------------------------------------------------------------------------------------\n")
    sys.stdout.write(file.read())
    sys.stdout.write("----------------------------------------------------------------------------------------------------\n")
    file.close()

    # Execute the script.
    try:
        execfile(script_file, local)
    except KeyboardInterrupt:
        sys.stdout.write("\nScript execution cancelled.\n")
    except AllRelaxErrors, instance:
        sys.stdout.write(instance.__str__())
    sys.stdout.write("\n")
