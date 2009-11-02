###############################################################################
#                                                                             #
# Copyright (C) 2003-2008 Edward d'Auvergne                                   #
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

# Module docstring.
"""The prompt based relax user interface (UI)."""

# Dependency check module.
import dep_check

# Python module imports.
from code import InteractiveConsole, softspace
from os import F_OK, access
if dep_check.readline_module:
    import readline
import sys

# Python modules accessible on the command prompt.
from math import pi

# RelaxError system.
from relax_errors import AllRelaxErrors, RelaxBinError, RelaxError, RelaxNoneError, RelaxStrError

# Auxiliary modules.
from help import _Helper, _Helper_python
from command import Ls, Lh, Ll, system
if dep_check.readline_module:
    from tab_completion import Tab_completion

# User functions.
from angles import Angles
from dx import OpenDX
from eliminate import Eliminate
from fix import Fix
from gpl import GPL
from reset import Reset
from minimisation import Minimisation
from model_selection import Modsel
from temperature import Temp

# User classes.
from align_tensor import Align_tensor
from consistency_tests import Consistency_tests
from dasha import Dasha
from diffusion_tensor import Diffusion_tensor
from frame_order import Frame_order
from frq import Frq
from grace import Grace
from jw_mapping import Jw_mapping
from model_free import Model_free
from molmol import Molmol
from molecule import Molecule
from monte_carlo import Monte_carlo
from n_state_model import N_state_model
from noe import Noe
from palmer import Palmer
from residue import Residue
from structure import Structure
from pcs import PCS
from pymol import Pymol
from rdc import RDC
from relax_data import Relax_data
from relax_disp import Relax_disp
from relax_fit import Relax_fit
from results import Results
from pipe import Pipe
from select import Select
from sequence import Sequence
from spectrum import Spectrum
from spin import Spin
from state import State
from deselect import Deselect
from value import Value
from vmd import Vmd


