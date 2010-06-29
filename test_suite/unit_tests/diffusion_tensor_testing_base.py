###############################################################################
#                                                                             #
# Copyright (C) 2007-2008 Edward d'Auvergne                                   #
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
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns import pipes
from relax_errors import RelaxError, RelaxNoPipeError, RelaxNoTensorError



class Diffusion_tensor_base_class:
    """Base class for the tests of the diffusion tensor modules.
    
    This includes both the 'prompt.diffusion_tensor' and 'generic_fns.diffusion_tensor' modules.
    The base class also contains many shared unit tests.
    """


    def setUp(self):
        """Set up for all the diffusion tensor unit tests."""

        # Reset the relax data storage object.
        ds.__reset__()

        # Add a data pipe to the data store.
        ds.add(pipe_name='orig', pipe_type='mf')

        # Add a second data pipe for copying tests.
        ds.add(pipe_name='test', pipe_type='mf')

        # Set the current data pipe to 'orig'.
        pipes.switch('orig')


    def tearDown(self):
        """Reset the relax data storage object."""

        ds.__reset__()


    def test_copy_pull_ellipsoid(self):
        """Test the copying of an ellipsoid diffusion tensor (pulling the data from another pipe).

        The functions tested are both generic_fns.diffusion_tensor.copy() and
        prompt.diffusion_tensor.copy().
        """

        # Initialise the tensor.
        self.diffusion_tensor_fns.init(params=(13.9, 1.8, 0.7, 10.6, -23.3, 0.34), time_scale=1e-9, d_scale=1e7, angle_units='rad', param_types=0, fixed=True)

        # Change the current data pipe.
        pipes.switch('test')

        # Get the data pipe.
        dp = pipes.get_pipe('test')

        # Copy the tensor to the test pipe.
        self.diffusion_tensor_fns.copy(pipe_from='orig')

        # Test the diffusion tensor.
        self.assertEqual(dp.diff_tensor.type, 'ellipsoid')
        self.assertAlmostEqual(dp.diff_tensor.tm * 1e9, 13.9, 14)
        self.assertEqual(dp.diff_tensor.Da, 1.8e7)
        self.assertEqual(dp.diff_tensor.Dr, 0.7)
        self.assertEqual(dp.diff_tensor.alpha, 1.1752220392306203)
        self.assertEqual(dp.diff_tensor.beta, 1.8327412287183442)
        self.assertEqual(dp.diff_tensor.gamma, 0.34)
        self.assertEqual(dp.diff_tensor.fixed, 1)


    def test_copy_pull_sphere(self):
        """Test the copying of a spherical diffusion tensor (pulling the data from another pipe).

        The functions tested are both generic_fns.diffusion_tensor.copy() and
        prompt.diffusion_tensor.copy().
        """

        # Initialise the tensor.
        self.diffusion_tensor_fns.init(params=1e-9)

        # Change the current data pipe.
        pipes.switch('test')

        # Get the data pipe.
        dp = pipes.get_pipe('test')

        # Copy the tensor to the test pipe.
        self.diffusion_tensor_fns.copy(pipe_from='orig')

        # Test the diffusion tensor 
        self.assertEqual(dp.diff_tensor.type, 'sphere')
        self.assertEqual(dp.diff_tensor.tm, 1e-9)
        self.assertEqual(dp.diff_tensor.fixed, 1)


    def test_copy_pull_spheroid(self):
        """Test the copying of a spheroidal diffusion tensor (pulling the data from another pipe).

        The functions tested are both generic_fns.diffusion_tensor.copy() and
        prompt.diffusion_tensor.copy().
        """

        # Initialise the tensor.
        self.diffusion_tensor_fns.init(params=(8.6, 1.3, 600, -20), time_scale=1e-9, d_scale=1e7, angle_units='deg', param_types=2, spheroid_type='prolate', fixed=False)

        # Change the current data pipe.
        pipes.switch('test')

        # Get the data pipe.
        dp = pipes.get_pipe('test')

        # Copy the tensor to the test pipe.
        self.diffusion_tensor_fns.copy(pipe_from='orig', pipe_to='test')

        # Test the diffusion tensor.
        self.assertEqual(dp.diff_tensor.type, 'spheroid')
        self.assertEqual(dp.diff_tensor.spheroid_type, 'prolate')
        self.assertAlmostEqual(dp.diff_tensor.tm * 1e9, 8.6, 14)
        self.assertEqual(dp.diff_tensor.Da, 5.2854122621564493e6)
        self.assertEqual(dp.diff_tensor.theta, 5.2359877559829879)
        self.assertEqual(dp.diff_tensor.phi, 1.0471975511965983)
        self.assertEqual(dp.diff_tensor.fixed, 0)


    def test_copy_push_ellipsoid(self):
        """Test the copying of an ellipsoid diffusion tensor (pushing the data from another pipe).

        The functions tested are both generic_fns.diffusion_tensor.copy() and
        prompt.diffusion_tensor.copy().
        """

        # Initialise the tensor.
        self.diffusion_tensor_fns.init(params=(13.9, 1.8, 0.7, 10.6, -23.3, 0.34), time_scale=1e-9, d_scale=1e7, angle_units='rad', param_types=0, fixed=True)

        # Copy the tensor to the test pipe.
        self.diffusion_tensor_fns.copy(pipe_to='test')

        # Get the data pipe.
        dp = pipes.get_pipe('test')

        # Test the diffusion tensor.
        self.assertEqual(dp.diff_tensor.type, 'ellipsoid')
        self.assertAlmostEqual(dp.diff_tensor.tm * 1e9, 13.9, 14)
        self.assertEqual(dp.diff_tensor.Da, 1.8e7)
        self.assertEqual(dp.diff_tensor.Dr, 0.7)
        self.assertEqual(dp.diff_tensor.alpha, 1.1752220392306203)
        self.assertEqual(dp.diff_tensor.beta, 1.8327412287183442)
        self.assertEqual(dp.diff_tensor.gamma, 0.34)
        self.assertEqual(dp.diff_tensor.fixed, 1)


    def test_copy_push_sphere(self):
        """Test the copying of a spherical diffusion tensor (pushing the data from another pipe).

        The functions tested are both generic_fns.diffusion_tensor.copy() and
        prompt.diffusion_tensor.copy().
        """

        # Initialise the tensor.
        self.diffusion_tensor_fns.init(params=1e-9)

        # Copy the tensor to the test pipe.
        self.diffusion_tensor_fns.copy(pipe_to='test')

        # Get the data pipe.
        dp = pipes.get_pipe('test')

        # Test the diffusion tensor 
        self.assertEqual(dp.diff_tensor.type, 'sphere')
        self.assertEqual(dp.diff_tensor.tm, 1e-9)
        self.assertEqual(dp.diff_tensor.fixed, 1)


    def test_copy_push_spheroid(self):
        """Test the copying of a spheroidal diffusion tensor (pushing the data from another pipe).

        The functions tested are both generic_fns.diffusion_tensor.copy() and
        prompt.diffusion_tensor.copy().
        """

        # Initialise the tensor.
        self.diffusion_tensor_fns.init(params=(8.6, 1.3, 600, -20), time_scale=1e-9, d_scale=1e7, angle_units='deg', param_types=2, spheroid_type='prolate', fixed=False)

        # Copy the tensor to the test pipe.
        self.diffusion_tensor_fns.copy(pipe_from='orig', pipe_to='test')

        # Get the data pipe.
        dp = pipes.get_pipe('test')

        # Test the diffusion tensor.
        self.assertEqual(dp.diff_tensor.type, 'spheroid')
        self.assertEqual(dp.diff_tensor.spheroid_type, 'prolate')
        self.assertAlmostEqual(dp.diff_tensor.tm * 1e9, 8.6, 14)
        self.assertEqual(dp.diff_tensor.Da, 5.2854122621564493e6)
        self.assertEqual(dp.diff_tensor.theta, 5.2359877559829879)
        self.assertEqual(dp.diff_tensor.phi, 1.0471975511965983)
        self.assertEqual(dp.diff_tensor.fixed, 0)


    def test_delete(self):
        """Test the deletion of the diffusion tensor data structure.

        The functions tested are both generic_fns.diffusion_tensor.delete() and
        prompt.diffusion_tensor.delete().
        """

        # Initialise the tensor.
        self.diffusion_tensor_fns.init(params=(8.6, 1.3, 600, -20), time_scale=1e-9, d_scale=1e7, angle_units='deg', param_types=2, spheroid_type='prolate', fixed=False)

        # Delete the tensor data.
        self.diffusion_tensor_fns.delete()

        # Get the data pipe.
        dp = pipes.get_pipe('test')

        # Test that the diff_tensor object does not exist.
        self.failIf(hasattr(dp, 'diff_tensor'))


    def test_delete_fail_no_data(self):
        """Failure of deletion of the diffusion tensor data structure when there is no data.

        The functions tested are both generic_fns.diffusion_tensor.delete() and
        prompt.diffusion_tensor.delete().
        """

        # Try to delete the tensor data.
        self.assertRaises(RelaxNoTensorError, self.diffusion_tensor_fns.delete)


    def test_delete_fail_no_pipe(self):
        """Failure of deletion of the diffusion tensor data structure when there is no data pipe.

        The functions tested are both generic_fns.diffusion_tensor.delete() and
        prompt.diffusion_tensor.delete().
        """

        # Reset the relax data store.
        ds.__reset__()

        # Try to delete the tensor data.
        self.assertRaises(RelaxNoPipeError, self.diffusion_tensor_fns.delete)


    def test_display_ellipsoid(self):
        """Display an ellipsoidal diffusion tensor.

        The functions tested are both generic_fns.diffusion_tensor.display() and
        prompt.diffusion_tensor.display().
        """

        # Initialise the tensor.
        self.diffusion_tensor_fns.init(params=(13.9, 1.8, 0.7, 10.6, -23.3, 0.34), time_scale=1e-9, d_scale=1e7, angle_units='rad', param_types=0, fixed=True)

        # Display the diffusion tensor.
        self.diffusion_tensor_fns.display()


    def test_display_fail_no_data(self):
        """Failure of the display of the diffusion tensor data structure when there is no data.

        The functions tested are both generic_fns.diffusion_tensor.display() and
        prompt.diffusion_tensor.display().
        """

        # Try to display the tensor data.
        self.assertRaises(RelaxNoTensorError, self.diffusion_tensor_fns.display)


    def test_display_fail_no_pipe(self):
        """Failure of the display of the diffusion tensor data structure when there is no data pipe.

        The functions tested are both generic_fns.diffusion_tensor.display() and
        prompt.diffusion_tensor.display().
        """

        # Reset the relax data store.
        ds.__reset__()

        # Try to display the tensor data.
        self.assertRaises(RelaxNoPipeError, self.diffusion_tensor_fns.display)


    def test_display_sphere(self):
        """Display a spherical diffusion tensor.

        The functions tested are both generic_fns.diffusion_tensor.display() and
        prompt.diffusion_tensor.display().
        """

        # Initialise the tensor.
        self.diffusion_tensor_fns.init(params=1e-9)

        # Display the diffusion tensor.
        self.diffusion_tensor_fns.display()


    def test_display_spheroid(self):
        """Display a spheroidal diffusion tensor.

        The functions tested are both generic_fns.diffusion_tensor.display() and
        prompt.diffusion_tensor.display().
        """

        # Initialise the tensor.
        self.diffusion_tensor_fns.init(params=(8.6, 1.3, 600, -20), time_scale=1e-9, d_scale=1e7, angle_units='deg', param_types=2, spheroid_type='prolate', fixed=False)

        # Display the diffusion tensor.
        self.diffusion_tensor_fns.display()



    def test_init_bad_angle_units(self):
        """Test the failure of setting up a diffusion tensor when angle_units is incorrect.

        The functions tested are both generic_fns.diffusion_tensor.init() and
        prompt.diffusion_tensor.init().
        """

        # Initialise the tensor.
        self.assertRaises(RelaxError, self.diffusion_tensor_fns.init, params=1e-9, angle_units='aaa')


    def test_init_ellipsoid(self):
        """Test the setting up of a ellipsoid diffusion tensor.

        The functions tested are both generic_fns.diffusion_tensor.init() and
        prompt.diffusion_tensor.init().
        """

        # Get the data pipe.
        dp = pipes.get_pipe('orig')

        # Initialise the tensor.
        self.diffusion_tensor_fns.init(params=(13.9, 1.8, 0.7, 10.6, -23.3, 0.34), time_scale=1e-9, d_scale=1e7, angle_units='rad', param_types=0, fixed=True)

        # Test the diffusion tensor.
        self.assertEqual(dp.diff_tensor.type, 'ellipsoid')
        self.assertAlmostEqual(dp.diff_tensor.tm * 1e9, 13.9, 14)
        self.assertEqual(dp.diff_tensor.Da, 1.8e7)
        self.assertEqual(dp.diff_tensor.Dr, 0.7)
        self.assertEqual(dp.diff_tensor.alpha, 1.1752220392306203)
        self.assertEqual(dp.diff_tensor.beta, 1.8327412287183442)
        self.assertEqual(dp.diff_tensor.gamma, 0.34)
        self.assertEqual(dp.diff_tensor.fixed, 1)


    def test_init_sphere(self):
        """Test the setting up of a spherical diffusion tensor.

        The functions tested are both generic_fns.diffusion_tensor.init() and
        prompt.diffusion_tensor.init().
        """

        # Get the data pipe.
        dp = pipes.get_pipe('orig')

        # Initialise the tensor.
        self.diffusion_tensor_fns.init(params=1e-9)

        # Test the diffusion tensor 
        self.assertEqual(dp.diff_tensor.type, 'sphere')
        self.assertEqual(dp.diff_tensor.tm, 1e-9)
        self.assertEqual(dp.diff_tensor.fixed, 1)


    def test_init_spheroid(self):
        """Test the setting up of a spheroidal diffusion tensor.

        The functions tested are both generic_fns.diffusion_tensor.init() and
        prompt.diffusion_tensor.init().
        """

        # Get the data pipe.
        dp = pipes.get_pipe('orig')

        # Initialise the tensor.
        self.diffusion_tensor_fns.init(params=(8.6, 1.3, 600, -20), time_scale=1e-9, d_scale=1e7, angle_units='deg', param_types=2, spheroid_type='prolate', fixed=False)

        # Test the diffusion tensor.
        self.assertEqual(dp.diff_tensor.type, 'spheroid')
        self.assertEqual(dp.diff_tensor.spheroid_type, 'prolate')
        self.assertAlmostEqual(dp.diff_tensor.tm * 1e9, 8.6, 14)
        self.assertEqual(dp.diff_tensor.Da, 5.2854122621564493e6)
        self.assertEqual(dp.diff_tensor.theta, 5.2359877559829879)
        self.assertEqual(dp.diff_tensor.phi, 1.0471975511965983)
        self.assertEqual(dp.diff_tensor.fixed, 0)
