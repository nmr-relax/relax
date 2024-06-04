###############################################################################
#                                                                             #
# Copyright (C) 2003-2004,2006,2008-2010,2012,2014 Edward d'Auvergne          #
# Copyright (C) 2014 Troels E. Linnet                                         #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""The prompt based relax user interface (UI)."""

# Dependency check module.
import dep_check

# Python module imports.
from code import InteractiveConsole
from lib import ansi
from math import pi
from os import getcwd, path
from pydoc import pager
from re import search
if dep_check.readline_module:
    import readline
if dep_check.runpy_module:
    import runpy
import sys

# relax module imports.
from info import Info_box
from prompt.command import Ls, Lh, Ll, system
from prompt.help import _Helper, _Helper_python
if dep_check.readline_module:
    from prompt.tab_completion import Tab_completion
from prompt.uf_objects import Class_container, Uf_object
from lib.errors import AllRelaxErrors, RelaxError
from status import Status; status = Status()
from user_functions import uf_translation_table
from user_functions.data import Uf_info; uf_info = Uf_info()


# Module variables.
###################

# The prompts (to change the Python prompt, as well as the function printouts).
PS1_ORIG = 'relax> '
PS2_ORIG = 'relax| '
PS3_ORIG = '\n%s' % PS1_ORIG

# Coloured text.
PS1_COLOUR = "%s%s%s" % (ansi.relax_prompt, PS1_ORIG, ansi.end)
PS2_COLOUR = "%s%s%s" % (ansi.relax_prompt, PS2_ORIG, ansi.end)
PS3_COLOUR = "\n%s%s%s" % (ansi.relax_prompt, PS1_ORIG, ansi.end)


class Interpreter:
    def __init__(self, show_script=True, raise_relax_error=False):
        """The interpreter class.

        @param show_script:         If true, the relax will print the script contents prior to
                                    executing the script.
        @type show_script:          bool
        @param raise_relax_error:   If false, the default, then relax will print a nice error
                                    message to STDERR, without a traceback, when a RelaxError
                                    occurs.  This is to make things nicer for the user.
        @type raise_relax_error:    bool
        """

        # Place the arguments in the class namespace.
        self.__show_script = show_script
        self.__raise_relax_error = raise_relax_error

        # Build the intro string.
        info = Info_box()
        self.__intro_string = info.intro_text()

        # The prompts (change the Python prompt, as well as the function printouts).
        if ansi.enable_control_chars(stream=1) and not status.show_gui:
            self.prompt_colour_on()
        else:
            self.prompt_colour_off()

        # Set up the interpreter objects.
        self._locals = self._setup()


    def _execute_uf(self, *args, **kargs):
        """Private method for executing the given user function.

        @keyword uf_name:   The name of the user function.
        @type uf_name:      str
        """

        # Checks.
        if 'uf_name' not in kargs:
            raise RelaxError("The user function name argument 'uf_name' has not been supplied.")

        # Process the user function name.
        uf_name = kargs.pop('uf_name')

        # Split up the name.
        if search(r'\.', uf_name):
            class_name, uf_name = uf_name.split('.')
        else:
            class_name = None

        # Get the class object.
        if class_name:
            class_obj = self._locals[class_name]

        # Get the user function.
        if class_name:
            uf = getattr(class_obj, uf_name)
        else:
            uf = self._locals[uf_name]

        # Call the user function.
        uf(*args, **kargs)


    def _setup(self):
        """Set up all the interpreter objects.

        All objects are initialised and placed in a dictionary.  These will be later placed in different namespaces such as the run() method local namespace.  All the user functions and classes will be auto-generated.

        @return:    The dictionary of interpreter objects.
        @rtype:     dict
        """

        # Initialise the dictionary.
        objects = {}

        # Python objects.
        objects['pi'] = pi

        # Import the functions emulating system commands.
        objects['lh'] = Lh()
        objects['ll'] = Ll()
        objects['ls'] = Ls()
        objects['system'] = system

        # The GPL license.
        objects['gpl'] = objects['GPL'] = GPL()

        # Builtin interpreter functions.
        objects['intro_off'] = self.off
        objects['intro_on'] = self.on
        objects['exit'] = objects['bye'] = objects['quit'] = objects['q'] = _Exit()

        # Modify the help system.
        objects['help_python'] = _Helper_python()
        objects['help'] = _Helper()

        # Add the user function classes.
        for name, data in uf_info.class_loop():
            # Generate a new container.
            obj = Class_container(name, data.title)

            # Add the object to the local namespace.
            objects[name] = obj

        # Add the user functions.
        self._uf_dict = {}
        for name, data in uf_info.uf_loop():
            # Split up the name.
            if search(r'\.', name):
                class_name, uf_name = name.split('.')
            else:
                class_name = None

            # Generate a new container.
            obj = Uf_object(name, title=data.title, kargs=data.kargs, backend=data.backend, desc=data.desc)

            # Get the class object.
            if class_name:
                class_obj = objects[class_name]

            # Add the object to the local namespace or user function class.
            if class_name:
                setattr(class_obj, uf_name, obj)
            else:
                objects[name] = obj

            # Store the user functions by full text name (for faster retrieval).
            self._uf_dict[name] = obj

        # Return the dictionary.
        return objects


    def off(self, verbose=True):
        """Turn the user function introductions off."""

        status.uf_intro = False

        # Print out.
        if verbose:
            print("Echoing of user function calls has been disabled.")


    def on(self, verbose=True):
        """Turn the user function introductions on."""

        status.uf_intro = True

        # Print out.
        if verbose:
            print("Echoing of user function calls has been enabled.")


    def populate_self(self):
        """Place all special objects into self."""

        # Add the interpreter objects to the class namespace.
        for name in self._locals:
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
        for name in self._locals:
            locals()[name] = self._locals[name]

        # Setup tab completion.
        if dep_check.readline_module:
            readline.set_completer(Tab_completion(name_space=locals()).finish)
            readline.set_completer_delims(' \t\n`~!@#$%^&*()=+{}\\|;:",<>/?')
            if readline.__doc__ != None and 'libedit' in readline.__doc__:
                readline.parse_and_bind("bind ^I rl_complete")
            else:
                readline.parse_and_bind("tab: complete")

        # Execute the script file if given.
        if script_file and not status.prompt:
            # Turn on the user function intro flag.
            status.uf_intro = True

            # Run the script.
            return run_script(intro=self.__intro_string, local=locals(), script_file=script_file, show_script=self.__show_script, raise_relax_error=self.__raise_relax_error)

        # Execute the script and go into prompt if the interactive flag -p --prompt is given at startup.
        if script_file and status.prompt:
            # Turn on the user function intro flag.
            status.uf_intro = True

            # Run the script.
            run_script(intro=self.__intro_string, local=locals(), script_file=script_file, show_script=self.__show_script, raise_relax_error=self.__raise_relax_error)

            # Turn off the user function intro flag.
            status.uf_intro = False

            # Go to the prompt.
            prompt(intro=None, local=locals())

        # Go to the prompt.
        else:
            prompt(intro=self.__intro_string, local=locals())



