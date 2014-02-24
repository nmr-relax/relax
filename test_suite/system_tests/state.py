###############################################################################
#                                                                             #
# Copyright (C) 2008-2013 Edward d'Auvergne                                   #
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
from copy import deepcopy
from os import sep
from tempfile import mktemp

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
import dep_check
from pipe_control.interatomic import interatomic_loop
from pipe_control.pipes import VALID_TYPES, get_pipe
from pipe_control.reset import reset
from status import Status; status = Status()
from test_suite.system_tests.base_classes import SystemTestCase


class State(SystemTestCase):
    """Class for testing the state saving and loading user functions."""

    def __init__(self, methodName='runTest'):
        """Skip the tests if the C modules are non-functional.

        @keyword methodName:    The name of the test.
        @type methodName:       str
        """

        # Execute the base class method.
        super(State, self).__init__(methodName)

        # Missing module.
        if not dep_check.C_module_exp_fn and methodName in ['test_write_read_pipes']:
            # Store in the status object. 
            status.skipped_tests.append([methodName, 'Relax curve-fitting C module', self._skip_type])


    def setUp(self):
        """Common set up for these system tests."""

        # Create a temporary file name.
        self.tmpfile = mktemp()


    def test_align_tensor_with_mc_sims(self):
        """Test the loading of a relax state with an alignment tensor with MC simulation structures."""

        # The file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'saved_states'+sep+'align_tensor_mc.bz2'

        # Load the state.
        self.interpreter.state.load(path)

        # The data.
        domains = ['Dy N-dom', 'Dy C-dom']
        rdc = {
            "Dy N-dom" : [-6.41, -21.55],
            "Dy C-dom" : [-21.55]
        }
        rdc_bc = {
            "Dy N-dom" : [None, -20.87317257368743],
            "Dy C-dom" : [None]
        }

        rdc_err = {
            "Dy N-dom" : [1.0, 1.0],
            "Dy C-dom" : [1.0]
        }

        # Check the data.
        for domain in domains:
            # Switch to the X-domain data pipe.
            self.interpreter.pipe.switch(domain)

            # Check the interatomic data.
            i = 0
            for interatom in interatomic_loop():
                # Check the RDC data.
                self.assertEqual(interatom.rdc[domain], rdc[domain][i])
                if rdc_bc[domain][i]:
                    self.assertEqual(interatom.rdc_bc[domain], rdc_bc[domain][i])
                if rdc_err[domain][i]:
                    self.assertEqual(interatom.rdc_err[domain], rdc_err[domain][i])

                # Increment the index.
                i += 1


    def test_bug_21716_no_cdp_state_save(self):
        """Catch U{bug #21716<https://gna.org/bugs/?21716>}, the failure to save the relax state when no current data pipe is set."""

        # Create two data pipes.
        self.interpreter.pipe.create('a', 'mf')
        self.interpreter.pipe.create('b', 'mf')

        # Delete the current data pipe.
        self.interpreter.pipe.delete('b')

        # Save the state.
        self.interpreter.state.save(self.tmpfile, force=True)


    def test_state_xml(self):
        """Test the saving, loading, and second saving and loading of the program state in XML format."""

        # Create a data pipe.
        self.interpreter.pipe.create('test', 'mf')

        # Save the state.
        self.interpreter.state.save(self.tmpfile, force=True)

        # Load the state.
        self.interpreter.state.load(self.tmpfile, force=True)

        # Save the state.
        self.interpreter.state.save(self.tmpfile, force=True)

        # Load the state.
        self.interpreter.state.load(self.tmpfile, force=True)


    def test_write_read_pipes(self):
        """Test the writing out, and re-reading of data pipes from the state file."""

        # Create a data pipe.
        self.interpreter.pipe.create('test', 'mf')

        # Reset relax.
        reset()

        # The data pipe list.
        pipe_types = deepcopy(VALID_TYPES)
        pipe_types.pop(pipe_types.index("frame order"))

        # Create a few data pipes.
        for i in range(len(pipe_types)):
            self.interpreter.pipe.create('test' + repr(i), pipe_types[i])

        # Write the results.
        self.interpreter.state.save(self.tmpfile)

        # Reset relax.
        reset()

        # Re-read the results.
        self.interpreter.state.load(self.tmpfile)

        # Test the pipes.
        for i in range(len(pipe_types)):
            # Name.
            name = 'test' + repr(i)
            self.assert_(name in ds)

            # Type.
            pipe = get_pipe(name)
            self.assertEqual(pipe.pipe_type, pipe_types[i])
