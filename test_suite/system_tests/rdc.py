###############################################################################
#                                                                             #
# Copyright (C) 2011 Edward d'Auvergne                                        #
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
"""RDC-based system tests."""


# Python module imports.
from os import sep

# relax module imports.
from base_classes import SystemTestCase
from generic_fns.interatomic import interatomic_loop
from generic_fns.mol_res_spin import count_spins
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
        self.interpreter.sequence.attach_protons()
        self.interpreter.sequence.display()

        # Load the RDCs.
        self.interpreter.rdc.read(align_id='tb', file='tb.txt', dir=dir, spin_id1_col=1, spin_id2_col=2, data_col=3, error_col=4)
        self.interpreter.sequence.display()

        # The RDCs.
        rdcs = [ -26.2501958629, 9.93081766942, 7.26317614156, -1.24840526981, 5.31803314334, 14.0362909456, 1.33652530397, -1.6021670281]

        # Checks.
        self.assertEqual(count_spins(), 16)
        self.assertEqual(len(cdp.interatomic), 8)
        i = 0
        for interatom in interatomic_loop():
            self.assertAlmostEqual(rdcs[i], interatom.rdc['tb'])
            i += 1

