###############################################################################
#                                                                             #
# Copyright (C) 2003-2012 Edward d'Auvergne                                   #
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
import ansi
from code import InteractiveConsole, softspace
from os import F_OK, access, chdir, getcwd, path
import platform
from re import search
if dep_check.readline_module:
    import readline
if dep_check.runpy_module:
    import runpy
from string import split
import sys

# Python modules accessible on the command prompt.
from math import pi

# RelaxError system.
from relax_errors import AllRelaxErrors, RelaxBinError, RelaxError, RelaxNoneError, RelaxStrError

# Auxiliary modules.
from prompt.base_class import PS1_ORIG, PS2_ORIG, PS3_ORIG, PS1_COLOUR, PS2_COLOUR, PS3_COLOUR
from command import Ls, Lh, Ll, system
from help import _Helper, _Helper_python
from info import Info_box
if dep_check.readline_module:
    from tab_completion import Tab_completion
from status import Status; status = Status()

# User functions.
from angles import Angles
from dx import OpenDX
from eliminate import Eliminate
from fix import Fix
from gpl import GPL
from reset import Reset
from minimisation import Minimisation
from model_selection import Modsel
from sys_info import Sys_info
from temperature import Temp

# User classes.
from align_tensor import Align_tensor
from bmrb import BMRB
from bruker import Bruker
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
from paramag import Paramag
from pcs import PCS
from pymol_control import Pymol
from rdc import RDC
from relax_data import Relax_data
from relax_fit import Relax_fit
from results import Results
from select import Select
from sequence import Sequence
from spectrum import Spectrum
from spin import Spin
from state import State
from deselect import Deselect
from value import Value
from vmd import Vmd

# User function data structure.
from user_functions.data import Uf_info; uf_info = Uf_info()

# Auto-generation objects.
from prompt.objects import Class_container, Uf_object


