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

# Module docstring.
"""RDC-based system tests."""


# Python module imports.
from os import sep

# relax module imports.
from base_classes import SystemTestCase
from generic_fns.mol_res_spin import count_spins, spin_loop
from status import Status; status = Status()


class Rdc(SystemTestCase):
    """Class for testing RDC operations."""

    def test_rdc_load(self):
        """Test for the loading of some RDC data with the spin ID format."""

        # Create a data pipe.
        self.interpreter.pipe.create('test', 'N-state')

        # Data directory.
        dir = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep

        # Load the spins.
        self.interpreter.sequence.read(file='tb.txt', dir=dir, spin_id_col=1)

        # Load the RDCs.
        self.interpreter.rdc.read(align_id='tb', file='tb.txt', dir=dir, spin_id_col=1, data_col=2, error_col=3)

        # The RDCs.
        rdcs = [ -26.2501958629, 9.93081766942, 7.26317614156, -1.24840526981, 5.31803314334, 14.0362909456, 1.33652530397, -1.6021670281]

        # Checks.
        self.assertEqual(count_spins(), 8)
        i = 0
        for spin in spin_loop():
            self.assertAlmostEqual(rdcs[i], spin.rdc['tb'])
            i += 1

