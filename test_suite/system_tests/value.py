###############################################################################
#                                                                             #
# Copyright (C) 2013 Edward d'Auvergne                                        #
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

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from test_suite.system_tests.base_classes import SystemTestCase


class Value(SystemTestCase):
    """Class for testing various aspects specific to the value user functions."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.interpreter.pipe.create('mf', 'mf')


    def test_value_copy(self):
        """Test the value.copy user function."""

        # Create a data pipe.
        self.interpreter.pipe.create('orig', 'mf')

        # Add some new spins.
        self.interpreter.spin.create(mol_name='test mol', res_name='Gly', res_num=1, spin_name='N')
        self.interpreter.spin.create(mol_name='test mol', res_name='Gly', res_num=2, spin_name='N')
        self.interpreter.spin.create(mol_name='test mol', res_name='Gly', res_num=3, spin_name='N')

        # Add some values and errors.
        self.interpreter.value.set(val=0.8, param='s2', spin_id=':1,2')
        self.interpreter.value.set(val=0.1, param='s2', spin_id=':1', error=True)
        self.interpreter.value.set(val=0.2, param='s2', spin_id=':2', error=True)
        self.interpreter.value.set(val=0.3, param='s2', spin_id=':3', error=True)

        # Create a new data pipe.
        self.interpreter.pipe.create('new', 'mf')

        # Copy the sequence data and value.
        self.interpreter.sequence.copy(pipe_from='orig', pipe_to='new')
        self.interpreter.value.copy(pipe_from='orig', pipe_to='new', param='s2')
