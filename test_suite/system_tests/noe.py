###############################################################################
#                                                                             #
# Copyright (C) 2006-2010 Edward d'Auvergne                                   #
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


class Noe(SystemTestCase):
    """Class for testing various aspects specific to the NOE analysis."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.interpreter.pipe.create('noe', 'noe')


    def tearDown(self):
        """Reset the relax data storage object."""

        ds.__reset__()


    def test_noe_analysis(self):
        """Test the NOE analysis."""

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'noe.py')

        # The real data.
        sat = [5050.0, 51643.0, 53663.0]
        ref = [148614.0, 166842.0, 128690.0]
        noe = [0.033980647852826784, 0.30953237194471417, 0.4169943274535706]
        noe_err = [0.02020329903276632, 0.2320024671657343, 0.026067523940084526]

        # Check the data.
        i = 0
        for spin in spin_loop():
            # Skip deselected spins.
            if not spin.select:
                continue

            # Check the intensity data.
            self.assertEqual(sat[i], spin.intensities['sat_ave'])
            self.assertEqual(ref[i], spin.intensities['ref_ave'])

            # Check the NOE data.
            self.assertEqual(noe[i], spin.noe)
            self.assertEqual(noe_err[i], spin.noe_err)

            # Increment the spin index.
            i += 1
