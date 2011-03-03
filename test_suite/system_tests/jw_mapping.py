###############################################################################
#                                                                             #
# Copyright (C) 2006 Chris MacRaild                                           #
# Copyright (C) 2007-2011 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

# Python module imports.
from os import sep
import sys

# relax module imports.
from base_classes import SystemTestCase
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.mol_res_spin import residue_loop
from physical_constants import N15_CSA, NH_BOND_LENGTH
from status import Status; status = Status()


class Jw(SystemTestCase):
    """Class for testing various aspects specific to reduced spectral density mapping."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.interpreter.pipe.create('jw', 'jw')


    def tearDown(self):
        """Reset the relax data storage object."""

        ds.__reset__()


    def test_calc(self):
        """The spectral density calculation test."""

        # Data directory.
        dir = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'jw_mapping'+sep

        # The data.
        ri_ids = ['NOE_600', 'R1_600', 'R2_600']
        ri_type = ['NOE', 'R1', 'R2']
        frq = [600e6]*3
        data_paths = [dir + 'noe.dat', dir + 'R1.dat', dir + 'R2.dat']

        # Correct jw values:
        j0 = [4.0703318681008998e-09, 3.7739393907014834e-09]
        jwx = [1.8456254300773903e-10, 1.6347516082378241e-10]
        jwh = [1.5598167512718012e-12, 2.9480536599037041e-12]

        # Read the sequence.
        self.interpreter.sequence.read(file='test_seq', dir=status.install_path + sep+'test_suite'+sep+'shared_data', res_num_col=1, res_name_col=2)

        # Read the data.
        for i in xrange(len(ri_ids)):
            self.interpreter.relax_data.read(ri_id=ri_ids[i], ri_type=ri_type[i], frq=frq[i], file=data_paths[i], res_num_col=1, res_name_col=2, data_col=3, error_col=4)

        # Set r, csa, heteronucleus type, and proton type.
        self.interpreter.value.set(NH_BOND_LENGTH, 'bond_length')
        self.interpreter.value.set(N15_CSA, 'csa')
        self.interpreter.value.set('15N', 'heteronucleus')
        self.interpreter.value.set('1H', 'proton')

        # Select the frequency.
        self.interpreter.jw_mapping.set_frq(frq=600.0 * 1e6)

        # Try the reduced spectral density mapping.
        self.interpreter.calc()

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

        # Read the sequence.
        self.interpreter.sequence.read(file='test_seq', dir=status.install_path + sep+'test_suite'+sep+'shared_data', res_num_col=1, res_name_col=2)

        # Try to set the values.
        bond_length = NH_BOND_LENGTH
        csa = N15_CSA
        self.interpreter.value.set(bond_length, 'bond_length')
        self.interpreter.value.set(csa, 'csa')

        # Loop over residues.
        for res in residue_loop():
            self.assertEqual(res.spin[0].r, NH_BOND_LENGTH)
            self.assertEqual(res.spin[0].csa, N15_CSA)


    def test_mapping(self):
        """Test a complete jw mapping run using a script."""

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'jw_mapping.py')
