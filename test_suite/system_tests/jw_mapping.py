###############################################################################
#                                                                             #
# Copyright (C) 2006 Chris MacRaild                                           #
# Copyright (C) 2007-2013 Edward d'Auvergne                                   #
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
from lib.physical_constants import N15_CSA, NH_BOND_LENGTH
from status import Status; status = Status()
from test_suite.system_tests.base_classes import SystemTestCase


class Jw(SystemTestCase):
    """Class for testing various aspects specific to reduced spectral density mapping."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.interpreter.pipe.create('jw', 'jw')


    def test_calc(self):
        """The spectral density calculation test."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'jw_mapping_calc_test.py')

        # Correct jw values.
        j0 = [4.0703318681008998e-09, 3.7739393907014834e-09]
        jwx = [1.8456254300773903e-10, 1.6347516082378241e-10]
        jwh = [1.5598167512718012e-12, 2.9480536599037041e-12]

        # Loop over residues.
        index = 0
        for res in residue_loop():
            # Residues -2 and -1 have data.
            if res.num == -2 or res.num == -1:
                self.assert_(res.spin[0].select)
                self.assertAlmostEqual(res.spin[0].j0, j0[index])
                self.assertAlmostEqual(res.spin[0].jwh, jwh[index])
                self.assertAlmostEqual(res.spin[0].jwx, jwx[index])
                index = index + 1

            # Other residues have insufficient data.
            else:
                self.assert_(not res.spin[0].select)


    def test_set_value(self):
        """The user function value.set()."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'jw_mapping_set_value.py')

        # Loop over residues.
        for res in residue_loop():
            self.assertAlmostEqual(res.spin[0].csa, N15_CSA)


    def test_mapping(self):
        """Test a complete jw mapping run using a script."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'jw_mapping.py')
