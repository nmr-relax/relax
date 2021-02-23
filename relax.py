###############################################################################
#                                                                             #
# Copyright (C) 2001-2014,2019 Edward d'Auvergne                              #
# Copyright (C) 2006 Chris MacRaild                                           #
# Copyright (C) 2007 Gary Thompson                                            #
# Copyright (C) 2008 Sebastien Morin                                          #
# Copyright (C) 2019 Troels Schwarz-Linnet                                    #
#                                                                             #
# This program is free software; you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU Library General Public License for more details.                        #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program; if not, write to the Free Software                 #
#                                                                             #
###############################################################################

# Module docstring.
"""The main module for relax execution."""

# Dependency checks.
import dep_check

# Eliminate the ^[[?1034h escape code being produced on Linux systems by the import of the readline module.
import os
if 'TERM' in os.environ and os.environ['TERM'] == 'xterm':
    os.environ['TERM'] = 'linux'

# Set up the Python 2 and 3 work-arounds.
import lib.compat

# Python modules.
from argparse import ArgumentParser
import numpy
from os import F_OK, access, getpid, putenv
if dep_check.cprofile_module:
    import cProfile as profile
elif dep_check.profile_module:
    import profile
import pstats
from pydoc import pager
import sys

# relax modules.
from info import Info_box
import lib.errors
from lib.io import io_streams_log, io_streams_tee
import lib.warnings
from multi import Application_callback, load_multiprocessor
from prompt import interpreter
from status import Status; status = Status()
import user_functions
import version


# Set up the user functions.
user_functions.initialise()

# Modify the environmental variables.
putenv('PDBVIEWER', 'vmd')


def start(mode=None, profile_flag=False):
    """Execute relax.

    @keyword mode:          Force a relax mode, overriding the command line.
    @type mode:             str
    @keyword profile_flag:  Change this flag to True for code profiling.
    @type profile_flag:     bool
    """

    # Normal relax operation.
    relax = Relax()

    # Override normal operation.
    if mode:
        # Override the mode.
        relax.mode = mode

        # Some defaults.
        relax.script_file = None
        relax.log_file = None
        relax.tee_file = None
        relax.multiprocessor_type = 'uni'
        relax.n_processors = 1

    # Process the command line arguments.
    else:
        relax.arguments()

    # Store some start up info in the status object.
    status.relax_mode = relax.mode

    # Set up the multi-processor elements.
    callbacks = Application_callback(master=relax)
    verbosity = 0
    if status.debug:
        verbosity = 1
    processor = load_multiprocessor(relax.multiprocessor_type, callbacks, processor_size=relax.n_processors, verbosity=verbosity)

    # Place the processor fabric intro string into the info box.
    info = Info_box()
    info.multi_processor_string = processor.get_intro_string()

    # Normal relax operation.
    if not profile_flag:
        # Execute relax in multi-processor mode (this includes the uni-processor for normal operation).
        processor.run()
        sys.exit(callbacks.master.exit_code)

    # relax in profiling mode.
    else:
        def print_stats(stats, status=0):
            pstats.Stats(stats).sort_stats('time', 'name').print_stats()

        # No profile module.
        if not dep_check.profile_module:
            sys.stderr.write("The profile module is not available, please install the Python development packages for profiling.\n\n")
            sys.exit()

        # Run relax in profiling mode.
        profile.Profile.print_stats = print_stats
        profile.runctx('processor.run()', globals(), locals())



