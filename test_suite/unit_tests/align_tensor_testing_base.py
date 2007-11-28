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
from relax_errors import RelaxError, RelaxNoPipeError, RelaxNoTensorError


class Align_tensor_base_class:
    """Base class for the tests of the alignment tensor modules.

    This includes both the 'prompt.align_tensor' and 'generic_fns.align_tensor' modules.
    This base class also contains many shared unit tests.
    """


    def setUp(self):
        """Set up for all the alignment tensor unit tests."""

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


    def test_copy_pull(self):
        """Test the copying of an alignment tensor (pulling the data from another pipe).

        The functions tested are both generic_fns.align_tensor.copy() and
        prompt.align_tensor.copy().
        """

        # Initialise the tensor.
        self.align_tensor_fns.init(tensor='Pf1', params=(-16.6278, 6.13037, 7.65639, -1.89157, 19.2561), scale=1.0, angle_units='rad', param_types=0)

        # Change the current data pipe.
        relax_data_store.current_pipe = 'test'

        # Copy the tensor to the test pipe.
        self.align_tensor_fns.copy(pipe_from='orig')

        # Test the alignment tensor.
        self.assertEqual(relax_data_store['test'].align_tensor.Axx, -16.6278)
        self.assertEqual(relax_data_store['test'].align_tensor.Ayy, 6.13037)
        self.assertEqual(relax_data_store['test'].align_tensor.Axy, 7.65639)
        self.assertEqual(relax_data_store['test'].align_tensor.Axz, -1.89157)
        self.assertEqual(relax_data_store['test'].align_tensor.Ayz, 19.2561)


    def test_copy_push(self):
        """Test the copying of an alignment tensor (pushing the data from another pipe).

        The functions tested are both generic_fns.align_tensor.copy() and
        prompt.align_tensor.copy().
        """

        # Initialise the tensor.
        self.align_tensor_fns.init(tensor='Pf1', params=(-16.6278, 6.13037, 7.65639, -1.89157, 19.2561), scale=1.0, angle_units='rad', param_types=0)

        # Copy the tensor to the test pipe.
        self.align_tensor_fns.copy(pipe_to='test')

        # Test the alignment tensor.
        self.assertEqual(relax_data_store['test'].align_tensor.Axx, -16.6278)
        self.assertEqual(relax_data_store['test'].align_tensor.Ayy, 6.13037)
        self.assertEqual(relax_data_store['test'].align_tensor.Axy, 7.65639)
        self.assertEqual(relax_data_store['test'].align_tensor.Axz, -1.89157)
        self.assertEqual(relax_data_store['test'].align_tensor.Ayz, 19.2561)


    def test_delete(self):
        """Test the deletion of the alignment tensor data structure.

        The functions tested are both generic_fns.align_tensor.delete() and
        prompt.align_tensor.delete().
        """

        # Initialise the tensor.
        self.align_tensor_fns.init(tensor='Pf1', params=(-16.6278, 6.13037, 7.65639, -1.89157, 19.2561), scale=1.0, angle_units='rad', param_types=0)

        # Delete the tensor data.
        self.align_tensor_fns.delete()

        # Test that Axx does not exist.
        self.failIf(hasattr(relax_data_store['orig'], 'align_tensor'))


    def test_delete_fail_no_data(self):
        """Failure of deletion of the alignment tensor data structure when there is no data.

        The functions tested are both generic_fns.align_tensor.delete() and
        prompt.align_tensor.delete().
        """

        # Try to delete the tensor data.
        self.assertRaises(RelaxNoTensorError, self.align_tensor_fns.delete)


    def test_delete_fail_no_pipe(self):
        """Failure of deletion of the alignment tensor data structure when there is no data pipe.

        The functions tested are both generic_fns.align_tensor.delete() and
        prompt.align_tensor.delete().
        """

        # Reset the relax data store.
        relax_data_store.__reset__()

        # Try to delete the tensor data.
        self.assertRaises(RelaxNoPipeError, self.align_tensor_fns.delete)


    def test_display(self):
        """Display an alignment tensor.

        The functions tested are both generic_fns.align_tensor.display() and
        prompt.align_tensor.display().
        """

        # Initialise the tensor.
        self.align_tensor_fns.init(tensor='Pf1', params=(-16.6278, 6.13037, 7.65639, -1.89157, 19.2561), scale=1.0, angle_units='rad', param_types=0)

        # Display the alignment tensor.
        self.align_tensor_fns.display()


    def test_display_fail_no_data(self):
        """Failure of the display of the alignment tensor data structure when there is no data.

        The functions tested are both generic_fns.align_tensor.display() and
        prompt.align_tensor.display().
        """

        # Try to display the tensor data.
        self.assertRaises(RelaxNoTensorError, self.align_tensor_fns.display)


    def test_display_fail_no_pipe(self):
        """Failure of the display of the alignment tensor data structure when there is no data pipe.

        The functions tested are both generic_fns.align_tensor.display() and
        prompt.align_tensor.display().
        """

        # Reset the relax data store.
        relax_data_store.__reset__()

        # Try to display the tensor data.
        self.assertRaises(RelaxNoPipeError, self.align_tensor_fns.display)


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

        # Initialise the tensor.
        self.align_tensor_fns.init(tensor='Pf1', params=(-16.6278, 6.13037, 7.65639, -1.89157, 19.2561), scale=1.0, angle_units='rad', param_types=0)

        # Test the alignment tensor.
        self.assertEqual(relax_data_store['orig'].align_tensor.Axx, -16.6278)
        self.assertEqual(relax_data_store['orig'].align_tensor.Ayy, 6.13037)
        self.assertEqual(relax_data_store['orig'].align_tensor.Axy, 7.65639)
        self.assertEqual(relax_data_store['orig'].align_tensor.Axz, -1.89157)
        self.assertEqual(relax_data_store['orig'].align_tensor.Ayz, 19.2561)
