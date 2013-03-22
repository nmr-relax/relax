###############################################################################
#                                                                             #
# Copyright (C) 2006 Chris MacRaild                                           #
# Copyright (C) 2007-2008 Sebastien Morin                                     #
# Copyright (C) 2010-2013 Edward d'Auvergne                                   #
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
import sys

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from generic_fns.mol_res_spin import residue_loop
from lib.physical_constants import N15_CSA
from status import Status; status = Status()
from test_suite.system_tests.base_classes import SystemTestCase


class Ct(SystemTestCase):
    """Class for testing various aspects specific to consistency testing."""


    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.interpreter.pipe.create('ct', 'ct')


    def test_calc(self):
        """The consistency testing calculation test."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'consistency_tests_calc_test.py')

        # Correct consistency functions values.
        j0 = [4.0703318681008998e-09, 3.7739393907014834e-09]
        f_eta = [0.20413244790407614, 0.18898977395296815]
        f_r2 = [2.0482909381655862e-09, 1.8998154021753067e-09]

        # Loop over residues.
        index = 0
        for res in residue_loop():
            # Residues -2 and -1 have data.
            if res.num == -2 or res.num == -1:
                self.assert_(res.spin[0].select)
                self.assertAlmostEqual(res.spin[0].j0, j0[index])
                self.assertAlmostEqual(res.spin[0].f_eta, f_eta[index])
                self.assertAlmostEqual(res.spin[0].f_r2, f_r2[index])
                index = index + 1

            # Other residues have insufficient data.
            else:
                self.assert_(not res.spin[0].select)


    def test_set_value(self):
        """The user function value.set()."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'consistency_tests_set_value.py')

        # Loop over residues.
        for res in residue_loop():
            self.assertAlmostEqual(res.spin[0].csa, N15_CSA)


    def test_consistency(self):
        """Test a complete consistency tests run using a script."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'consistency_tests.py')
