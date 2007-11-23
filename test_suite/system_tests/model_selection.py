###############################################################################
#                                                                             #
# Copyright (C) 2006-2007 Edward d'Auvergne                                   #
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

# relax module imports.
from data import Data as relax_data_store


# The relax data storage object.



class Modsel:
    def __init__(self, relax, test_name):
        """Class for testing model selection."""

        self.relax = relax

        # Diffusion tensor selection.
        if test_name == 'diff tensor':
            # The name of the test.
            self.name = "AIC model selection between two diffusion tensors"

            # The test.
            self.test = self.diff


    def diff(self, pipe):
        """The test of selecting between diffusion tensors using AIC."""

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
            self.relax.interpreter._Diffusion_tensor.init('sphere', tensors[i], fixed=0)

        # Set some global stats.
        relax_data_store['sphere'].chi2 = 200
        relax_data_store['spheroid'].chi2 = 0

        # Create the data pipe for model selection.
        self.relax.interpreter._Pipe.create('aic', 'mf')

        # Model selection.
        self.relax.interpreter._Modsel.model_selection(method='AIC')

        # Test if the spheroid has been selected.
        if not hasattr(relax_data_store['aic'], 'diff') or not relax_data_store['aic'].diff.type == 'spheroid':
            print "\nThe spheroid diffusion tensor has not been selected."
            return

        # Success.
        return 1
