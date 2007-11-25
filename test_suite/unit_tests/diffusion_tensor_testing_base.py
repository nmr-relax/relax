###############################################################################
#                                                                             #
# Copyright (C) 2007 Edward d'Auvergne                                        #
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

# relax module imports.
from data import Data as relax_data_store
from relax_errors import RelaxError, RelaxNoPipeError, RelaxResSelectDisallowError, RelaxSpinSelectDisallowError



class Diffusion_tensor_base_class:
    """Base class for the tests of the diffusion tensor modules.
    
    This includes both the 'prompt.diffusion_tensor' and 'generic_fns.diffusion_tensor' modules.
    The base class also contains many shared unit tests.
    """


    def setUp(self):
        """Set up for all the diffusion tensor unit tests."""

        # Reset the relax data storage object.
        relax_data_store.__reset__()

        # Add a data pipe to the data store.
        relax_data_store.add(pipe_name='orig', pipe_type='mf')

        # Add a second data pipe for copying tests.
        relax_data_store.add(pipe_name='test', pipe_type='mf')

        # Set the current data pipe to 'orig'.
        relax_data_store.current_pipe = 'orig'


    def tearDown(self):
        """Reset the relax data storage object."""

        relax_data_store.__reset__()


    def test_init_bad_angle_units(self):
        """Test the failure of setting up a diffusion tensor when the angle_units is incorrect.

        The functions tested are both generic_fns.diffusion_tensor.init() and
        prompt.diffusion_tensor.init().
        """

        # Initialise the tensor.
        self.assertRaises(RelaxError, self.diffusion_tensor_fns.init, params=1e-9, angle_units='aaa')


    def test_init_sphere(self):
        """Test the setting up of a spherical diffusion tensor.

        The functions tested are both generic_fns.diffusion_tensor.init() and
        prompt.diffusion_tensor.init().
        """

        # Initialise the tensor.
        self.diffusion_tensor_fns.init(params=1e-9)

        # Test the diffusion tensor 
        self.assertEqual(relax_data_pipe['orig'].diff.type, 'sphere')
        self.assertEqual(relax_data_pipe['orig'].diff.tm, 1e-9)

