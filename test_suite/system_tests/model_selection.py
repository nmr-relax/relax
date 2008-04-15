###############################################################################
#                                                                             #
# Copyright (C) 2006-2008 Edward d'Auvergne                                   #
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
import sys
from unittest import TestCase

# relax module imports.
from data import Data as relax_data_store


class Modsel(TestCase):
    """Class for testing model selection."""

    def tearDown(self):
        """Reset the relax data storage object."""

        relax_data_store.__reset__()


    def test_diff(self):
        """AIC model selection between two diffusion tensors."""

        # Init.
        pipes = ['sphere', 'spheroid']
        tensors = [1e-9, (1e-9, 0, 0, 0)]

        # Path of the files.
        path = sys.path[-1] + '/test_suite/system_tests/data/model_free/S2_0.970_te_2048_Rex_0.149'

        # Loop over the data pipes.
        for i in xrange(2):
            # Create the data pipe.
            self.relax.interpreter._Pipe.create(pipes[i], 'mf')

            # Read the sequence.
            self.relax.interpreter._Sequence.read(file='r1.600.out', dir=path)

            # Select the model.
            self.relax.interpreter._Model_free.select_model(model='m4')

            # Read the relaxation data.
            self.relax.interpreter._Relax_data.read('R1', '600', 600.0 * 1e6, 'r1.600.out', dir=path)
            self.relax.interpreter._Relax_data.read('R2', '600', 600.0 * 1e6, 'r2.600.out', dir=path)
            self.relax.interpreter._Relax_data.read('NOE', '600', 600.0 * 1e6, 'noe.600.out', dir=path)
            self.relax.interpreter._Relax_data.read('R1', '500', 500.0 * 1e6, 'r1.500.out', dir=path)
            self.relax.interpreter._Relax_data.read('R2', '500', 500.0 * 1e6, 'r2.500.out', dir=path)
            self.relax.interpreter._Relax_data.read('NOE', '500', 500.0 * 1e6, 'noe.500.out', dir=path)

            # Set the diffusion tensors.
            self.relax.interpreter._Diffusion_tensor.init(tensors[i], fixed=False)

        # Set some global stats.
        relax_data_store['sphere'].chi2 = 200
        relax_data_store['spheroid'].chi2 = 0

        # Create the data pipe for model selection.
        self.relax.interpreter._Pipe.create('aic', 'mf')

        # Model selection.
        self.relax.interpreter._Modsel.model_selection(method='AIC')

        # Test if the spheroid has been selected.
        self.assert_(hasattr(relax_data_store['aic'], 'diff_tensor'))
        self.assertEqual(relax_data_store['aic'].diff.type, 'spheroid')
