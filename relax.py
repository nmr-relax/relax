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
# Copyright (C) 2006-2012  the relax development team                         #
#                                                                             #
# This program is free software; you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU Library General Public License for more details.                        #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program; if not, write to the Free Software                 #
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.  #
#                                                                             #
###############################################################################

# First of all, store the relax installation path before the site-packages mangle sys.path.
from status import Status; status = Status()
import sys
status.install_path = sys.path[0]

# Dependency checks.
import dep_check

# Python modules.
from optparse import Option, OptionParser
from os import F_OK, access, getpid, putenv
if dep_check.cprofile_module:
    import cProfile as profile
elif dep_check.profile_module:
    import profile
import pstats
from re import match
from string import split, strip
import sys

# relax modules.
from info import Info_box
import generic_fns
if dep_check.wx_module:
    import gui
from multi.processor import Application_callback, Processor
from prompt.gpl import gpl
from prompt import interpreter
import relax_errors
from relax_io import io_streams_log, io_streams_tee
import relax_warnings
from test_suite.test_suite_runner import Test_suite_runner
from version import version

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

    # Process the command line arguments.
    relax.arguments()

    # Override the mode.
    if mode:
        relax.mode = mode

    # Set up the multi-processor elements.
    callbacks = Application_callback(master=relax)
    processor = Processor.load_multiprocessor(relax.multiprocessor_type, callbacks, processor_size=relax.n_processors)

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

        # Setup the object containing the generic functions.
        self.generic = generic_fns


    def run(self):
        """Execute relax.

        This is the application callback method executed by the multi-processor framework.
        """

        # Set up the warning system.
        relax_warnings.setup()

        # Show the version number and exit.
        if self.mode == 'version':
            print(('relax ' + version))
            sys.exit()

        # Show the relax info and exit.
        if self.mode == 'info':
            info = Info_box()
            print(info.sys_info())
            sys.exit()

        # Logging.
        if self.log_file:
            io_streams_log(self.log_file)

        # Tee.
        elif self.tee_file:
            io_streams_tee(self.tee_file)

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
                sys.exit()

            # Set the GUI flag in the status object.
            status.show_gui = True

            # Start the relax GUI wx application.
            app = gui.App(script=self.script_file)
            app.MainLoop()

        # Execute the relax test suite
        elif self.mode == 'test suite':
            # Load the interpreter and turn intros on.
            self.interpreter = interpreter.Interpreter(show_script=False, quit=False, raise_relax_error=True)
            self.interpreter.on()

            # Run the tests.
            runner = Test_suite_runner(self.tests)
            runner.run_all_tests()

        # Execute the relax system tests.
        elif self.mode == 'system tests':
            # Load the interpreter and turn intros on.
            self.interpreter = interpreter.Interpreter(show_script=False, quit=False, raise_relax_error=True)
            self.interpreter.on()

            # Run the tests.
            runner = Test_suite_runner(self.tests)
            runner.run_system_tests()

        # Execute the relax unit tests.
        elif self.mode == 'unit tests':
            # Run the tests.
            runner = Test_suite_runner(self.tests)
            runner.run_unit_tests()

        # Execute the relax GUI tests.
        elif self.mode == 'GUI tests':
            # Run the tests.
            runner = Test_suite_runner(self.tests)
            runner.run_gui_tests()

        # Test mode.
        elif self.mode == 'test':
            self.test_mode()

        # Licence mode.
        elif self.mode == 'licence':
            self.licence()

        # Unknown mode.
        else:
            raise relax_errors.RelaxError("The '%s' mode is unknown." % self.mode)


    def arguments(self):
        """Process the command line arguments."""

        # Parser object.
        parser = RelaxParser(self, usage="usage: %prog [options] [script_file]")

        # Recognised command line options.
        parser.add_option('-d', '--debug', action='store_true', dest='debug', default=0, help='enable debugging output')
        parser.add_option('-l', '--log', action='store', type='string', dest='log', help='log relax output to the file LOG_FILE', metavar='LOG_FILE')
        parser.add_option('--licence', action='store_true', dest='licence', default=0, help='display the licence')
        parser.add_option('-t', '--tee', action='store', type='string', dest='tee', help='tee relax output to stdout and the file LOG_FILE', metavar='LOG_FILE')
        parser.add_option('-g', '--gui', action='store_true', dest='gui', default=0, help='launch the relax GUI')
        parser.add_option('-p', '--pedantic', action='store_true', dest='pedantic', default=0, help='escalate all warnings to errors')
        parser.add_option('--test', action='store_true', dest='test', default=0, help='run relax in test mode')
        parser.add_option('-x', '--test-suite', action='store_true', dest='test_suite', default=0, help='execute the relax test suite')
        parser.add_option('-s', '--system-tests', action='store_true', dest='system_tests', default=0, help='execute the relax system/functional tests (part of the test suite)')
        parser.add_option('-u', '--unit-tests', action='store_true', dest='unit_tests', default=0, help='execute the relax unit tests (part of the test suite)')
        parser.add_option('--gui-tests', action='store_true', dest='gui_tests', default=0, help='execute the relax GUI tests (part of the test suite)')
        parser.add_option('-i', '--info', action='store_true', dest='info', default=0, help='display information about this version of relax')
        parser.add_option('-v', '--version', action='store_true', dest='version', default=0, help='show the version number and exit')
        parser.add_option('-m', '--multi', action='store', type='string', dest='multiprocessor', default='uni', help='set multi processor method')
        parser.add_option('-n', '--processors', action='store', type='int', dest='n_processors', default=-1, help='set number of processors (may be ignored)')

        # Parse the options.
        (options, args) = parser.parse_args()

        # Debugging flag.
        if options.debug:
            status.debug = True

        # Pedantic flag.
        if options.pedantic:
            status.pedantic = True

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
        if options.test_suite or options.system_tests or options.unit_tests or options.gui_tests:
            self.tests = args

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
        elif options.test_suite or options.system_tests or options.unit_tests or options.gui_tests:
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

            # Set the status flag.
            status.test_mode = True

        # Test mode.
        elif options.test:
            # Make sure no script is supplied.
            if self.script_file:
                parser.error("a script should not be supplied in test mode")

            # Exclusive modes.
            if options.test_suite or options.system_tests or options.unit_tests or options.gui_tests:
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
            if options.test_suite or options.system_tests or options.unit_tests or options.gui_tests:
                parser.error("the relax licence mode and executing the test suite are mutually exclusive")
            elif options.test:
                parser.error("the relax modes licence and test are mutually exclusive")

            # Set the mode.
            self.mode = 'licence'

        # GUI.
        elif options.gui:
            # Exclusive models.
            if options.test_suite or options.system_tests or options.unit_tests or options.gui_tests:
                parser.error("the relax GUI mode and testing modes are mutually exclusive")
            elif options.licence:
                parser.error("the relax GUI mode and licence mode are mutually exclusive")

            # Missing wx module.
            if not dep_check.wx_module:
                parser.error("To use the GUI, the wx python module must be installed.")

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

        help(gpl)


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
            raise relax_errors.RelaxError(message)
        except relax_errors.AllRelaxErrors, instance:
            sys.stderr.write(instance.__str__())

        # Exit.
        sys.exit()


# Start relax if this file is passed to Python.
if __name__ == "__main__":
    start()