class Interpreter:
    def __init__(self, relax, intro_string=None, show_script=True, quit=True, raise_relax_error=False):
        """The interpreter class.

        @param relax:               The relax instance.
        @type relax:                instance
        @param intro_string:        The string to print at the start of execution.
        @type intro_string:         str
        @param show_script:         If true, the relax will print the script contents prior to
                                    executing the script.
        @type show_script:          bool
        @param quit:                If true, the default, then relax will exit after running the
                                    run() method.
        @type quit:                 bool
        @param raise_relax_error:   If false, the default, then relax will print a nice error
                                    message to STDERR, without a traceback, when a RelaxError
                                    occurs.  This is to make things nicer for the user.
        @type raise_relax_error:    bool
        """

        # Place the arguments in the class namespace.
        self.relax = relax
        self.__intro_string = intro_string
        self.__show_script = show_script
        self.__quit_flag = quit
        self.__raise_relax_error = raise_relax_error

        # The prompts.
        sys.ps1 = 'relax> '
        sys.ps2 = 'relax| '
        sys.ps3 = '\nrelax> '

        # The function intro flag.
        self.intro = False

        # Python modules.
        self._pi = pi

        # Place the user functions into the namespace of the interpreter class.
        self._Angles = Angles(relax)
        self._Eliminate = Eliminate(relax)
        self._Fix = Fix(relax)
        self._GPL = GPL
        self._Reset = Reset(relax)
        self._Minimisation = Minimisation(relax)
        self._Modsel = Modsel(relax)
        self._Temp = Temp(relax)
        self._OpenDX = OpenDX(relax)
        self._system = system

        # Place the user classes into the interpreter class namespace.
        self._Align_tensor = Align_tensor(relax)
        self._Consistency_tests = Consistency_tests(relax)
        self._Dasha = Dasha(relax)
        self._Diffusion_tensor = Diffusion_tensor(relax)
        self._Frame_order = Frame_order(relax)
        self._OpenDX = OpenDX(relax)
        self._Frq = Frq(relax)
        self._Grace = Grace(relax)
        self._Jw_mapping = Jw_mapping(relax)
        self._Model_free = Model_free(relax)
        self._Molmol = Molmol(relax)
        self._Molecule = Molecule(relax)
        self._Monte_carlo = Monte_carlo(relax)
        self._N_state_model = N_state_model(relax)
        self._Noe = Noe(relax)
        self._Palmer = Palmer(relax)
        self._Residue = Residue(relax)
        self._Structure = Structure(relax)
        self._PCS = PCS(relax)
        self._Pymol = Pymol(relax)
        self._RDC = RDC(relax)
        self._Relax_data = Relax_data(relax)
        self._Relax_disp = Relax_disp(relax)
        self._Relax_fit = Relax_fit(relax)
        self._Results = Results(relax)
        self._Pipe = Pipe(relax)
        self._Select = Select(relax)
        self._Sequence = Sequence(relax)
        self._Spectrum = Spectrum(relax)
        self._Spin = Spin(relax)
        self._State = State(relax)
        self._Deselect = Deselect(relax)
        self._Value = Value(relax)
        self._Vmd = Vmd(relax)


    def run(self, script_file=None):
        """Run the python interpreter.

        The namespace of this function is the namespace seen inside the interpreter.  All user
        accessible functions, classes, etc, should be placed in this namespace.


        @param script_file: The script file to be executed.  For the interpreter mode, this
                            should be left as None.
        @type script_file:  None or str
        """

        # Python modules.
        pi = self._pi

        # Import the functions emulating system commands.
        lh = Lh()
        ll = Ll()
        ls = Ls()
        system = self._system

        # Place functions in the local namespace.
        gpl = GPL = self._GPL()

        # Place the user functions in the local namespace.
        angle_diff_frame = self._Angles.angle_diff_frame
        calc = self._Minimisation.calc
        eliminate = self._Eliminate.eliminate
        fix = self._Fix.fix
        grid_search = self._Minimisation.grid_search
        reset = self._Reset.reset
        minimise = self._Minimisation.minimise
        model_selection = self._Modsel.model_selection
        temperature = self._Temp.set

        # Place the user classes in the local namespace.
        align_tensor = self._Align_tensor
        consistency_tests = self._Consistency_tests
        dasha = self._Dasha
        diffusion_tensor = self._Diffusion_tensor
        frame_order = self._Frame_order
        dx = self._OpenDX
        frq = self._Frq
        grace = self._Grace
        jw_mapping = self._Jw_mapping
        model_free = self._Model_free
        molmol = self._Molmol
        molecule = self._Molecule
        monte_carlo = self._Monte_carlo
        n_state_model = self._N_state_model
        noe = self._Noe
        palmer = self._Palmer
        structure = self._Structure
        pcs = self._PCS
        pymol = self._Pymol
        rdc = self._RDC
        relax_data = self._Relax_data
        relax_disp = self._Relax_disp
        relax_fit = self._Relax_fit
        residue = self._Residue
        results = self._Results
        pipe = self._Pipe
        select = self._Select
        sequence = self._Sequence
        spectrum = self._Spectrum
        spin = self._Spin
        state = self._State
        deselect = self._Deselect
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
        if dep_check.readline_module:
            readline.set_completer(Tab_completion(name_space=self.local).finish)
            readline.set_completer_delims(' \t\n`~!@#$%^&*()=+{}\\|;:",<>/?')
            #readline.set_completer_delims(' \t\n`~!@#$%^&*()=+{}\\|;:\'",<>/?')
            readline.parse_and_bind("tab: complete")

        # Execute the script file if given.
        if script_file:
            # Turn on the function intro flag.
            self.intro = True

            # Run the script.
            return run_script(intro=self.__intro_string, local=self.local, script_file=script_file, quit=self.__quit_flag, show_script=self.__show_script, raise_relax_error=self.__raise_relax_error)

        # Test for the dummy mode for generating documentation (then exit).
        elif hasattr(self.relax, 'dummy_mode'):
            # Place the namespace into self.relax
            self.relax.local = self.local
            return

        # Go to the prompt.
        else:
            prompt(intro=self.__intro_string, local=self.local)


    def _off(self):
        """Function for turning the function introductions off."""

        self.intro = False
        print("Echoing of user function calls has been disabled.")


    def _on(self):
        """Function for turning the function introductions on."""

        self.intro = True
        print("Echoing of user function calls has been enabled.")


    def script(self, file=None, quit=False):
        """Function for executing a script file."""

        # Function intro text.
        if self.intro:
            text = sys.ps3 + "script("
            text = text + "file=" + repr(file)
            text = text + ", quit=" + repr(quit) + ")"
            print(text)

        # File argument.
        if file == None:
            raise RelaxNoneError('file')
        elif not isinstance(file, str):
            raise RelaxStrError('file', file)

        # Test if the script file exists.
        if not access(file, F_OK):
            raise RelaxError("The script file '" + file + "' does not exist.")

        # Quit argument.
        if not isinstance(quit, int) or (quit != False and quit != True):
            raise RelaxBinError('quit', quit)

        # Turn on the function intro flag.
        orig_intro_state = self.intro
        self.intro = True

        # Execute the script.
        run_script(local=self.local, script_file=file, quit=quit)

        # Return the function intro flag to the original value.
        self.intro = orig_intro_state


class _Exit:
    def __repr__(self):
        """Exit the program."""

        print("Exiting the program.")
        sys.exit()


def interact_prompt(self, intro=None, local={}):
    """Replacement function for 'code.InteractiveConsole.interact'.

    This will enter into the prompt.

    @param intro:   The string to print prior to jumping to the prompt mode.
    @type intro:    str
    @param local:   A namespace which will become that of the prompt (i.e. the namespace visible to
                    the user when in the prompt mode).  This should be the output of a function such
                    as locals().
    @type local:    dict
    """

    # Print the program introduction.
    if intro:
        self.write("%s\n" % intro)

    # Ignore SIGINT.
    #signal.signal(2, 1)

    # Prompt.
    more = False
    while True:
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
            more = False


