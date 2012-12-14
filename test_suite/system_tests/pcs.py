###############################################################################
#                                                                             #
# Copyright (C) 2011-2012 Edward d'Auvergne                                   #
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
"""PCS-based system tests."""


# Python module imports.
from os import sep

# relax module imports.
from generic_fns.mol_res_spin import count_spins, spin_loop
from status import Status; status = Status()
from test_suite.system_tests.base_classes import SystemTestCase


class Pcs(SystemTestCase):
    """Class for testing PCS operations."""

    def test_pcs_copy(self):
        """Test the operation of the pcs.copy user function."""

        # Create a data pipe.
        self.interpreter.pipe.create('orig', 'N-state')

        # Data directory.
        dir = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep

        # Load the spins.
        self.interpreter.sequence.read(file='pcs.txt', dir=dir, spin_name_col=1)
        self.interpreter.sequence.display()

        # Load the PCSs.
        self.interpreter.pcs.read(align_id='tb', file='pcs.txt', dir=dir, spin_name_col=1, data_col=2)
        self.interpreter.sequence.display()

        # The PCSs.
        pcs = [0.004, 0.008, 0.021, 0.029, 0.016, 0.010, 0.008, 0.003, 0.006, 0.003, 0.007, 0.005, 0.001, 0.070, None, 0.025, 0.098, 0.054, 0.075, 0.065, None, 0.070, 0.015, 0.098, 0.060, 0.120]

        # Create a new data pipe by copying the old, then switch to it.
        self.interpreter.pipe.copy(pipe_from='orig', pipe_to='new')
        self.interpreter.pipe.switch(pipe_name='new')

        # Delete the PCS data.
        self.interpreter.pcs.delete()

        # Copy the PCSs.
        self.interpreter.pcs.copy(pipe_from='orig', align_id='tb')

        # Checks.
        self.assertEqual(count_spins(), 26)
        self.assertEqual(len(cdp.interatomic), 0)
        i = 0
        for spin in spin_loop():
            self.assertEqual(pcs[i], spin.pcs['tb'])
            i += 1


    def test_pcs_load(self):
        """Test for the loading of some PCS data with the spin ID format."""

        # Create a data pipe.
        self.interpreter.pipe.create('test', 'N-state')

        # Data directory.
        dir = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep

        # Load the spins.
        self.interpreter.sequence.read(file='pcs.txt', dir=dir, spin_name_col=1)
        self.interpreter.sequence.display()

        # Load the PCSs.
        self.interpreter.pcs.read(align_id='tb', file='pcs.txt', dir=dir, spin_name_col=1, data_col=2)
        self.interpreter.sequence.display()

        # The PCSs.
        pcs = [0.004, 0.008, 0.021, 0.029, 0.016, 0.010, 0.008, 0.003, 0.006, 0.003, 0.007, 0.005, 0.001, 0.070, None, 0.025, 0.098, 0.054, 0.075, 0.065, None, 0.070, 0.015, 0.098, 0.060, 0.120]

        # Checks.
        self.assertEqual(count_spins(), 26)
        self.assertEqual(len(cdp.interatomic), 0)
        i = 0
        for spin in spin_loop():
            self.assertEqual(pcs[i], spin.pcs['tb'])
            i += 1