class _Exit:
    def __repr__(self):
        """Exit the program."""

        print("Exiting the program.")
        sys.exit()


class GPL:
    """A special object for displaying the GPL license."""

    def __repr__(self):
        """Replacement representation."""

        # First display the GPL using paging.
        file = open('docs/COPYING')
        pager(file.read())

        # Then return some text to print out.
        return "The GNU General Public License."



def exec_script(name, globals):
    """Execute the script."""

    # Execution lock.
    status.exec_lock.acquire('script UI', mode='script')

    # The module path.
    head, tail = path.split(name)
    script_path = path.join(getcwd(), head)
    sys.path.append(script_path)

    # The module name.
    module, ext = path.splitext(tail)

    # Check if the script name is ok.
    if search(r'\.', module):
        raise RelaxError("The relax script must not contain the '.' character (except before the extension '*.py').")
    if ext != '.py':
        raise RelaxError("The script must have the extension *.py.")

    # Read the contents of the script for finding old user function calls, prepending a newline character so that old user functions on the first line of a script can be handled.
    file = open(name)
    text = '\n'
    text += file.read()
    file.close()

    # Parse the code in the module for old user function calls.
    for old_uf in uf_translation_table:
        # Find an old call.
        if search('[ \\n]'+old_uf+r'\(', text):
            raise RelaxError("The user function '%s' has been renamed to '%s', please update your script." % (old_uf, uf_translation_table[old_uf]))

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


def interact_script(self, intro=None, local={}, script_file=None, show_script=True, raise_relax_error=False):
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
        except IOError:
            try:
                raise RelaxError("The script file '" + script_file + "' does not exist.")
            except AllRelaxErrors:
                instance = sys.exc_info()[1]
                sys.stdout.write(instance.__str__())
                sys.stdout.write("\n")
                return

        # Coloured text.
        if ansi.enable_control_chars(stream=1) and not status.show_gui:
            sys.stdout.write(ansi.script)

        # Print the script.
        sys.stdout.write("script = " + repr(script_file) + "\n")
        sys.stdout.write("----------------------------------------------------------------------------------------------------\n")
        sys.stdout.write(file.read())
        sys.stdout.write("\n----------------------------------------------------------------------------------------------------")

        # End coloured text.
        if ansi.enable_control_chars(stream=1) and not status.show_gui:
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
        # Throw the error.
        if status.debug:
            raise

        # Be nicer to the user.
        else:
            sys.stderr.write("\nScript execution cancelled.\n")

        # The script failed.
        exec_pass = False

    # Catch the RelaxErrors.
    except AllRelaxErrors:
        instance = sys.exc_info()[1]

        # Throw the error.
        if raise_relax_error:
            raise

        # Nice output for the user.
        else:
            # Print the scary traceback normally hidden from the user.
            if status.debug or status.traceback:
                self.showtraceback()

            # Print the RelaxError message line.
            else:
                sys.stderr.write(instance.__str__())

            # The script failed.
            exec_pass = False

    # Throw all other errors.
    except:
        # Raise the error.
        raise

    # Add an empty line to make exiting relax look better.
    if show_script:
        sys.stdout.write("\n")

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


def run_script(intro=None, local=None, script_file=None, show_script=True, raise_relax_error=False):
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
    return console.interact(intro, local, script_file, show_script=show_script, raise_relax_error=raise_relax_error)


def runcode(self, code):
    """Replacement code for code.InteractiveInterpreter.runcode.

    @param code:    The code to execute.
    @type code:     str
    """

    # Safely run the code.
    try:
        # Catch old user function calls or class method calls.
        if code.co_code in ['e\x00\x00\x83\x00\x00Fd\x00\x00S', 'e\x00\x00j\x01\x00\x83\x00\x00Fd\x00\x00S']:
            # Is this an old user function?
            if len(code.co_names) and '.'.join(code.co_names) in uf_translation_table:
                raise RelaxError("The user function '%s' has been renamed to '%s'." % (code.co_names[0], uf_translation_table[code.co_names[0]]))

        # Execute the code.
        exec(code, self.locals)

    # Allow the system to exit.
    except SystemExit:
        raise

    # Handle RelaxErrors nicely.
    except AllRelaxErrors:
        instance = sys.exc_info()[1]
        self.write(instance.__str__())
        self.write("\n")

    # Everything else.
    except:
        self.showtraceback()