class Relax:
    """The main relax class.

    This contains information about the running state, for example the mode of operation of relax,
    whether debugging is turned on, etc.
    """

    def __init__(self):
        """The top level class for initialising the program."""

        # Get and store the PID of this process.
        self.pid = getpid()

        # Set up default process-management exit code
        self.exit_code = 0


    def run(self):
        """Execute relax.

        This is the application callback method executed by the multi-processor framework.
        """

        # Set up the warning system.
        lib.warnings.setup()

        # Logging.
        if self.log_file:
            io_streams_log(self.log_file)

        # Tee.
        elif self.tee_file:
            io_streams_tee(self.tee_file)

        # Show the version number and exit.
        if self.mode == 'version':
            print('relax ' + version.version_full())
            return

        # Show the relax info and exit.
        if self.mode == 'info':
            # Initialise the information box.
            info = Info_box()

            # Print the program intro.
            print(info.intro_text())

            # Print the system info.
            print(info.sys_info())

            # Stop execution.
            return

        # Run the interpreter for the prompt or script modes.
        if self.mode == 'prompt' or self.mode == 'script':
            # Run the interpreter.
            self.interpreter = interpreter.Interpreter()
            self.interpreter.run(self.script_file)

        # Execute the relax GUI.
        elif self.mode == 'gui':
            # Dependency check.
            if not dep_check.wx_module:
                sys.stderr.write("Please install the wx Python module to access the relax GUI.\n\n")
                return

            # Only import the module in this mode (to improve program start up speeds).
            import gui

            # Set the GUI flag in the status object.
            status.show_gui = True

            # Start the relax GUI wx application.
            app = gui.App(script_file=self.script_file)
            app.MainLoop()

        # Execute the relax test suite
        elif self.mode == 'test suite':
            # Only import the module in the test modes (to improve program start up speeds).
            from test_suite.test_suite_runner import Test_suite_runner

            # Load the interpreter and turn intros on.
            self.interpreter = interpreter.Interpreter(show_script=False, raise_relax_error=True)
            self.interpreter.on()

            # Run the tests.
            runner = Test_suite_runner(self.tests, timing=self.test_timings, io_capture=self.io_capture, list_tests=self.list_tests)
            self.exit_code = int(not runner.run_all_tests())

        # Execute the relax system tests.
        elif self.mode == 'system tests':
            # Only import the module in the test modes (to improve program start up speeds).
            from test_suite.test_suite_runner import Test_suite_runner

            # Load the interpreter and turn intros on.
            self.interpreter = interpreter.Interpreter(show_script=False, raise_relax_error=True)
            self.interpreter.on()

            # Run the tests.
            runner = Test_suite_runner(self.tests, timing=self.test_timings, io_capture=self.io_capture, list_tests=self.list_tests)
            self.exit_code = int(not runner.run_system_tests())

        # Execute the relax unit tests.
        elif self.mode == 'unit tests':
            # Only import the module in the test modes (to improve program start up speeds).
            from test_suite.test_suite_runner import Test_suite_runner

            # Run the tests.
            runner = Test_suite_runner(self.tests, timing=self.test_timings, io_capture=self.io_capture, list_tests=self.list_tests)
            self.exit_code = int(not runner.run_unit_tests())

        # Execute the relax GUI tests.
        elif self.mode == 'GUI tests':
            # Only import the module in the test modes (to improve program start up speeds).
            from test_suite.test_suite_runner import Test_suite_runner

            # Run the tests.
            runner = Test_suite_runner(self.tests, timing=self.test_timings, io_capture=self.io_capture, list_tests=self.list_tests)
            self.exit_code = int(not runner.run_gui_tests())

        # Execute the relax verification tests.
        elif self.mode == 'verification tests':
            # Only import the module in the test modes (to improve program start up speeds).
            from test_suite.test_suite_runner import Test_suite_runner

            # Run the tests.
            runner = Test_suite_runner(self.tests, timing=self.test_timings, io_capture=self.io_capture, list_tests=self.list_tests)
            self.exit_code = int(not runner.run_verification_tests())

        # Test mode.
        elif self.mode == 'test':
            self.test_mode()

        # Licence mode.
        elif self.mode == 'licence':
            self.licence()

        # Unknown mode.
        else:
            raise lib.errors.RelaxError("The '%s' mode is unknown." % self.mode)


    def arguments(self):
        """Process the command line arguments."""

        # Parser object.
        parser = RelaxParser(description="Molecular dynamics by NMR data analysis.")

        # Recognised command line arguments for the UI.
        group = parser.add_argument_group('UI arguments', description="The arguments for selecting between the different user interfaces (UI) of relax.  If none of these arguments are supplied relax will default into prompt mode or, if a script is supplied, into script mode.")
        group.add_argument('-p', '--prompt', action='store_true', dest='prompt', default=0, help='launch relax in prompt mode after running any optionally supplied scripts')
        group.add_argument('-g', '--gui', action='store_true', dest='gui', default=0, help='launch the relax graphical user interface (GUI)')
        group.add_argument('-i', '--info', action='store_true', dest='info', default=0, help='display information about this version of relax')
        group.add_argument('-v', '--version', action='store_true', dest='version', default=0, help='show the version number and exit')
        group.add_argument('--licence', action='store_true', dest='licence', default=0, help='display the licence')
        group.add_argument('--test', action='store_true', dest='test', default=0, help='run relax in test mode')

        # Recognised command line arguments for the multiprocessor.
        group = parser.add_argument_group('Multi-processor arguments', description="The arguments allowing relax to run in multi-processor environments.")
        group.add_argument('-m', '--multi', action='store', type=str, dest='multiprocessor', default='uni', help='set multi processor method to one of \'uni\' or \'mpi4py\'')
        group.add_argument('-n', '--processors', action='store', type=int, dest='n_processors', default=-1, help='set number of processors (may be ignored)')

        # Recognised command line arguments for IO redirection.
        group = parser.add_argument_group('IO redirection arguments', description="The arguments for sending relax output into a file.")
        group.add_argument('-l', '--log', action='store', type=str, dest='log', help='log relax output to the file LOG_FILE', metavar='LOG_FILE')
        group.add_argument('-t', '--tee', action='store', type=str, dest='tee', help='tee relax output to both stdout and the file LOG_FILE', metavar='LOG_FILE')

        # Recognised command line arguments for the test suite.
        group = parser.add_argument_group('Test suite arguments', description="The arguments for activating the relax test suite.  A subset of tests can be selected by providing the name of one or more test classes, test modules, or individual tests.  The names of the tests are shown if the test fails, errors, when the test timings are active, or when IO capture is disabled.")
        group.add_argument('-x', '--test-suite', action='store_true', dest='test_suite', default=0, help='execute the full relax test suite')
        group.add_argument('-s', '--system-tests', action='store_true', dest='system_tests', default=0, help='execute the system/functional tests')
        group.add_argument('-u', '--unit-tests', action='store_true', dest='unit_tests', default=0, help='execute the unit tests')
        group.add_argument('--gui-tests', action='store_true', dest='gui_tests', default=0, help='execute the GUI tests')
        group.add_argument('--verification-tests', action='store_true', dest='verification_tests', default=0, help='execute the software verification tests')
        group.add_argument('--time', action='store_true', dest='tt', default=0, help='print out the timings of individual tests in the test suite')
        group.add_argument('--no-capt', '--no-capture', action='store_true', dest='no_capture', default=0, help='disable IO capture in the test suite')
        group.add_argument('--no-skip', action='store_true', dest='no_skip', default=0, help='a debugging option for relax developers to turn on all blacklisted tests, even those that will fail')
        group.add_argument('--list-tests', action='store_true', dest='list_tests', default=0, help='list the selected tests instead of executing them')

        # Recognised command line arguments for debugging.
        group = parser.add_argument_group('Debugging arguments', "The arguments for helping to debug relax.")
        group.add_argument('-d', '--debug', action='store_true', dest='debug', default=0, help='enable verbose debugging output')
        group.add_argument('--error-state', action='store_true', dest='error_state', default=0, help='save a pickled state file when a RelaxError occurs')
        group.add_argument('--traceback', action='store_true', dest='traceback', default=0, help='show stack tracebacks on all RelaxErrors and RelaxWarnings')
        group.add_argument('-e', '--escalate', action='store_true', dest='escalate', default=0, help='escalate all warnings into errors')
        group.add_argument('--numpy-raise', action='store_true', dest='numpy_raise', default=0, help='convert numpy warnings into errors')

        # The script file or tests to run.
        parser.add_argument('script', nargs='*', help='the script file or one or more test classes or individual tests to run')

        # Parse the arguments.
        args = parser.parse_args()

        # Debugging arguments:  Debugging flag, escalate flag, traceback flag, and numpy warning to error conversion.
        if args.debug:
            status.debug = True
        if args.escalate:
            lib.warnings.ESCALATE = True
        if args.traceback:
            status.traceback = True
            lib.warnings.TRACEBACK = True
        if args.numpy_raise:
            numpy.seterr(all='raise')
        if args.error_state:
            lib.errors.SAVE_ERROR_STATE = True

        # Script prompt interactive inspection flag.
        if args.prompt:
            status.prompt = True

        # Logging.
        if args.log:
            # Exclusive modes.
            if args.tee:
                parser.error("The logging and tee arguments cannot be set simultaneously.")

            # The log file.
            self.log_file = args.log

            # Fail if the file already exists.
            if access(self.log_file, F_OK):
                parser.error("The log file '%s' already exists." % self.log_file)
        else:
            self.log_file = None

        # Tee.
        if args.tee:
            # Exclusive modes.
            if args.log:
                parser.error("The tee and logging options cannot be set simultaneously.")

            # The tee file.
            self.tee_file = args.tee

            # Fail if the file already exists.
            if access(self.tee_file, F_OK):
                parser.error("The tee file '%s' already exists." % self.tee_file)
        else:
            self.tee_file = None

        # Test suite mode, therefore the args are the tests to run and not a script file.
        if args.test_suite or args.system_tests or args.unit_tests or args.gui_tests or args.verification_tests:
            # Store the arguments.
            self.tests = args.script
            self.io_capture = not args.no_capture
            self.list_tests = args.list_tests

            # Test timings.
            self.test_timings = False
            if args.tt:
                self.test_timings = True

            # Run blacklisted tests.
            status.skip_blacklisted_tests = True
            if args.no_skip:
                status.skip_blacklisted_tests = False

        # The argument is a script (or nothing has been supplied).
        else:
            # Number of positional arguments should only be 0 or 1.  1 should be the script file.
            if len(args.script) > 1:
                parser.error("Incorrect number of arguments.")

            # Script file.
            self.script_file = None
            if len(args.script) == 1:
                self.script_file = args.script[0]

                # Test if the script file exists.
                if not access(self.script_file, F_OK):
                    parser.error("The script file '%s' does not exist." % self.script_file)

        # Set the multi-processor type and number.
        if args.multiprocessor not in ['uni', 'mpi4py']:
            parser.error("The processor type '%s' is not supported.\n" % args.multiprocessor)
        self.multiprocessor_type = args.multiprocessor
        self.n_processors = args.n_processors

        # Checks for the multiprocessor mode.
        if self.multiprocessor_type == 'mpi4py' and not dep_check.mpi4py_module:
            parser.error(dep_check.mpi4py_message)


        # Determine the relax mode and test for mutually exclusive modes.
        #################################################################

        # Show the version number.
        if args.version:
            self.mode = 'version'

        # Show the info about this relax version.
        elif args.info:
            self.mode = 'info'

        # Run the relax tests.
        elif args.test_suite or args.system_tests or args.unit_tests or args.gui_tests or args.verification_tests:
            # Exclusive modes.
            if args.test:
                parser.error("Executing the relax test suite and running relax in test mode are mutually exclusive.")
            elif args.licence:
                parser.error("Executing the relax test suite and running relax in licence mode are mutually exclusive.")

            # Set the mode.
            if args.test_suite:
                self.mode = 'test suite'
            elif args.system_tests:
                self.mode = 'system tests'
            elif args.unit_tests:
                self.mode = 'unit tests'
            elif args.gui_tests:
                self.mode = 'GUI tests'
            elif args.verification_tests:
                self.mode = 'verification tests'

            # Set the status flag.
            status.test_mode = True

        # Test mode.
        elif args.test:
            # Make sure no script is supplied.
            if self.script_file:
                parser.error("A script should not be supplied in test mode.")

            # Exclusive modes.
            if args.test_suite or args.system_tests or args.unit_tests or args.gui_tests or args.verification_tests:
                parser.error("The relax test mode and executing the test suite are mutually exclusive.")
            elif args.licence:
                parser.error("The relax modes test and licence are mutually exclusive.")

            # Set the mode.
            self.mode = 'test'

        # Licence mode.
        elif args.licence:
            # Make sure no script is supplied.
            if self.script_file:
                parser.error("A script should not be supplied in test mode.")

            # Exclusive modes.
            if args.test_suite or args.system_tests or args.unit_tests or args.gui_tests or args.verification_tests:
                parser.error("The relax licence mode and executing the test suite are mutually exclusive.")
            elif args.test:
                parser.error("The relax modes licence and test are mutually exclusive.")

            # Set the mode.
            self.mode = 'licence'

        # GUI.
        elif args.gui:
            # Exclusive models.
            if args.test_suite or args.system_tests or args.unit_tests or args.gui_tests or args.verification_tests:
                parser.error("The relax GUI mode and testing modes are mutually exclusive.")
            elif args.licence:
                parser.error("The relax GUI mode and licence mode are mutually exclusive.")

            # Missing wx module.
            if not dep_check.wx_module:
                # Not installed.
                if dep_check.wx_module_message == "No module named 'wx'":
                    parser.error("To use the GUI, the wxPython module must be installed.")

                # Broken.
                else:
                    parser.error("The wxPython installation is broken:\n%s." % dep_check.wx_module_message)

            # Set the mode.
            self.mode = 'gui'

        # Script mode.
        elif self.script_file:
            self.mode = 'script'

        # Prompt mode (default).
        else:
            self.mode = 'prompt'


    def licence(self):
        """Function for displaying the licence."""

        # Present the GPL using paging.
        file = open('docs/COPYING')
        pager(file.read())


    def test_mode(self):
        """Relax test mode code."""

        # Don't actually do anything.
        return



class RelaxParser(ArgumentParser):
    """A custom ArgumentParser class."""

    def error(self, message):
        """Replace ArgumentParser.error() with a custom function, enabling the use of RelaxErrors.

        @param message: The error message to output.
        @type message:  str
        """

        # Usage message.
        self.print_usage(sys.stderr)

        # Raise a clean error.
        try:
            raise lib.errors.RelaxError(message)
        except lib.errors.AllRelaxErrors:
            instance = sys.exc_info()[1]
            sys.stderr.write(instance.__str__())

        # Exit with the Unix command line error code of 2.
        sys.exit(2)


# Start relax if this file is passed to Python.
if __name__ == "__main__":
    start()