def interact_script(self, intro=None, local={}, script_file=None, quit=True, show_script=True, raise_relax_error=False):
    """Replacement function for 'code.InteractiveConsole.interact'.

    This will execute the script file.


    @param intro:               The string to print prior to jumping to the prompt mode.
    @type intro:                str
    @param local:               A namespace which will become that of the prompt (i.e. the namespace
                                visible to the user when in the prompt mode).  This should be the
                                output of a function such as locals().
    @type local:                dict
    @param script_file:         The script file to be executed.
    @type script_file:          None or str
    @param quit:                If true, the default, then relax will exit after running the script.
    @type quit:                 bool
    @param show_script:         If true, the relax will print the script contents prior to executing
                                the script.
    @type show_script:          bool
    @param raise_relax_error:   If false, the default, then a nice error message will be sent to
                                STDERR, without a traceback, when a RelaxError occurs.  This is to
                                make things nicer for the user.
    @type raise_relax_error:    bool
    """

    # Print the program introduction.
    if intro:
        sys.stdout.write("%s\n" % intro)

    # Turn the intro flag on so functions will print their intro strings.
    local['self'].intro = True

    # Print the script.
    if show_script:
        try:
            file = open(script_file, 'r')
        except IOError, warning:
            try:
                raise RelaxError("The script file '" + script_file + "' does not exist.")
            except AllRelaxErrors, instance:
                sys.stdout.write(instance.__str__())
                sys.stdout.write("\n")
                return
        sys.stdout.write("script = " + repr(script_file) + "\n")
        sys.stdout.write("----------------------------------------------------------------------------------------------------\n")
        sys.stdout.write(file.read())
        sys.stdout.write("----------------------------------------------------------------------------------------------------\n")
        file.close()

    # The execution status.
    status = True

    # Execute the script.
    try:
        exec(compile(open(script_file).read(), script_file, 'exec'), local)

    # Catch ctrl-C.
    except KeyboardInterrupt:
        # Throw the error.
        if Debug:
            raise

        # Be nicer to the user.
        else:
            sys.stderr.write("\nScript execution cancelled.\n")

        # The script failed.
        status = False

    # Catch the RelaxErrors.
    except AllRelaxErrors, instance:
        # Throw the error.
        if raise_relax_error:
            raise

        # Nice output for the user.
        else:
            # Print the scary traceback normally hidden from the user.
            if Debug:
                self.showtraceback()

            # Print the RelaxError message line.
            else:
                sys.stderr.write(instance.__str__())

            # The script failed.
            status = False

    # Throw all other errors.
    except:
        raise

    # Add an empty line to make exiting relax look better.
    if show_script:
        sys.stdout.write("\n")

    # Quit relax.
    if quit:
        sys.exit()

    # Return the status.
    return status


def prompt(intro=None, local=None):
    """Python interpreter emulation.

    This function replaces 'code.interact'.


    @param intro:   The string to print prior to jumping to the prompt mode.
    @type intro:    str
    @param local:   A namespace which will become that of the prompt (i.e. the namespace visible to
                    the user when in the prompt mode).  This should be the output of a function such
                    as locals().
    @type local:    dict
    """

    # Replace the 'InteractiveConsole.interact' and 'InteractiveConsole.runcode' functions.
    InteractiveConsole.interact = interact_prompt
    InteractiveConsole.runcode = runcode

    # The console.
    console = InteractiveConsole(local)
    console.interact(intro, local)


def run_script(intro=None, local=None, script_file=None, quit=True, show_script=True, raise_relax_error=False):
    """Python interpreter emulation.

    This function replaces 'code.interact'.


    @param intro:               The string to print prior to jumping to the prompt mode.
    @type intro:                str
    @param local:               A namespace which will become that of the prompt (i.e. the namespace
                                visible to the user when in the prompt mode).  This should be the
                                output of a function such as locals().
    @type local:                dict
    @param script_file:         The script file to be executed.
    @type script_file:          None or str
    @param quit:                If true, the default, then relax will exit after running the script.
    @type quit:                 bool
    @param show_script:         If true, the relax will print the script contents prior to executing
                                the script.
    @type show_script:          bool
    @param raise_relax_error:   If false, the default, then a nice error message will be sent to
                                STDERR, without a traceback, when a RelaxError occurs.  This is to
                                make things nicer for the user.
    @type raise_relax_error:    bool
    """

    # Replace the 'InteractiveConsole.interact' and 'InteractiveConsole.runcode' functions.
    InteractiveConsole.interact = interact_script
    InteractiveConsole.runcode = runcode

    # The console.
    console = InteractiveConsole(local)
    return console.interact(intro, local, script_file, quit, show_script=show_script, raise_relax_error=raise_relax_error)


def runcode(self, code):
    """Replacement code for code.InteractiveInterpreter.runcode.

    @param code:    The code to execute.
    @type code:     str
    """

    try:
        exec(code, self.locals)
    except SystemExit:
        raise
    except AllRelaxErrors, instance:
        self.write(instance.__str__())
        self.write("\n")
    except:
        self.showtraceback()
    else:
        if softspace(sys.stdout, 0):
            print('')
