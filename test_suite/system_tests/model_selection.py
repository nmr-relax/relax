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
from generic_fns import pipes
from status import Status; status = Status()


class Modsel(SystemTestCase):
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
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'S2_0.970_te_2048_Rex_0.149'

        # Loop over the data pipes.
        for i in xrange(2):
            # Create the data pipe.
            self.interpreter.pipe.create(pipe_list[i], 'mf')

            # Read the sequence.
            self.interpreter.sequence.read(file='r1.600.out', dir=path, res_num_col=1, res_name_col=2)

            # Select the model.
            self.interpreter.model_free.select_model(model='m4')

            # Read the relaxation data.
            self.interpreter.relax_data.read('R1', '600', 600.0 * 1e6, 'r1.600.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
            self.interpreter.relax_data.read('R2', '600', 600.0 * 1e6, 'r2.600.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
            self.interpreter.relax_data.read('NOE', '600', 600.0 * 1e6, 'noe.600.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
            self.interpreter.relax_data.read('R1', '500', 500.0 * 1e6, 'r1.500.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
            self.interpreter.relax_data.read('R2', '500', 500.0 * 1e6, 'r2.500.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
            self.interpreter.relax_data.read('NOE', '500', 500.0 * 1e6, 'noe.500.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)

            # Set the diffusion tensors.
            self.interpreter.diffusion_tensor.init(tensors[i], fixed=False)

        # Get the data pipes.
        dp_sphere = pipes.get_pipe('sphere')
        dp_spheroid = pipes.get_pipe('spheroid')

        # Set some global stats.
        dp_sphere.chi2 = 200
        dp_spheroid.chi2 = 0

        # Model selection.
        self.interpreter.model_selection(method='AIC', modsel_pipe='aic')

        # Get the AIC data pipe.
        dp_aic = pipes.get_pipe('aic')

        # Test if the spheroid has been selected.
        self.assert_(hasattr(dp_aic, 'diff_tensor'))
        self.assertEqual(dp_aic.diff_tensor.type, 'spheroid')
