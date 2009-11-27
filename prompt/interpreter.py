###############################################################################
#                                                                             #
# Copyright (C) 2003-2005 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
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
#import signal
import sys

# Python modules accessible on the command prompt.
from math import pi
import Numeric
import Scientific

# Auxiliary modules.
from help import _Helper, _Helper_python
from command import Ls, Lh, Ll, system
from tab_completion import Tab_completion

# User functions.
from angles import Angles
from dx import OpenDX
from eliminate import Eliminate
from fix import Fix
from gpl import GPL
from init_data import Init_data
from minimisation import Minimisation
from model_selection import Modsel
from nuclei import Nuclei
from pdb import PDB

# User classes.
from dasha import Dasha
from diffusion_tensor import Diffusion_tensor
from grace import Grace
from jw_mapping import Jw_mapping
from model_free import Model_free
from model_free_csa import Model_free_csa
from molmol import Molmol
from monte_carlo import Monte_carlo
from noe import Noe
from palmer import Palmer
from relax_data import Relax_data
from csa_data import Csa_data
from relax_fit import Relax_fit
from results import Results
from run import Run
from select import Select
from sequence import Sequence
from state import State
from thread import Threading
from unselect import Unselect
from value import Value
from vmd import Vmd


class Interpreter:
    def __init__(self, relax):
        """The interpreter class."""

        # Place the program class structure under self.relax
        self.relax = relax

        # The prompts.
        sys.ps1 = 'relax> '
        sys.ps2 = 'relax| '
        sys.ps3 = '\nrelax> '

        # The function intro flag.
        self.intro = 0

        # Python modules.
        self._pi = pi
        self._Numeric = Numeric
        self._Scientific = Scientific

        # Place the user functions into the namespace of the interpreter class.
        self._Angles = Angles(relax)
        self._Eliminate = Eliminate(relax)
        self._Fix = Fix(relax)
        self._GPL = GPL
        self._Init_data = Init_data(relax)
        self._Minimisation = Minimisation(relax)
        self._Modsel = Modsel(relax)
        self._Nuclei = Nuclei(relax)
        self._OpenDX = OpenDX(relax)
        self._PDB = PDB(relax)
        self._system = system

        # Place the user classes into the interpreter class namespace.
        self._Dasha = Dasha(relax)
        self._Diffusion_tensor = Diffusion_tensor(relax)
        self._OpenDX = OpenDX(relax)
        self._Grace = Grace(relax)
        self._Jw_mapping = Jw_mapping(relax)
        self._Model_free = Model_free(relax)
        self._Model_free_csa = Model_free_csa(relax)
        self._Molmol = Molmol(relax)
        self._Monte_carlo = Monte_carlo(relax)
        self._Noe = Noe(relax)
        self._Palmer = Palmer(relax)
        self._Relax_data = Relax_data(relax)
        self._Csa_data = Csa_data(relax)
        self._Relax_fit = Relax_fit(relax)
        self._Results = Results(relax)
        self._Run = Run(relax)
        self._Select = Select(relax)
        self._Sequence = Sequence(relax)
        self._State = State(relax)
        self._Threading = Threading(relax)
        self._Unselect = Unselect(relax)
        self._Value = Value(relax)
        self._Vmd = Vmd(relax)


    def run(self):
        """Run the python interpreter.

        The namespace of this function is the namespace seen inside the interpreter.  All user
        accessible functions, classes, etc, should be placed in this namespace.
        """

        # Python modules.
        pi = self._pi
        Numeric = self._Numeric
        Scientific = self._Scientific

        # Import the functions emulating system commands.
        lh = Lh()
        ll = Ll()
        ls = Ls()
        system = self._system

        # Place functions in the local namespace.
        gpl = GPL = self._GPL()

        # Place the user functions in the local namespace.
        angles = self._Angles.angles
        calc = self._Minimisation.calc
        eliminate = self._Eliminate.eliminate
        fix = self._Fix.fix
        grid_search = self._Minimisation.grid_search
        init_data = self._Init_data.init
        minimise = self._Minimisation.minimise
        model_selection = self._Modsel.model_selection
        nuclei = self._Nuclei.nuclei
        pdb = self._PDB.pdb

        # Place the user classes in the local namespace.
        dasha = self._Dasha
        diffusion_tensor = self._Diffusion_tensor
        dx = self._OpenDX
        grace = self._Grace
        jw_mapping = self._Jw_mapping
        model_free = self._Model_free
        model_free_csa = self._Model_free_csa
        molmol = self._Molmol
        monte_carlo = self._Monte_carlo
        noe = self._Noe
        palmer = self._Palmer
        relax_data = self._Relax_data
        csa_data = self._Csa_data
        relax_fit = self._Relax_fit
        results = self._Results
        run = self._Run
        select = self._Select
        sequence = self._Sequence
        state = self._State
        thread = self._Threading
        unselect = self._Unselect
        vmd = self._Vmd
        value = self._Value

        # Builtin interpreter functions.
        intro_off = self._off
        intro_on = self._on
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

        # Execute the script file if given.
        if self.relax.script_file:
            # Turn on the function intro flag.
            self.intro = 1

            # Run the script.
            run_script(intro=self.relax.intro_string, local=self.local, script_file=self.relax.script_file, quit=1)

        # Test for the dummy mode for generating documentation (then exit).
        elif hasattr(self.relax, 'dummy_mode'):
            # Place the namespace into self.relax
            self.relax.local = self.local
            return

        # Go to the prompt.
        else:
            prompt(intro=self.relax.intro_string, local=self.local)


    def _off(self):
        """Function for turning the function introductions off."""

        self.intro = 0
        print "Function intros have been disabled."


    def _on(self):
        """Function for turning the function introductions on."""

        self.intro = 1
        print "Function intros have been enabled."


    def script(self, file=None, quit=0):
        """Function for executing a script file."""

        # File argument.
        if file == None:
            raise RelaxNoneError, 'file'
        elif type(file) != str:
            raise RelaxStrError, ('file', file)

        # Test if the script file exists.
        if not access(file, F_OK):
            raise RelaxError, "The script file '" + file + "' does not exist."

        # Quit argument.
        if type(quit) != int or (quit != 0 and quit != 1):
            raise RelaxBinError, ('quit', quit)

        # Turn on the function intro flag.
        self.intro = 1

        # Execute the script.
        run_script(local=self.local, script_file=file, quit=quit)

        # Turn off the function intro flag.
        self.intro = 0


