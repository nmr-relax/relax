###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
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
"""System tests of the interatomic data container operations."""


# Python module imports.
from os import sep

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()
from test_suite.system_tests.base_classes import SystemTestCase


class Interatomic(SystemTestCase):
    """Class for testing the interatomic functions."""

    def test_copy(self):
        """Test the operation of the interatomic.copy user function."""

        # Create an initial data pipe.
        self.interpreter.pipe.create(pipe_name="orig", pipe_type='N-state')

        # Create some sequence data.
        self.interpreter.molecule.create(mol_name='Test mol')
        self.interpreter.residue.create(mol_name='Test mol', res_name='His', res_num=1)
        self.interpreter.residue.create(mol_name='Test mol', res_name='His', res_num=2)
        self.interpreter.spin.create(res_num=1, spin_name='N')
        self.interpreter.spin.create(res_num=1, spin_name='H')
        self.interpreter.spin.create(res_num=2, spin_name='N')
        self.interpreter.spin.create(res_num=2, spin_name='H')

        # Define the interatomic interaction.
        self.interpreter.interatomic.create(spin_id1=':1@N', spin_id2=':1@H')
        self.interpreter.interatomic.create(spin_id1=':2@N', spin_id2=':2@H')

        # Add some test data.
        cdp.interatomic[0].x = 1
        cdp.interatomic[1].y = 2

        # Create a new data pipe to copy the data to.
        self.interpreter.pipe.create(pipe_name="new", pipe_type='N-state')

        # Copy the data.
        self.interpreter.sequence.copy(pipe_from='orig')
        self.interpreter.interatomic.copy(pipe_from='orig', spin_id1=':2@N', spin_id2=':2@H')
        self.interpreter.interatomic.copy(pipe_from='orig', spin_id1=':1@H', spin_id2=':1@N')

        # Check the sequence data.
        self.assertEqual(cdp.mol[0].name, 'Test mol')
        self.assertEqual(cdp.mol[0].res[0].name, 'His')
        self.assertEqual(cdp.mol[0].res[0].spin[0].name, 'N')
        self.assertEqual(cdp.mol[0].res[0].spin[1].name, 'H')
        self.assertEqual(cdp.mol[0].res[1].name, 'His')
        self.assertEqual(cdp.mol[0].res[1].spin[0].name, 'N')
        self.assertEqual(cdp.mol[0].res[1].spin[1].name, 'H')

        # Check the interatomic data.
        self.assertEqual(cdp.interatomic[0].spin_id1, ':2@N')
        self.assertEqual(cdp.interatomic[0].spin_id2, ':2@H')
        self.assertEqual(cdp.interatomic[0].y, 2)
        self.assertEqual(cdp.interatomic[1].spin_id1, ':1@N')
        self.assertEqual(cdp.interatomic[1].spin_id2, ':1@H')
        self.assertEqual(cdp.interatomic[1].x, 1)


    def test_manipulation(self):
        """Test the manipulation of interatomic data containers."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'interatomic_tests.py')

        # The data.
        select = [True, False] + [True]*3 + [False]*2 + [True]*5 + [False]*2 + [True, False]

        # Check the data.
        self.assertEqual(len(cdp.interatomic), 16)
        for i in range(len(cdp.interatomic)):
            # A printout to know where the problem is.
            print("Checking container:  %-30s %-30s" % (cdp.interatomic[i].spin_id1, cdp.interatomic[i].spin_id2))

            # The container checks.
            self.assertEqual(cdp.interatomic[i].select, select[i])
