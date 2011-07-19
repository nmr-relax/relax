###############################################################################
#                                                                             #
# Copyright (C) 2007-2011 Edward d'Auvergne                                   #
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
from math import pi

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns import pipes
from generic_fns.reset import reset
from relax_errors import RelaxError, RelaxNoPipeError, RelaxNoTensorError
from test_suite.unit_tests.base_classes import UnitTestCase


class Align_tensor_base_class(UnitTestCase):
    """Base class for the tests of the alignment tensor modules.

    This includes both the 'prompt.align_tensor' and 'generic_fns.align_tensor' modules.  This base class also contains many shared unit tests.
    """

    def setUp(self):
        """Set up for all the alignment tensor unit tests."""

        # Add a data pipe to the data store.
        ds.add(pipe_name='orig', pipe_type='mf')

        # Add a second data pipe for copying tests.
        ds.add(pipe_name='test', pipe_type='mf')

        # Set the current data pipe to 'orig'.
        pipes.switch('orig')


    def test_copy_pull(self):
        """Test the copying of an alignment tensor (pulling the data from another pipe).

        The functions tested are both generic_fns.align_tensor.copy() and
        prompt.align_tensor.copy().
        """

        # Initialise the tensor.
        self.align_tensor_fns.init(tensor='Pf1', params=(-16.6278, 6.13037, 7.65639, -1.89157, 19.2561), scale=1.0, angle_units='rad', param_types=0)

        # Change the current data pipe.
        pipes.switch('test')

        # Get the data pipe.
        dp = pipes.get_pipe('test')

        # Copy the tensor to the test pipe.
        self.align_tensor_fns.copy(tensor_from='Pf1', pipe_from='orig', tensor_to='Pf1')

        # Test the alignment tensor.
        self.assertEqual(dp.align_tensors[0].Sxx, -16.6278)
        self.assertEqual(dp.align_tensors[0].Syy, 6.13037)
        self.assertEqual(dp.align_tensors[0].Sxy, 7.65639)
        self.assertEqual(dp.align_tensors[0].Sxz, -1.89157)
        self.assertAlmostEqual(dp.align_tensors[0].Syz, 19.2561)


    def test_copy_push(self):
        """Test the copying of an alignment tensor (pushing the data from another pipe).

        The functions tested are both generic_fns.align_tensor.copy() and
        prompt.align_tensor.copy().
        """

        # Initialise the tensor.
        self.align_tensor_fns.init(tensor='Pf1', params=(-16.6278, 6.13037, 7.65639, -1.89157, 19.2561), scale=1.0, angle_units='rad', param_types=0)

        # Copy the tensor to the test pipe.
        self.align_tensor_fns.copy(tensor_from='Pf1', pipe_to='test', tensor_to='Pf1')

        # Get the data pipe.
        dp = pipes.get_pipe('test')

        # Test the alignment tensor.
        self.assertEqual(dp.align_tensors[0].Sxx, -16.6278)
        self.assertEqual(dp.align_tensors[0].Syy, 6.13037)
        self.assertEqual(dp.align_tensors[0].Sxy, 7.65639)
        self.assertEqual(dp.align_tensors[0].Sxz, -1.89157)
        self.assertAlmostEqual(dp.align_tensors[0].Syz, 19.2561)


    def test_copy_fail(self):
        """Test the failure of copying of an alignment tensor (target and source are the same).

        The functions tested are both generic_fns.align_tensor.copy() and
        prompt.align_tensor.copy().
        """

        # Initialise the tensor.
        self.align_tensor_fns.init(tensor='Pf1', params=(-16.6278, 6.13037, 7.65639, -1.89157, 19.2561), scale=1.0, angle_units='rad', param_types=0)

        # Copy the tensor to the test pipe.
        self.assertRaises(RelaxError, self.align_tensor_fns.copy, tensor_from='Pf1', tensor_to='Pf1')


    def test_delete(self):
        """Test the deletion of the alignment tensor data structure.

        The functions tested are both generic_fns.align_tensor.delete() and
        prompt.align_tensor.delete().
        """

        # Initialise the tensor.
        self.align_tensor_fns.init(tensor='Pf1', params=(-16.6278, 6.13037, 7.65639, -1.89157, 19.2561), scale=1.0, angle_units='rad', param_types=0)

        # Delete the tensor data.
        self.align_tensor_fns.delete(tensor='Pf1')

        # Get the data pipe.
        dp = pipes.get_pipe('test')

        # Test that Axx does not exist.
        self.failIf(hasattr(dp, 'align_tensors'))


    def test_delete_fail_no_data(self):
        """Failure of deletion of the alignment tensor data structure when there is no data.

        The functions tested are both generic_fns.align_tensor.delete() and
        prompt.align_tensor.delete().
        """

        # Try to delete the tensor data.
        self.assertRaises(RelaxNoTensorError, self.align_tensor_fns.delete, 'Pf1')


    def test_delete_fail_no_pipe(self):
        """Failure of deletion of the alignment tensor data structure when there is no data pipe.

        The functions tested are both generic_fns.align_tensor.delete() and
        prompt.align_tensor.delete().
        """

        # Reset relax.
        reset()

        # Try to delete the tensor data.
        self.assertRaises(RelaxNoPipeError, self.align_tensor_fns.delete, 'Pf1')


    def test_display(self):
        """Display an alignment tensor.

        The functions tested are both generic_fns.align_tensor.display() and
        prompt.align_tensor.display().
        """

        # Initialise the tensor.
        self.align_tensor_fns.init(tensor='Pf1', params=(-16.6278, 6.13037, 7.65639, -1.89157, 19.2561), scale=1.0, angle_units='rad', param_types=0)

        # Display the alignment tensor.
        self.align_tensor_fns.display(tensor='Pf1')


    def test_display_fail_no_data(self):
        """Failure of the display of the alignment tensor data structure when there is no data.

        The functions tested are both generic_fns.align_tensor.display() and
        prompt.align_tensor.display().
        """

        # Try to display the tensor data.
        self.assertRaises(RelaxNoTensorError, self.align_tensor_fns.display, 'Pf1')


    def test_display_fail_no_pipe(self):
        """Failure of the display of the alignment tensor data structure when there is no data pipe.

        The functions tested are both generic_fns.align_tensor.display() and
        prompt.align_tensor.display().
        """

        # Reset relax.
        reset()

        # Try to display the tensor data.
        self.assertRaises(RelaxNoPipeError, self.align_tensor_fns.display, 'Pf1')


    def test_init_bad_angle_units(self):
        """Test the failure of setting up a alignment tensor when angle_units is incorrect.

        The functions tested are both generic_fns.align_tensor.init() and
        prompt.align_tensor.init().
        """

        # Initialise the tensor.
        self.assertRaises(RelaxError, self.align_tensor_fns.init, tensor='Pf1', params=(-16.6278, 6.13037, 7.65639, -1.89157, 19.2561), angle_units='aaa')


    def test_init(self):
        """Test the setting up of an alignment tensor.

        The functions tested are both generic_fns.align_tensor.init() and
        prompt.align_tensor.init().
        """

        # Get the data pipe.
        dp = pipes.get_pipe('orig')

        # Initialise the tensor.
        self.align_tensor_fns.init(tensor='Pf1', params=(-16.6278, 6.13037, 7.65639, -1.89157, 19.2561), scale=1.0, angle_units='rad', param_types=0)

        # Test the alignment tensor.
        self.assertEqual(dp.align_tensors[0].Sxx, -16.6278)
        self.assertEqual(dp.align_tensors[0].Syy, 6.13037)
        self.assertEqual(dp.align_tensors[0].Sxy, 7.65639)
        self.assertEqual(dp.align_tensors[0].Sxz, -1.89157)
        self.assertAlmostEqual(dp.align_tensors[0].Syz, 19.2561)


    def test_matrix_angles_identity(self):
        """Test the matrix angles for a 5x5 identity matrix.

        The functions tested are both generic_fns.align_tensor.matrix_angles() and
        prompt.align_tensor.matrix_angles().
        """

        # Get the data pipe.
        dp = pipes.get_pipe('orig')

        # Initialise the 5 tensors.
        self.align_tensor_fns.init(tensor='1', params=(1, 0, 0, 0, 0))
        self.align_tensor_fns.init(tensor='2', params=(0, 1, 0, 0, 0))
        self.align_tensor_fns.init(tensor='3', params=(0, 0, 1, 0, 0))
        self.align_tensor_fns.init(tensor='4', params=(0, 0, 0, 1, 0))
        self.align_tensor_fns.init(tensor='5', params=(0, 0, 0, 0, 1))

        # Matrix angles.
        self.align_tensor_fns.matrix_angles()

        # Test the angles.
        self.assertEqual(dp.align_tensors.angles[0, 0], 0.0)
        self.assertEqual(dp.align_tensors.angles[0, 1], pi/2)
        self.assertEqual(dp.align_tensors.angles[0, 2], pi/2)
        self.assertEqual(dp.align_tensors.angles[0, 3], pi/2)
        self.assertEqual(dp.align_tensors.angles[0, 4], pi/2)

        self.assertEqual(dp.align_tensors.angles[1, 0], pi/2)
        self.assertEqual(dp.align_tensors.angles[1, 1], 0.0)
        self.assertEqual(dp.align_tensors.angles[1, 2], pi/2)
        self.assertEqual(dp.align_tensors.angles[1, 3], pi/2)
        self.assertEqual(dp.align_tensors.angles[1, 4], pi/2)

        self.assertEqual(dp.align_tensors.angles[2, 0], pi/2)
        self.assertEqual(dp.align_tensors.angles[2, 1], pi/2)
        self.assertEqual(dp.align_tensors.angles[2, 2], 0.0)
        self.assertEqual(dp.align_tensors.angles[2, 3], pi/2)
        self.assertEqual(dp.align_tensors.angles[2, 4], pi/2)

        self.assertEqual(dp.align_tensors.angles[3, 0], pi/2)
        self.assertEqual(dp.align_tensors.angles[3, 1], pi/2)
        self.assertEqual(dp.align_tensors.angles[3, 2], pi/2)
        self.assertEqual(dp.align_tensors.angles[3, 3], 0.0)
        self.assertEqual(dp.align_tensors.angles[3, 4], pi/2)

        self.assertEqual(dp.align_tensors.angles[4, 0], pi/2)
        self.assertEqual(dp.align_tensors.angles[4, 1], pi/2)
        self.assertEqual(dp.align_tensors.angles[4, 2], pi/2)
        self.assertEqual(dp.align_tensors.angles[4, 3], pi/2)
        self.assertEqual(dp.align_tensors.angles[4, 4], 0.0)


    def test_svd_identity(self):
        """Test the SVD and condition number for a 5x5 identity matrix.

        The functions tested are both generic_fns.align_tensor.svd() and
        prompt.align_tensor.svd().
        """

        # Get the data pipe.
        dp = pipes.get_pipe('orig')

        # Initialise the 5 tensors.
        self.align_tensor_fns.init(tensor='1', params=(1, 0, 0, 0, 0))
        self.align_tensor_fns.init(tensor='2', params=(0, 1, 0, 0, 0))
        self.align_tensor_fns.init(tensor='3', params=(0, 0, 1, 0, 0))
        self.align_tensor_fns.init(tensor='4', params=(0, 0, 0, 1, 0))
        self.align_tensor_fns.init(tensor='5', params=(0, 0, 0, 0, 1))

        # SVD.
        self.align_tensor_fns.svd()

        # Test the values
        self.assertEqual(dp.align_tensors.singular_vals[0], 1.0)
        self.assertEqual(dp.align_tensors.singular_vals[1], 1.0)
        self.assertEqual(dp.align_tensors.singular_vals[2], 1.0)
        self.assertEqual(dp.align_tensors.singular_vals[3], 1.0)
        self.assertEqual(dp.align_tensors.singular_vals[4], 1.0)
        self.assertEqual(dp.align_tensors.cond_num, 1.0)
