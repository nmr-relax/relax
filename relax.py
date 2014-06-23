###############################################################################
#                                                                             #
#                                    relax                                    #
#                                                                             #
#               Protein dynamics by NMR relaxation data analysis              #
#                                                                             #
#                             by Edward d'Auvergne                            #
#                                                                             #
###############################################################################
#                                                                             #
#                                   Licence                                   #
#                                                                             #
# relax, a program for relaxation data analysis.                              #
#                                                                             #
# Copyright (C) 2001-2006  Edward d'Auvergne                                  #
# Copyright (C) 2006-2014  the relax development team                         #
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
os.environ['TERM'] = ''

# Set up the Python 2 and 3 work-arounds.
import lib.compat

# Python modules.
import numpy
from optparse import Option, OptionGroup, OptionParser
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
        """The top level class for initialising the program.

        @keyword mode:          Force a relax mode, overriding the command line.
        @type mode:             str
        """

        # Get and store the PID of this process.
        self.pid = getpid()


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
            runner = Test_suite_runner(self.tests, timing=self.test_timings)
            runner.run_all_tests()

        # Execute the relax system tests.
        elif self.mode == 'system tests':
            # Only import the module in the test modes (to improve program start up speeds).
            from test_suite.test_suite_runner import Test_suite_runner

            # Load the interpreter and turn intros on.
            self.interpreter = interpreter.Interpreter(show_script=False, raise_relax_error=True)
            self.interpreter.on()

            # Run the tests.
            runner = Test_suite_runner(self.tests, timing=self.test_timings)
            runner.run_system_tests()

        # Execute the relax unit tests.
        elif self.mode == 'unit tests':
            # Only import the module in the test modes (to improve program start up speeds).
            from test_suite.test_suite_runner import Test_suite_runner

            # Run the tests.
            runner = Test_suite_runner(self.tests, timing=self.test_timings)
            runner.run_unit_tests()

        # Execute the relax GUI tests.
        elif self.mode == 'GUI tests':
            # Only import the module in the test modes (to improve program start up speeds).
            from test_suite.test_suite_runner import Test_suite_runner

            # Run the tests.
            runner = Test_suite_runner(self.tests, timing=self.test_timings)
            runner.run_gui_tests()

        # Execute the relax verification tests.
        elif self.mode == 'verification tests':
            # Only import the module in the test modes (to improve program start up speeds).
            from test_suite.test_suite_runner import Test_suite_runner

            # Run the tests.
            runner = Test_suite_runner(self.tests, timing=self.test_timings)
            runner.run_verification_tests()

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
        parser = RelaxParser(self, usage="usage: %prog [options] [script_file]")

        # Recognised command line options for the UI.
        group = OptionGroup(parser, 'UI options')
        group.add_option('-p', '--prompt', action='store_true', dest='prompt', default=0, help='launch relax in prompt mode after running any optionally supplied scripts')
        group.add_option('-g', '--gui', action='store_true', dest='gui', default=0, help='launch the relax GUI')
        group.add_option('-i', '--info', action='store_true', dest='info', default=0, help='display information about this version of relax')
        group.add_option('-v', '--version', action='store_true', dest='version', default=0, help='show the version number and exit')
        group.add_option('--licence', action='store_true', dest='licence', default=0, help='display the licence')
        group.add_option('--test', action='store_true', dest='test', default=0, help='run relax in test mode')
        parser.add_option_group(group)

        # Recognised command line options for the multiprocessor.
        group = OptionGroup(parser, 'Multi-processor options')
        group.add_option('-m', '--multi', action='store', type='string', dest='multiprocessor', default='uni', help='set multi processor method')
        group.add_option('-n', '--processors', action='store', type='int', dest='n_processors', default=-1, help='set number of processors (may be ignored)')
        parser.add_option_group(group)

        # Recognised command line options for IO redirection.
        group = OptionGroup(parser, 'IO redirection options')
        group.add_option('-l', '--log', action='store', type='string', dest='log', help='log relax output to the file LOG_FILE', metavar='LOG_FILE')
        group.add_option('-t', '--tee', action='store', type='string', dest='tee', help='tee relax output to both stdout and the file LOG_FILE', metavar='LOG_FILE')
        parser.add_option_group(group)

        # Recognised command line options for the test suite.
        group = OptionGroup(parser, 'Test suite options')
        group.add_option('-x', '--test-suite', action='store_true', dest='test_suite', default=0, help='execute the full relax test suite')
        group.add_option('-s', '--system-tests', action='store_true', dest='system_tests', default=0, help='execute the system/functional tests')
        group.add_option('-u', '--unit-tests', action='store_true', dest='unit_tests', default=0, help='execute the unit tests')
        group.add_option('--gui-tests', action='store_true', dest='gui_tests', default=0, help='execute the GUI tests')
        group.add_option('--verification-tests', action='store_true', dest='verification_tests', default=0, help='execute the software verification tests')
        group.add_option('--time', action='store_true', dest='tt', default=0, help='enable the timing of individual tests in the test suite')
        parser.add_option_group(group)

        # Recognised command line options for debugging.
        group = OptionGroup(parser, 'Debugging options')
        group.add_option('-d', '--debug', action='store_true', dest='debug', default=0, help='enable debugging output')
        group.add_option('--error-state', action='store_true', dest='error_state', default=0, help='save a pickled state file when a RelaxError occurs')
        group.add_option('--traceback', action='store_true', dest='traceback', default=0, help='show stack tracebacks on all RelaxErrors and RelaxWarnings')
        group.add_option('-e', '--escalate', action='store_true', dest='escalate', default=0, help='escalate all warnings to errors')
        group.add_option('--numpy-raise', action='store_true', dest='numpy_raise', default=0, help='convert numpy warnings to errors')
        parser.add_option_group(group)

        # Parse the options.
        (options, args) = parser.parse_args()

        # Debugging options:  Debugging flag, escalate flag, traceback flag, and numpy warning to error conversion.
        if options.debug:
            status.debug = True
        if options.escalate:
            lib.warnings.ESCALATE = True
        if options.traceback:
            status.traceback = True
            lib.warnings.TRACEBACK = True
        if options.numpy_raise:
            numpy.seterr(all='raise')
        if options.error_state:
            lib.errors.SAVE_ERROR_STATE = True

        # Script prompt interactive inspection flag.
        if options.prompt:
            status.prompt = True

        # Logging.
        if options.log:
            # Exclusive modes.
            if options.tee:
                parser.error("the logging and tee options cannot be set simultaneously")

            # The log file.
            self.log_file = options.log

            # Fail if the file already exists.
            if access(self.log_file, F_OK):
                parser.error("the log file " + repr(self.log_file) + " already exists")
        else:
            self.log_file = None

        # Tee.
        if options.tee:
            # Exclusive modes.
            if options.log:
                parser.error("the tee and logging options cannot be set simultaneously")

            # The tee file.
            self.tee_file = options.tee

            # Fail if the file already exists.
            if access(self.tee_file, F_OK):
                parser.error("the tee file " + repr(self.tee_file) + " already exists")
        else:
            self.tee_file = None

        # Test suite mode, therefore the args are the tests to run and not a script file.
        if options.test_suite or options.system_tests or options.unit_tests or options.gui_tests or options.verification_tests:
            # Store the arguments.
            self.tests = args

            # Test timings.
            self.test_timings = False
            if options.tt:
                self.test_timings = True

        # The argument is a script.
        else:
            # Number of positional arguments should only be 0 or 1.  1 should be the script file.
            if len(args) > 1:
                parser.error("incorrect number of arguments")

            # Script file.
            self.script_file = None
            if len(args) == 1:
                self.script_file = args[0]

                # Test if the script file exists.
                if not access(self.script_file, F_OK):
                    parser.error("the script file " + repr(self.script_file) + " does not exist")

        # Set the multi-processor type and number.
        self.multiprocessor_type = options.multiprocessor
        self.n_processors = options.n_processors

        # Checks for the multiprocessor mode.
        if self.multiprocessor_type == 'mpi4py' and not dep_check.mpi4py_module:
            parser.error(dep_check.mpi4py_message)


        # Determine the relax mode and test for mutually exclusive modes.
        #################################################################

        # Show the version number.
        if options.version:
            self.mode = 'version'

        # Show the info about this relax version.
        elif options.info:
            self.mode = 'info'

        # Run the relax tests.
        elif options.test_suite or options.system_tests or options.unit_tests or options.gui_tests or options.verification_tests:
            # Exclusive modes.
            if options.test:
                parser.error("executing the relax test suite and running relax in test mode are mutually exclusive")
            elif options.licence:
                parser.error("executing the relax test suite and running relax in licence mode are mutually exclusive")

            # Set the mode.
            if options.test_suite:
                self.mode = 'test suite'
            elif options.system_tests:
                self.mode = 'system tests'
            elif options.unit_tests:
                self.mode = 'unit tests'
            elif options.gui_tests:
                self.mode = 'GUI tests'
            elif options.verification_tests:
                self.mode = 'verification tests'

            # Set the status flag.
            status.test_mode = True

        # Test mode.
        elif options.test:
            # Make sure no script is supplied.
            if self.script_file:
                parser.error("a script should not be supplied in test mode")

            # Exclusive modes.
            if options.test_suite or options.system_tests or options.unit_tests or options.gui_tests or options.verification_tests:
                parser.error("the relax test mode and executing the test suite are mutually exclusive")
            elif options.licence:
                parser.error("the relax modes test and licence are mutually exclusive")

            # Set the mode.
            self.mode = 'test'

        # Licence mode.
        elif options.licence:
            # Make sure no script is supplied.
            if self.script_file:
                parser.error("a script should not be supplied in test mode")

            # Exclusive modes.
            if options.test_suite or options.system_tests or options.unit_tests or options.gui_tests or options.verification_tests:
                parser.error("the relax licence mode and executing the test suite are mutually exclusive")
            elif options.test:
                parser.error("the relax modes licence and test are mutually exclusive")

            # Set the mode.
            self.mode = 'licence'

        # GUI.
        elif options.gui:
            # Exclusive models.
            if options.test_suite or options.system_tests or options.unit_tests or options.gui_tests or options.verification_tests:
                parser.error("the relax GUI mode and testing modes are mutually exclusive")
            elif options.licence:
                parser.error("the relax GUI mode and licence mode are mutually exclusive")

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



class RelaxParser(OptionParser):
    def __init__(self, relax, usage=None, option_list=None, option_class=Option, version=None, conflict_handler="error", description=None, formatter=None, add_help_option=1, prog=None):
        """Subclassed OptionParser class with a replacement error function."""

        # Relax base class.
        self.relax = relax

        # Run the __init__ method of the OptionParser class.
        OptionParser.__init__(self, usage, option_list, option_class, version, conflict_handler, description, formatter, add_help_option, prog)


    def error(self, message):
        """Replacement error function."""

        # Usage message.
        self.print_usage(sys.stderr)

        # Raise a clean error.
        try:
            raise lib.errors.RelaxError(message)
        except lib.errors.AllRelaxErrors:
            instance = sys.exc_info()[1]
            sys.stderr.write(instance.__str__())

        # Exit.
        sys.exit()


# Start relax if this file is passed to Python.
if __name__ == "__main__":
    start()
