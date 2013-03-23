###############################################################################
#                                                                             #
# Copyright (C) 2011-2013 Edward d'Auvergne                                   #
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
from pipe_control.mol_res_spin import spin_loop
from status import Status; status = Status()
from test_suite.system_tests.base_classes import SystemTestCase


class Relax_data(SystemTestCase):
    """Class for testing various aspects specific to relaxation data back calculation."""

    def test_back_calc(self):
        """Test the back calculation of relaxation data from model-free results (U{bug #14941<https://gna.org/bugs/?14941>})."""

        # Load the original state.
        self.interpreter.state.load(state='sphere_trunc', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'bug_14941_local_tm_global_selection')

        # Back calculate the relaxation data.
        self.interpreter.relax_data.back_calc()

        # The actual data.
        ri_data_bc = [{'R2_600': 4.7159538829340821, 'R1_500': 2.4779663389365068, 'NOE_500': 0.51989421750722165, 'R2_500': 4.3440970032224548, 'R1_600': 2.2831801922968129, 'NOE_600': 0.63592506242171432},
                      {'R2_600': 4.7211287713315739, 'R1_500': 2.5267468751446214, 'NOE_500': 0.57703969243842634, 'R2_500': 4.6185111669453738, 'R1_600': 2.2320234021052801, 'NOE_600': 0.66505178335932991}]

        # Loop over the spins.
        index = 0
        for spin in spin_loop():
            # Skip deselected protons.
            if not spin.select:
                continue

            # Check the back calculated data.
            self.assertEqual(spin.ri_data_bc, ri_data_bc[index])

            # Increment.
            index += 1


    def test_back_calc_specific(self):
        """Test the back calculation of specific relaxation data from model-free results (U{bug #14941<https://gna.org/bugs/?14941>})."""

        # Load the original state.
        self.interpreter.state.load(state='sphere_trunc', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'bug_14941_local_tm_global_selection')

        # Back calculate the relaxation data.
        self.interpreter.relax_data.back_calc('NOE_500')

        # The actual data.
        ri_data_bc = [{'NOE_500': 0.51989421750722165},
                      {'NOE_500': 0.57703969243842634}]

        # Loop over the spins.
        index = 0
        for spin in spin_loop():
            # Skip deselected protons.
            if not spin.select:
                continue

            # Check the back calculated data.
            self.assertEqual(spin.ri_data_bc, ri_data_bc[index])

            # Increment.
            index += 1


    def test_back_calc_new(self):
        """Test the back calculation of new relaxation data from model-free results (U{bug #14941<https://gna.org/bugs/?14941>})."""

        # Load the original state.
        self.interpreter.state.load(state='sphere_trunc', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'bug_14941_local_tm_global_selection')

        # Back calculate the relaxation data.
        self.interpreter.relax_data.back_calc('NOE_500.001', ri_type='NOE', frq=500.001e6)

        # The actual data.
        ri_data_bc = [{'NOE_500.001': 0.52064607759431081},
                      {'NOE_500.001': 0.57759452179767434}]

        # Loop over the spins.
        index = 0
        for spin in spin_loop():
            # Skip deselected protons.
            if not spin.select:
                continue

            # Check the back calculated data.
            self.assertEqual(spin.ri_data_bc, ri_data_bc[index])

            # Increment.
            index += 1


    def test_delete(self):
        """Test the relax_data.delete user function, replicating U{bug #19785<https://gna.org/bugs/?19785>}."""

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'bug_19785_relax_data_delete.py')

        # Switch to the first pipe.
        self.interpreter.pipe.switch('delete 1')

        # Checks.
        self.assertEqual(cdp.ri_ids, ['R1_900', 'NOE_900', 'R1_500', 'R2_500', 'NOE_500'])
        self.assert_(not 'R2_900' in cdp.frq)
        self.assert_(not 'R2_900' in cdp.ri_type)
        for spin in spin_loop():
            # Protons.
            if spin.name in ['H', 'HE1']:
                self.assert_(not hasattr(spin, 'ri_data'))

            # Nitrogens.
            else:
                self.assert_(not 'R2_900' in spin.ri_data)
                self.assert_(not 'R2_900' in spin.ri_data_err)

        # Switch to the second pipe.
        self.interpreter.pipe.switch('delete 2')

        # Checks.
        self.assert_(not hasattr(cdp, 'ri_ids'))
        self.assert_(not hasattr(cdp, 'frq'))
        self.assert_(not hasattr(cdp, 'ri_type'))
        for spin in spin_loop():
            self.assert_(not hasattr(spin, 'ri_data'))
            self.assert_(not hasattr(spin, 'ri_data_err'))


    def test_reset(self):
        """Test the relax_data.frq and relax_data.type user functions to reset the data."""

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_data_reset.py')

        # The data, as it should be.
        ids = ['R1_900', 'R2_900', 'NOE_900', 'R1_500', 'R2_500', 'NOE_500']
        frqs = [900100000, 900100000, 900100000, 400100000, 500*1e6, 500*1e6]
        types = ['R1', 'R2', 'R2', 'R1', 'R2', 'R2']

        # Checks.
        for i in range(len(ids)):
            self.assertEqual(cdp.ri_ids[i], ids[i])
            self.assertAlmostEqual(cdp.frq[ids[i]], frqs[i])
            self.assertEqual(cdp.ri_type[ids[i]], types[i])
