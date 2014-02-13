###############################################################################
#                                                                             #
# Copyright (C) 2010-2014 Edward d'Auvergne                                   #
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
"""Base classes for the system tests."""

# Python module imports.
from unittest import TestCase

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from pipe_control.reset import reset
from prompt.interpreter import Interpreter
from test_suite.clean_up import deletion


class SystemTestCase(TestCase):
    """The system test base class."""

    def __init__(self, methodName=None):
        """Set up the test case class for the system tests."""

        # Execute the TestCase __init__ method.
        super(SystemTestCase, self).__init__(methodName)

        # A string used for classifying skipped tests.
        if not hasattr(self, '_skip_type'):
            self._skip_type = 'system'

        # Load the interpreter.
        self.interpreter = Interpreter(show_script=False, raise_relax_error=True)
        self.interpreter.populate_self()
        self.interpreter.on(verbose=False)


    def script_exec(self, script):
        """Execute a relax script within the system test framework.

        @param script:  The full path of the script to execute.
        @type script:   str
        """

        # Execute the script.
        self.interpreter.run(script_file=script)


    def tearDown(self):
        """Default tearDown operation - delete temp directories and files and reset relax."""

        # Remove the temporary directory and variable (if there is a deletion failure, continue to allow the test suite to survive).
        try:
            deletion(obj=ds, name='tmpdir', dir=True)
        except:
            pass
        try:
            deletion(obj=self, name='tmpdir', dir=True)
        except:
            pass

        # Remove temporary file and variable (if there is a deletion failure, continue to allow the test suite to survive).
        try:
            deletion(obj=ds, name='tmpfile', dir=False)
        except:
            pass
        try:
            deletion(obj=self, name='tmpfile', dir=False)
        except:
            pass

        # Reset relax.
        reset()