class _Exit:
    def __repr__(self):
        """Exit the program."""

        print "Exiting the program."
        sys.exit()


def interact_prompt(self, intro, local):
    """Replacement function for 'code.InteractiveConsole.interact'.

    This will enter into the prompt.
    """

    # Print the program introduction.
    if intro:
        self.write("%s\n" % intro)

    # Ignore SIGINT.
    #signal.signal(2, 1)

    # Prompt.
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


def interact_script(self, intro, local, script_file, quit):
    """Replacement function for 'code.InteractiveConsole.interact'.

    This will execute the script file.
    """

    # Print the program introduction.
    if intro:
        sys.stdout.write("%s\n" % intro)

    # Turn the intro flag on so functions will print their intro strings.
    local['self'].intro = 1

    # Print the script.
    try:
        file = open(script_file, 'r')
    except IOError, warning:
        try:
            raise RelaxError, "The script file '" + script_file + "' does not exist."
        except AllRelaxErrors, instance:
            sys.stdout.write(instance.__str__())
            sys.stdout.write("\n")
            return
    sys.stdout.write("script = " + `script_file` + "\n")
    sys.stdout.write("----------------------------------------------------------------------------------------------------\n")
    sys.stdout.write(file.read())
    sys.stdout.write("----------------------------------------------------------------------------------------------------\n")
    file.close()

    # Execute the script.
    try:
        execfile(script_file, local)
    except KeyboardInterrupt:
        if Debug:
            raise
        else:
            sys.stderr.write("\nScript execution cancelled.\n")
    except AllRelaxErrors, instance:
        if Debug:
            self.showtraceback()
        else:
            sys.stderr.write(instance.__str__())
    except:
        raise

    sys.stdout.write("\n")

    # Quit.
    if quit:
        sys.exit()


def prompt(intro=None, local=None):
    """Python interpreter emulation.

    This function replaces 'code.interact'.
    """

    # Replace the 'InteractiveConsole.interact' and 'InteractiveConsole.runcode' functions.
    InteractiveConsole.interact = interact_prompt
    InteractiveConsole.runcode = runcode

    # The console.
    console = InteractiveConsole(local)
    console.interact(intro, local)


def run_script(intro=None, local=None, script_file=None, quit=1):
    """Python interpreter emulation.

    This function replaces 'code.interact'.
    """

    # Replace the 'InteractiveConsole.interact' and 'InteractiveConsole.runcode' functions.
    InteractiveConsole.interact = interact_script
    InteractiveConsole.runcode = runcode

    # The console.
    console = InteractiveConsole(local)
    console.interact(intro, local, script_file, quit)


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
