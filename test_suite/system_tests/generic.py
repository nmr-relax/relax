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
import sys

# relax module imports.
from base_classes import SystemTestCase
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns import pipes


class Generic(SystemTestCase):
    """Class containing generic tests of relax execution."""

    def tearDown(self):
        """Reset the relax data storage object."""

        ds.__reset__()


    def test_value_diff(self):
        """S2 difference stored in a new data pipe."""

        # Init.
        pipe_list = ['orig1', 'orig2', 'new']
        s2 = [0.9, 0.7, None]

        # Loop over the data pipes to create and fill.
        for i in xrange(3):
            # Create the data pipe.
            self.interpreter.pipe.create(pipe_list[i], 'mf')

            # Load the Lupin Ap4Aase sequence.
            self.interpreter.sequence.read(file="Ap4Aase.seq", dir=sys.path[-1] + sep+'test_suite'+sep+'shared_data', res_num_col=1, res_name_col=2)

            # Only select residue 8.
            self.interpreter.select.spin(spin_id=':8', change_all=True)

            # Set the order parameter value.
            if s2[i]:
                self.interpreter.value.set(s2[i], 'S2', spin_id=':8')

        # Get the data pipes.
        dp_orig1 = pipes.get_pipe('orig1')
        dp_orig2 = pipes.get_pipe('orig2')
        dp_new = pipes.get_pipe('new')

        # Calculate the difference and assign it to residue 8 (located in position 7).
        diff = dp_orig1.mol[0].res[7].spin[0].s2 - dp_orig2.mol[0].res[7].spin[0].s2
        self.interpreter.value.set(diff, 'S2', spin_id=':8')

        # Test if the difference is 0.2!
        self.assertAlmostEqual(dp_new.mol[0].res[7].spin[0].s2, 0.2)


    def test_xh_vector_distribution(self):
        """Test the creation of a PDB representation of the distribution of XH bond vectors."""

        # Execute the script.
        self.interpreter.run(script_file=sys.path[-1] + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'xh_vector_dist.py')
