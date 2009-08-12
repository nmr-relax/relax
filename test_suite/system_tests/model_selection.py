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
from os import sep
import sys
from unittest import TestCase

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns import pipes


class Modsel(TestCase):
    """Class for testing model selection."""

    def tearDown(self):
        """Reset the relax data storage object."""

        ds.__reset__()


    def test_aic_mod_sel_diff_tensor(self):
        """AIC model selection between two diffusion tensors."""

        # Init.
        pipe_list = ['sphere', 'spheroid']
        tensors = [1e-9, (1e-9, 0, 0, 0)]

        # Path of the files.
        path = sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'S2_0.970_te_2048_Rex_0.149'

        # Loop over the data pipes.
        for i in xrange(2):
            # Create the data pipe.
            self.relax.interpreter._Pipe.create(pipe_list[i], 'mf')

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

        # Get the data pipes.
        dp_sphere = pipes.get_pipe('sphere')
        dp_spheroid = pipes.get_pipe('spheroid')

        # Set some global stats.
        dp_sphere.chi2 = 200
        dp_spheroid.chi2 = 0

        # Model selection.
        self.relax.interpreter._Modsel.model_selection(method='AIC', modsel_pipe='aic')

        # Get the AIC data pipe.
        dp_aic = pipes.get_pipe('aic')

        # Test if the spheroid has been selected.
        self.assert_(hasattr(dp_aic, 'diff_tensor'))
        self.assertEqual(dp_aic.diff_tensor.type, 'spheroid')