class Interpreter:
    def __init__(self, show_script=True, quit=True, raise_relax_error=False):
        """The interpreter class.

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
        self.__show_script = show_script
        self.__quit_flag = quit
        self.__raise_relax_error = raise_relax_error

        # Build the intro string.
        info = Info_box()
        self.__intro_string = info.intro_text()

        # The prompts (change the Python prompt, as well as the function print outs).
        if ansi.enable_control_chars(stream=1):
            self.prompt_colour_on()
        else:
            self.prompt_colour_off()

        # The function intro flag (store in the execution information container).
        status.prompt_intro = False

        # Set up the interpreter objects.
        self._locals = self._setup()

        # Auto-generate the user functions and classes.
        self._auto_generate()


    def _auto_generate(self):
        """Build the user function objects from the user function data object information."""

        # First generate the classes.
        for name, data in uf_info.class_loop():
            # Generate a new container.
            obj = Class_container(name, data.title)

            # Add the object to the local namespace.
            self._locals[name] = obj

        # Then generate the user functions.
        for name, data in uf_info.uf_loop():
            # Split up the name.
            class_name, uf_name = split(name, '.')

            # Generate a new container.
            obj = Uf_object(name, title=data.title, kargs=data.kargs, backend=data.backend, desc=data.desc, examples=data.prompt_examples)

            # Get the class object.
            class_obj = self._locals[class_name]

            # Add the object to the user function class.
            setattr(class_obj, uf_name, obj)



    def _setup(self):
        """Set up all the interpreter objects.

        All objects are initialised and placed in a dictionary.  These will be later placed in different namespaces such as the run() method local namespace.

        @return:    The dictionary of interpreter objects.
        @rtype:     dict
        """

        # Initialise the dictionary.
        objects = {}

        # Python modules.
        objects['pi'] = pi

        # Import the functions emulating system commands.
        objects['lh'] = Lh()
        objects['ll'] = Ll()
        objects['ls'] = Ls()
        objects['system'] = system

        # Place functions in the local namespace.
        objects['gpl'] = objects['GPL'] = GPL()

        # Initialise the user functions (those not in user function classes)
        angles = Angles()
        eliminate = Eliminate()
        fix = Fix()
        reset = Reset()
        minimisation = Minimisation()
        modsel = Modsel()
        opendx = OpenDX()
        sys_info = Sys_info()
        temp = Temp()

        # Place the user functions in the local namespace.
        objects['angle_diff_frame'] = angles.angle_diff_frame
        objects['calc'] = minimisation.calc
        objects['eliminate'] = eliminate.eliminate
        objects['fix'] = fix.fix
        objects['grid_search'] = minimisation.grid_search
        objects['reset'] = reset.reset
        objects['minimise'] = minimisation.minimise
        objects['model_selection'] = modsel.model_selection
        objects['sys_info'] = sys_info.sys_info
        objects['temperature'] = temp.set

        # Place the user classes in the local namespace.
        objects['align_tensor'] = Align_tensor()
        objects['bmrb'] = BMRB()
        objects['bruker'] = Bruker()
        objects['consistency_tests'] = Consistency_tests()
        objects['dasha'] = Dasha()
        objects['deselect'] = Deselect()
        objects['diffusion_tensor'] = Diffusion_tensor()
        objects['frame_order'] = Frame_order()
        objects['dx'] = OpenDX()
        objects['frq'] = Frq()
        objects['grace'] = Grace()
        objects['jw_mapping'] = Jw_mapping()
        objects['model_free'] = Model_free()
        objects['molmol'] = Molmol()
        objects['molecule'] = Molecule()
        objects['monte_carlo'] = Monte_carlo()
        objects['n_state_model'] = N_state_model()
        objects['noe'] = Noe()
        objects['palmer'] = Palmer()
        objects['paramag'] = Paramag()
        objects['pcs'] = PCS()
        objects['pymol'] = Pymol()
        objects['rdc'] = RDC()
        objects['relax_data'] = Relax_data()
        objects['relax_fit'] = Relax_fit()
        objects['residue'] = Residue()
        objects['results'] = Results()
        objects['select'] = Select()
        objects['sequence'] = Sequence()
        objects['spectrum'] = Spectrum()
        objects['spin'] = Spin()
        objects['state'] = State()
        objects['structure'] = Structure()
        objects['value'] = Value()
        objects['vmd'] = Vmd()

        # Builtin interpreter functions.
        objects['intro_off'] = self.off
        objects['intro_on'] = self.on
        objects['exit'] = objects['bye'] = objects['quit'] = objects['q'] = _Exit()
        objects['script'] = self.script

        # Modify the help system.
        objects['help_python'] = _Helper_python()
        objects['help'] = _Helper()

        # Return the dictionary.
        return objects


    def off(self, verbose=True):
        """Turn the function introductions off."""

        status.prompt_intro = False

        # Print out.
        if verbose:
            print("Echoing of user function calls has been disabled.")


    def on(self, verbose=True):
        """Turn the function introductions on."""

        status.prompt_intro = True

        # Print out.
        if verbose:
            print("Echoing of user function calls has been enabled.")


    def populate_self(self):
        """Place all user functions and other special objects into self."""

        # Add the interpreter objects to the class namespace.
        for name in self._locals.keys():
            setattr(self, name, self._locals[name])


    def prompt_colour_off(self):
        """Turn the prompt colouring ANSI escape sequences off."""

        sys.ps1 = status.ps1 = PS1_ORIG
        sys.ps2 = status.ps2 = PS2_ORIG
        sys.ps3 = status.ps3 = PS3_ORIG


    def prompt_colour_on(self):
        """Turn the prompt colouring ANSI escape sequences off."""

        sys.ps1 = status.ps1 = PS1_COLOUR
        sys.ps2 = status.ps2 = PS2_COLOUR
        sys.ps3 = status.ps3 = PS3_COLOUR


    def run(self, script_file=None):
        """Run the python interpreter.

        The namespace of this function is the namespace seen inside the interpreter.  All user
        accessible functions, classes, etc, should be placed in this namespace.


        @param script_file: The script file to be executed.  For the interpreter mode, this
                            should be left as None.
        @type script_file:  None or str
        """

        # Add the interpreter objects to the local run namespace.
        for name in self._locals.keys():
            locals()[name] = self._locals[name]

        # Setup tab completion.
        if dep_check.readline_module:
            readline.set_completer(Tab_completion(name_space=locals()).finish)
            readline.set_completer_delims(' \t\n`~!@#$%^&*()=+{}\\|;:",<>/?')
            readline.parse_and_bind("tab: complete")

        # Execute the script file if given.
        if script_file:
            # Turn on the function intro flag.
            status.prompt_intro = True

            # Run the script.
            return run_script(intro=self.__intro_string, local=locals(), script_file=script_file, quit=self.__quit_flag, show_script=self.__show_script, raise_relax_error=self.__raise_relax_error)

        # Go to the prompt.
        else:
            prompt(intro=self.__intro_string, local=locals())


    def script(self, file=None, quit=False):
        """Function for executing a script file."""

        # Function intro text.
        if status.prompt_intro:
            text = status.ps3 + "script("
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
        orig_intro_state = status.prompt_intro
        status.prompt_intro = True

        # Execute the script.
        run_script(local=self._locals, script_file=file, quit=quit)

        # Return the function intro flag to the original value.
        status.prompt_intro = orig_intro_state


class _Exit:
    def __repr__(self):
        """Exit the program."""

        print("Exiting the program.")
        sys.exit()



def exec_script(name, globals):
    """Execute the script."""

    # Execution lock.
    status.exec_lock.acquire('script UI', mode='script')

    # The module path.
    head, tail = path.split(name)
    script_path = path.join(getcwd(), head)
    sys.path.append(script_path)

    # Switch directories for nested scripting.
    if head:
        orig_dir = getcwd()
        chdir(head)

    # The module name.
    module, ext = path.splitext(tail)

    # Check if the script name is ok.
    if search('\.', module):
        raise RelaxError("The relax script must not contain the '.' character (except before the extension '*.py').")
    if ext != '.py':
        raise RelaxError("The script must have the extension *.py.")

    # Execute the module.
    try:
        # Reverse the system path so that the script path is first.
        sys.path.reverse()

        # Execute the script as a module.
        if dep_check.runpy_module:
            runpy.run_module(module, globals)

        # Allow scripts to run under Python <= 2.4.
        else:
            exec(compile(open(name).read(), name, 'exec'), globals)

    finally:
        # Switch back to the original working directory.
        if head:
            chdir(orig_dir)

        # Remove the script path.
        sys.path.reverse()
        sys.path.pop(sys.path.index(script_path))

    # Unlock execution if needed.
    status.exec_lock.release()


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
        sys.stdout.write("%s\n" % intro)

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

        # Coloured text.
        if ansi.enable_control_chars(stream=1):
            sys.stdout.write(ansi.script)

        # Print the script.
        sys.stdout.write("script = " + repr(script_file) + "\n")
        sys.stdout.write("----------------------------------------------------------------------------------------------------\n")
        sys.stdout.write(file.read())
        sys.stdout.write("----------------------------------------------------------------------------------------------------")

        # End coloured text.
        if ansi.enable_control_chars(stream=1):
            sys.stdout.write(ansi.end)

        # Terminating newline.
        sys.stdout.write("\n")

        # Close the script file handle.
        file.close()

    # The execution flag.
    exec_pass = True

    # Execute the script.
    try:
        exec_script(script_file, local)

    # Catch ctrl-C.
    except KeyboardInterrupt:
        # Unlock execution.
        status.exec_lock.release()

        # Throw the error.
        if status.debug:
            raise

        # Be nicer to the user.
        else:
            sys.stderr.write("\nScript execution cancelled.\n")

        # The script failed.
        exec_pass = False

    # Catch the RelaxErrors.
    except AllRelaxErrors, instance:
        # Unlock execution.
        status.exec_lock.release()

        # Throw the error.
        if raise_relax_error:
            raise

        # Nice output for the user.
        else:
            # Print the scary traceback normally hidden from the user.
            if status.debug:
                self.showtraceback()

            # Print the RelaxError message line.
            else:
                sys.stderr.write(instance.__str__())

            # The script failed.
            exec_pass = False

    # Throw all other errors.
    except:
        # Unlock execution.
        status.exec_lock.release()

        # Raise the error.
        raise

    # Add an empty line to make exiting relax look better.
    if show_script:
        sys.stdout.write("\n")

    # Quit relax.
    # FIXME: need to drop off end of interpreter loop to exit cleanly
    #if quit:
    #    sys.exit()

    # Return the execution flag.
    return exec_pass


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
