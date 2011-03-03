###############################################################################
#                                                                             #
# Copyright (C) 2011 Edward d'Auvergne                                        #
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

# relax module imports.
from base_classes import SystemTestCase
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.mol_res_spin import spin_loop
from status import Status; status = Status()


class Relax_data(SystemTestCase):
    """Class for testing various aspects specific to relaxation data back calculation."""

    def tearDown(self):
        """Reset the relax data storage object."""

        # Reset the relax data storage object.
        ds.__reset__()


    def test_back_calc(self):
        """Test the back calculation of relaxation data from model-free results."""

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
            # Check the back calculated data.
            self.assertEqual(spin.ri_data_bc, ri_data_bc[index])

            # Increment.
            index += 1


    def test_back_calc_specific(self):
        """Test the back calculation of specific relaxation data from model-free results."""

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
            # Check the back calculated data.
            self.assertEqual(spin.ri_data_bc, ri_data_bc[index])

            # Increment.
            index += 1


    def test_back_calc_new(self):
        """Test the back calculation of new relaxation data from model-free results."""

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
            # Check the back calculated data.
            self.assertEqual(spin.ri_data_bc, ri_data_bc[index])

            # Increment.
            index += 1
