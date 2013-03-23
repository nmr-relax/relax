###############################################################################
#                                                                             #
# Copyright (C) 2006-2013 Edward d'Auvergne                                   #
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

# Python module imports.
from os import sep

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
import dep_check
from pipe_control import pipes
from status import Status; status = Status()
from test_suite.system_tests.base_classes import SystemTestCase


class Pipes(SystemTestCase):
    """TestCase class for the functional tests of relax data pipes."""

    def __init__(self, methodName='runTest'):
        """Skip some tests if scipy is not installed.

        @keyword methodName:    The name of the test.
        @type methodName:       str
        """

        # Execute the base class method.
        super(Pipes, self).__init__(methodName)

        # Missing module.
        if not dep_check.scipy_module and methodName in ['test_change_type']:
            # Store in the status object. 
            status.skipped_tests.append([methodName, 'Scipy', self._skip_type])


    def test_change_type(self):
        """Test the pipe.change_type user function."""

        # Create the data pipe.
        self.interpreter.pipe.create('test', 'frame order')

        # Change the type.
        self.interpreter.pipe.change_type('N-state')

        # Check the type.
        self.assertEqual(cdp.pipe_type, 'N-state')


    def test_pipe_bundle(self):
        """Test the pipe bundle concepts."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'pipe_bundle.py')

        # Checks.
        self.assertEqual(pipes.cdp_name(), None)
        self.assertEqual(pipes.has_bundle('test bundle 1'), True)
        self.assertEqual(pipes.has_bundle('test bundle 2'), True)
        self.assertEqual(pipes.has_bundle('test bundle 3'), False)
        bundles = sorted(pipes.bundle_names())
        self.assertEqual(bundles, ['test bundle 1', 'test bundle 2'])
        for pipe, name in pipes.pipe_loop(name=True):
            self.assert_(name in ['test pipe 1', 'test pipe 2', 'test pipe 3', 'test pipe 4', 'test pipe 5', 'test pipe 6'])
            self.assert_(pipes.get_bundle(name) in ['test bundle 1', 'test bundle 2'])


    def test_pipe_create(self):
        """Create a data pipe."""

        # Create the data pipe.
        self.interpreter.pipe.create('test', 'mf')
